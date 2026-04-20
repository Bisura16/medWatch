"""
safety_checker.py
=================
Fitur 2 anggota 4:
Melakukan cross-reference obat terhadap database efek samping,
merangkum tingkat keparahan, dan mendeteksi efek yang tumpang tindih.
"""

from collections import Counter, defaultdict
from typing import Dict, List

from data_loader import ambil_obat_terbaik, buat_index_efek_samping, normalisasi_teks

BOBOT_KEPARAHAN = {"ringan": 1, "sedang": 2, "serius": 4}
URUTAN_KEPARAHAN = {"serius": 0, "sedang": 1, "ringan": 2}


def _hitung_skor_risiko(efek_dikenali: List[Dict]) -> float:
    """
    Konversi daftar efek samping menjadi skor 0-100.
    Rumus dibuat sederhana agar mudah dijelaskan dan cukup informatif.
    """
    if not efek_dikenali:
        return 0.0

    total_bobot = sum(
        BOBOT_KEPARAHAN.get(item["tingkat_keparahan"], 0)
        for item in efek_dikenali
    )
    skor_maksimum = len(efek_dikenali) * max(BOBOT_KEPARAHAN.values())
    return round((total_bobot / skor_maksimum) * 100, 1)


def _label_risiko(skor_risiko: float) -> str:
    """Ubah angka skor menjadi label risiko yang lebih mudah dibaca."""
    if skor_risiko >= 70:
        return "tinggi"
    if skor_risiko >= 40:
        return "sedang"
    return "rendah"


def cross_reference_efek_obat(obat: Dict) -> Dict:
    """
    Cocokkan daftar efek samping suatu obat dengan master database efek samping.
    Return berisi efek dikenali, efek belum terpetakan, dan ringkasan risikonya.
    """
    index_efek = buat_index_efek_samping()
    efek_dikenali = []
    efek_tidak_dikenali = []

    for nama_efek in obat.get("efek_samping", []):
        data_efek = index_efek.get(normalisasi_teks(nama_efek))

        if data_efek:
            efek_dikenali.append(
                {
                    "nama_efek": data_efek["nama_efek"],
                    "kategori": data_efek["kategori"],
                    "tingkat_keparahan": data_efek["tingkat_keparahan"],
                    "rekomendasi": data_efek["rekomendasi"],
                }
            )
        else:
            efek_tidak_dikenali.append(nama_efek)

    efek_dikenali.sort(
        key=lambda item: (
            URUTAN_KEPARAHAN.get(item["tingkat_keparahan"], 99),
            item["nama_efek"],
        )
    )

    ringkasan = Counter(item["tingkat_keparahan"] for item in efek_dikenali)
    skor_risiko = _hitung_skor_risiko(efek_dikenali)

    return {
        "obat": obat,
        "efek_dikenali": efek_dikenali,
        "efek_tidak_dikenali": efek_tidak_dikenali,
        "ringkasan_keparahan": {
            "serius": ringkasan.get("serius", 0),
            "sedang": ringkasan.get("sedang", 0),
            "ringan": ringkasan.get("ringan", 0),
        },
        "skor_risiko": skor_risiko,
        "label_risiko": _label_risiko(skor_risiko),
    }


def _susun_efek_tumpang_tindih(hasil_obat: List[Dict]) -> List[Dict]:
    """
    Cari efek samping yang muncul pada dua obat atau lebih.
    Ini berguna untuk menyoroti potensi keluhan yang bisa terasa lebih dominan.
    """
    peta_efek: Dict[str, List[Dict]] = defaultdict(list)

    for hasil in hasil_obat:
        nama_obat = hasil["obat"]["nama_obat"]
        for efek in hasil["efek_dikenali"]:
            key = normalisasi_teks(efek["nama_efek"])
            peta_efek[key].append(
                {
                    "nama_obat": nama_obat,
                    "nama_efek": efek["nama_efek"],
                    "tingkat_keparahan": efek["tingkat_keparahan"],
                }
            )

    efek_tumpang_tindih = []
    for daftar in peta_efek.values():
        obat_terkait = sorted({item["nama_obat"] for item in daftar})
        if len(obat_terkait) < 2:
            continue

        tingkat_tertinggi = min(
            (item["tingkat_keparahan"] for item in daftar),
            key=lambda nilai: URUTAN_KEPARAHAN.get(nilai, 99),
        )

        efek_tumpang_tindih.append(
            {
                "nama_efek": daftar[0]["nama_efek"],
                "obat_terkait": obat_terkait,
                "tingkat_tertinggi": tingkat_tertinggi,
            }
        )

    efek_tumpang_tindih.sort(
        key=lambda item: (
            URUTAN_KEPARAHAN.get(item["tingkat_tertinggi"], 99),
            item["nama_efek"],
        )
    )
    return efek_tumpang_tindih


