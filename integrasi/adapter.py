"""
Adapter / shim layer untuk panggil modul anggota1-5 dari app_terpadu.py.
Tidak ngubah file anggota manapun, cuma orchestrate via subprocess atau import.
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
ANGGOTA = {
    "anggota1": ROOT / "anggota1",
    "anggota2": ROOT / "anggota2",
    "anggota3": ROOT / "anggota3",
    "anggota4": ROOT / "anggota4",
    "anggota5": ROOT / "anggota5",
}


def jalankan_scraper() -> int:
    folder = ANGGOTA["anggota1"]
    file = folder / "anggota1.py"
    if not file.exists():
        print(f"[!] File scraper tidak ditemukan di {file}.")
        return 1
    print("[i] Scraper butuh internet, estimasi 5 menit. Ctrl+C untuk cancel.")
    if input("Lanjut? (y/n): ").strip().lower() != "y":
        return 0
    try:
        return subprocess.run([sys.executable, "anggota1.py"], cwd=folder).returncode
    except KeyboardInterrupt:
        print("\n[i] Scraper dibatalkan.")
        return 130


def jalankan_pasien_crud() -> int:
    folder = ANGGOTA["anggota2"]
    return subprocess.run([sys.executable, "PasienCRUD.py"], cwd=folder).returncode


def jalankan_pencarian_obat() -> int:
    folder = ANGGOTA["anggota4"]
    entry = folder / "pencarian_obat.py"
    return subprocess.run([sys.executable, str(entry)], cwd=folder).returncode


def jalankan_visualisasi() -> int:
    folder = ANGGOTA["anggota3"]
    return subprocess.run([sys.executable, "TampilGrafik.py"], cwd=folder).returncode


def jalankan_tkesehatan_crud() -> int:
    """Admin-only CRUD tenaga kesehatan, dipanggil langsung sebagai modul."""
    folder = ANGGOTA["anggota5"]
    sys.path.insert(0, str(folder))
    try:
        from tkesehatan_crud import menu_tkesehatan_crud
        menu_tkesehatan_crud()
        return 0
    except Exception as e:
        print(f"[!] Gagal load tkesehatan_crud: {e}")
        return 1
    finally:
        if str(folder) in sys.path:
            sys.path.remove(str(folder))


def jalankan_export_pdf() -> int:
    """Call anggota5 export_pdf flow without re-prompting login.

    Loads ambil_data.ambil_seluruh_data_pasien() to get patient data in
    anggota5's expected nested format, then calls export_pdf.buat_laporan_pdf().
    """
    folder = ANGGOTA["anggota5"]
    sys.path.insert(0, str(folder))
    try:
        from ambil_data import ambil_seluruh_data_pasien
        from export_pdf import buat_laporan_pdf
        data = ambil_seluruh_data_pasien()
        if not data:
            print("[!] Data pasien kosong atau tidak ditemukan.")
            return 1
        buat_laporan_pdf(data, "Laporan_MedWatch.pdf")
        return 0
    except Exception as e:
        print(f"[!] Gagal export PDF: {e}")
        return 1
    finally:
        if str(folder) in sys.path:
            sys.path.remove(str(folder))
