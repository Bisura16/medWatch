"""openFDA acquisition script.

Replaces the blocked drugs.com scraper with a real, large-scale pull
from the public openFDA REST API. Run as:

    OPENFDA_API_KEY=<your-key-here> .venv/bin/python -m anggota1.openfda.fetch

CLI tuning flags (see ``parse_args`` for the full list):

    --drugs FILE           Newline-separated drug names for adverse events.
    --max-drugs N          Cap how many drug names to query.
    --max-recall-pages N   Cap the number of recall pages (page = 1000).
    --skip-events          Skip the adverse-event pull.
    --skip-recalls         Skip the recall pull.

Hard rules enforced in this file:

- ``OPENFDA_API_KEY`` is read from the environment only. Its value is
  never echoed, never logged, never written to any file on disk. It
  is sent solely as the ``api_key`` query parameter to
  ``requests.get``.
- Polite delay of at least 250 ms between requests.
- Exponential backoff with jitter on HTTP 429 / 5xx (max 5 retries).
- 404 from openFDA is treated as an empty result (drug not present
  in the corpus); the run continues with the next drug.

Output files (schema preserved so existing consumers keep working):

    anggota1/data/drug_safety_data.json
    anggota1/data/drug_recalls.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Iterable

import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EVENT_ENDPOINT = "https://api.fda.gov/drug/event.json"
ENFORCEMENT_ENDPOINT = "https://api.fda.gov/drug/enforcement.json"

POLITE_DELAY_S = 0.25
RECALL_PAGE_SIZE = 1000
EVENT_COUNT_LIMIT = 25  # top N reactions per drug
MAX_RETRIES = 5

# Curated list of common Indonesian and global drug INNs (>= 50 names).
# Sourced from the WHO Essential Medicines List 2023 and BPOM
# common-use formularies for Faskes 1. Names are lowercase ASCII so they
# match the ``medicinalproduct`` field in openFDA, which is normalized
# to brand or INN by the FAERS submission process.
DEFAULT_DRUGS: list[str] = [
    # analgesics / NSAIDs
    "paracetamol", "acetaminophen", "ibuprofen", "aspirin", "naproxen",
    "diclofenac", "tramadol", "celecoxib", "meloxicam", "ketoprofen",
    "mefenamic acid",
    # antibiotics
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline",
    "cephalexin", "clindamycin", "metronidazole", "levofloxacin",
    "erythromycin", "ampicillin", "ceftriaxone", "cefixime",
    # antihistamines
    "cetirizine", "loratadine", "diphenhydramine", "fexofenadine",
    "chlorpheniramine",
    # antidepressants and anxiolytics
    "sertraline", "fluoxetine", "escitalopram", "amitriptyline",
    "alprazolam", "diazepam",
    # cardiovascular
    "amlodipine", "lisinopril", "losartan", "valsartan", "metoprolol",
    "atenolol", "captopril", "bisoprolol", "nifedipine", "furosemide",
    "spironolactone", "hydrochlorothiazide",
    # statins and antithrombotics
    "simvastatin", "atorvastatin", "rosuvastatin", "warfarin",
    "clopidogrel",
    # antidiabetics
    "metformin", "glipizide", "glimepiride", "sitagliptin", "insulin",
    "gliclazide",
    # gastric
    "omeprazole", "lansoprazole", "ranitidine", "pantoprazole",
    "famotidine", "domperidone", "ondansetron", "loperamide",
    # corticosteroids and respiratory
    "prednisone", "prednisolone", "dexamethasone", "salbutamol",
    "montelukast", "budesonide",
    # thyroid / others
    "levothyroxine", "allopurinol", "metoclopramide",
]


# ---------------------------------------------------------------------------
# Category mapping (same coarse buckets as anggota1.py for compatibility)
# ---------------------------------------------------------------------------

KATEGORI_MAP: dict[str, list[str]] = {
    "Antibiotik": [
        "amox", "azith", "cipro", "doxy", "ceph", "clinda", "metro",
        "levo", "eryth", "ampi", "ceft", "cefix",
    ],
    "Analgesik": [
        "ibu", "paracet", "acetam", "aspir", "napro", "diclo", "tramad",
        "cele", "melox", "keto", "mefen",
    ],
    "Antihistamin": ["ceti", "lorat", "diphen", "fexo", "chlorph"],
    "Antidepresan": ["sertr", "fluo", "escit", "amit", "alpraz", "diaze"],
    "Antihipertensi": [
        "amlo", "lisin", "losar", "valsa", "metop", "aten", "capto",
        "biso", "nife", "furos", "spiron", "hydroch",
    ],
    "Statin": ["simva", "atorva", "rosuva"],
    "Antitrombotik": ["warfa", "clopi"],
    "Antidiabetik": ["metfor", "glipi", "glime", "sita", "insul", "glicla"],
    "Saluran Cerna": [
        "omepra", "lansop", "raniti", "pantop", "famot", "domper",
        "ondan", "loper", "metoclo",
    ],
    "Kortikosteroid": ["predni", "dexam", "budeso"],
    "Saluran Napas": ["salbut", "monte"],
}


def tebak_kategori(nama: str) -> str:
    """Return a coarse therapeutic category for a drug name."""
    n = nama.lower()
    for kat, prefixes in KATEGORI_MAP.items():
        if any(p in n for p in prefixes):
            return kat
    if "thyrox" in n:
        return "Hormon Tiroid"
    if "allopu" in n:
        return "Anti-gout"
    return "Umum"


# ---------------------------------------------------------------------------
# HTTP helper with backoff
# ---------------------------------------------------------------------------

logger = logging.getLogger("openfda.fetch")


def _redact_params(params: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of params with the api_key value masked."""
    safe = dict(params)
    if "api_key" in safe:
        safe["api_key"] = "<redacted>"
    return safe


