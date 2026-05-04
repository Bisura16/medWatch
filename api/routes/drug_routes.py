"""Drug catalog routes wrapping anggota4."""
import logging
from flask import Blueprint, request
from ..bootstrap import get_module
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("drug_routes", __name__)


def _data_loader():
    return get_module("anggota4", "data_loader")


def _pencarian():
    return get_module("anggota4", "pencarian_obat")


@bp.route("/api/drugs", methods=["GET"])
def list_drugs():
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
    pen = _pencarian()
    if not pen:
        return err("drug profile unavailable", 503)
    profil = pen.ambil_profil_keamanan_lengkap(nama_obat)
    if profil.get("status") != "found":
        return err("not found", 404)
    return ok(profil)
