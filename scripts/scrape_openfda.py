"""openFDA prescription-drug scraper.

Pulls drug/ndc.json, drug/label.json (per NDC), drug/event.json (per generic name),
and drug/enforcement.json into a single SQLite database with FTS5.

Resumable via a checkpoint table. Reads OPENFDA_API_KEY from env, never logs it.

Part of the MedWatch Windows installer data bundle (openFDA prescription drug scrape).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Iterator

import requests

API_BASE = "https://api.fda.gov"
ENDPOINT_DRUGS = "drugs"
ENDPOINT_REACTIONS = "reactions"
ENDPOINT_RECALLS = "recalls"
ALL_ENDPOINTS = (ENDPOINT_DRUGS, ENDPOINT_REACTIONS, ENDPOINT_RECALLS)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, "anggota1", "Hasil-Scrap", "drugs.db")
CHECKPOINT_DB_PATH = os.path.join(REPO_ROOT, ".scrape-cache", "scrape_checkpoint.sqlite")
PROGRESS_JSONL = os.path.join(REPO_ROOT, ".scrape-cache", "scrape_progress.jsonl")

REQUEST_DELAY_SEC = 0.2
MAX_BACKOFF_SEC = 60.0
REQUEST_TIMEOUT_SEC = 60
USER_AGENT = "MedWatch-OpenFDA-Scraper/1.0 (POLBAN)"

# Page size for paged endpoints (drugs/recalls).
PAGE_LIMIT = 1000

# Top-N reactions per generic.
REACTIONS_PER_GENERIC = 20


# ---------------------------------------------------------------------------
# Logging helpers (stderr only; never prints the API key).
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Write a one-line progress message to stderr with a UTC timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stderr.write(f"[{ts}] {msg}\n")
    sys.stderr.flush()


def write_progress(event: dict[str, Any]) -> None:
    """Append a single JSON line to the progress journal."""
    os.makedirs(os.path.dirname(PROGRESS_JSONL), exist_ok=True)
    event = dict(event)
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with open(PROGRESS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# API key + HTTP session.
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Read OPENFDA_API_KEY from env. Never returned to logs."""
    key = os.environ.get("OPENFDA_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "OPENFDA_API_KEY is not set in the environment. "
            "Export it before running this scraper."
        )
    return key


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return session


def redact_url(url: str) -> str:
    """Strip api_key parameter from a URL for safe logging."""
    parsed = urllib.parse.urlsplit(url)
    qs = [
        (k, v) for k, v in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() != "api_key"
    ]
    safe_query = urllib.parse.urlencode(qs)
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, safe_query, parsed.fragment)
    )


# ---------------------------------------------------------------------------
# HTTP with retry and rate-limit handling.
# ---------------------------------------------------------------------------

