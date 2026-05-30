"""SQLite-backed drug catalog loader for the bundled drugs.db.

The desktop build ships a real openFDA-derived SQLite database
(``drugs.db``) with a ``drugs`` table (one row per NDC), an FTS5
index (``drugs_fts``), a ``reactions`` table (FAERS counts), and a
``recalls`` table (enforcement reports). This module reads that
database read-only and maps every row into the same dict shape the
rest of the backend already speaks (the anggota4 catalog schema:
``nama_obat``, ``alias``, ``kategori``, ``bahan_aktif``, ...), so the
existing routes and the frontend keep working unchanged while the
data source moves from a 6-row JSON file to the full catalog.

Path resolution order:
    1. ``MEDWATCH_DB_PATH`` / ``MEDWATCH_DB_PATH_RESOLVED`` (set by the
       Electron desktop launcher).
    2. A local development fallback at
       ``<repo>/anggota1/Hasil-Scrap/drugs.db``.
    3. ``None`` when neither exists, in which case :func:`available`
       returns ``False`` and callers fall back to the anggota4 JSON.

Every connection is opened read-only (``mode=ro``) and per-call, so
the loader is safe under Flask's threaded request handling and never
mutates the shipped database.
"""
import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .config import BASE_DIR

logger = logging.getLogger(__name__)

_DEV_FALLBACK = BASE_DIR / "anggota1" / "Hasil-Scrap" / "drugs.db"

# How many list items each long free-text label field is split into,
# and the max characters kept per item, so list payloads stay small.
_MAX_LIST_ITEMS = 12
_MAX_ITEM_CHARS = 400
_INGREDIENT_SPLIT = re.compile(r"\s+and\s+|[,/;+]", re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?:\r?\n|•|;|\.\s+(?=[A-Z]))")


def db_path() -> Optional[str]:
    """Return the resolved drugs.db path, or ``None`` when unavailable."""
    env = os.environ.get("MEDWATCH_DB_PATH_RESOLVED") or os.environ.get("MEDWATCH_DB_PATH")
    if env and Path(env).exists():
        return env
    if _DEV_FALLBACK.exists():
        return str(_DEV_FALLBACK)
    return None


def _connect() -> Optional[sqlite3.Connection]:
    """Open a fresh read-only connection with a row factory, or ``None``."""
    path = db_path()
    if not path:
        return None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.warning("drugs.db open failed: %s", e)
        return None


_available_cache: Optional[bool] = None


def available() -> bool:
    """Return ``True`` when a queryable drugs.db with a ``drugs`` table exists.

    The result is memoised for the process lifetime so the cheap-but-
    repeated check does not reopen the database on every request.
    """
    global _available_cache
    if _available_cache is not None:
        return _available_cache
    conn = _connect()
    if not conn:
        _available_cache = False
        return False
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM sqlite_master WHERE type='table' AND name='drugs'"
        ).fetchone()
        _available_cache = bool(row and row["n"])
    except sqlite3.Error:
        _available_cache = False
    finally:
        conn.close()
    return _available_cache


def _clean(text: Optional[str]) -> str:
    """Collapse whitespace in a free-text field; return ``""`` for ``None``."""
    return re.sub(r"\s+", " ", (text or "").strip())


def _to_list(text: Optional[str]) -> list[str]:
    """Split a long openFDA label field into a short, clean list of items."""
    if not text:
        return []
    parts = [p.strip(" .;:-•\t") for p in _SENTENCE_SPLIT.split(text)]
    out: list[str] = []
    seen: set[str] = set()
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        if len(p) > _MAX_ITEM_CHARS:
            p = p[:_MAX_ITEM_CHARS].rsplit(" ", 1)[0] + "..."
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
        if len(out) >= _MAX_LIST_ITEMS:
            break
    return out


def _ingredients(generic_name: Optional[str]) -> list[str]:
    """Derive a deduped active-ingredient list from a generic name string."""
    if not generic_name:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for part in _INGREDIENT_SPLIT.split(generic_name):
        name = part.strip().title()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def _kategori(route: Optional[str]) -> str:
    """Map the openFDA administration route into a display category."""
    r = _clean(route)
    if not r:
        return "Lainnya"
    return r.split(";")[0].strip().title()


