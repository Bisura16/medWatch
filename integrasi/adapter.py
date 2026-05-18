"""Shim layer for calling anggota1-5 modules from app_terpadu.py.

Every dispatcher in this file either spawns the target module as a
subprocess (so its own ``__main__`` block runs and its imports
resolve relative to its own folder) or imports it read-only inside
a guarded ``sys.path`` window. None of the teammate files are
modified; this module is the integration seam.
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
    """Run anggota1's drugs.com scraper with a confirmation prompt.

    Returns:
        The subprocess return code. ``1`` when the entry script is
        missing, ``130`` when the user cancels with Ctrl+C, ``0``
        when the user declines the confirmation prompt.
    """
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
    """Launch anggota2's PasienCRUD as a subprocess and return its exit code."""
    folder = ANGGOTA["anggota2"]
    return subprocess.run([sys.executable, "PasienCRUD.py"], cwd=folder).returncode


def jalankan_pencarian_obat() -> int:
    """Launch anggota4's pencarian_obat entry script and return its exit code."""
    folder = ANGGOTA["anggota4"]
    entry = folder / "pencarian_obat.py"
    return subprocess.run([sys.executable, str(entry)], cwd=folder).returncode


def jalankan_visualisasi() -> int:
    """Launch anggota3's TampilGrafik viewer and return its exit code."""
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
