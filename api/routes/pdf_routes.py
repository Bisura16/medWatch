"""PDF generation endpoints.

Two categories of generator live here:

1. Per-patient and aggregate SOAP reports delegated to anggota5/export_pdf
   (rekam-medis, laporan-bulanan). Schema translation (anggota2 flat SOAP
   -> anggota5 nested) happens inline so we don't depend on
   anggota5/ambil_data.py reading from the filesystem.

2. Drug safety and inventory reports built directly with fpdf2 here
   (efek-samping, inventaris). These read anggota1/drug_safety_data.json
   and anggota4/drug_database.json read-only and never modify anggota
   source files.
"""
import json
import logging
import tempfile
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fpdf import FPDF
from flask import Blueprint, request, send_file

from ..config import BASE_DIR
from ..middleware import require_role
from ..storage import load_patients
from ..bootstrap import get_module
from ..helpers import err

logger = logging.getLogger(__name__)
bp = Blueprint("pdf_routes", __name__)

# WIB tz, fixed offset for footer timestamp
_WIB = timezone(timedelta(hours=7))


def _now_wib_str() -> str:
    return datetime.now(_WIB).strftime("%d-%m-%Y %H:%M WIB")


def _safe(text: object) -> str:
    """fpdf2 helvetica is Latin-1; replace anything outside that range."""
    s = str(text) if text is not None else "-"
    return s.encode("latin-1", "replace").decode("latin-1")


class MedWatchReportPDF(FPDF):
    """Generic header + footer for non-SOAP MedWatch PDFs.

    Title is set via ``set_title`` on the FPDF instance before ``add_page``.
    """

    def header(self) -> None:
        self.set_font("helvetica", "B", 14)
        title = _safe(self.title or "Laporan MedWatch")
        self.cell(0, 10, title, align="C", ln=True)
        self.set_font("helvetica", "I", 9)
        self.cell(
            0,
            6,
            _safe(f"Klinik Posyandu Faskes 1 - Dicetak {_now_wib_str()}"),
            align="C",
            ln=True,
        )
        self.line(10, 24, 200, 24)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(
            0,
            10,
            _safe(f"Halaman {self.page_no()} | MedWatch v1.0"),
            align="C",
        )


def _load_drug_safety_data() -> list[dict]:
    path = BASE_DIR / "anggota1" / "data" / "drug_safety_data.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        logger.warning("drug_safety_data.json not found at %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.warning("drug_safety_data.json invalid: %s", e)
        return []


def _load_drug_database() -> list[dict]:
    path = BASE_DIR / "anggota4" / "data" / "drug_database.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        logger.warning("drug_database.json not found at %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.warning("drug_database.json invalid: %s", e)
        return []


_SEVERITY_LABEL_ID = {
    "mild": "Ringan",
    "moderate": "Sedang",
    "severe": "Berat",
}


def _parse_resep_drugs(resep: str) -> list[str]:
    """Split resep free-text into drug-name tokens.

    Splits on newline and comma; strips dosage hints and whitespace; lowercases
    for matching but returns title case tokens. Empty in, empty out.
    """
    if not resep or not isinstance(resep, str):
        return []
    raw_tokens: list[str] = []
    for line in resep.replace(",", "\n").split("\n"):
        s = line.strip()
        if not s:
            continue
        # Drop trailing dosage phrasing after a digit (e.g. "Paracetamol 500 mg 3x sehari").
        first_word = s.split()
        if first_word:
            raw_tokens.append(first_word[0].strip(".:;").title())
    return raw_tokens


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
        # month is YYYY-MM, tanggal_kunjungan is DD-MM-YYYY: compare MM-YYYY suffix.
        year, mo = month.split("-")[:2] if "-" in month else (month, "")
        suffix = f"{mo}-{year}"
        patients = [p for p in patients if p.get("tanggal_kunjungan", "").endswith(suffix)]

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