def _map_light(row: sqlite3.Row) -> dict[str, Any]:
    """Map a drugs row into the light catalog shape (no long text fields)."""
    generic = _clean(row["generic_name"])
    brand = _clean(row["brand_name"])
    nama = generic or brand or "(tanpa nama)"
    alias = [brand] if brand and brand.lower() != nama.lower() else []
    return {
        "nama_obat": nama,
        "alias": alias,
        "kategori": _kategori(row["route"]),
        "bahan_aktif": _ingredients(generic),
        "produsen": _clean(row["manufacturer"]),
        "rute": _kategori(row["route"]),
        "bentuk_sediaan": _clean(row["dosage_form"]).title(),
        "product_ndc": row["product_ndc"],
        "sumber": "openFDA",
    }


def _map_catalog(row: sqlite3.Row) -> dict[str, Any]:
    """Map a row into the catalog list shape (BackendDrug-compatible).

    Includes the fields the frontend catalog card and client-side search
    need (name, class, ingredients, a short indication and warning), but
    keeps long label text out so the full-catalog payload stays small.
    """
    base = _map_light(row)
    indikasi = _to_list(row["indications"])
    peringatan = _to_list(row["warnings"])
    base.update({
        "indikasi": [indikasi[0][:200]] if indikasi else [],
        "dosis_umum": _clean(row["dosage_administration"])[:120],
        "peringatan": [peringatan[0][:200]] if peringatan else [],
        "interaksi": [],
    })
    return base


def _map_full(row: sqlite3.Row, conn: sqlite3.Connection) -> dict[str, Any]:
    """Map a drugs row into the full detail shape (anggota4-compatible)."""
    base = _map_light(row)
    generic = _clean(row["generic_name"])
    base.update({
        "indikasi": _to_list(row["indications"]),
        "dosis_umum": _clean(row["dosage_administration"])[:_MAX_ITEM_CHARS],
        "kehamilan": _clean(row["pregnancy"])[:_MAX_ITEM_CHARS],
        "peringatan": _to_list(row["warnings"]),
        "kontraindikasi": _to_list(row["contraindications"]),
        "interaksi": [],
        "efek_samping": _to_list(row["adverse_reactions"]),
        "nomor_aplikasi": _clean(row["application_number"]),
    })
    # Attach FAERS reaction frequencies and recall reports when present.
    if generic:
        reacts = conn.execute(
            "SELECT reaction_term, count FROM reactions WHERE generic_name = ? "
            "ORDER BY count DESC LIMIT 10",
            (generic,),
        ).fetchall()
        base["efek_samping_faers"] = [
            {"efek": _clean(r["reaction_term"]), "jumlah": r["count"]} for r in reacts
        ]
    ndc = row["product_ndc"]
    recalls = conn.execute(
        "SELECT classification, status, reason, recall_initiation_date "
        "FROM recalls WHERE product_ndc = ? ORDER BY recall_initiation_date DESC LIMIT 5",
        (ndc,),
    ).fetchall()
    base["penarikan"] = [
        {
            "klasifikasi": _clean(r["classification"]),
            "status": _clean(r["status"]),
            "alasan": _clean(r["reason"])[:_MAX_ITEM_CHARS],
            "tanggal": _clean(r["recall_initiation_date"]),
        }
        for r in recalls
    ]
    return base


_COLS = (
    "product_ndc, brand_name, generic_name, manufacturer, route, dosage_form, "
    "indications, contraindications, warnings, adverse_reactions, "
    "dosage_administration, pregnancy, pediatric_use, application_number, "
    "product_type, scraped_at"
)


def list_drugs(category: Optional[str] = None, limit: int = 0, offset: int = 0) -> list[dict[str, Any]]:
    """Return the drug catalog as a bare list of BackendDrug-shaped rows.

    The frontend loads the catalog once and searches client-side, so by
    default (``limit=0``) every row is returned with the compact catalog
    projection. A positive ``limit`` paginates instead.

    Args:
        category: Optional case-insensitive route/category filter.
        limit: ``0`` returns all rows; a positive value paginates.
        offset: Row offset when paginating.

    Returns:
        List of catalog dicts (empty when the database is unavailable).
    """
    conn = _connect()
    if not conn:
        return []
    try:
        params: list[Any] = []
        where = ""
        if category:
            where = "WHERE UPPER(route) LIKE ?"
            params.append(f"%{category.upper()}%")
        sql = f"SELECT {_COLS} FROM drugs {where} ORDER BY generic_name"
        limit = int(limit or 0)
        if limit > 0:
            sql += " LIMIT ? OFFSET ?"
            params += [min(limit, 10000), max(0, int(offset or 0))]
        rows = conn.execute(sql, params).fetchall()
        return [_map_catalog(r) for r in rows]
    except sqlite3.Error as e:
        logger.warning("list_drugs failed: %s", e)
        return []
    finally:
        conn.close()


