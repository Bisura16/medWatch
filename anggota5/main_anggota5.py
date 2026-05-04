"""
Entry point modul anggota5.
Login dulu, terus tampilin menu sesuai role.
- Admin: scraper, CRUD tenaga kesehatan, ekspor PDF
- Tenaga kesehatan: ekspor PDF (CRUD pasien diakses lewat anggota2)
"""
import os
import sys
import subprocess

from auth import verifikasi_login, hanya_admin
from tkesehatan_crud import menu_tkesehatan_crud


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANGGOTA1_DIR = os.path.join(BASE_DIR, "anggota1")
ANGGOTA1_FILE = os.path.join(ANGGOTA1_DIR, "anggota1.py")


def trigger_scraper():
    """Admin jalanin scraper anggota1. Subprocess ke folder anggota1."""
    if not os.path.exists(ANGGOTA1_FILE):
        print(f"[!] File scraper tidak ditemukan di {ANGGOTA1_FILE}.")
        return

    print("\n[i] Menjalankan scraper anggota1.py. Butuh internet, estimasi 5 menit.")
    print("    Tekan Ctrl+C kalau mau cancel.")
    konfirmasi = input("Lanjut? (y/n): ").strip().lower()
    if konfirmasi != "y":
        return

    try:
        subprocess.run([sys.executable, "anggota1.py"], cwd=ANGGOTA1_DIR)
    except KeyboardInterrupt:
        print("\n[i] Scraper dibatalkan.")
    except Exception as e:
        print(f"[!] Error jalanin scraper: {e}")


def ekspor_pdf():
    """Placeholder yang panggil fungsi export_pdf existing.

    Kalau Abhidal udah punya fungsi ekspor PDF di export_pdf.py atau ambil_data.py,
    panggil dari sini. Kalau belum, biarkan placeholder ini sebagai TODO.
    """
    try:
        from export_pdf import buat_laporan_pdf
        from ambil_data import ambil_seluruh_data_pasien
        data = ambil_seluruh_data_pasien()
        if not data:
            print("[!] Data pasien kosong atau tidak ditemukan.")
            return
        buat_laporan_pdf(data, "Laporan_MedWatch.pdf")
    except ImportError:
        print("[!] Modul export_pdf belum ready. Cek anggota5/export_pdf.py.")
    except Exception as e:
        print(f"[!] Gagal ekspor PDF: {e}")


def menu_admin():
    """Menu utama untuk role admin."""
    while True:
        print("\n" + "=" * 50)
        print("   MENU ADMIN MEDWATCH")
        print("=" * 50)
        print("  [1] Jalankan Scraper Data Obat (anggota1)")
        print("  [2] CRUD Tenaga Kesehatan")
        print("  [3] Ekspor Laporan PDF")
        print("  [0] Logout")
        print("-" * 50)

        pilihan = input("Pilih menu: ").strip()
        if pilihan == "1":
            trigger_scraper()
        elif pilihan == "2":
            menu_tkesehatan_crud()
        elif pilihan == "3":
            ekspor_pdf()
        elif pilihan == "0":
            print("Logout.")
            break
        else:
            print("[!] Pilihan tidak valid.")


def menu_tkesehatan():
    """Menu utama untuk role tenaga_kesehatan."""
    while True:
        print("\n" + "=" * 50)
        print("   MENU TENAGA KESEHATAN MEDWATCH")
        print("=" * 50)
        print("  [1] Ekspor Laporan PDF")
        print("  [0] Logout")
        print("-" * 50)
        print("\n  Catatan: CRUD pasien diakses lewat modul anggota2.")
        print("           Pencarian obat dan safety check lewat modul anggota4.")
        print("-" * 50)

        pilihan = input("Pilih menu: ").strip()
        if pilihan == "1":
            ekspor_pdf()
        elif pilihan == "0":
            print("Logout.")
            break
        else:
            print("[!] Pilihan tidak valid.")


def main():
    """Entry point. Login dulu, terus dispatch ke menu sesuai role."""
    status, username, role = verifikasi_login()
    if not status:
        print("\n[!] Login gagal. Program berhenti.")
        sys.exit(1)

    print(f"\n[OK] Login berhasil. Selamat datang, {username} (role: {role}).")

    if role == "admin":
        menu_admin()
    elif role == "tenaga_kesehatan":
        menu_tkesehatan()
    else:
        print(f"[!] Role tidak dikenal: {role}")
        sys.exit(1)


if __name__ == "__main__":
    main()
