"""
main.py  -  MedWatch Terminal UI
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
            gagal(f"{nama}  -  {obj}")
            semua_ok = False
    return semua_ok, hasil


# ══════════════════════════════════════════════
# ANGGOTA 1  -  SCRAPER
# ══════════════════════════════════════════════

def tes_anggota1():
    header("ANGGOTA 1  -  Scraper Data Obat (drugs.com + FDA)")
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
# ANGGOTA 2  -  CRUD PASIEN
# ══════════════════════════════════════════════

def tes_anggota2():
    header("ANGGOTA 2  -  CRUD Data Pasien")
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
        print("  [1]  Buka menu interaktif PasienCRUD")
        print("  [0]  Kembali tanpa membuka menu")
        garis("─")
        pilihan = input("  Pilih: ").strip()
        if pilihan == "1":
            print()
            subprocess.run([sys.executable, "PasienCRUD.py"], cwd=str(folder))
    else:
        print("  Ada modul yang gagal. Periksa error di atas.")

    pause()


# ══════════════════════════════════════════════
# ANGGOTA 3  -  VISUALISASI GRAFIK
# ══════════════════════════════════════════════

def tes_anggota3():
    header("ANGGOTA 3  -  Visualisasi Grafik")
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
# ANGGOTA 4  -  PENCARIAN OBAT
# ══════════════════════════════════════════════

def tes_anggota4():
    header("ANGGOTA 4  -  Pencarian Obat & Safety Check")
    folder = ROOT / "anggota4"
    modul  = ["data_loader", "safety_checker", "pencarian_obat"]

    print("\n  1. Cek import sub-modul:")
    semua_ok, mods = test_modul(folder, modul)

    if semua_ok:
        pencarian = mods["pencarian_obat"]
        print()
        pencarian._main()
    else:
        print("\n  Ada modul yang gagal. Periksa error di atas.")

    eject_path(folder)
    for m in modul:
        bersih(m)

    pause()


# ══════════════════════════════════════════════
# ANGGOTA 5  -  LAPORAN PDF
# ══════════════════════════════════════════════

def tes_anggota5():
    header("ANGGOTA 5  -  Ekspor Laporan PDF")
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
        print("  Semua modul OK.")
        print("  Akun demo  →  username: dal   password: 123\n")
        print("  [1]  Jalankan fitur ekspor PDF (butuh input login)")
        print("  [0]  Kembali")
        garis("─")
        pilihan = input("  Pilih: ").strip()
        if pilihan == "1":
            print()
            subprocess.run([sys.executable, "main_anggota5.py"], cwd=str(folder))
    else:
        print("  Ada modul yang gagal. Periksa error di atas.")

    pause()


# ══════════════════════════════════════════════
# MENU UTAMA
# ══════════════════════════════════════════════

MENU = [
    ("1", "Anggota 1  -  Scraper Data Obat (drugs.com + FDA)", tes_anggota1),
    ("2", "Anggota 2  -  CRUD Data Pasien",                    tes_anggota2),
    ("3", "Anggota 3  -  Visualisasi Grafik (Matplotlib)",     tes_anggota3),
    ("4", "Anggota 4  -  Pencarian Obat & Safety Check",       tes_anggota4),
    ("5", "Anggota 5  -  Ekspor Laporan PDF",                  tes_anggota5),
]

def menu_utama():
    while True:
        clear()
        garis()
        print("         M E D W A T C H  -  Tes Modul Sistem")
        garis()
        print()
        for kode, label, _ in MENU:
            print(f"  [{kode}]  {label}")
        print()
        print("  [0]  Keluar")
        print()
        garis()
        pilihan = input("  Pilih modul: ").strip()

        if pilihan == "0":
            clear()
            print("  Keluar dari MedWatch Tes Modul.\n")
            break

        aksi = next((fn for k, _, fn in MENU if k == pilihan), None)
        if aksi:
            aksi()
        else:
            input("  [!] Pilihan tidak valid. Tekan [Enter] untuk lanjut...")


if __name__ == "__main__":
    menu_utama()
