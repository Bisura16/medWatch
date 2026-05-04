"""
===================================================
  fungsi PasienCRUD.py
<<<<<<< HEAD
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
=======
  Deskripsi: Menu utama modul PasienCRUD yang sudah 
             mendukung Role-Based Access Control (RBAC).
"""
import sys
from TambahPasien   import TambahPasien
from ReadDataPasien import TampilDashboardDokter, TampilDetailPasien
from HapusDataPasien import HapusDataPasien
from EditDataPasien  import EditDataPasien

def menu_pasien_crud(role_aktif, id_faskes_aktif):
    """Menu utama PasienCRUD dengan pengecekan hak akses."""
    
    # 1. PROTEKSI AKSES: Hanya Dokter dan Admin Faskes yang boleh masuk
    if role_aktif == "pasien":
        print("\n" + "!" * 50)
        print("  [!] AKSES DITOLAK: Fitur ini bukan untuk Pasien.")
        print("  Silakan hubungi tenaga medis di faskes Anda.")
        print("!" * 50)
        return

    while True:
        print("\n" + "=" * 50)
        print(f"   MENU PASIEN CRUD - Faskes ID: {id_faskes_aktif}")
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
        print("=" * 50)
        print("  [1] Tambah Pasien Baru")
        print("  [2] Lihat Semua Pasien (Dashboard Dokter)")
        print("  [3] Lihat Detail Pasien (by ID)")
        print("  [4] Edit Data Pasien")
        print("  [5] Hapus Data Pasien")
        print("  [0] Keluar")
        print("-" * 50)

        pilihan = input("Pilih menu : ").strip()

<<<<<<< HEAD
        if   pilihan == "1": TambahPasien()
        elif pilihan == "2": TampilDashboardDokter()
        elif pilihan == "3":
            id_cari = input("Masukkan ID pasien : ").strip()
            TampilDetailPasien(id_cari)
        elif pilihan == "4": EditDataPasien()
        elif pilihan == "5": HapusDataPasien()
=======
        # 2. INJEKSI ID FASKES: Teruskan ID faskes ke fungsi terkait
        if   pilihan == "1": TambahPasien(id_faskes_aktif)
        elif pilihan == "2": TampilDashboardDokter(id_faskes_aktif)
        elif pilihan == "3":
            id_cari = input("Masukkan ID pasien : ").strip()
            TampilDetailPasien(id_cari, id_faskes_aktif)
        elif pilihan == "4": EditDataPasien(id_faskes_aktif)
        elif pilihan == "5": HapusDataPasien(id_faskes_aktif)
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
        elif pilihan == "0":
            print("\n[✓] Keluar dari PasienCRUD.")
            break
        else:
            print("[!] Pilihan tidak valid.")

<<<<<<< HEAD

if __name__ == "__main__":
    menu_pasien_crud()
=======
if __name__ == "__main__":
    # 3. PENANGANAN ARGUMEN: Menangkap data dari main.py (subprocess)
    # sys.argv[1] = role, sys.argv[2] = id_faskes
    role_aktif = sys.argv[1] if len(sys.argv) > 1 else "pasien"
    id_faskes_aktif = sys.argv[2] if len(sys.argv) > 2 else "PUBLIC"
    
    menu_pasien_crud(role_aktif, id_faskes_aktif)
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