def fetch_json(
    url: str,
    params: dict[str, Any],
    *,
    timeout: int = 30,
    max_retries: int = MAX_RETRIES,
) -> dict[str, Any] | None:
    """GET ``url`` with backoff and return parsed JSON.

    Returns None on 404 (openFDA returns 404 when a ``search`` matches
    zero documents) or on permanent failure. Logs the redacted URL.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            resp = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            logger.warning(
                "request error %s (attempt %d) for %s params=%s",
                exc, attempt, url, _redact_params(params),
            )
            if attempt >= max_retries:
                return None
            time.sleep(_backoff_seconds(attempt))
            continue

        status = resp.status_code

        if status == 200:
            try:
                return resp.json()
            except ValueError:
                logger.warning("invalid JSON from %s", url)
                return None

        if status == 404:
            return None

        if status == 429 or 500 <= status < 600:
            if attempt >= max_retries:
                logger.warning(
                    "giving up after %d retries on %s status=%d",
                    attempt, url, status,
                )
                return None
            wait = _backoff_seconds(attempt)
            logger.info(
                "backoff %.1fs after status=%d on %s (attempt %d)",
                wait, status, url, attempt,
            )
            time.sleep(wait)
            continue

        # 4xx other than 404: do not retry
        logger.warning(
            "non-retryable status=%d on %s params=%s",
            status, url, _redact_params(params),
        )
        return None


def _backoff_seconds(attempt: int) -> float:
    """Exponential backoff with jitter, capped at 30 s."""
    base = min(30.0, 0.5 * (2 ** (attempt - 1)))
    return base + random.uniform(0.0, 0.5)


# ---------------------------------------------------------------------------
# Severity mapping
# ---------------------------------------------------------------------------

def _severity_from_event_aggregate(
    *,
    serious_fraction: float,
    death_fraction: float,
) -> str:
    """Map FAERS seriousness aggregate to the project's severity bucket.

    The project schema uses three Indonesian buckets: ``ringan``,
    ``sedang``, ``serius``. The mapping below is conservative.
    """
    if death_fraction > 0.05 or serious_fraction >= 0.70:
        return "serius"
    if serious_fraction >= 0.30:
        return "sedang"
    return "ringan"


# ---------------------------------------------------------------------------
# Adverse-event pull
# ---------------------------------------------------------------------------

def fetch_adverse_events_for_drug(
    drug_name: str,
    api_key: str | None,
) -> dict[str, Any] | None:
    """Fetch adverse-event aggregate for a single drug.

    Strategy: one ``count=patient.reaction.reactionmeddrapt.exact``
    call (top reactions), plus one ``count=serious`` call for the same
    drug query (serious vs non-serious distribution), plus one
    ``count=seriousnessdeath`` call (fatal fraction). All three are
    combined into the record we write to disk.
    """
    base_search = f'patient.drug.medicinalproduct:"{drug_name}"'
    common_params: dict[str, Any] = {"search": base_search}
    if api_key:
        common_params["api_key"] = api_key

    # 1) Top reactions
    params_react = dict(common_params, count="patient.reaction.reactionmeddrapt.exact",
                        limit=EVENT_COUNT_LIMIT)
    src_react = _build_source_url(EVENT_ENDPOINT, params_react)
    j_react = fetch_json(EVENT_ENDPOINT, params_react)
    time.sleep(POLITE_DELAY_S)
    if not j_react:
        return None
    reactions = [
        str(r.get("term", "")).title()
        for r in j_react.get("results", [])
        if r.get("term")
    ]
    if not reactions:
        return None

    # 2) Total report count for this drug (for accurate fractions)
    params_total = dict(common_params, limit=1)
    j_total = fetch_json(EVENT_ENDPOINT, params_total)
    time.sleep(POLITE_DELAY_S)
    total_reports = 0
    if j_total:
        total_reports = int(
            j_total.get("meta", {}).get("results", {}).get("total", 0)
        )
    if total_reports <= 0:
        total_reports = sum(int(r.get("count", 0)) for r in j_react.get("results", []))

    # 3) Seriousness distribution (1=serious, 2=non-serious in FAERS)
    serious_fraction = 0.0
    params_serious = dict(common_params, count="serious")
    j_serious = fetch_json(EVENT_ENDPOINT, params_serious)
    time.sleep(POLITE_DELAY_S)
    if j_serious and total_reports > 0:
        counts = {str(r.get("term")): int(r.get("count", 0))
                  for r in j_serious.get("results", [])}
        # FAERS encodes 1 = serious, 2 = non-serious. Fraction is over
        # the union of reports that populated the field; the union
        # itself approximates total_reports closely.
        union = sum(counts.values()) or 1
        serious_fraction = counts.get("1", 0) / union

    # 4) Death fraction over the whole drug-specific report population
    # (seriousnessdeath is only populated when a report flagged death,
    # so dividing the death-count by total_reports gives the true
    # population-level fatal fraction).
    death_fraction = 0.0
    params_death = dict(common_params, count="seriousnessdeath")
    j_death = fetch_json(EVENT_ENDPOINT, params_death)
    time.sleep(POLITE_DELAY_S)
    if j_death and total_reports > 0:
        counts = {str(r.get("term")): int(r.get("count", 0))
                  for r in j_death.get("results", [])}
        death_fraction = counts.get("1", 0) / total_reports

    severity = _severity_from_event_aggregate(
        serious_fraction=serious_fraction,
        death_fraction=death_fraction,
    )

    warnings_text = (
        f"Berdasarkan {total_reports} laporan FAERS untuk "
        f"{drug_name}, fraksi laporan serius {serious_fraction:.0%}, "
        f"fraksi laporan kematian {death_fraction:.1%}. Konsultasikan "
        "dengan tenaga kesehatan dan rujuk monograph BPOM atau "
        "FDA Drugs sebelum digunakan."
    )

    return {
        "drug_name": drug_name.title(),
        "category": tebak_kategori(drug_name),
        "side_effects": reactions,
        "severity_level": severity,
        "warnings": warnings_text,
        "source_url": src_react,
    }


# ---------------------------------------------------------------------------
# Recall pull
# ---------------------------------------------------------------------------

_RECALL_DATE_RE = ("%Y%m%d",)


def _parse_recall_date(raw: str | None) -> str:
    """Normalize ``recall_initiation_date`` (YYYYMMDD) to ISO."""
    if not raw:
        return ""
    raw = str(raw).strip()
    # openFDA returns YYYYMMDD as 8 digits, no separators
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    # already ISO
    if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
        return raw
    return ""


def _coerce_classification(value: str | None) -> str:
    if not value:
        return "Unknown"
    v = value.strip()
    if v in ("Class I", "Class II", "Class III"):
        return v
    upper = v.upper()
    if "CLASS I" in upper and "CLASS II" not in upper and "CLASS III" not in upper:
        return "Class I"
    if "CLASS II" in upper and "CLASS III" not in upper:
        return "Class II"
    if "CLASS III" in upper:
        return "Class III"
    return v


def fetch_drug_recalls(
    api_key: str | None,
    *,
    max_pages: int = 26,
    page_size: int = RECALL_PAGE_SIZE,
) -> list[dict[str, Any]]:
    """Page through ``/drug/enforcement`` and return normalized records."""
    out: list[dict[str, Any]] = []
    for page in range(max_pages):
        skip = page * page_size
        params: dict[str, Any] = {
            "limit": page_size,
            "skip": skip,
            # Sort newest first; older records still useful but newest
            # are more representative of current safety signals.
            "sort": "recall_initiation_date:desc",
        }
        if api_key:
            params["api_key"] = api_key

        logger.info("recall page %d/%d (skip=%d)", page + 1, max_pages, skip)
        body = fetch_json(ENFORCEMENT_ENDPOINT, params)
        time.sleep(POLITE_DELAY_S)
        if not body:
            logger.info("recall page %d returned no body, stopping", page + 1)
            break

        results = body.get("results", [])
        if not results:
            logger.info("recall page %d empty, stopping", page + 1)
            break

        for rec in results:
            out.append({
                "product_name": str(rec.get("product_description") or "")[:240],
                "reason": str(rec.get("reason_for_recall") or "Detail tidak tersedia")[:500],
                "recall_date": _parse_recall_date(rec.get("recall_initiation_date")),
                "severity_class": _coerce_classification(rec.get("classification")),
                "company": str(rec.get("recalling_firm") or "Tidak diketahui")[:200],
            })

        # Stop early if we got fewer records than the page size (final page).
        if len(results) < page_size:
            logger.info("recall short page (%d) detected, stopping", len(results))
            break

    return out


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------

def _build_source_url(endpoint: str, params: dict[str, Any]) -> str:
    """Return a URL-shaped string for traceability, with key redacted."""
    redacted = _redact_params(params)
    pairs = []
    for k, v in redacted.items():
        pairs.append(f"{k}={v}")
    return f"{endpoint}?{'&'.join(pairs)}"


def load_drug_list(path: Path | None) -> list[str]:
    if path is None:
        return list(DEFAULT_DRUGS)
    if not path.exists():
        raise FileNotFoundError(f"--drugs file not found: {path}")
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            names.append(s)
    if not names:
        raise ValueError(f"--drugs file is empty: {path}")
    return names


def write_json(path: Path, records: Iterable[dict[str, Any]]) -> int:
    data = list(records)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(data)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="openFDA real large-scale data acquisition for MedWatch.",
    )
    p.add_argument("--drugs", type=Path, default=None,
                   help="Newline-separated drug names (defaults to bundled list).")
    p.add_argument("--max-drugs", type=int, default=0,
                   help="Cap on number of drug names to query (0 = no cap).")
    p.add_argument("--max-recall-pages", type=int, default=26,
                   help="Maximum recall pages to pull (page_size=1000).")
    p.add_argument("--skip-events", action="store_true",
                   help="Skip adverse-event acquisition.")
    p.add_argument("--skip-recalls", action="store_true",
                   help="Skip recall acquisition.")
    p.add_argument("--log-level", default="INFO",
                   help="Python logging level (DEBUG/INFO/WARNING).")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    api_key = os.environ.get("OPENFDA_API_KEY", "").strip() or None
    if api_key:
        logger.info("OPENFDA_API_KEY present (length=%d); using authenticated rate limit", len(api_key))
    else:
        logger.warning("OPENFDA_API_KEY not set; falling back to unauthenticated quota")

    safety_count = 0
    if not args.skip_events:
        drugs = load_drug_list(args.drugs)
        if args.max_drugs and args.max_drugs > 0:
            drugs = drugs[: args.max_drugs]
        logger.info("adverse-event pull starts for %d drug names", len(drugs))
        safety_records: list[dict[str, Any]] = []
        for i, drug in enumerate(drugs, 1):
            logger.info("[%d/%d] %s", i, len(drugs), drug)
            rec = fetch_adverse_events_for_drug(drug, api_key)
            if rec is None:
                logger.info("  no FAERS data for %s, skipping", drug)
                continue
            safety_records.append(rec)
        out_safety = DATA_DIR / "drug_safety_data.json"
        safety_count = write_json(out_safety, safety_records)
        total_reaction_terms = sum(len(r.get("side_effects", [])) for r in safety_records)
        logger.info(
            "adverse-event pull wrote %d drug records, %d total reaction terms -> %s",
            safety_count, total_reaction_terms, out_safety,
        )
        print(
            f"adverse_events_drugs={safety_count} "
            f"adverse_events_total_terms={total_reaction_terms} "
            f"file={out_safety}"
        )
    else:
        logger.info("--skip-events set; not pulling adverse events")

    recall_count = 0
    if not args.skip_recalls:
        logger.info("recall pull starts (max_pages=%d)", args.max_recall_pages)
        recall_records = fetch_drug_recalls(
            api_key, max_pages=args.max_recall_pages, page_size=RECALL_PAGE_SIZE,
        )
        out_recalls = DATA_DIR / "drug_recalls.json"
        recall_count = write_json(out_recalls, recall_records)
        logger.info("recall pull wrote %d records -> %s", recall_count, out_recalls)
        print(f"recalls={recall_count} file={out_recalls}")
    else:
        logger.info("--skip-recalls set; not pulling recalls")

    print(
        f"\nselesai. drug_safety_data={safety_count} entri, "
        f"drug_recalls={recall_count} entri"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
