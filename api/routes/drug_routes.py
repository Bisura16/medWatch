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
    """List the full drug catalog, optionally filtered by category.

    Query parameters:
        category: Case-insensitive ``kategori`` filter.

    Returns:
        HTTP 200 with a list of drug records. HTTP 503 when the
        anggota4 data_loader module failed to load.
    """
    dl = _data_loader()
    if not dl:
        return err("drug catalog unavailable", 503)
    drugs = dl.muat_database_obat()
    category = request.args.get("category")
    if category:
        drugs = [d for d in drugs if d.get("kategori", "").lower() == category.lower()]
    return ok(drugs)


@bp.route("/api/drugs/search", methods=["GET"])
def search_drugs():
    """Full-text search across the drug catalog.

    Query parameters:
        q: Search term. Empty string short-circuits to an empty list
            so the frontend autocomplete UI never sees a 4xx for a
            blank input.

    Returns:
        HTTP 200 with the ``hasil`` array from anggota4's
        ``cari_obat``. HTTP 503 when search is unavailable.
    """
    q = (request.args.get("q") or "").strip()
    if not q:
        return ok([])
    pen = _pencarian()
    if not pen:
        return err("search unavailable", 503)
    payload = pen.cari_obat(q)
    return ok(payload.get("hasil", []))


@bp.route("/api/drugs/<nama_obat>", methods=["GET"])
def get_drug(nama_obat: str):
    """Return the full safety profile for a single drug.

    Args:
        nama_obat: Drug name from the URL; passed through to
            anggota4's ``ambil_profil_keamanan_lengkap``.

    Returns:
        HTTP 200 with the profile. HTTP 404 when anggota4 reports
        the drug as not found. HTTP 503 when the module is missing.
    """
    pen = _pencarian()
    if not pen:
        return err("drug profile unavailable", 503)
    profil = pen.ambil_profil_keamanan_lengkap(nama_obat)
    if profil.get("status") != "found":
        return err("not found", 404)
    return ok(profil)