class FdaHttp:
    """Thin wrapper that adds api_key, rate limiting, and backoff."""

    def __init__(self, session: requests.Session, api_key: str) -> None:
        self._session = session
        self._api_key = api_key
        self.request_count = 0

    def fetch(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        full_url: str | None = None,
    ) -> tuple[dict[str, Any] | None, requests.Response | None]:
        """Make one GET request. Returns (json_body, response).

        json_body is None when the API responds 404 (no matches). For all
        other non-2xx outcomes a SystemExit is raised after exhausting
        retries.
        """
        if full_url is not None:
            url = full_url
            # Ensure api_key is present even when following a Link header.
            if "api_key=" not in url:
                joiner = "&" if "?" in url else "?"
                url = f"{url}{joiner}api_key={self._api_key}"
        else:
            base = f"{API_BASE}{path}"
            qparams = dict(params or {})
            qparams["api_key"] = self._api_key
            url = f"{base}?{urllib.parse.urlencode(qparams, safe=':\"+(),')}"

        backoff = 1.0
        attempts = 0
        while True:
            attempts += 1
            try:
                resp = self._session.get(url, timeout=REQUEST_TIMEOUT_SEC)
            except requests.RequestException as exc:
                if attempts >= 6:
                    raise SystemExit(
                        f"HTTP error after {attempts} attempts for "
                        f"{redact_url(url)}: {exc}"
                    )
                log(f"network error attempt {attempts}: {exc}; sleeping {backoff:.1f}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF_SEC)
                continue

            self.request_count += 1
            time.sleep(REQUEST_DELAY_SEC)

            if resp.status_code == 200:
                try:
                    return resp.json(), resp
                except ValueError as exc:
                    raise SystemExit(
                        f"Invalid JSON from {redact_url(url)}: {exc}"
                    )

            if resp.status_code == 404:
                # openFDA returns 404 when zero documents match; treat as
                # empty rather than an error.
                return None, resp

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempts >= 8:
                    raise SystemExit(
                        f"openFDA returned {resp.status_code} after "
                        f"{attempts} attempts for {redact_url(url)}"
                    )
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait = min(float(retry_after), MAX_BACKOFF_SEC)
                    except ValueError:
                        wait = backoff
                else:
                    wait = backoff
                log(
                    f"openFDA {resp.status_code} attempt {attempts}; "
                    f"sleeping {wait:.1f}s ({redact_url(url)})"
                )
                time.sleep(wait)
                backoff = min(backoff * 2, MAX_BACKOFF_SEC)
                continue

            raise SystemExit(
                f"openFDA returned {resp.status_code} for {redact_url(url)}"
            )


LINK_NEXT_RE = re.compile(r"<([^>]+)>\s*;\s*rel=\"next\"", re.IGNORECASE)


def extract_next_link(resp: requests.Response | None) -> str | None:
    """Pull the rel=next URL from a Link header, or None."""
    if resp is None:
        return None
    link = resp.headers.get("Link") or resp.headers.get("link")
    if not link:
        return None
    match = LINK_NEXT_RE.search(link)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# SQLite setup.
# ---------------------------------------------------------------------------

DRUGS_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS drugs (
  product_ndc TEXT PRIMARY KEY,
  brand_name TEXT,
  generic_name TEXT,
  manufacturer TEXT,
  route TEXT,
  dosage_form TEXT,
  indications TEXT,
  contraindications TEXT,
  warnings TEXT,
  adverse_reactions TEXT,
  dosage_administration TEXT,
  pregnancy TEXT,
  pediatric_use TEXT,
  application_number TEXT,
  product_type TEXT,
  scraped_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_drugs_generic_name ON drugs(generic_name);
CREATE INDEX IF NOT EXISTS idx_drugs_brand_name ON drugs(brand_name);
CREATE INDEX IF NOT EXISTS idx_drugs_application_number ON drugs(application_number);

CREATE TABLE IF NOT EXISTS reactions (
  generic_name TEXT,
  reaction_term TEXT,
  count INTEGER,
  scraped_at TEXT,
  PRIMARY KEY (generic_name, reaction_term)
);

CREATE INDEX IF NOT EXISTS idx_reactions_generic ON reactions(generic_name);

CREATE TABLE IF NOT EXISTS recalls (
  recall_number TEXT PRIMARY KEY,
  product_ndc TEXT,
  classification TEXT,
  status TEXT,
  reason TEXT,
  recall_initiation_date TEXT,
  scraped_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_recalls_ndc ON recalls(product_ndc);

CREATE VIRTUAL TABLE IF NOT EXISTS drugs_fts USING fts5(
  product_ndc UNINDEXED,
  brand_name,
  generic_name,
  indications,
  contraindications,
  warnings,
  adverse_reactions,
  content='drugs',
  content_rowid='rowid'
);
"""

CHECKPOINT_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS checkpoint (
  endpoint TEXT PRIMARY KEY,
  last_cursor TEXT,
  last_ts TEXT,
  records_fetched INTEGER,
  status TEXT
);
"""


def open_drugs_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.executescript(DRUGS_SCHEMA)
    return conn


def open_checkpoint_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(CHECKPOINT_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(CHECKPOINT_DB_PATH, timeout=30)
    conn.executescript(CHECKPOINT_SCHEMA)
    return conn


def upsert_checkpoint(
    conn: sqlite3.Connection,
    endpoint: str,
    last_cursor: str | None,
    records_fetched: int,
    status: str,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO checkpoint(endpoint, last_cursor, last_ts, records_fetched, status) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(endpoint) DO UPDATE SET "
        "  last_cursor = excluded.last_cursor, "
        "  last_ts = excluded.last_ts, "
        "  records_fetched = excluded.records_fetched, "
        "  status = excluded.status",
        (endpoint, last_cursor, now, records_fetched, status),
    )
    conn.commit()


def get_checkpoint(
    conn: sqlite3.Connection, endpoint: str
) -> tuple[str | None, int, str | None]:
    row = conn.execute(
        "SELECT last_cursor, records_fetched, status FROM checkpoint WHERE endpoint = ?",
        (endpoint,),
    ).fetchone()
    if row is None:
        return None, 0, None
    return row[0], int(row[1] or 0), row[2]


# ---------------------------------------------------------------------------
# Field extraction helpers.
# ---------------------------------------------------------------------------

def first_str(value: Any) -> str | None:
    """Pull the first string out of a value that may be list / scalar / None."""
    if value is None:
        return None
    if isinstance(value, list):
        for item in value:
            text = first_str(item)
            if text:
                return text
        return None
    if isinstance(value, dict):
        return None
    text = str(value).strip()
    return text or None


def join_strs(value: Any, sep: str = "; ") -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return sep.join(parts) or None
    text = str(value).strip()
    return text or None


def extract_ndc_row(record: dict[str, Any]) -> dict[str, Any] | None:
    """Map a /drug/ndc.json record to a partial drugs row (no label fields)."""
    product_ndc = first_str(record.get("product_ndc"))
    if not product_ndc:
        return None
    openfda = record.get("openfda") or {}
    brand = first_str(record.get("brand_name")) or first_str(openfda.get("brand_name"))
    generic = first_str(record.get("generic_name")) or first_str(openfda.get("generic_name"))
    manufacturer = (
        first_str(record.get("labeler_name"))
        or first_str(openfda.get("manufacturer_name"))
    )
    route = join_strs(record.get("route")) or join_strs(openfda.get("route"))
    dosage_form = first_str(record.get("dosage_form")) or first_str(openfda.get("dosage_form"))
    application_number = (
        first_str(record.get("application_number"))
        or first_str(openfda.get("application_number"))
    )
    product_type = first_str(record.get("product_type")) or first_str(openfda.get("product_type"))
    return {
        "product_ndc": product_ndc,
        "brand_name": brand,
        "generic_name": generic,
        "manufacturer": manufacturer,
        "route": route,
        "dosage_form": dosage_form,
        "application_number": application_number,
        "product_type": product_type,
    }


LABEL_FIELDS = {
    "indications": "indications_and_usage",
    "contraindications": "contraindications",
    "warnings": None,  # special: warnings or warnings_and_cautions
    "adverse_reactions": "adverse_reactions",
    "dosage_administration": "dosage_and_administration",
    "pregnancy": "pregnancy",
    "pediatric_use": "pediatric_use",
}


def extract_label_fields(record: dict[str, Any]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for column, src_key in LABEL_FIELDS.items():
        if column == "warnings":
            value = record.get("warnings") or record.get("warnings_and_cautions")
        else:
            value = record.get(src_key)
        out[column] = join_strs(value, sep="\n\n")
    return out


# ---------------------------------------------------------------------------
# Drugs scrape.
# ---------------------------------------------------------------------------

def _build_drugs_url_from_cursor(cursor: str | None, api_key: str) -> tuple[str | None, dict | None, str | None]:
    """If cursor is a stored Link URL, return it as full_url; else None."""
    if cursor and cursor.startswith("http"):
        return cursor, None, None
    return None, None, None


def scrape_drugs(
    http: FdaHttp,
    conn: sqlite3.Connection,
    chk_conn: sqlite3.Connection,
    limit_records: int | None,
) -> int:
    """Drugs pass: paginate /drug/ndc.json, dedupe, insert rows, then label-enrich."""

    last_cursor, records_fetched, status = get_checkpoint(chk_conn, ENDPOINT_DRUGS)
    if status == "complete":
        log("drugs endpoint already marked complete; skipping ndc pass")
    else:
        log(f"drugs pass starting (resume cursor present: {bool(last_cursor)})")
        upsert_checkpoint(chk_conn, ENDPOINT_DRUGS, last_cursor, records_fetched, "in_progress")

        # Dedupe lookup populated on the fly: (generic, dosage_form, route) -> lowest ndc.
        dedupe: dict[tuple[str, str, str], str] = {}
        existing_keys = conn.execute(
            "SELECT product_ndc, COALESCE(generic_name,''), COALESCE(dosage_form,''), COALESCE(route,'') "
            "FROM drugs"
        ).fetchall()
        for ndc, gen, form, route in existing_keys:
            dedupe[(gen, form, route)] = ndc

        start_time = time.monotonic()
        cursor_url = last_cursor if last_cursor and last_cursor.startswith("http") else None
        page_index = 0
        while True:
            if cursor_url:
                body, resp = http.fetch("", full_url=cursor_url)
            else:
                params = {
                    "search": 'finished:true AND product_type:"HUMAN PRESCRIPTION DRUG"',
                    "limit": PAGE_LIMIT,
                }
                body, resp = http.fetch("/drug/ndc.json", params=params)
            page_index += 1

            if not body:
                log("drugs pass: empty body; ending pagination")
                break

            results = body.get("results") or []
            if not results:
                log("drugs pass: results list empty; ending pagination")
                break

            with conn:
                for record in results:
                    row = extract_ndc_row(record)
                    if not row:
                        continue
                    key = (
                        row.get("generic_name") or "",
                        row.get("dosage_form") or "",
                        row.get("route") or "",
                    )
                    incumbent = dedupe.get(key)
                    if incumbent is None or row["product_ndc"] < incumbent:
                        if incumbent and incumbent != row["product_ndc"]:
                            conn.execute(
                                "DELETE FROM drugs WHERE product_ndc = ?",
                                (incumbent,),
                            )
                        dedupe[key] = row["product_ndc"]
                        conn.execute(
                            "INSERT OR REPLACE INTO drugs("
                            " product_ndc, brand_name, generic_name, manufacturer, "
                            " route, dosage_form, application_number, product_type, scraped_at"
                            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                row["product_ndc"],
                                row["brand_name"],
                                row["generic_name"],
                                row["manufacturer"],
                                row["route"],
                                row["dosage_form"],
                                row["application_number"],
                                row["product_type"],
                                datetime.now(timezone.utc).isoformat(),
                            ),
                        )

            records_fetched += len(results)
            next_url = extract_next_link(resp)

            elapsed = max(time.monotonic() - start_time, 0.001)
            rate_per_min = (http.request_count / elapsed) * 60.0
            log(
                f"drugs pass: page {page_index}, fetched {records_fetched} total, "
                f"rate {rate_per_min:.1f} req/min"
            )
            write_progress({
                "endpoint": ENDPOINT_DRUGS,
                "records_so_far": records_fetched,
                "rate_req_per_min": round(rate_per_min, 2),
                "page": page_index,
            })

            upsert_checkpoint(
                chk_conn,
                ENDPOINT_DRUGS,
                next_url,
                records_fetched,
                "in_progress" if next_url else "ndc_done",
            )

            if limit_records is not None and records_fetched >= limit_records:
                log(f"drugs pass: hit limit-records cap at {records_fetched}")
                break

            if not next_url:
                log("drugs pass: no next link; ndc pagination complete")
                break

            cursor_url = next_url

        upsert_checkpoint(chk_conn, ENDPOINT_DRUGS, "label_pending", records_fetched, "in_progress")

    # ------------------------------------------------------------------
    # Label enrichment pass: one request per unique application_number when
    # available, otherwise per NDC. Results applied to all rows sharing the
    # application_number.
    # ------------------------------------------------------------------
    log("drugs pass: label enrichment starting")
    rows = conn.execute(
        "SELECT product_ndc, application_number FROM drugs "
        "WHERE indications IS NULL AND warnings IS NULL"
    ).fetchall()
    log(f"label enrichment targets: {len(rows)} drug rows")

    # Group NDCs by application_number (None grouped individually).
    by_app: dict[str | None, list[str]] = {}
    for ndc, app in rows:
        by_app.setdefault(app, []).append(ndc)

    enriched_count = 0
    for app, ndc_list in by_app.items():
        # Fetch one representative NDC for each app group.
        primary_ndc = ndc_list[0]
        params = {
            "search": f'openfda.product_ndc.exact:"{primary_ndc}"',
            "limit": 1,
        }
        body, _ = http.fetch("/drug/label.json", params=params)
        fields = {col: None for col in LABEL_FIELDS}
        if body and body.get("results"):
            fields = extract_label_fields(body["results"][0])

        with conn:
            for ndc in ndc_list:
                conn.execute(
                    "UPDATE drugs SET "
                    " indications = COALESCE(?, indications), "
                    " contraindications = COALESCE(?, contraindications), "
                    " warnings = COALESCE(?, warnings), "
                    " adverse_reactions = COALESCE(?, adverse_reactions), "
                    " dosage_administration = COALESCE(?, dosage_administration), "
                    " pregnancy = COALESCE(?, pregnancy), "
                    " pediatric_use = COALESCE(?, pediatric_use) "
                    "WHERE product_ndc = ?",
                    (
                        fields["indications"],
                        fields["contraindications"],
                        fields["warnings"],
                        fields["adverse_reactions"],
                        fields["dosage_administration"],
                        fields["pregnancy"],
                        fields["pediatric_use"],
                        ndc,
                    ),
                )
                enriched_count += 1

        if enriched_count % 500 == 0:
            log(f"label enrichment progress: {enriched_count} rows updated")
            write_progress({
                "endpoint": ENDPOINT_DRUGS,
                "phase": "label_enrichment",
                "records_so_far": enriched_count,
            })

    log(f"label enrichment complete: {enriched_count} drug rows touched")

    # Rebuild FTS once after enrichment.
    log("rebuilding drugs_fts index")
    conn.execute("INSERT INTO drugs_fts(drugs_fts) VALUES('rebuild')")
    conn.commit()

    drugs_count = conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
    upsert_checkpoint(chk_conn, ENDPOINT_DRUGS, None, drugs_count, "complete")
    write_progress({"endpoint": ENDPOINT_DRUGS, "status": "complete", "rows": drugs_count})
    return drugs_count


# ---------------------------------------------------------------------------
# Reactions scrape.
# ---------------------------------------------------------------------------

def scrape_reactions(
    http: FdaHttp,
    conn: sqlite3.Connection,
    chk_conn: sqlite3.Connection,
    limit_records: int | None,
) -> int:
    """One request per unique generic_name; store top N reactions."""
    last_cursor, records_fetched, status = get_checkpoint(chk_conn, ENDPOINT_REACTIONS)
    if status == "complete":
        log("reactions endpoint already marked complete; skipping")
        return conn.execute("SELECT COUNT(*) FROM reactions").fetchone()[0]

    upsert_checkpoint(chk_conn, ENDPOINT_REACTIONS, last_cursor, records_fetched, "in_progress")

    generics = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT generic_name FROM drugs "
            "WHERE generic_name IS NOT NULL AND TRIM(generic_name) <> '' "
            "ORDER BY generic_name"
        ).fetchall()
        if row[0]
    ]
    if limit_records is not None:
        generics = generics[:limit_records]
    log(f"reactions pass: {len(generics)} unique generic names")

    # Skip ones we have already processed when resuming.
    completed_generics = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT generic_name FROM reactions"
        ).fetchall()
    }
    remaining = [g for g in generics if g not in completed_generics]
    log(f"reactions pass: {len(remaining)} generics still to fetch")

    start_time = time.monotonic()
    rows_written = 0
    for idx, generic in enumerate(remaining, start=1):
        params = {
            "search": f'patient.drug.openfda.generic_name.exact:"{generic}"',
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": REACTIONS_PER_GENERIC,
        }
        body, _ = http.fetch("/drug/event.json", params=params)
        if not body or not body.get("results"):
            continue

        now = datetime.now(timezone.utc).isoformat()
        with conn:
            for entry in body["results"]:
                term = first_str(entry.get("term"))
                count = entry.get("count")
                if not term or count is None:
                    continue
                conn.execute(
                    "INSERT OR REPLACE INTO reactions("
                    " generic_name, reaction_term, count, scraped_at"
                    ") VALUES (?, ?, ?, ?)",
                    (generic, term, int(count), now),
                )
                rows_written += 1

        records_fetched += 1
        if idx % 100 == 0 or idx == len(remaining):
            elapsed = max(time.monotonic() - start_time, 0.001)
            rate = (http.request_count / elapsed) * 60.0
            log(
                f"reactions pass: {idx}/{len(remaining)} generics done; "
                f"{rows_written} rows; rate {rate:.1f} req/min"
            )
            write_progress({
                "endpoint": ENDPOINT_REACTIONS,
                "records_so_far": rows_written,
                "rate_req_per_min": round(rate, 2),
                "generics_done": idx,
            })
            upsert_checkpoint(chk_conn, ENDPOINT_REACTIONS, generic, rows_written, "in_progress")

    final = conn.execute("SELECT COUNT(*) FROM reactions").fetchone()[0]
    upsert_checkpoint(chk_conn, ENDPOINT_REACTIONS, None, final, "complete")
    write_progress({"endpoint": ENDPOINT_REACTIONS, "status": "complete", "rows": final})
    return final


