"""Drug catalog routes backed by the bundled SQLite catalog.

The catalog is the openFDA-derived ``drugs.db`` (read-only, FTS5). All
list and search responses are bounded so the frontend never pulls the
whole catalog into memory; the search-first UI requests small pages.

When the database is not available the endpoints fail LOUDLY with HTTP
503 and a clear message instead of silently serving a tiny curated
fallback that would look like a working catalog with only a handful of
drugs. Single-drug detail still consults anggota4's curated profiles,
but only when the real database is present and has no match for that
name.
"""
import logging
from flask import Blueprint, request
from ..bootstrap import get_module
from .. import drug_db
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("drug_routes", __name__)

# Default page size for the search-first UI. Small on purpose: the entry
# view shows a handful of rows and typing fetches a handful of matches.
_DEFAULT_LIMIT = 15
_CATALOG_UNAVAILABLE = "Katalog obat tidak ter-load. Database obat tidak ditemukan atau tidak terbaca."


def _pencarian():
    """Return the cached anggota4 pencarian_obat module or ``None``."""
    return get_module("anggota4", "pencarian_obat")


def _int_arg(name: str, default: int) -> int:
    """Read an integer query arg, falling back to ``default`` on bad input."""
    try:
        return int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default


@bp.route("/api/drugs", methods=["GET"])
def list_drugs():
    """List a bounded page of the drug catalog.

    Query parameters:
        category: Case-insensitive route/category filter.
        limit: Page size (default 15). ``0`` returns the full catalog and
            is reserved for export/admin use, never the normal UI.
        offset: Row offset for pagination.

    Returns:
        HTTP 200 with a JSON array of catalog rows (each exposing the clean
        ``display_name``). HTTP 503 when the database is unavailable.
    """
    if not drug_db.available():
        logger.error("drug catalog unavailable: drugs.db missing or unreadable")
        return err(_CATALOG_UNAVAILABLE, 503)
    category = request.args.get("category")
    limit = _int_arg("limit", _DEFAULT_LIMIT)
    offset = _int_arg("offset", 0)
    return ok(drug_db.list_drugs(category=category, limit=limit, offset=offset))


@bp.route("/api/drugs/count", methods=["GET"])
def count_drugs():
    """Return the total catalog size so the UI can show it without a full load.

    Returns:
        HTTP 200 with ``{total: <int>}``. HTTP 503 when unavailable.
    """
    if not drug_db.available():
        return err(_CATALOG_UNAVAILABLE, 503)
    return ok({"total": drug_db.count_drugs()})


@bp.route("/api/drugs/search", methods=["GET"])
def search_drugs():
    """Full-text search across the catalog (FTS5, bounded).

    Query parameters:
        q: Search term. Empty string returns an empty list so typeahead
            never sees a 4xx for blank input.
        limit: Max results (default 15, hard-capped at 100 by the loader).

    Returns:
        HTTP 200 with a list of matched rows (each exposing display_name).
        HTTP 503 when the database is unavailable.
    """
    if not drug_db.available():
        logger.error("drug search unavailable: drugs.db missing or unreadable")
        return err(_CATALOG_UNAVAILABLE, 503)
    q = (request.args.get("q") or "").strip()
    if not q:
        return ok([])
    limit = _int_arg("limit", _DEFAULT_LIMIT)
    return ok(drug_db.search_drugs(q, limit=limit))


@bp.route("/api/drugs/<nama_obat>", methods=["GET"])
def get_drug(nama_obat: str):
    """Return the full safety profile for a single drug.

    Prefers the SQLite catalog detail and, only when the database is
    present but has no match, falls back to anggota4's curated profiles.

    Returns:
        HTTP 200 with the profile, HTTP 404 when not found, HTTP 503 when
        the database is unavailable.
    """
    if not drug_db.available():
        logger.error("drug profile unavailable: drugs.db missing or unreadable")
        return err(_CATALOG_UNAVAILABLE, 503)
    profil = drug_db.get_drug(nama_obat)
    if profil:
        return ok(profil)
    # Database present but no SQLite match: consult anggota4 curated profiles.
    pen = _pencarian()
    if pen:
        try:
            curated = pen.ambil_profil_keamanan_lengkap(nama_obat)
            if curated and curated.get("status") == "found":
                return ok(curated)
        except Exception as e:
            logger.warning("anggota4 profile lookup failed for %s: %s", nama_obat, e)
    return err("not found", 404)
