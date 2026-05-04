"""
main.py  —  MedWatch Terminal UI
Tes semua modul anggota 1-5 dari satu titik.
Jalankan dari folder medWatch-main:  python main.py
"""

import sys
import os
import importlib
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "anggota5")) # Pastikan auth.py ada di folder ini
try:
    from auth import verifikasi_login, registrasi_akun
except ImportError:
    print("[!] Modul auth.py tidak ditemukan. Pastikan path-nya benar.")


# ══════════════════════════════════════════════
# HELPER UI
# ══════════════════════════════════════════════

def clear():
    os.system("clear")

def garis(char="═", lebar=58):
    print(char * lebar)

def header(judul):
    clear()
    garis()
    print(f"  MEDWATCH  │  {judul}")
    garis()

def pause():
    input("\n  ↩  Tekan [Enter] untuk kembali ke menu utama...")

def ok(pesan):
    print(f"  [OK]     {pesan}")

def gagal(pesan):
    print(f"  [GAGAL]  {pesan}")


# ══════════════════════════════════════════════
# HELPER IMPORT
# ══════════════════════════════════════════════

def inject_path(folder: Path):
    p = str(folder)
    if p not in sys.path:
        sys.path.insert(0, p)

def eject_path(folder: Path):
    p = str(folder)
    while p in sys.path:
        sys.path.remove(p)

def bersih(nama_modul: str):
    """Hapus satu modul dari sys.modules agar fresh import."""
    for key in list(sys.modules):
        if key == nama_modul or key.startswith(nama_modul + "."):
            del sys.modules[key]

def coba_import(nama: str) -> tuple[bool, object]:
    """Return (sukses, modul_atau_None)."""
    try:
        mod = importlib.import_module(nama)
        return True, mod
    except Exception as e:
        return False, e

def test_deps(deps: list[str]) -> bool:
    all_ok = True
    for dep in deps:
        sukses, hasil = coba_import(dep)
        if sukses:
            ok(f"import {dep}")
        else:
            gagal(f"import {dep}  ← pip install {dep}")
            all_ok = False
    return all_ok

def test_modul(folder: Path, nama_list: list[str]) -> tuple[bool, dict]:
    """
    Inject folder ke sys.path, lalu coba import tiap nama.
    Return (semua_ok, {nama: modul}).
    """
    inject_path(folder)
    hasil = {}
    semua_ok = True
    for nama in nama_list:
        bersih(nama)
        sukses, obj = coba_import(nama)
        if sukses:
            ok(nama)
            hasil[nama] = obj
        else:
            gagal(f"{nama}  —  {obj}")
            semua_ok = False
    return semua_ok, hasil


# ══════════════════════════════════════════════
# ANGGOTA 1  —  SCRAPER
# ══════════════════════════════════════════════

def tes_anggota1():
    header("ANGGOTA 1  —  Scraper Data Obat (drugs.com + FDA)")
    folder = ROOT / "anggota1"
    file   = folder / "anggota1.py"

    print("\n  Scraper membutuhkan koneksi internet & ±5 menit.")
    print("  Tes ini hanya memverifikasi modul bisa dimuat.\n")

    print("  1. Cek library eksternal:")
    ok_dep = test_deps(["requests", "bs4"])

    print("\n  2. Load modul anggota1.py:")
    try:
        spec = importlib.util.spec_from_file_location("anggota1_mod", str(file))
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ok("anggota1.py berhasil dimuat")
        ok(f"Jumlah obat terdaftar  : {len(mod.DRUGS)}")
        ok(f"Jumlah kategori        : {len(mod.KATEGORI)}")
        ok("Fungsi scrape_efek_samping() tersedia")
        ok("Fungsi scrape_recall()       tersedia")
    except Exception as e:
        gagal(f"Gagal load: {e}")

    print()
    garis("─")
    print("  Untuk menjalankan scraper sungguhan:")
    print("    cd anggota1 && python anggota1.py")
    pause()


# ══════════════════════════════════════════════
# ANGGOTA 2  —  CRUD PASIEN
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
# ANGGOTA 2  —  CRUD PASIEN (DIPERBARUI)
# ══════════════════════════════════════════════

