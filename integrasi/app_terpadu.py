"""Unified desktop CLI app combining anggota1-5.

Authenticates the user via anggota5's ``verifikasi_login`` and
dispatches the appropriate role-scoped menu. The admin menu adds
the scraper and tenaga-kesehatan CRUD on top of the bidan menu.

The integration is non-invasive: no anggota file is modified.
Everything is either run as a subprocess or imported through a
guarded ``sys.path`` window in :mod:`integrasi.adapter`.

Run::

    python integrasi/app_terpadu.py   (from the medWatch repo root)
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
ANGGOTA5 = ROOT / "anggota5"

# Inject anggota5 ke sys.path supaya bisa import auth langsung
sys.path.insert(0, str(ANGGOTA5))

from auth import verifikasi_login  # noqa: E402

from integrasi.adapter import (  # noqa: E402
    jalankan_scraper,
    jalankan_pasien_crud,
    jalankan_pencarian_obat,
    jalankan_visualisasi,
    jalankan_tkesehatan_crud,
    jalankan_export_pdf,
)


def garis(char="=", lebar=58):
    """Print a horizontal divider line for the CLI menus."""
    print(char * lebar)


def menu_admin():
    """Admin menu loop: scraper, tkesehatan CRUD, plus full feature access."""
    while True:
        print()
        garis()
        print("   MEDWATCH TERPADU - MENU ADMIN")
        garis()
        print("  [1] Jalankan Scraper Data Obat (anggota1)")
        print("  [2] CRUD Tenaga Kesehatan (anggota5)")
        print("  [3] CRUD Data Pasien (anggota2)")
        print("  [4] Pencarian Obat & Safety Check (anggota4)")
        print("  [5] Visualisasi Grafik (anggota3)")
        print("  [6] Ekspor Laporan PDF (anggota5)")
        print("  [0] Logout")
        garis("-")

        pilihan = input("Pilih menu: ").strip()
        if   pilihan == "1": jalankan_scraper()
        elif pilihan == "2": jalankan_tkesehatan_crud()
        elif pilihan == "3": jalankan_pasien_crud()
        elif pilihan == "4": jalankan_pencarian_obat()
        elif pilihan == "5": jalankan_visualisasi()
        elif pilihan == "6": jalankan_export_pdf()
        elif pilihan == "0":
            print("Logout.")
            break
        else:
            print("[!] Pilihan tidak valid.")


def menu_tkesehatan():
    """Tenaga kesehatan menu loop: patient CRUD, drug search, viz, and PDF export."""
    while True:
        print()
        garis()
        print("   MEDWATCH TERPADU - MENU TENAGA KESEHATAN")
        garis()
        print("  [1] CRUD Data Pasien (anggota2)")
        print("  [2] Pencarian Obat & Safety Check (anggota4)")
        print("  [3] Visualisasi Grafik (anggota3)")
        print("  [4] Ekspor Laporan PDF (anggota5)")
        print("  [0] Logout")
        garis("-")

        pilihan = input("Pilih menu: ").strip()
        if   pilihan == "1": jalankan_pasien_crud()
        elif pilihan == "2": jalankan_pencarian_obat()
        elif pilihan == "3": jalankan_visualisasi()
        elif pilihan == "4": jalankan_export_pdf()
        elif pilihan == "0":
            print("Logout.")
            break
        else:
            print("[!] Pilihan tidak valid.")


def main():
    """CLI entry: login, then dispatch to the role-specific menu loop."""
    print()
    garis()
    print("        M E D W A T C H   T E R P A D U")
    print("   Desktop CLI komposit anggota1 sampai anggota5")
    garis()

    status, username, role = verifikasi_login()
    if not status:
        print("\n[!] Login gagal. Program berhenti.")
        sys.exit(1)

    print(f"\n[OK] Selamat datang, {username} (role: {role}).")

    if role == "admin":
        menu_admin()
    elif role == "tenaga_kesehatan":
        menu_tkesehatan()
    else:
        print(f"[!] Role tidak dikenal: {role}. Program berhenti.")
        sys.exit(1)


if __name__ == "__main__":
    main()
