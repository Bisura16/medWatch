"""
===================================================
  fungsi PasienCRUD.py
  Deskripsi: Menu utama modul PasienCRUD.
  Struktur:

  PasienCRUD.py
  ── TambahPasien.py      = input SOAP per kategori
  ── ReadDataPasien.py    = dashboard dokter
  ── HapusDataPasien.py   = hapus dengan konfirmasi
  ── EditDataPasien.py    = edit data & SOAP
  ── pasien_helper.py     = baca/simpan Pasien.json
"""

from TambahPasien   import TambahPasien
from ReadDataPasien import ReadDataPasien, TampilDashboardDokter, TampilDetailPasien
from HapusDataPasien import HapusDataPasien
from EditDataPasien  import EditDataPasien


def menu_pasien_crud():
    """Menu utama PasienCRUD."""
    while True:
        print("\n" + "=" * 50)
        print("   MENU PASIEN CRUD - MEDWATCH - Fasilitas Kesehatan Tingkat 1")
        print("=" * 50)
        print("  [1] Tambah Pasien Baru")
        print("  [2] Lihat Semua Pasien (Dashboard Dokter)")
        print("  [3] Lihat Detail Pasien (by ID)")
        print("  [4] Edit Data Pasien")
        print("  [5] Hapus Data Pasien")
        print("  [0] Keluar")
        print("-" * 50)

        pilihan = input("Pilih menu : ").strip()

        if   pilihan == "1": TambahPasien()
        elif pilihan == "2": TampilDashboardDokter()
        elif pilihan == "3":
            id_cari = input("Masukkan ID pasien : ").strip()
            TampilDetailPasien(id_cari)
        elif pilihan == "4": EditDataPasien()
        elif pilihan == "5": HapusDataPasien()
        elif pilihan == "0":
            print("\n[✓] Keluar dari PasienCRUD.")
            break
        else:
            print("[!] Pilihan tidak valid.")


if __name__ == "__main__":
    menu_pasien_crud()