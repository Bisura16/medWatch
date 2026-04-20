"""

  fungsi ReadDataPasien.py
  Deskripsi: Membaca dan menampilkan data pasien
             ke dashboard dokter

"""
from pasien_helper import baca_file, FILE_PASIEN


def ReadDataPasien(id_pasien: str = None):
    """
    - Tanpa id_pasien → kembalikan semua data (list)
    - Dengan id_pasien → kembalikan 1 data (dict)
    """
    data = baca_file(FILE_PASIEN)

    if id_pasien is None:
        print(f"[✓] Total pasien: {len(data)}")
        return data

    for pasien in data:
        if pasien["id"] == id_pasien:
            print(f"[✓] Ditemukan: {pasien['nama']}")
            return pasien

    print(f"[✗] ID '{id_pasien}' tidak ditemukan.")
    return None


def TampilDashboardDokter() -> None:
    """
    Tampilkan data pasien dalam 2 bagian:
    1. Tabel ringkasan (ID, Nama, Tgl, Kategori, Diagnosa)
    2. Detail lengkap tiap pasien (semua field SOAP)
    """
    data = ReadDataPasien()

    if not data:
        print("Belum ada data pasien.")
        return

    W = 90

    #  BAGIAN 1 : TABEL RINGKASAN

    print("\n" + "=" * W)
    print(f"  {'DASHBOARD DOKTER - MEDWATCH - Fasilitas Kesehatan Tingkat 1':^{W-2}}")
    print("=" * W)
    print(f"  {'ID':<7} {'Nama':<22} {'Umur':<6} {'Tgl Kunjungan':<14} {'Kategori':<14} {'Diagnosa'}")
    print("-" * W)

    for p in data:
        diagnosa = p.get("A", {}).get("diagnosa", "-")
        print(
            f"  {p['id']:<7} {p['nama']:<22} {str(p.get('umur','-')):<6} "
            f"{p['tanggal_kunjungan']:<14} {p.get('kategori','-'):<14} {diagnosa}"
        )

    print("=" * W)
    print(f"  Total: {len(data)} pasien")

    #  BAGIAN 2 : DETAIL LENGKAP PER PASIEN
    print("\n" + "=" * W)
    print(f"  {'DETAIL LENGKAP SEMUA PASIEN':^{W-2}}")
    print("=" * W)

    for p in data:
        s  = p.get("S", {})
        o  = p.get("O", {})
        a  = p.get("A", {})
        pl = p.get("P", {})

        print(f"\n  ┌─ {p['id']} │ {p['nama']} │ {p.get('umur','-')} thn │ {p['tanggal_kunjungan']} │ {p.get('kategori','-')}")
        print(f"  │  Alamat         : {p.get('alamat', '-')}")
        print(f"  │")
        print(f"  │  [S] Keluhan    : {s.get('keluhan', '-')}")
        print(f"  │      Riwayat    : {s.get('riwayat', '-') or '-'}")
        print(f"  │")
        print(f"  │  [O] TD         : {o.get('tekanan_darah', '-') or '-'}")
        print(f"  │      BB / TB    : {o.get('bb_kg', '-') or '-'} kg / {o.get('tb_cm', '-') or '-'} cm")
        print(f"  │      Nadi       : {o.get('nadi', '-') or '-'}   Suhu: {o.get('suhu_c', '-') or '-'} °C   RR: {o.get('respirasi', '-') or '-'}")
        print(f"  │      LILA       : {o.get('lila_cm', '-') or '-'} cm")
        print(f"  │      Catatan    : {o.get('catatan', '-') or '-'}")
        print(f"  │")
        print(f"  │  [A] Diagnosa   : {a.get('diagnosa', '-') or '-'}")
        print(f"  │")
        print(f"  │  [P] Tindakan   : {pl.get('tindakan', '-') or '-'}")
        print(f"  │      Resep      : {pl.get('resep', '-') or '-'}")
        print(f"  └─    Kontrol     : {pl.get('jadwal_kontrol', '-') or '-'}")

    print("\n" + "=" * W)


def TampilDetailPasien(id_pasien: str) -> None:
    """Tampilkan detail lengkap 1 pasien beserta SOAP."""
    p = ReadDataPasien(id_pasien)
    if not p:
        return

    o  = p.get("O", {})
    s  = p.get("S", {})
    a  = p.get("A", {})
    pl = p.get("P", {})
    W  = 55

    print("\n" + "=" * W)
    print(f"  DETAIL PASIEN - {p['id']}")
    print("=" * W)
    print(f"  Tanggal Kunjungan : {p['tanggal_kunjungan']}")
    print(f"  Nama              : {p['nama']}")
    print(f"  Umur              : {p.get('umur', '-')}")
    print(f"  Alamat            : {p.get('alamat', '-')}")
    print(f"  Kategori          : {p.get('kategori', '-')}")
    print(f"\n  ── S : SUBJEKTIF ──────────────────────")
    print(f"  Keluhan           : {s.get('keluhan', '-')}")
    print(f"  Riwayat penyakit  : {s.get('riwayat', '-') or '-'}")
    print(f"\n  ── O : OBJEKTIF ───────────────────────")
    print(f"  Tekanan Darah     : {o.get('tekanan_darah', '-') or '-'}")
    print(f"  BB / TB           : {o.get('bb_kg', '-') or '-'} kg / {o.get('tb_cm', '-') or '-'} cm")
    print(f"  Nadi              : {o.get('nadi', '-') or '-'}")
    print(f"  Suhu              : {o.get('suhu_c', '-') or '-'} °C")
    print(f"  Respirasi         : {o.get('respirasi', '-') or '-'}")
    print(f"  LILA              : {o.get('lila_cm', '-') or '-'} cm")
    print(f"  Catatan           : {o.get('catatan', '-') or '-'}")
    print(f"\n  ── A : ASSESSMENT ─────────────────────")
    print(f"  Diagnosa          : {a.get('diagnosa', '-') or '-'}")
    print(f"\n  ── P : PLANNING ───────────────────────")
    print(f"  Tindakan/Anjuran  : {pl.get('tindakan', '-') or '-'}")
    print(f"  Resep Obat        : {pl.get('resep', '-') or '-'}")
    print(f"  Jadwal Kontrol    : {pl.get('jadwal_kontrol', '-') or '-'}")
    print("=" * W)


if __name__ == "__main__":
    TampilDashboardDokter()