@bp.route("/api/pdf/generate-efek-samping", methods=["POST"])
@require_role("tenaga_kesehatan", "admin")
def generate_efek_samping():
    """Top adverse-event report aggregated across all patients.

    Combines patient resep frequency (api/data/patients.json) with the
    drug safety database (anggota1/data/drug_safety_data.json) to produce
    a ranked top-25 side-effects table plus a per-drug severity summary.
    Works even if no patients exist yet (falls back to drug-database scope).
    """
    safety = _load_drug_safety_data()
    if not safety:
        return err("data efek samping tidak tersedia", 503)

    patients = load_patients()

    # Count how often each drug appears in patient resep (case-insensitive match
    # against drug_safety_data drug_name).
    resep_counter: Counter[str] = Counter()
    for p in patients:
        resep = (p.get("P", {}) or {}).get("resep", "")
        for token in _parse_resep_drugs(resep):
            resep_counter[token.lower()] += 1

    # Effect frequency: each drug's side effects contribute weight = max(1, resep_count).
    # When no patients, every drug contributes weight 1 (so the report still ranks
    # by how commonly an effect appears across the safety database).
    effect_freq: Counter[str] = Counter()
    drug_rows: list[tuple[str, str, int, int]] = []  # (drug, severity_id, n_effects, weight)
    for entry in safety:
        drug = (entry.get("drug_name") or "").strip()
        if not drug:
            continue
        weight = max(1, resep_counter.get(drug.lower(), 0))
        effects = entry.get("side_effects") or []
        for eff in effects:
            if isinstance(eff, str) and eff.strip():
                effect_freq[eff.strip()] += weight
        sev_raw = (entry.get("severity_level") or "").lower()
        sev_id = _SEVERITY_LABEL_ID.get(sev_raw, sev_raw or "-")
        drug_rows.append((drug, sev_id, len(effects), weight))

    drug_rows.sort(key=lambda x: (-x[3], x[0]))
    top_effects = effect_freq.most_common(25)
    total_patients = len(patients)
    total_prescribed = sum(resep_counter.values())

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        pdf = MedWatchReportPDF()
        pdf.set_title("Laporan Efek Samping Obat")
        pdf.add_page()

        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Ringkasan"), ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(
            0,
            6,
            _safe(
                f"Total pasien terdaftar: {total_patients}\n"
                f"Total entri resep diolah: {total_prescribed}\n"
                f"Total obat dalam basis data keamanan: {len(safety)}\n"
                f"Total efek samping unik teridentifikasi: {len(effect_freq)}"
            ),
        )
        pdf.ln(4)

        # Top efek samping table
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Top 25 efek samping terlapor"), ln=True, fill=True)
        pdf.ln(1)

        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(12, 7, _safe("No"), border=1, fill=True, align="C")
        pdf.cell(130, 7, _safe("Efek samping"), border=1, fill=True)
        pdf.cell(45, 7, _safe("Frekuensi tertimbang"), border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("helvetica", "", 9)
        for i, (eff, freq) in enumerate(top_effects, start=1):
            pdf.cell(12, 6, _safe(str(i)), border=1, align="C")
            pdf.cell(130, 6, _safe(eff[:80]), border=1)
            pdf.cell(45, 6, _safe(str(freq)), border=1, align="C")
            pdf.ln()
        if not top_effects:
            pdf.cell(187, 6, _safe("Belum ada efek samping yang dapat ditampilkan."), border=1, align="C")
            pdf.ln()

        pdf.ln(4)

        # Per-drug severity summary table (top 25 by weight)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Severitas per obat (25 teratas)"), ln=True, fill=True)
        pdf.ln(1)

        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(70, 7, _safe("Obat"), border=1, fill=True)
        pdf.cell(35, 7, _safe("Severitas"), border=1, fill=True, align="C")
        pdf.cell(40, 7, _safe("Jumlah efek"), border=1, fill=True, align="C")
        pdf.cell(42, 7, _safe("Bobot resep"), border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("helvetica", "", 9)
        for drug, sev_id, n_eff, weight in drug_rows[:25]:
            pdf.cell(70, 6, _safe(drug[:40]), border=1)
            pdf.cell(35, 6, _safe(sev_id), border=1, align="C")
            pdf.cell(40, 6, _safe(str(n_eff)), border=1, align="C")
            pdf.cell(42, 6, _safe(str(weight)), border=1, align="C")
            pdf.ln()
        if not drug_rows:
            pdf.cell(187, 6, _safe("Belum ada data obat untuk ditampilkan."), border=1, align="C")
            pdf.ln()

        pdf.ln(4)
        pdf.set_font("helvetica", "I", 8)
        pdf.multi_cell(
            0,
            5,
            _safe(
                "Catatan: bobot resep dihitung dari jumlah kemunculan obat pada kolom "
                "P.resep seluruh pasien. Jika belum ada pasien terdaftar, setiap obat "
                "diberi bobot 1 sehingga peringkat efek samping mengikuti basis data keamanan obat."
            ),
        )

        pdf.output(tmp_path)
        return send_file(
            tmp_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="laporan-efek-samping.pdf",
        )
    except Exception as e:
        logger.exception("PDF efek-samping generation failed")
        return err(f"PDF generation failed: {e}", 500)


@bp.route("/api/pdf/generate-inventaris", methods=["POST"])
@require_role("tenaga_kesehatan", "admin")
def generate_inventaris():
    """Inventory report: current drug catalog with category and indikasi.

    Source: anggota4/data/drug_database.json. The desktop module does not
    track stock count, so this report lists the catalog (kategori, bahan
    aktif, indikasi, dosis umum, kategori kehamilan) which is what the
    bidan actually needs to reference at a Faskes 1 clinic.
    """
    drugs = _load_drug_database()
    if not drugs:
        return err("data inventaris obat tidak tersedia", 503)

    # Group by kategori for the summary section.
    by_kategori: Counter[str] = Counter(
        (d.get("kategori") or "Tidak terklasifikasi") for d in drugs
    )

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        pdf = MedWatchReportPDF()
        pdf.set_title("Laporan Inventaris Obat")
        pdf.add_page()

        # Summary
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Ringkasan inventaris"), ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(
            0,
            6,
            _safe(
                f"Total jenis obat: {len(drugs)}\n"
                f"Total kategori farmakologi: {len(by_kategori)}"
            ),
        )
        pdf.ln(2)

        # Kategori breakdown
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 7, _safe("Distribusi per kategori"), ln=True)
        pdf.set_font("helvetica", "", 10)
        for kat, n in sorted(by_kategori.items(), key=lambda x: (-x[1], x[0])):
            pdf.cell(0, 6, _safe(f"  - {kat}: {n} obat"), ln=True)

        pdf.ln(4)

        # Detail table
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Daftar obat"), ln=True, fill=True)
        pdf.ln(1)

        # Table widths sum to ~190
        col_w = {"no": 10, "nama": 40, "kategori": 50, "indikasi": 60, "kehamilan": 30}

        def _table_header() -> None:
            pdf.set_font("helvetica", "B", 9)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(col_w["no"], 7, _safe("No"), border=1, fill=True, align="C")
            pdf.cell(col_w["nama"], 7, _safe("Nama obat"), border=1, fill=True)
            pdf.cell(col_w["kategori"], 7, _safe("Kategori"), border=1, fill=True)
            pdf.cell(col_w["indikasi"], 7, _safe("Indikasi"), border=1, fill=True)
            pdf.cell(col_w["kehamilan"], 7, _safe("Kehamilan"), border=1, fill=True)
            pdf.ln()

        _table_header()
        pdf.set_font("helvetica", "", 9)
        for i, d in enumerate(drugs, start=1):
            nama = d.get("nama_obat") or "-"
            kat = d.get("kategori") or "-"
            indikasi = ", ".join(d.get("indikasi") or []) or "-"
            kehamilan = d.get("kehamilan") or "-"
            # Re-check page break before each row
            if pdf.get_y() > 260:
                pdf.add_page()
                _table_header()
                pdf.set_font("helvetica", "", 9)
            pdf.cell(col_w["no"], 6, _safe(str(i)), border=1, align="C")
            pdf.cell(col_w["nama"], 6, _safe(nama[:25]), border=1)
            pdf.cell(col_w["kategori"], 6, _safe(kat[:32]), border=1)
            pdf.cell(col_w["indikasi"], 6, _safe(indikasi[:40]), border=1)
            pdf.cell(col_w["kehamilan"], 6, _safe(kehamilan[:18]), border=1)
            pdf.ln()

        # Detail per obat (dosis dan peringatan singkat)
        pdf.ln(4)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, _safe(" Detail dosis dan peringatan"), ln=True, fill=True)
        pdf.ln(2)
        for i, d in enumerate(drugs, start=1):
            if pdf.get_y() > 250:
                pdf.add_page()
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, _safe(f"{i}. {d.get('nama_obat', '-')}"), ln=True)
            pdf.set_font("helvetica", "", 9)
            pdf.multi_cell(
                0,
                5,
                _safe(
                    f"Dosis umum: {d.get('dosis_umum', '-')}\n"
                    f"Bahan aktif: {', '.join(d.get('bahan_aktif') or []) or '-'}\n"
                    f"Peringatan: {' '.join(d.get('peringatan') or []) or '-'}"
                ),
            )
            pdf.ln(1)

        pdf.output(tmp_path)
        return send_file(
            tmp_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="laporan-inventaris-obat.pdf",
        )
    except Exception as e:
        logger.exception("PDF inventaris generation failed")
        return err(f"PDF generation failed: {e}", 500)
