"""Drug catalog routes wrapping anggota4.

The endpoints in this blueprint surface Iqbal's anggota4 catalog
(``data_loader``, ``pencarian_obat``) over HTTP. None of them
mutate the catalog; the team has agreed to keep drug data
read-only on the API side. When the anggota4 modules fail to
import the routes try a direct JSON read from the bundled file
before returning a 503 error.
"""
import json
import logging
from flask import Blueprint, request
from ..bootstrap import get_module
from .. import drug_db
from ..config import BASE_DIR
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("drug_routes", __name__)


def _data_loader():
    """Return the cached anggota4 data_loader module or ``None``."""
    return get_module("anggota4", "data_loader")


def _pencarian():
    """Return the cached anggota4 pencarian_obat module or ``None``."""
    return get_module("anggota4", "pencarian_obat")


# ── Direct JSON fallback (last resort when anggota4 imports fail) ──

_ANGGOTA4_DRUG_DB = BASE_DIR / "anggota4" / "data" / "drug_database.json"


def _load_drug_db_direct() -> list[dict]:
    """Read ``drug_database.json`` directly, bypassing anggota4 imports.

    Used as a last-resort fallback when the anggota4 modules cannot be
    loaded (e.g. in a PyInstaller frozen bundle where the ``importlib``
    re-import of data-directory ``.py`` files may fail).
    """
    try:
        with open(_ANGGOTA4_DRUG_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("direct drug DB read failed: %s", e)
        return []


def _search_drug_db_direct(q: str) -> list[dict]:
    """Simple case-insensitive search over the direct JSON catalog."""
    q_lower = q.strip().lower()
    if not q_lower:
        return []
    drugs = _load_drug_db_direct()
    if not drugs:
        return []
    results = []
    for d in drugs:
        name = (d.get("nama_obat") or "").lower()
        alias = [a.lower() for a in d.get("alias") or []]
        bahan = [b.lower() for b in d.get("bahan_aktif") or []]
        indikasi = [i.lower() for i in d.get("indikasi") or []]
        if (q_lower in name or any(q_lower in a for a in alias)
                or any(q_lower in b for b in bahan)
                or any(q_lower in i for i in indikasi)):
            results.append(d)
    return results


@bp.route("/api/drugs", methods=["GET"])
def list_drugs():
    """List the drug catalog, optionally filtered and paginated.

    Prefers the bundled SQLite catalog (full openFDA 20k+ dataset)
    and falls back to the anggota4 curated JSON catalog when SQLite
    is absent or contains zero matching rows.

    Query parameters:
        category: Case-insensitive category/route filter.
        limit / offset: Pagination over the SQLite catalog.

    Returns:
        HTTP 200 with a JSON array of catalog rows (both the SQLite
        and anggota4 paths return a bare list; the frontend loads the
        whole catalog once and searches client-side). HTTP 503 when
        neither source is available.
    """
    category = request.args.get("category")
    sqlite_results: list | None = None
    if drug_db.available():
        limit = request.args.get("limit", 0)
        offset = request.args.get("offset", 0)
        sqlite_results = drug_db.list_drugs(category=category, limit=limit, offset=offset)
        if sqlite_results:
            return ok(sqlite_results)

    # 2) Fallback to anggota4 curated JSON catalog.
    dl = _data_loader()
    if dl:
        drugs = dl.muat_database_obat()
        if category:
            drugs = [d for d in drugs if d.get("kategori", "").lower() == category.lower()]
        if drugs:
            return ok(drugs)

    # 3) Direct JSON read as last resort (PyInstaller-safe).
    direct = _load_drug_db_direct()
    if direct:
        if category:
            direct = [d for d in direct if d.get("kategori", "").lower() == category.lower()]
        return ok(direct)

    if sqlite_results is not None:
        return ok(sqlite_results)
    return err("drug catalog unavailable", 503)


@bp.route("/api/drugs/search", methods=["GET"])
def search_drugs():
    """Full-text search across the drug catalog.

    Prefers the SQLite FTS5 index, falling back to anggota4 search
    when the SQLite database is absent or returns zero results.

    Query parameters:
        q: Search term. Empty string short-circuits to an empty list
            so the frontend autocomplete UI never sees a 4xx for a
            blank input.

    Returns:
        HTTP 200 with a list of matched drug records.
    """
    q = (request.args.get("q") or "").strip()
    if not q:
        return ok([])

    # 1) Try the bundled SQLite catalog (multi-source 20k+ rows).
    sqlite_results: list | None = None
    if drug_db.available():
        sqlite_results = drug_db.search_drugs(q)
        if sqlite_results:
            return ok(sqlite_results)

    # 2) Fallback to anggota4 curated JSON database when SQLite is
    #    unavailable or returned nothing (corrupt db, schema mismatch,
    #    or the query simply matched zero rows).
    pen = _pencarian()
    if pen:
        payload = pen.cari_obat(q)
        hasil = payload.get("hasil", [])
        if hasil:
            return ok(hasil)

    # 3) Direct JSON search as last resort (PyInstaller-safe).
    direct = _search_drug_db_direct(q)
    if direct:
        return ok(direct)

    # 4) Return whatever we got from SQLite (possibly empty) so the
    #    frontend never sees a 503 for an empty-result query.
    if sqlite_results is not None:
        return ok(sqlite_results)

    return err("search unavailable", 503)


@bp.route("/api/drugs/<nama_obat>", methods=["GET"])
def get_drug(nama_obat: str):
    """Return the full safety profile for a single drug.

    Prefers the SQLite catalog detail record and falls back to
    anggota4's ``ambil_profil_keamanan_lengkap``.

    Args:
        nama_obat: Drug name from the URL.

    Returns:
        HTTP 200 with the profile. HTTP 404 when not found.
        HTTP 503 when no source is available.
    """
    if drug_db.available():
        profil = drug_db.get_drug(nama_obat)
        if profil:
            return ok(profil)
        # Fall through to anggota4 for curated drugs not matched in SQLite.
    pen = _pencarian()
    if not pen:
        return err("not found", 404) if drug_db.available() else err("drug profile unavailable", 503)
    try:
        profil = pen.ambil_profil_keamanan_lengkap(nama_obat)
    except Exception as e:
        logger.warning("anggota4 profile lookup failed for %s: %s", nama_obat, e)
        return err("not found", 404)
    if not profil or profil.get("status") != "found":
        return err("not found", 404)
    return ok(profil)