def count_drugs() -> int:
    """Return the total number of catalog rows, or 0 when unavailable."""
    conn = _connect()
    if not conn:
        return 0
    try:
        return conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def _fts_escape(q: str) -> str:
    """Build a safe FTS5 prefix query from arbitrary user input."""
    tokens = re.findall(r"[A-Za-z0-9]+", q)
    if not tokens:
        return ""
    return " ".join(f'"{t}"*' for t in tokens)


def search_drugs(q: str, limit: int = 50) -> list[dict[str, Any]]:
    """Full-text search the catalog, returning light records.

    Uses the FTS5 index with a prefix query and falls back to a
    ``LIKE`` scan on generic/brand name when FTS yields nothing.
    """
    conn = _connect()
    if not conn:
        return []
    try:
        limit = max(1, min(int(limit or 50), 100))
        match = _fts_escape(q)
        rows: list[sqlite3.Row] = []
        if match:
            try:
                rows = conn.execute(
                    f"SELECT d.product_ndc, d.brand_name, d.generic_name, d.manufacturer, "
                    f"d.route, d.dosage_form FROM drugs_fts f "
                    f"JOIN drugs d ON d.rowid = f.rowid "
                    f"WHERE drugs_fts MATCH ? ORDER BY rank LIMIT ?",
                    (match, limit),
                ).fetchall()
            except sqlite3.Error:
                rows = []
        if not rows:
            like = f"%{q.strip()}%"
            rows = conn.execute(
                "SELECT product_ndc, brand_name, generic_name, manufacturer, route, dosage_form "
                "FROM drugs WHERE generic_name LIKE ? OR brand_name LIKE ? LIMIT ?",
                (like, like, limit),
            ).fetchall()
        # _map_light reads more columns than the search projection selects;
        # re-read full columns only for the matched NDCs to keep payload light.
        ndcs = [r["product_ndc"] for r in rows]
        if not ndcs:
            return []
        placeholders = ",".join("?" * len(ndcs))
        full = conn.execute(
            f"SELECT {_COLS} FROM drugs WHERE product_ndc IN ({placeholders})", ndcs
        ).fetchall()
        order = {ndc: i for i, ndc in enumerate(ndcs)}
        full.sort(key=lambda r: order.get(r["product_ndc"], 1_000))
        return [_map_light(r) for r in full]
    except sqlite3.Error as e:
        logger.warning("search_drugs failed: %s", e)
        return []
    finally:
        conn.close()


def get_drug(nama_obat: str) -> Optional[dict[str, Any]]:
    """Return the full mapped detail record for the best name match."""
    conn = _connect()
    if not conn:
        return None
    try:
        name = (nama_obat or "").strip()
        if not name:
            return None
        row = conn.execute(
            f"SELECT {_COLS} FROM drugs WHERE LOWER(generic_name) = LOWER(?) "
            f"OR LOWER(brand_name) = LOWER(?) LIMIT 1",
            (name, name),
        ).fetchone()
        if not row:
            like = f"%{name}%"
            row = conn.execute(
                f"SELECT {_COLS} FROM drugs WHERE generic_name LIKE ? OR brand_name LIKE ? "
                f"ORDER BY LENGTH(generic_name) LIMIT 1",
                (like, like),
            ).fetchone()
        if not row:
            return None
        return _map_full(row, conn)
    except sqlite3.Error as e:
        logger.warning("get_drug failed: %s", e)
        return None
    finally:
        conn.close()


# Indonesian risk buckets shared with anggota4's safety checker output so the
# safety route can aggregate SQLite and anggota4 verdicts uniformly.
_RISK_HIGH = re.compile(
    r"\b(boxed warning|black box|fatal|death|life-threatening|anaphyla|"
    r"hepatotox|cardiac arrest|respiratory depression|suicidal)\b",
    re.IGNORECASE,
)


