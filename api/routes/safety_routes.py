"""Safety check endpoint wrapping anggota4.safety_checker."""
import logging
from flask import Blueprint, request
from ..middleware import require_auth
from ..bootstrap import get_module
from ..storage import load_patients
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("safety_routes", __name__)

_LABEL_MAP = {"rendah": "low", "sedang": "medium", "tinggi": "high"}
_LABEL_ORDER = {"rendah": 0, "sedang": 1, "tinggi": 2}


@bp.route("/api/safety/check", methods=["POST"])
@require_auth
def safety_check():
    body = request.get_json(silent=True) or {}
    drugs = body.get("drugs") or []
    pasien_id = body.get("pasien_id")

    if not isinstance(drugs, list) or not drugs:
        return err("drugs (non-empty list) required", 400)

    sc = get_module("anggota4", "safety_checker")
    if not sc:
        return err("safety checker unavailable", 503)

    payload = sc.cek_keamanan_obat(drugs)

    hasil_obat = payload.get("hasil_obat", [])
    if hasil_obat:
        max_skor = max(h.get("skor_risiko", 0) for h in hasil_obat)
        agg_label_id = max(
            (h.get("label_risiko", "rendah") for h in hasil_obat),
            key=lambda l: _LABEL_ORDER.get(l, 0),
        )
    else:
        max_skor = 0
        agg_label_id = "rendah"

    pasien_context = None
    if pasien_id:
        patients = load_patients()
        target = next((p for p in patients if p.get("id") == pasien_id), None)
        if target:
            pasien_context = {
                "id": target["id"],
                "nama": target.get("nama"),
                "kategori": target.get("kategori"),
                "diagnosa": target.get("A", {}).get("diagnosa"),
                "kondisi_umum": target.get("S", {}).get("riwayat", ""),
            }

    return ok({
        "drugs": hasil_obat,
        "interactions": payload.get("efek_tumpang_tindih", []),
        "severity_score": int(round(max_skor)),
        "severity_level": _LABEL_MAP.get(agg_label_id, "low"),
        "warnings": payload.get("peringatan_prioritas", []),
        "obat_tidak_ditemukan": payload.get("obat_tidak_ditemukan", []),
        "pasien_context": pasien_context,
    })
