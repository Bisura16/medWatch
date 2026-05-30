"""Drug catalog routes wrapping anggota4.

The endpoints in this blueprint surface Iqbal's anggota4 catalog
(``data_loader``, ``pencarian_obat``) over HTTP. None of them
mutate the catalog; the team has agreed to keep drug data
read-only on the API side. When the anggota4 modules fail to
import the routes return HTTP 503 so the frontend can show a
friendly maintenance message instead of crashing.
"""
import logging
from flask import Blueprint, request
from ..bootstrap import get_module
from .. import drug_db
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("drug_routes", __name__)


def _data_loader():
    """Return the cached anggota4 data_loader module or ``None``."""
    return get_module("anggota4", "data_loader")


def _pencarian():
    """Return the cached anggota4 pencarian_obat module or ``None``."""
    return get_module("anggota4", "pencarian_obat")


@bp.route("/api/drugs", methods=["GET"])
def list_drugs():
    """List the drug catalog, optionally filtered and paginated.

    Prefers the bundled SQLite catalog (full openFDA dataset) and
    falls back to the anggota4 JSON when no database is present.

    Query parameters:
        category: Case-insensitive category/route filter.
        limit / offset: Pagination over the SQLite catalog.

    Returns:
        HTTP 200 with ``{items, total}`` (SQLite) or a list
        (anggota4). HTTP 503 when neither source is available.
    """
    category = request.args.get("category")
    if drug_db.available():
        limit = request.args.get("limit", 0)
        offset = request.args.get("offset", 0)
        return ok(drug_db.list_drugs(category=category, limit=limit, offset=offset))
    dl = _data_loader()
    if not dl:
        return err("drug catalog unavailable", 503)
    drugs = dl.muat_database_obat()
    if category:
        drugs = [d for d in drugs if d.get("kategori", "").lower() == category.lower()]
    return ok(drugs)


@bp.route("/api/drugs/search", methods=["GET"])
def search_drugs():
    """Full-text search across the drug catalog.

    Prefers the SQLite FTS5 index, falling back to anggota4 search.

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
    if drug_db.available():
        return ok(drug_db.search_drugs(q))
    pen = _pencarian()
    if not pen:
        return err("search unavailable", 503)
    payload = pen.cari_obat(q)
    return ok(payload.get("hasil", []))


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