def tes_anggota2(role_aktif, id_faskes_aktif):
    header("ANGGOTA 2  —  CRUD Data Pasien")
    folder = ROOT / "anggota2"
    modul  = ["pasien_helper", "TambahPasien", "ReadDataPasien",
              "HapusDataPasien", "EditDataPasien", "PasienCRUD"]

    print("\n  1. Cek import semua sub-modul:")
    semua_ok, _ = test_modul(folder, modul)

    eject_path(folder)
    for m in modul:
        bersih(m)

    print()
    garis("─")
    if semua_ok:
        print("  Semua modul OK.\n")
        print(f"  Login sebagai : {role_aktif.upper()}")
        print(f"  ID Faskes     : {id_faskes_aktif}")
        print("-" * 30)
        print("  [1]  Buka menu interaktif PasienCRUD")
        print("  [0]  Kembali tanpa membuka menu")
        garis("─")
        pilihan = input("  Pilih: ").strip()
        
        if pilihan == "1":
            print()
            # Meneruskan role dan id_faskes sebagai argumen sistem (sys.argv)
            # Ini akan ditangkap oleh blok 'if __name__ == "__main__":' di PasienCRUD.py
            subprocess.run([sys.executable, "PasienCRUD.py", role_aktif, id_faskes_aktif], cwd=str(folder))
    else:
        print("  Ada modul yang gagal. Periksa error di atas.")

    pause()


# ══════════════════════════════════════════════
# ANGGOTA 3  —  VISUALISASI GRAFIK
# ══════════════════════════════════════════════

def tes_anggota3():
    header("ANGGOTA 3  —  Visualisasi Grafik")
    folder = ROOT / "anggota3"
    modul  = ["BacaData", "PerbandinganObat", "TampilGrafik",
              "grafik_efek", "grafik_penyakit", "grafik_top_efek"]

    print("\n  1. Cek library eksternal:")
    ok_dep = test_deps(["matplotlib", "numpy"])

    print("\n  2. Cek import sub-modul:")
    semua_ok, mods = test_modul(folder, modul)
    semua_ok = semua_ok and ok_dep

    if semua_ok:
        TampilGrafik = mods["TampilGrafik"]
        print()
        garis("─")
        print("  Pilih grafik yang ingin ditampilkan:\n")
        print("  [1]  Pie Chart + Bar Chart Distribusi Keluhan")
        print("  [2]  Heatmap Efek Samping Obat")
        print("  [3]  Bar Chart Top 10 Efek Samping")
        print("  [4]  Tampilkan semua (3 jenis)")
        print("  [0]  Lewati")
        garis("─")
        pilihan = input("  Pilih: ").strip()

        try:
            if pilihan == "1":
                print("  Membuka grafik distribusi keluhan...")
                TampilGrafik.visgrafikkeluhan()
            elif pilihan == "2":
                print("  Membuka heatmap efek samping...")
                TampilGrafik.visgrafikEfek()
            elif pilihan == "3":
                print("  Membuka top 10 efek samping...")
                TampilGrafik.Vgrafik10topEfek()
            elif pilihan == "4":
                print("  Membuka semua grafik...")
                TampilGrafik.visgrafikkeluhan()
                TampilGrafik.visgrafikEfek()
                TampilGrafik.Vgrafik10topEfek()
        except Exception as e:
            gagal(f"Gagal tampil grafik: {e}")
    else:
        print()
        print("  Ada modul yang gagal. Periksa error di atas.")

    eject_path(folder)
    for m in modul:
        bersih(m)

    pause()


# ══════════════════════════════════════════════
# ANGGOTA 4  —  PENCARIAN OBAT
# ══════════════════════════════════════════════

def tes_anggota4():
    header("ANGGOTA 4  —  Pencarian Obat & Safety Check")
    folder = ROOT / "anggota4"
    modul  = ["data_loader", "safety_checker", "pencarian_obat"]

    print("\n  1. Cek import sub-modul:")
    semua_ok, mods = test_modul(folder, modul)

    if semua_ok:
        pencarian = mods["pencarian_obat"]
        print()
        garis("─")
        print("  Modul siap. Ketik nama obat untuk dicari.")
        print("  Contoh: ibuprofen  |  amoxicillin  |  metformin")
        print("  Ketik 'selesai' atau biarkan kosong untuk kembali.\n")

        while True:
            garis("─")
            kata = input("  Cari obat: ").strip()
            if not kata or kata.lower() in ("selesai", "exit", "0"):
                break

            print()
            hasil = pencarian.cari_obat(kata)
            print(pencarian.format_hasil_pencarian(hasil))

            if hasil["jumlah_hasil"] > 0:
                print()
                tanya = input("  Tampilkan profil keamanan lengkap? [y/n]: ").strip().lower()
                if tanya == "y":
                    profil = pencarian.ambil_profil_keamanan_lengkap(kata)
                    print()
                    print(pencarian.format_profil_keamanan(profil))

    else:
        print("\n  Ada modul yang gagal. Periksa error di atas.")

    eject_path(folder)
    for m in modul:
        bersih(m)

    pause()


