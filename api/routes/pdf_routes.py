"""PDF generation endpoints wrapping anggota5/export_pdf.

Schema translation (anggota2 flat SOAP -> anggota5 nested) happens inline so
we don't depend on anggota5/ambil_data.py reading from the filesystem.
"""
import logging
import os
import tempfile
from flask import Blueprint, request, send_file
from ..middleware import require_role
from ..storage import load_patients
from ..bootstrap import get_module
from ..helpers import err

logger = logging.getLogger(__name__)
bp = Blueprint("pdf_routes", __name__)


def _to_anggota5_format(p: dict) -> dict:
    """Translate canonical Bimo SOAP shape -> Abhidal nested shape for export_pdf."""
    S = p.get("S", {}) or {}
    O = p.get("O", {}) or {}
    A = p.get("A", {}) or {}
    P = p.get("P", {}) or {}
    return {
        "identitas": {
            "ID Pasien": p.get("id", "-"),
            "Nama Pasien": p.get("nama", "-"),
            "Umur": f"{p.get('umur', '-')} Tahun",
            "Tanggal Kunjungan": p.get("tanggal_kunjungan", "-"),
            "Alamat": p.get("alamat", "-"),
        },
        "anamnesis": (
            f"Keluhan Utama : {S.get('keluhan', '-')}\n"
            f"Riwayat Sakit : {S.get('riwayat', '-')}"
        ),
        "pemeriksaan": (
            f"Tekanan Darah : {O.get('tekanan_darah', '-')} mmHg\n"
            f"Nadi : {O.get('nadi', '-')} x/menit\n"
            f"Suhu Tubuh : {O.get('suhu_c', '-')} °C\n"
            f"Berat Badan : {O.get('bb_kg', '-')} kg\n"
            f"Catatan Lain : {O.get('catatan', '-')}"
        ),
        "diagnosis_tindakan": (
            f"DIAGNOSA (A) :\n{A.get('diagnosa', '-')}\n\n"
            f"TINDAKAN (P) :\n{P.get('tindakan', '-')}\n\n"
            f"RESEP OBAT : {P.get('resep', '-')}\n"
            f"JADWAL KONTROL : {P.get('jadwal_kontrol', '-')}"
        ),
    }


@bp.route("/api/pdf/generate-rekam-medis", methods=["POST"])
@require_role("tenaga_kesehatan", "admin")
def generate_rekam_medis():
    body = request.get_json(silent=True) or {}
    pasien_id = body.get("pasien_id")
    if not pasien_id:
        return err("pasien_id required", 400)

    patients = load_patients()
    target = next((p for p in patients if p.get("id") == pasien_id), None)
    if not target:
        return err("not found", 404)

    export_pdf = get_module("anggota5", "export_pdf")
    if not export_pdf:
        return err("PDF generator unavailable", 503)

    nested = _to_anggota5_format(target)

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        export_pdf.buat_laporan_pdf([nested], tmp_path, id_pasien_terpilih=pasien_id)
        return send_file(
            tmp_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"rekam-medis-{pasien_id}.pdf",
        )
    except Exception as e:
        logger.exception("PDF generation failed")
        return err(f"PDF generation failed: {e}", 500)


@bp.route("/api/pdf/generate-laporan-bulanan", methods=["POST"])
@require_role("admin")
def generate_laporan_bulanan():
    body = request.get_json(silent=True) or {}
    month = body.get("month", "")

    patients = load_patients()
    if month:
        patients = [p for p in patients if p.get("tanggal_kunjungan", "").endswith(month.replace("-", "-"))]

    export_pdf = get_module("anggota5", "export_pdf")
    if not export_pdf:
        return err("PDF generator unavailable", 503)

    nested_list = [_to_anggota5_format(p) for p in patients]

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        export_pdf.buat_laporan_pdf(nested_list, tmp_path)
        return send_file(
            tmp_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"laporan-bulanan-{month or 'semua'}.pdf",
        )
    except Exception as e:
        logger.exception("PDF generation failed")
        return err(f"PDF generation failed: {e}", 500)
