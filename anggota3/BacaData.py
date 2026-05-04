"""
BacaData.py
===========
Modul pusat pembacaan data MedWatch.
Semua data yang dibutuhkan grafik dibaca dari sini.

Dibaca oleh : TampilGrafik.py, PerbandinganObat.py
Sumber data : data/medicalrecords.json, data/drugs.json
<<<<<<< HEAD
              (jika file tidak ada → pakai data dummy otomatis)
=======
                (jika file tidak ada → pakai data dummy otomatis)
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
"""

import json
import os
from collections import defaultdict, Counter

<<<<<<< HEAD
# ─────────────────────────────────────────────
# PATH FILE JSON
# ─────────────────────────────────────────────
=======
# =============================================
# PATH FILE JSON
# =============================================
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RM_JSON  = os.path.join(BASE_DIR, "data", "medicalrecords.json")
DRG_JSON = os.path.join(BASE_DIR, "data", "drugs.json")


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _kategori_umur(umur: int) -> str:
    if umur <= 18:
        return "anak"
    elif umur <= 59:
        return "dewasa"
    else:
        return "lansia"


<<<<<<< HEAD
# ══════════════════════════════════════════════════════
# 1. DATA DISTRIBUSI KELUHAN
#    → dipakai grafik Pie Chart & Horizontal Bar
# ══════════════════════════════════════════════════════
=======
# ======================================================
# 1. DATA DISTRIBUSI KELUHAN
#    → dipakai grafik Pie Chart & Horizontal Bar
# ======================================================
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
def get_data_distribusi_keluhan() -> dict:
    """
    Menghitung distribusi keluhan pasien dipecah per rentang umur.

    Return:
        {
<<<<<<< HEAD
          "keluhan" : ["Demam", "Batuk & Pilek", ...],
          "total"   : [87, 74, ...],
          "anak"    : [35, 30, ...],   # 0-18 th
          "dewasa"  : [32, 28, ...],   # 19-59 th
          "lansia"  : [20, 16, ...],   # >60 th
=======
            "keluhan" : ["Demam", "Batuk & Pilek", ...],
            "total"   : [87, 74, ...],
            "anak"    : [35, 30, ...],   # 0-18 th
            "dewasa"  : [32, 28, ...],   # 19-59 th
            "lansia"  : [20, 16, ...],   # >60 th
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
        }
    """
    records = _load_json(RM_JSON)

    if records:
        bucket: dict[str, dict] = defaultdict(
            lambda: {"anak": 0, "dewasa": 0, "lansia": 0}
        )
        for r in records:
            keluhan = r.get("keluhan_utama", "Lainnya")
            umur    = int(r.get("umur_pasien", 30))
            kat     = _kategori_umur(umur)
            bucket[keluhan][kat] += 1

        items = sorted(
            bucket.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True,
        )
        return {
            "keluhan": [i[0]                  for i in items],
            "anak"   : [i[1]["anak"]          for i in items],
            "dewasa" : [i[1]["dewasa"]         for i in items],
            "lansia" : [i[1]["lansia"]         for i in items],
            "total"  : [sum(i[1].values())    for i in items],
        }

    # ── DATA DUMMY ──
    keluhan = ["Demam", "Batuk & Pilek", "Hipertensi", "Diare",
               "Nyeri Kepala", "Gatal / Alergi", "Sesak Napas", "Lainnya"]
    anak    = [35, 30,  2, 20,  8, 12, 5, 6]
    dewasa  = [32, 28, 25, 18, 20, 10, 9, 5]
    lansia  = [20, 16, 34,  7, 10,  5, 5, 3]
    total   = [a + d + l for a, d, l in zip(anak, dewasa, lansia)]

    return {"keluhan": keluhan, "total": total,
            "anak": anak, "dewasa": dewasa, "lansia": lansia}