# ══════════════════════════════════════════════
# ANGGOTA 5  —  LAPORAN PDF
# ══════════════════════════════════════════════

# ══════════════════════════════════════════════
# ANGGOTA 5  —  LAPORAN PDF (DIPERBARUI)
# ══════════════════════════════════════════════

def tes_anggota5(role_aktif, id_faskes_aktif):
    header("ANGGOTA 5  —  Ekspor Laporan PDF")
    folder = ROOT / "anggota5"
    modul  = ["auth", "ambil_data", "export_pdf"]

    print("\n  1. Cek library eksternal:")
    ok_dep = test_deps(["fpdf"])

    print("\n  2. Cek import sub-modul:")
    semua_ok, _ = test_modul(folder, modul)
    semua_ok = semua_ok and ok_dep

    eject_path(folder)
    for m in modul:
        bersih(m)

    print()
    garis("─")
    if semua_ok:
        print("  Semua modul OK.\n")
        print(f"  Login sebagai : {role_aktif.upper()}")
        print(f"  ID Faskes     : {id_faskes_aktif}")
        print("-" * 30)
        # Keterangan diubah karena sekarang login sudah otomatis diteruskan
        print("  [1]  Jalankan fitur ekspor PDF (Langsung Masuk)")
        print("  [0]  Kembali")
        garis("─")
        pilihan = input("  Pilih: ").strip()
        if pilihan == "1":
            print()
            # Meneruskan role dan id_faskes ke main_anggota5.py
            # Argumen ini akan ditangkap oleh sys.argv di file tujuan
            subprocess.run([sys.executable, "main_anggota5.py", role_aktif, id_faskes_aktif], cwd=str(folder))
    else:
        print("  Ada modul yang gagal. Periksa error di atas.")

    pause()


# ══════════════════════════════════════════════
# MENU UTAMA (DIPERBARUI DENGAN AUTH)
# ══════════════════════════════════════════════

def menu_dashboard(user, role, faskes):
    """Menu pengujian modul setelah berhasil login."""
    
    # VARIABEL MENU HARUS ADA DI DALAM SINI
    # Agar dia mengenali variabel 'role' dan 'faskes' dari parameter di atas
    MENU = [
        ("1", "Anggota 1  —  Scraper Data Obat", tes_anggota1),
        ("2", "Anggota 2  —  CRUD Data Pasien", lambda: tes_anggota2(role, faskes)),
        ("3", "Anggota 3  —  Visualisasi Grafik", tes_anggota3),
        ("4", "Anggota 4  —  Pencarian Obat & Safety Check", tes_anggota4),
        ("5", "Anggota 5  —  Ekspor Laporan PDF", lambda: tes_anggota5(role, faskes)),
    ]

    while True:
        clear()
        garis()
        print(f"  MEDWATCH — Tes Modul | Akun: {user.upper()} ({role.upper()})")
        print(f"  ID Faskes: {faskes}")
        garis()
        print()
        for kode, label, aksi in MENU:
            print(f"  [{kode}]  {label}")
        print("\n  [0]  Logout\n")
        garis()
        
        pilihan = input("  Pilih modul: ").strip()

        if pilihan == "0":
            break # Keluar dari loop dashboard, kembali ke menu_utama

        aksi = next((fn for k, _, fn in MENU if k == pilihan), None)
        if aksi:
            aksi() # Menjalankan lambda di sini
        else:
            input("  [!] Pilihan tidak valid. Tekan [Enter] untuk lanjut...")


def menu_utama():
    """Gerbang Pertama Aplikasi (Login / Register)"""
    while True:
        header("SISTEM MEDWATCH OFFLINE")
        print("  [1]  Login ke Sistem")
        print("  [2]  Registrasi Akun Baru")
        print("  [0]  Keluar Aplikasi\n")
        garis()
        
        pilihan = input("  Pilih: ").strip()
        
        if pilihan == "1":
            sukses, user, role, faskes = verifikasi_login()
            if sukses:
                pause()
                # Lempar data login ke menu_dashboard
                menu_dashboard(user, role, faskes) 
            else:
                gagal("Username atau Password salah!")
                pause()
                
        elif pilihan == "2":
            registrasi_akun()
            pause()
            
        elif pilihan == "0":
            clear()
            print("  Keluar dari MedWatch.\n")
            break

if __name__ == "__main__":
    menu_utama()
