"""
===================================================
  MEDWATCH - HapusDataPasien.py
  Deskripsi: Menghapus data pasien dari Pasien.json
===================================================
"""

from pasien_helper import baca_file, simpan_file, FILE_PASIEN


def HapusDataPasien() -> bool:
    """
    Meminta user memasukkan ID pasien, tampilkan
    data pasien, minta konfirmasi, lalu hapus.
    """
    print("\n" + "=" * 45)
    print("   HAPUS DATA PASIEN")
    print("=" * 45)

    id_pasien = input("Masukkan ID pasien yang ingin dihapus : ").strip()
    data      = baca_file(FILE_PASIEN)

    pasien_target = next((p for p in data if p["id"] == id_pasien), None)

    if pasien_target is None:
        print(f"\n[✗] ID '{id_pasien}' tidak ditemukan.")
        return False

    print(f"\n  Pasien yang akan dihapus:")
    print(f"  ID       : {pasien_target['id']}")
    print(f"  Nama     : {pasien_target['nama']}")
    print(f"  Kategori : {pasien_target['kategori']}")
    print(f"  Tgl      : {pasien_target['tanggal_kunjungan']}")

    konfirmasi = input("\nYakin ingin menghapus? (y/n) : ").strip().lower()
    if konfirmasi != "y":
        print("[!] Penghapusan dibatalkan.")
        return False

    data_baru = [p for p in data if p["id"] != id_pasien]
    simpan_file(data_baru, FILE_PASIEN)
    print(f"\n[✓] Data pasien '{pasien_target['nama']}' berhasil dihapus.")
    return True


# ── Test langsung ──────────────────────────────────
if __name__ == "__main__":
    HapusDataPasien()