
from database import load_database, save_database, generate_id, get_timestamp


def input_data_pasien() -> dict:
    """
    Mengumpulkan input dari pengguna untuk data pasien baru.
    Mengembalikan dictionary data pasien.
    """
    print("\n" + "=" * 55)
    print("       TAMBAH DATA PASIEN BARU - REKAM MEDIS")
    print("=" * 55)

    # --- DATA IDENTITAS PASIEN ---
    print("\n[IDENTITAS PASIEN]")
    tgl_kunjungan = input("Tanggal Kunjungan (dd-mm-yyyy)     : ").strip()
    nama          = input("Nama Pasien                        : ").strip()
    umur          = input("Umur (tahun)                       : ").strip()
    alamat        = input("Alamat                             : ").strip()

    # --- SUBJECTIVE (S) ---
    print("\n[S] SUBJECTIVE - Keluhan Pasien")
    subjective = input("Keluhan Pasien                     : ").strip()

    # --- OBJECTIVE (O) ---
    print("\n[O] OBJECTIVE - Pemeriksaan Fisik")
    tekanan_darah   = input("Tekanan Darah (mmHg)               : ").strip()
    berat_badan     = input("Berat Badan (kg)                   : ").strip()
    tinggi_badan    = input("Tinggi Badan (cm)                  : ").strip()
    lingkar_lengan  = input("Lingkar Lengan (cm)                : ").strip()
    pemeriksaan_lain = input("Pemeriksaan Tambahan (opsional)    : ").strip()

    # --- ASSESSMENT (A) ---
    print("\n[A] ASSESSMENT - Diagnosa")
    assessment = input("Diagnosa / Penilaian Klinis        : ").strip()

    # --- PLAN (P) ---
    print("\n[P] PLAN - Rencana Tatalaksana")
    print("Masukkan rencana tatalaksana (ketik 'selesai' untuk mengakhiri):")
    plan_lines = []
    while True:
        line = input("  > ").strip()
        if line.lower() == "selesai":
            break
        if line:
            plan_lines.append(line)

    pasien = {
        "tgl_kunjungan"  : tgl_kunjungan,
        "nama"           : nama,
        "umur"           : umur,
        "alamat"         : alamat,
        "subjective"     : subjective,
        "objective": {
            "tekanan_darah"   : tekanan_darah,
            "berat_badan"     : berat_badan,
            "tinggi_badan"    : tinggi_badan,
            "lingkar_lengan"  : lingkar_lengan,
            "pemeriksaan_lain": pemeriksaan_lain,
        },
        "assessment"     : assessment,
        "plan"           : plan_lines,
    }
    return pasien


def tambah_pasien() -> None:
    """
    Fungsi utama modul TambahPasien.
    Mengambil input, menetapkan ID unik, lalu menyimpan ke database.
    """
    data = load_database()

    pasien_baru = input_data_pasien()

    # Tetapkan metadata
    pasien_baru["id"]           = generate_id(data)
    pasien_baru["dibuat_pada"]  = get_timestamp()
    pasien_baru["diubah_pada"]  = get_timestamp()

    # Konfirmasi sebelum simpan
    print("\n" + "-" * 55)
    print("RINGKASAN DATA YANG AKAN DISIMPAN:")
    print("-" * 55)
    print(f"  ID          : {pasien_baru['id']}")
    print(f"  Tgl Kunjungan: {pasien_baru['tgl_kunjungan']}")
    print(f"  Nama        : {pasien_baru['nama']}")
    print(f"  Umur        : {pasien_baru['umur']} tahun")
    print(f"  Alamat      : {pasien_baru['alamat']}")
    print(f"  S           : {pasien_baru['subjective']}")
    print(f"  O - TD      : {pasien_baru['objective']['tekanan_darah']}")
    print(f"  A           : {pasien_baru['assessment']}")
    print(f"  P           : {'; '.join(pasien_baru['plan'])}")
    print("-" * 55)

    konfirmasi = input("Simpan data pasien ini? (y/n): ").strip().lower()
    if konfirmasi == "y":
        data.append(pasien_baru)
        save_database(data)
        print(f"\n✅ Data pasien '{pasien_baru['nama']}' berhasil disimpan dengan ID {pasien_baru['id']}.")
    else:
        print("\n❌ Penyimpanan dibatalkan.")


# ─── Jalankan langsung jika dipanggil sebagai skrip ───────────────────────────
if __name__ == "__main__":
    tambah_pasien()