<<<<<<< HEAD
# ══════════════════════════════════════════════════════
# 2. DATA PERBANDINGAN EFEK SAMPING OBAT
#    → dipakai grafik Heatmap (via PerbandinganObat.py)
# ══════════════════════════════════════════════════════
=======
# ======================================================
# 2. DATA PERBANDINGAN EFEK SAMPING OBAT
#    → dipakai grafik Heatmap (via PerbandinganObat.py)
# ======================================================
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
def get_data_perbandingan_obat() -> dict:
    """
    Membaca data efek samping per obat dari drugs.json.

    Return:
        {
<<<<<<< HEAD
          "obat"   : ["Aspirin", "Paracetamol", ...],
          "efek"   : ["Mual", "Pusing", ...],
          "matriks": [[55, 30, ...], [20, 15, ...], ...]
                      baris = obat, kolom = efek, nilai = frekuensi %
=======
            "obat"   : ["Aspirin", "Paracetamol", ...],
            "efek"   : ["Mual", "Pusing", ...],
            "matriks": [[55, 30, ...], [20, 15, ...], ...]
                        baris = obat, kolom = efek, nilai = frekuensi %
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
        }
    """
    drugs = _load_json(DRG_JSON)

    if drugs and isinstance(drugs, list) and "efek_samping" in (drugs[0] if drugs else {}):
        semua_efek = set()
        for d in drugs:
            semua_efek.update(d.get("efek_samping", {}).keys())
        semua_efek = sorted(semua_efek)

        obat_list = [d["nama_obat"] for d in drugs]
        matriks   = []
        for d in drugs:
            es  = d.get("efek_samping", {})
            baris = [es.get(efek, 0) for efek in semua_efek]
            matriks.append(baris)

        return {"obat": obat_list, "efek": semua_efek, "matriks": matriks}

    # ── DATA DUMMY ──
    obat = [
        "Aspirin", "Paracetamol", "Ibuprofen", "Amoxicillin",
        "Ciprofloxacin", "Metformin", "Omeprazole", "Captopril",
        "Diclofenac", "Cetirizine", "Dexamethasone", "Ranitidine",
    ]
    efek = [
        "Mual", "Pusing", "Diare", "Ruam Kulit", "Sakit Kepala",
        "Nyeri Lambung", "Kantuk", "Insomnia", "Batuk Kering",
        "Kelelahan", "Mulut Kering", "Tremor",
    ]
    matriks = [
        [55, 30, 20, 15, 70, 60, 10, 10,  5, 25,  5,  5],  # Aspirin
        [20, 15, 10,  5, 20, 15,  5,  5,  5, 20,  5,  0],  # Paracetamol
        [50, 20, 25, 15, 65, 70, 10, 10,  5, 20,  5,  0],  # Ibuprofen
        [35, 15, 40, 45, 20, 20, 10,  5,  5, 20,  5,  0],  # Amoxicillin
        [40, 30, 45, 30, 25, 30, 15, 20, 10, 25, 10,  5],  # Ciprofloxacin
        [60, 25, 50, 10, 15, 20, 10, 10,  5, 30, 10,  5],  # Metformin
        [25, 15, 20, 10, 15, 55, 10, 10,  5, 15, 10,  0],  # Omeprazole
        [15, 20, 15, 10, 20, 10,  5,  5, 75, 20,  5,  0],  # Captopril
        [40, 20, 20, 20, 60, 65, 10, 10,  5, 20,  5,  0],  # Diclofenac
        [20, 25, 15, 25, 70, 10, 55, 15,  5, 25, 40,  5],  # Cetirizine
        [30, 20, 20, 20, 20, 25, 45, 25,  5, 35, 10,  0],  # Dexamethasone
        [20, 15, 15, 10, 15, 25, 15, 10,  5, 15, 10,  0],  # Ranitidine
    ]

    return {"obat": obat, "efek": efek, "matriks": matriks}