# ---------------------------------------------------------------------------
# Recalls scrape.
# ---------------------------------------------------------------------------

def scrape_recalls(
    http: FdaHttp,
    conn: sqlite3.Connection,
    chk_conn: sqlite3.Connection,
    limit_records: int | None,
) -> int:
    last_cursor, records_fetched, status = get_checkpoint(chk_conn, ENDPOINT_RECALLS)
    if status == "complete":
        log("recalls endpoint already marked complete; skipping")
        return conn.execute("SELECT COUNT(*) FROM recalls").fetchone()[0]

    upsert_checkpoint(chk_conn, ENDPOINT_RECALLS, last_cursor, records_fetched, "in_progress")

    start_time = time.monotonic()
    cursor_url = last_cursor if last_cursor and last_cursor.startswith("http") else None
    page_index = 0
    inserted = 0
    while True:
        if cursor_url:
            body, resp = http.fetch("", full_url=cursor_url)
        else:
            params = {
                "search": 'product_type:"Drugs"',
                "limit": PAGE_LIMIT,
            }
            body, resp = http.fetch("/drug/enforcement.json", params=params)
        page_index += 1

        if not body:
            log("recalls pass: empty body; ending pagination")
            break
        results = body.get("results") or []
        if not results:
            log("recalls pass: results empty; ending pagination")
            break

        now = datetime.now(timezone.utc).isoformat()
        with conn:
            for record in results:
                recall_number = first_str(record.get("recall_number"))
                if not recall_number:
                    continue
                openfda = record.get("openfda") or {}
                product_ndc = first_str(openfda.get("product_ndc"))
                conn.execute(
                    "INSERT OR IGNORE INTO recalls("
                    " recall_number, product_ndc, classification, status, "
                    " reason, recall_initiation_date, scraped_at"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        recall_number,
                        product_ndc,
                        first_str(record.get("classification")),
                        first_str(record.get("status")),
                        first_str(record.get("reason_for_recall")),
                        first_str(record.get("recall_initiation_date")),
                        now,
                    ),
                )
                inserted += 1

        records_fetched += len(results)
        next_url = extract_next_link(resp)
        elapsed = max(time.monotonic() - start_time, 0.001)
        rate = (http.request_count / elapsed) * 60.0
        log(
            f"recalls pass: page {page_index}, {records_fetched} fetched, "
            f"{inserted} insert calls; rate {rate:.1f} req/min"
        )
        write_progress({
            "endpoint": ENDPOINT_RECALLS,
            "records_so_far": records_fetched,
            "rate_req_per_min": round(rate, 2),
            "page": page_index,
        })
        upsert_checkpoint(
            chk_conn,
            ENDPOINT_RECALLS,
            next_url,
            records_fetched,
            "in_progress" if next_url else "complete",
        )

        if limit_records is not None and records_fetched >= limit_records:
            log(f"recalls pass: hit limit-records cap at {records_fetched}")
            break
        if not next_url:
            log("recalls pass: no next link; pagination complete")
            break
        cursor_url = next_url

    final = conn.execute("SELECT COUNT(*) FROM recalls").fetchone()[0]
    upsert_checkpoint(chk_conn, ENDPOINT_RECALLS, None, final, "complete")
    write_progress({"endpoint": ENDPOINT_RECALLS, "status": "complete", "rows": final})
    return final


