"""Safety check endpoint wrapping anggota4.safety_checker.

The route takes a list of drug names and an optional patient id,
runs the anggota4 safety checker over the list, normalises the
Indonesian severity labels to English buckets the frontend expects,
and (when ``pasien_id`` is supplied) attaches the patient's active
medications parsed from ``P.resep`` so the UI can warn the bidan
about overlap (B05).
"""
import logging
from flask import Blueprint, request, g
from ..middleware import require_auth
from ..bootstrap import get_module
from ..storage import load_patients
from ..helpers import ok, err, parse_resep_to_meds

logger = logging.getLogger(__name__)
bp = Blueprint("safety_routes", __name__)

_LABEL_MAP = {"rendah": "low", "sedang": "medium", "tinggi": "high"}
_LABEL_ORDER = {"rendah": 0, "sedang": 1, "tinggi": 2}


@bp.route("/api/safety/check", methods=["POST"])
@require_auth
def safety_check():
    """Aggregate per-drug safety verdicts plus optional patient context.

    Request body: ``{drugs: list[str], pasien_id?: str}``.

    Returns:
        HTTP 200 with the drug-level results, the worst-case
        severity (score + ``low``/``medium``/``high`` label),
        prioritised warnings, the list of drugs anggota4 could not
        match, and the patient summary plus active medications when
        ``pasien_id`` resolves. HTTP 400 when ``drugs`` is missing
        or empty. HTTP 503 when anggota4 safety_checker is absent.
    """
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
    pasien_active_meds: list[str] = []
    # H07-1 (Wave 5): role-aware patient-context attachment. The masyarakat
    # role must never receive another patient's PII through this endpoint.
    # Bidan (tenaga_kesehatan) and admin retain their existing behaviour
    # because the patient roster is single-faskes (H07-2 documented). For
    # masyarakat we silently drop the pasien_context / pasien_active_meds
    # fields regardless of the supplied pasien_id so the safety verdict
    # itself still computes and the response shape stays stable.
    role = g.user.get("role") if getattr(g, "user", None) else None
    if pasien_id and role in ("tenaga_kesehatan", "admin"):
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
            # B05: surface the patient's active medications by parsing the
            # `P.resep` field of the most recent visit. The current Pasien
            # schema is single-visit-per-record, so the record itself is the
            # most recent visit.
            resep_text = target.get("P", {}).get("resep", "")
            pasien_active_meds = parse_resep_to_meds(resep_text)

    return ok({
        "drugs": hasil_obat,
        "interactions": payload.get("efek_tumpang_tindih", []),
        "severity_score": int(round(max_skor)),
        "severity_level": _LABEL_MAP.get(agg_label_id, "low"),
        "warnings": payload.get("peringatan_prioritas", []),
        "obat_tidak_ditemukan": payload.get("obat_tidak_ditemukan", []),
        "pasien_context": pasien_context,
        "pasien_active_meds": pasien_active_meds,
    })
