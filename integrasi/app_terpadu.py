"""
Unified desktop CLI app komposit anggota1-5.
Login pakai role dari anggota5/auth.py, terus dispatch menu sesuai role.

Tidak modifikasi file anggota manapun. Pure subprocess / import shim
via integrasi/adapter.py.

Run: python integrasi/app_terpadu.py  (dari root repo medWatch)
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
    print(char * lebar)


def menu_admin():
    """Menu admin: scraper + tkesehatan CRUD + akses penuh ke fitur lain."""
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
    """Menu tenaga kesehatan: CRUD pasien + cari obat + visualisasi + ekspor PDF."""
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