<<<<<<< HEAD
# ══════════════════════════════════════════════════════
# 3. DATA TOP 10 EFEK SAMPING
#    → dipakai grafik Bar Chart Top 10
# ══════════════════════════════════════════════════════
=======
# ======================================================
# 3. DATA TOP 10 EFEK SAMPING
#    → dipakai grafik Bar Chart Top 10
# ======================================================
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
def get_data_top10_efek_samping() -> dict:
    """
    Menghitung 10 efek samping obat yang paling banyak dilaporkan.

    Return:
        {
          "efek_samping": ["Mual", "Pusing", ...],
          "jumlah"      : [58, 47, ...],
        }
    """
    records = _load_json(RM_JSON)

    if records:
        semua_efek = []
        for r in records:
            efek = r.get("efek_samping", [])
            if isinstance(efek, list):
                semua_efek.extend(efek)
            elif isinstance(efek, str) and efek:
                semua_efek.append(efek)

        if semua_efek:
            top10 = Counter(semua_efek).most_common(10)
            return {
                "efek_samping": [x[0] for x in top10],
                "jumlah"      : [x[1] for x in top10],
            }

    # ── DATA DUMMY ──
    return {
        "efek_samping": [
            "Mual", "Pusing", "Sakit Kepala", "Diare",
            "Ruam Kulit", "Insomnia", "Kelelahan",
            "Nyeri Perut", "Muntah", "Mulut Kering",
        ],
        "jumlah": [58, 47, 43, 39, 34, 28, 25, 22, 18, 15],
    }
<<<<<<< HEAD
=======


# ======================================================
# 4. DATA TREN KUNJUNGAN PASIEN
# Menggunakan Line Chart dan Bar Chart
# ======================================================
def get_data_kunjungan_bulanan() -> dict;
    """
    Menghitung tren kunjungan pasien perbulan dalam 1 tahun terakhir

    Data yang digunakan : 
        - total_kunjungan   : semua pasien kunjungan perbulan 
        - pasien_baru       : pasien yang pertama kali datang dalam 1 bulan
        - laki_laki         : banyak pasien laki-laki dalam 1 bulan 
        - perempuan         : banyak pasien perempuan dalam 1 bulan

    """
    records = _load_json(RM_JSON)

    NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                   "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    
    if record:
        total       = [0] * 12
        baru        = [0] * 12
        laki        = [0] * 12
        perempuan   = [0] * 12
        id_pertama_kali = set()

        for r in records: 
            tanggal = r.get("tanggal_kunjungan", "")
            try: 
                bulan_idx = int(tanggal.split("-")[1]) - 1
            except (IndexError, ValueError):
                continue
            if not (0 <= bulan_idx <= 11):
                continue

            id_pasien       = r.get("id_pasien", "")
            kunjungan_ke    = int(r.get("kunjungan_ke", 1))
            jk           = r.get("jenis_kelamin", "").upper()

            total[bulan_idx] += 1

            if kunjungan_ke == 1 or id_pasien not in id_pertama_kali:
                if id_pasien not in id_pertama_kali:
                    baru[bulan_idx] += 1
                    id_pertama_kali.add(id_pasien)

            if jk == "L":
                laki[bulan_idx] += 1
            elif jk == "P":
                perempuan[bulan_idx] += 1

        return {
            "bulan"          : NAMA_BULAN,
            "total_kunjungan": total,
            "pasien_baru"    : baru,
            "laki_laki"      : laki,
            "perempuan"      : perempuan,
        }

    # -- DATA DUMMY --
    return {
        "bulan"          : NAMA_BULAN,
        "total_kunjungan": [45, 52, 60, 55, 70, 65, 80, 75, 68, 72, 85, 90],
        "pasien_baru"    : [20, 18, 25, 22, 30, 27, 35, 28, 24, 26, 32, 38],
        "laki_laki"      : [22, 25, 28, 26, 33, 30, 38, 36, 31, 34, 40, 42],
        "perempuan"      : [23, 27, 32, 29, 37, 35, 42, 39, 37, 38, 45, 48],
    }
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