def safety_profile(nama_obat: str) -> Optional[dict[str, Any]]:
    """Return a SQLite-derived per-drug safety verdict, or ``None`` if unknown.

    Used as a fallback by the safety-check route for drugs that are
    not in anggota4's curated 6-drug database, so the full catalog is
    covered. The risk score is a transparent heuristic over the label
    warnings text and FAERS reaction volume, not a clinical rating.
    """
    full = get_drug(nama_obat)
    if not full:
        return None
    warn_text = " ".join(full.get("peringatan", []) + full.get("kontraindikasi", []))
    faers = full.get("efek_samping_faers", [])
    faers_total = sum(f.get("jumlah", 0) for f in faers)
    if _RISK_HIGH.search(warn_text) or faers_total > 5000:
        label, skor = "tinggi", 4
    elif full.get("peringatan") or full.get("kontraindikasi") or faers_total > 0:
        label, skor = "sedang", 2
    else:
        label, skor = "rendah", 1
    return {
        "nama_obat": full["nama_obat"],
        "ditemukan": True,
        "label_risiko": label,
        "skor_risiko": skor,
        "efek_samping": full.get("efek_samping", []),
        "efek_samping_faers": faers,
        "peringatan": full.get("peringatan", []),
        "kontraindikasi": full.get("kontraindikasi", []),
        "kategori": full.get("kategori", ""),
        "sumber": "openFDA",
    }


def aggregates() -> dict[str, Any]:
    """Return catalog aggregates for the drugs-visualization dashboard.

    All counts come straight from the SQLite catalog so the frontend
    never has to pull thousands of rows to render charts.
    """
    conn = _connect()
    if not conn:
        return {}
    try:
        def scalar(sql: str) -> int:
            return conn.execute(sql).fetchone()[0]

        total_drugs = scalar("SELECT COUNT(*) FROM drugs")
        total_ndc = scalar("SELECT COUNT(DISTINCT product_ndc) FROM drugs")
        total_reactions = scalar("SELECT COUNT(*) FROM reactions")
        total_recalls = scalar("SELECT COUNT(*) FROM recalls")

        per_route = [
            {"label": _kategori(r["route"]), "value": r["c"]}
            for r in conn.execute(
                "SELECT route, COUNT(*) c FROM drugs GROUP BY route ORDER BY c DESC LIMIT 12"
            ).fetchall()
        ]
        per_form = [
            {"label": _clean(r["dosage_form"]).title() or "Lainnya", "value": r["c"]}
            for r in conn.execute(
                "SELECT dosage_form, COUNT(*) c FROM drugs "
                "GROUP BY dosage_form ORDER BY c DESC LIMIT 15"
            ).fetchall()
        ]
        recalls_by_class = [
            {"label": _clean(r["classification"]) or "Tidak diketahui", "value": r["c"]}
            for r in conn.execute(
                "SELECT classification, COUNT(*) c FROM recalls "
                "GROUP BY classification ORDER BY c DESC"
            ).fetchall()
        ]
        top_reactions = [
            {"label": _clean(r["reaction_term"]), "value": r["total"]}
            for r in conn.execute(
                "SELECT reaction_term, SUM(count) total FROM reactions "
                "GROUP BY reaction_term ORDER BY total DESC LIMIT 15"
            ).fetchall()
        ]
        n_routes = scalar("SELECT COUNT(DISTINCT route) FROM drugs")
        with_label = scalar(
            "SELECT COUNT(*) FROM drugs WHERE indications IS NOT NULL AND indications != ''"
        )
        generics_with_faers = scalar("SELECT COUNT(DISTINCT generic_name) FROM reactions")

        return {
            "stat_band": {
                "total_obat": total_drugs,
                "total_ndc": total_ndc,
                "total_rute": n_routes,
                "total_reaksi_faers": total_reactions,
                "total_penarikan": total_recalls,
            },
            "per_rute": per_route,
            "per_bentuk_sediaan": per_form,
            "penarikan_per_kelas": recalls_by_class,
            "efek_samping_terbanyak": top_reactions,
            "cakupan_sumber": [
                {"label": "Punya label openFDA", "value": with_label},
                {"label": "Punya data reaksi FAERS", "value": generics_with_faers},
                {"label": "Total obat", "value": total_drugs},
            ],
            "sumber": "U.S. National Library of Medicine / openFDA",
        }
    except sqlite3.Error as e:
        logger.warning("aggregates failed: %s", e)
        return {}
    finally:
        conn.close()