# ---------------------------------------------------------------------------
# Verify and status commands.
# ---------------------------------------------------------------------------

def cmd_verify() -> int:
    if not os.path.exists(DB_PATH):
        log(f"verify: db not found at {DB_PATH}")
        return 1
    conn = sqlite3.connect(DB_PATH)
    try:
        drugs_n = conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
        reactions_n = conn.execute("SELECT COUNT(*) FROM reactions").fetchone()[0]
        recalls_n = conn.execute("SELECT COUNT(*) FROM recalls").fetchone()[0]
        fts_pain_n = conn.execute(
            "SELECT COUNT(*) FROM drugs_fts WHERE drugs_fts MATCH 'pain'"
        ).fetchone()[0]
        sample = conn.execute(
            "SELECT product_ndc, brand_name, generic_name FROM drugs LIMIT 3"
        ).fetchall()
        idx_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type = 'index' AND name LIKE 'idx_%'"
        ).fetchone()[0]
        size_bytes = os.path.getsize(DB_PATH)
        log("verify report:")
        log(f"  db path: {DB_PATH}")
        log(f"  size: {size_bytes / (1024 * 1024):.2f} MB")
        log(f"  drugs rows: {drugs_n}")
        log(f"  reactions rows: {reactions_n}")
        log(f"  recalls rows: {recalls_n}")
        log(f"  indexes named idx_*: {idx_count}")
        log(f"  drugs_fts MATCH 'pain' rows: {fts_pain_n}")
        for row in sample:
            log(f"  sample drug: {row}")
        return 0
    finally:
        conn.close()


