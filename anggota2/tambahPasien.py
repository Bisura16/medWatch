"""
===================================================
  MEDWATCH - TambahPasien.py
  Deskripsi: Input data pasien baru dengan
             format SOAP (Subjektif, Objektif,
             Assessment, Planning)
===================================================
"""

from datetime import datetime
from pasien_helper import baca_file, simpan_file, generate_id, input_wajib, FILE_PASIEN


def TambahPasien() -> dict:
    """
    Meminta user mengisi data pasien + SOAP,
    lalu menyimpannya ke Pasien.json.
    """
    print("\n" + "=" * 50)
    print("   TAMBAH DATA PASIEN BARU - MEDWATCH")
    print("=" * 50)

    # ── DATA IDENTITAS ────────────────────────────
    print("\n── DATA PASIEN ──────────────────────────────")
    tanggal = input(f"Tanggal kunjungan (default {datetime.now().strftime('%d-%m-%Y')}): ").strip()
    if not tanggal:
        tanggal = datetime.now().strftime("%d-%m-%Y")

    nama     = input_wajib("Nama pasien       : ")
    umur     = input_wajib("Umur              : ")
    alamat   = input_wajib("Alamat            : ")
    kategori = input("Kategori pasien   : ").strip()  # bebas isi, contoh: Ibu Hamil, Umum, Anak, KB, dll

    # ── S : SUBJEKTIF ─────────────────────────────
    print("\n── S : SUBJEKTIF (Keluhan) ──────────────────")
    keluhan  = input_wajib("Keluhan           : ")
    riwayat  = input("Riwayat penyakit  : ").strip()

    # ── O : OBJEKTIF ──────────────────────────────
    print("\n── O : OBJEKTIF (Pemeriksaan Fisik) ─────────")
    td       = input("Tekanan darah     : ").strip()
    nadi     = input("Nadi (x/menit)    : ").strip()
    suhu     = input("Suhu tubuh (°C)   : ").strip()
    rr       = input("Respirasi (x/mnt) : ").strip()
    bb       = input("Berat badan (kg)  : ").strip()
    tb       = input("Tinggi badan (cm) : ").strip()
    lila     = input("LILA (cm)         : ").strip()
    catatan_o= input("Catatan lain      : ").strip()

    # ── A : ASSESSMENT ────────────────────────────
    print("\n── A : ASSESSMENT (Diagnosa) ────────────────")
    diagnosa = input_wajib("Diagnosa          : ")

    # ── P : PLANNING ──────────────────────────────
    print("\n── P : PLANNING (Tindakan & Resep) ──────────")
    tindakan = input_wajib("Tindakan/anjuran  : ")
    resep    = input("Resep obat        : ").strip()
    kontrol  = input("Jadwal kontrol    : ").strip()

    # ── SUSUN DATA ────────────────────────────────
    semua_data  = baca_file(FILE_PASIEN)
    pasien_baru = {
        "id"               : generate_id(semua_data),
        "tanggal_kunjungan": tanggal,
        "nama"             : nama,
        "umur"             : umur,
        "alamat"           : alamat,
        "kategori"         : kategori,
        "S": {
            "keluhan" : keluhan,
            "riwayat" : riwayat,
        },
        "O": {
            "tekanan_darah" : td,
            "nadi"          : nadi,
            "suhu_c"        : suhu,
            "respirasi"     : rr,
            "bb_kg"         : bb,
            "tb_cm"         : tb,
            "lila_cm"       : lila,
            "catatan"       : catatan_o,
        },
        "A": {
            "diagnosa" : diagnosa,
        },
        "P": {
            "tindakan"       : tindakan,
            "resep"          : resep,
            "jadwal_kontrol" : kontrol,
        },
    }

    semua_data.append(pasien_baru)
    simpan_file(semua_data, FILE_PASIEN)

    print(f"\n{'=' * 50}")
    print(f"[✓] Data '{nama}' berhasil disimpan. ID: {pasien_baru['id']}")
    print(f"{'=' * 50}")
    return pasien_baru


# ── Test langsung ──────────────────────────────────
if __name__ == "__main__":
    TambahPasien()