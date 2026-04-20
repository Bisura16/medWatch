from auth import verifikasi_login
from ambil_data import ambil_seluruh_data_pasien
from export_pdf import buat_laporan_pdf

def jalankan_fitur_anggota_5():
    # 1. GERBANG PERTAMA: Login
    is_logged_in, user_aktif = verifikasi_login()

    # 2. CEK STATUS: Jika gagal, langsung usir (stop)
    if not is_logged_in:
        print("\n[X] Login Gagal. Anda tidak punya akses ke fitur Ekspor.")
        return # Program berhenti di sini

    # 3. JIKA SUKSES: Masuk ke menu
    print(f"\n" + "="*30)
    print(f" HALO, {user_aktif.upper()}!")
    print("="*30)
    print("1. Ekspor Rekam Medis ke PDF")
    print("0. Keluar")
    
    pilihan = input("\nPilih tindakan: ")

    if pilihan == '1':
        print("\n[Wait] Sedang menarik data dan mencetak PDF...")
        data = ambil_seluruh_data_pasien()
        
        if data:
            buat_laporan_pdf(data)
            print(f"[OK] Laporan PDF berhasil dibuat di folder anggota5.")
        else:
            print("[!] Data pasien kosong. Gagal membuat PDF.")
    else:
        print("Keluar dari fitur...")

if __name__ == "__main__":
    jalankan_fitur_anggota_5()