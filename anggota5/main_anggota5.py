import sys
import os

# Memastikan Python bisa mengimport modul di folder yang sama
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ambil_data import ambil_seluruh_data_pasien
from export_pdf import buat_laporan_pdf

def jalankan_fitur_anggota_5():
    # 1. Autentikasi Sederhana (Sesuai akun demo di menu tester kamu)
    print("\n" + "═"*40)
    print("       LOGIN FITUR ANGGOTA 5")
    print("═"*40)
    username = input("  Username : ").strip()
    password = input("  Password : ").strip()

    if username != "dal" or password != "123":
        print("\n  [!] Login Gagal: Akses Ditolak.")
        return

    # 2. Ambil Data dari JSON (Sudah terformat melalui ambil_data.py)
    data = ambil_seluruh_data_pasien()
    if not data:
        print("\n  [!] Gagal: Data pasien tidak ditemukan atau JSON kosong.")
        return

    # 3. Menu Pilihan Ekspor
    while True:
        print("\n" + "─"*40)
        print("      MENU EKSPOR PDF MEDWATCH")
        print("─"*40)
        print("  [1] Cetak Semua Pasien (+ Grafik Analitik)")
        print("  [2] Cetak Pasien Tertentu (Berdasarkan ID)")
        print("  [0] Kembali ke Menu Utama")
        print("─"*40)
        
        pilihan = input("  Pilih opsi: ").strip()

        if pilihan == "1":
            print("\n  [*] Sedang memproses seluruh data...")
            buat_laporan_pdf(data, "Laporan_Lengkap_MedWatch.pdf")
            
        elif pilihan == "2":
            # Menampilkan daftar ID yang tersedia agar user tidak menebak
            ids_tersedia = [p.get("identitas", {}).get("ID Pasien") for p in data]
            print(f"\n  ID Tersedia: {', '.join(ids_tersedia)}")
            
            id_target = input("  Masukkan ID Pasien (contoh: P001): ").strip()
            
            print(f"  [*] Sedang memproses ID {id_target}...")
            # Memanggil fungsi dengan parameter id_pasien_terpilih
            buat_laporan_pdf(
                data, 
                output_filename=f"Laporan_Pasien_{id_target}.pdf", 
                id_pasien_terpilih=id_target
            )
            
        elif pilihan == "0":
            break
        else:
            print("  [!] Pilihan tidak valid.")

if __name__ == "__main__":
    jalankan_fitur_anggota_5()