def cmd_status() -> int:
    if not os.path.exists(CHECKPOINT_DB_PATH):
        log(f"status: no checkpoint db at {CHECKPOINT_DB_PATH}")
        return 0
    conn = sqlite3.connect(CHECKPOINT_DB_PATH)
    try:
        rows = conn.execute(
            "SELECT endpoint, status, records_fetched, last_ts, "
            " CASE WHEN last_cursor IS NULL THEN '(none)' ELSE 'present' END "
            "FROM checkpoint ORDER BY endpoint"
        ).fetchall()
        log("checkpoint status:")
        for row in rows:
            log(f"  {row[0]} status={row[1]} fetched={row[2]} last_ts={row[3]} cursor={row[4]}")
        return 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main entrypoint.
# ---------------------------------------------------------------------------

def cmd_scrape(endpoint: str, limit_records: int | None) -> int:
    api_key = load_api_key()
    session = make_session()
    http = FdaHttp(session, api_key)
    conn = open_drugs_db()
    chk_conn = open_checkpoint_db()

    try:
        if endpoint in (ENDPOINT_DRUGS, "all"):
            drugs_n = scrape_drugs(http, conn, chk_conn, limit_records)
            log(f"drugs final rows: {drugs_n}")
        if endpoint in (ENDPOINT_REACTIONS, "all"):
            reactions_n = scrape_reactions(http, conn, chk_conn, limit_records)
            log(f"reactions final rows: {reactions_n}")
        if endpoint in (ENDPOINT_RECALLS, "all"):
            recalls_n = scrape_recalls(http, conn, chk_conn, limit_records)
            log(f"recalls final rows: {recalls_n}")
    finally:
        with contextlib.suppress(Exception):
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
        chk_conn.close()

    log(f"scrape complete; total openFDA requests: {http.request_count}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="openFDA prescription-drug scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scrape = sub.add_parser("scrape", help="Run the scraper for one or all endpoints")
    p_scrape.add_argument(
        "--endpoint",
        choices=["drugs", "reactions", "recalls", "all"],
        required=True,
    )
    p_scrape.add_argument(
        "--limit-records",
        type=int,
        default=None,
        help="Cap records fetched per endpoint (smoke testing).",
    )

    sub.add_parser("verify", help="Run sanity checks against the output db.")
    sub.add_parser("status", help="Print the checkpoint table.")

    args = parser.parse_args(argv)
    if args.command == "scrape":
        return cmd_scrape(args.endpoint, args.limit_records)
    if args.command == "verify":
        return cmd_verify()
    if args.command == "status":
        return cmd_status()
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