def _bangun_peringatan_prioritas(
    hasil_obat: List[Dict], efek_tumpang_tindih: List[Dict]
) -> List[str]:
    """Kumpulkan pesan prioritas dari efek serius dan efek yang saling overlap."""
    peringatan = []

    for hasil in hasil_obat:
        efek_serius = [
            item["nama_efek"]
            for item in hasil["efek_dikenali"]
            if item["tingkat_keparahan"] == "serius"
        ]
        if efek_serius:
            peringatan.append(
                f"{hasil['obat']['nama_obat']}: waspadai efek serius "
                f"{', '.join(efek_serius)}."
            )

    for efek in efek_tumpang_tindih:
        if efek["tingkat_tertinggi"] in {"sedang", "serius"}:
            peringatan.append(
                f"Efek '{efek['nama_efek']}' muncul pada "
                f"{', '.join(efek['obat_terkait'])}; keluhan pasien bisa lebih menonjol."
            )

    return peringatan


def cek_keamanan_obat(daftar_nama_obat: List[str]) -> Dict:
    """
    Analisis satu atau beberapa obat.
    Input boleh berupa nama dagang, nama generik, atau alias yang ada di database.
    """
    hasil_obat = []
    obat_tidak_ditemukan = []
    obat_sudah_diproses = set()

    for nama_input in daftar_nama_obat:
        nama_input = nama_input.strip()
        if not nama_input:
            continue

        obat = ambil_obat_terbaik(nama_input)
        if not obat:
            obat_tidak_ditemukan.append(nama_input)
            continue

        nama_resmi = obat["nama_obat"]
        if nama_resmi in obat_sudah_diproses:
            continue

        obat_sudah_diproses.add(nama_resmi)
        hasil_obat.append(cross_reference_efek_obat(obat))

    efek_tumpang_tindih = _susun_efek_tumpang_tindih(hasil_obat)
    peringatan_prioritas = _bangun_peringatan_prioritas(
        hasil_obat, efek_tumpang_tindih
    )

    return {
        "jumlah_obat_dicek": len(hasil_obat),
        "hasil_obat": hasil_obat,
        "obat_tidak_ditemukan": obat_tidak_ditemukan,
        "efek_tumpang_tindih": efek_tumpang_tindih,
        "peringatan_prioritas": peringatan_prioritas,
    }


def format_laporan_safety_checker(payload: Dict) -> str:
    """Ubah hasil safety checker menjadi teks yang siap ditampilkan."""
    lines = ["=== SAFETY CHECKER OBAT ==="]
    lines.append(f"Jumlah obat dicek     : {payload.get('jumlah_obat_dicek', 0)}")

    obat_tidak_ditemukan = payload.get("obat_tidak_ditemukan", [])
    if obat_tidak_ditemukan:
        lines.append(
            f"Obat tidak ditemukan  : {', '.join(obat_tidak_ditemukan)}"
        )

    hasil_obat = payload.get("hasil_obat", [])
    if not hasil_obat:
        lines.append("Tidak ada obat yang berhasil dianalisis.")
        return "\n".join(lines)

    lines.append("-" * 55)
    lines.append("Ringkasan per obat:")
    for hasil in hasil_obat:
        obat = hasil["obat"]
        ringkasan = hasil["ringkasan_keparahan"]
        lines.append(
            f"- {obat['nama_obat']}: skor {hasil['skor_risiko']}/100 ({hasil['label_risiko']}), "
            f"serius={ringkasan['serius']}, sedang={ringkasan['sedang']}, ringan={ringkasan['ringan']}"
        )

    lines.append("-" * 55)
    lines.append("Efek tumpang tindih:")
    efek_tumpang_tindih = payload.get("efek_tumpang_tindih", [])
    if efek_tumpang_tindih:
        for efek in efek_tumpang_tindih:
            lines.append(
                f"- {efek['nama_efek']} [{efek['tingkat_tertinggi']}] pada "
                f"{', '.join(efek['obat_terkait'])}"
            )
    else:
        lines.append("- Tidak ada efek samping yang overlap antar obat.")

    lines.append("-" * 55)
    lines.append("Peringatan prioritas:")
    peringatan = payload.get("peringatan_prioritas", [])
    if peringatan:
        for item in peringatan:
            lines.append(f"- {item}")
    else:
        lines.append("- Tidak ada peringatan prioritas tambahan.")

    return "\n".join(lines)
