"""
  fungsi EditDataPasien.py
  Deskripsi: Edit data pasien di Pasien.json.
             Tampilkan data lama dulu, user isi
             yang ingin diubah (kosong = skip).
"""

from pasien_helper import baca_file, simpan_file, FILE_PASIEN


def EditDataPasien() -> dict | None:
    """
    Cari pasien by ID, tampilkan data lama,
    user isi field yang ingin diubah.
    Kosongkan = tidak diubah.
    """
    print("\n" + "=" * 50)
    print("   EDIT DATA PASIEN")
    print("=" * 50)

    id_pasien = input("Masukkan ID pasien yang ingin diedit : ").strip()
    data      = baca_file(FILE_PASIEN)

    pasien = next((p for p in data if p["id"] == id_pasien), None)
    if pasien is None:
        print(f"\n[✗] ID '{id_pasien}' tidak ditemukan.")
        return None

    print("\n(Kosongkan field yang tidak ingin diubah)\n")

    #DATA IDENTITAS
    print("── DATA PASIEN ──────────────────────────────")
    def upd(lama, baru): return baru if baru else lama

    tgl      = input(f"Tanggal kunjungan [{pasien['tanggal_kunjungan']}] : ").strip()
    nama     = input(f"Nama              [{pasien['nama']}] : ").strip()
    umur     = input(f"Umur              [{pasien['umur']}] : ").strip()
    alamat   = input(f"Alamat            [{pasien['alamat']}] : ").strip()
    kategori = input(f"Kategori          [{pasien.get('kategori','')}] : ").strip()

    pasien["tanggal_kunjungan"] = upd(pasien["tanggal_kunjungan"], tgl)
    pasien["nama"]              = upd(pasien["nama"], nama)
    pasien["umur"]              = upd(pasien["umur"], umur)
    pasien["alamat"]            = upd(pasien["alamat"], alamat)
    pasien["kategori"]          = upd(pasien.get("kategori", ""), kategori)

    #S : SUBJEKTIF
    s = pasien.get("S", {})
    print("\n── S : SUBJEKTIF ────────────────────────────")
    keluhan = input(f"Keluhan  [{s.get('keluhan','')}] : ").strip()
    riwayat = input(f"Riwayat  [{s.get('riwayat','')}] : ").strip()
    pasien["S"]["keluhan"] = upd(s.get("keluhan", ""), keluhan)
    pasien["S"]["riwayat"] = upd(s.get("riwayat", ""), riwayat)

    #O : OBJEKTIF
    o = pasien.get("O", {})
    print("\n── O : OBJEKTIF ─────────────────────────────")
    td       = input(f"Tekanan darah  [{o.get('tekanan_darah','')}] : ").strip()
    nadi     = input(f"Nadi           [{o.get('nadi','')}] : ").strip()
    suhu     = input(f"Suhu (°C)      [{o.get('suhu_c','')}] : ").strip()
    rr       = input(f"Respirasi      [{o.get('respirasi','')}] : ").strip()
    bb       = input(f"BB (kg)        [{o.get('bb_kg','')}] : ").strip()
    tb       = input(f"TB (cm)        [{o.get('tb_cm','')}] : ").strip()
    lila     = input(f"LILA (cm)      [{o.get('lila_cm','')}] : ").strip()
    cat_o    = input(f"Catatan lain   [{o.get('catatan','')}] : ").strip()

    pasien["O"]["tekanan_darah"] = upd(o.get("tekanan_darah",""), td)
    pasien["O"]["nadi"]          = upd(o.get("nadi",""), nadi)
    pasien["O"]["suhu_c"]        = upd(o.get("suhu_c",""), suhu)
    pasien["O"]["respirasi"]     = upd(o.get("respirasi",""), rr)
    pasien["O"]["bb_kg"]         = upd(o.get("bb_kg",""), bb)
    pasien["O"]["tb_cm"]         = upd(o.get("tb_cm",""), tb)
    pasien["O"]["lila_cm"]       = upd(o.get("lila_cm",""), lila)
    pasien["O"]["catatan"]       = upd(o.get("catatan",""), cat_o)

    #A : ASSESSMENT
    a = pasien.get("A", {})
    print("\n── A : ASSESSMENT ───────────────────────────")
    diagnosa = input(f"Diagnosa  [{a.get('diagnosa','')}] : ").strip()
    pasien["A"]["diagnosa"] = upd(a.get("diagnosa",""), diagnosa)

    #P : PLANNING
    p = pasien.get("P", {})
    print("\n── P : PLANNING ─────────────────────────────")
    tindakan = input(f"Tindakan/anjuran  [{p.get('tindakan','')}] : ").strip()
    resep    = input(f"Resep obat        [{p.get('resep','')}] : ").strip()
    kontrol  = input(f"Jadwal kontrol    [{p.get('jadwal_kontrol','')}] : ").strip()
    pasien["P"]["tindakan"]       = upd(p.get("tindakan",""), tindakan)
    pasien["P"]["resep"]          = upd(p.get("resep",""), resep)
    pasien["P"]["jadwal_kontrol"] = upd(p.get("jadwal_kontrol",""), kontrol)

    simpan_file(data, FILE_PASIEN)
    print(f"\n[✓] Data pasien ID '{id_pasien}' berhasil diperbarui.")
    return pasien


#Test langsung 
if __name__ == "__main__":
    EditDataPasien()