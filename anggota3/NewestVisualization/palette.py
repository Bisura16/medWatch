"""palette.py
============
Konstanta palet warna MedWatch yang dipakai ulang oleh seluruh visualisasi
di folder NewestVisualization. Nilai HEX direplikasi langsung dari berkas
`anggota3/TampilGrafik.py` milik Alia agar tampilan tetap selaras.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
"""

# ---------------------------------------------------------------------------
# Palet utama MedWatch (sama persis dengan TampilGrafik.py)
# ---------------------------------------------------------------------------
WARNA_ANAK = "#A78BFA"          # ungu muda, kelompok anak-anak
WARNA_DEWASA = "#7C3AED"        # ungu utama brand, kelompok dewasa
WARNA_LANSIA = "#1E1B4B"        # slate gelap, kelompok lansia
WARNA_LAKI = "#3B82F6"          # biru, jenis kelamin laki-laki
WARNA_PEREMPUAN = "#EC4899"     # pink, jenis kelamin perempuan

# Palet pie / kategori berurutan dari TampilGrafik.py
PALET_PIE = [
    "#7C3AED", "#A78BFA", "#C4B5FD", "#6D28D9",
    "#8B5CF6", "#DDD6FE", "#4C1D95", "#EDE9FE",
]

# Palet ungu sekuensial untuk gradient bar dan heatmap (ringan -> gelap)
PALET_UNGU_SEKUENSIAL = [
    "#EDE9FE", "#DDD6FE", "#C4B5FD", "#A78BFA",
    "#8B5CF6", "#7C3AED", "#6D28D9", "#4C1D95",
]

# ---------------------------------------------------------------------------
# Kode warna keparahan untuk efek samping dan klasifikasi recall
# (selaras dengan keputusan T1-HEATMAP, gaya risk-matrix MedWatch)
# ---------------------------------------------------------------------------
WARNA_RINGAN = "#A6D96A"        # hijau muda, severity ringan
WARNA_SEDANG = "#FDAE61"        # oranye, severity sedang
WARNA_SERIUS = "#D7191C"        # merah, severity serius
WARNA_TIDAK_DIKETAHUI = "#9CA3AF"  # abu, ketika severity_level tidak tersedia

WARNA_KEPARAHAN = {
    "ringan": WARNA_RINGAN,
    "sedang": WARNA_SEDANG,
    "serius": WARNA_SERIUS,
}

# Severity class FDA recall dipetakan ke palet risk-matrix
WARNA_RECALL_CLASS = {
    "Class I": "#D7191C",          # paling berbahaya
    "Class II": "#FDAE61",         # menengah
    "Class III": "#A6D96A",         # ringan
    "Not Yet Classified": "#9CA3AF",
}

# ---------------------------------------------------------------------------
# Warna pendukung (latar, garis, label) sesuai TampilGrafik.py
# ---------------------------------------------------------------------------
LATAR_FIGUR = "#FFFFFF"
LATAR_AXES = "#FAFAFA"
WARNA_GRID = "#E5E7EB"
WARNA_LABEL_GELAP = "#1C1C2E"
WARNA_LABEL_SEDANG = "#374151"
WARNA_LABEL_TERANG = "#9CA3AF"
WARNA_TICK = "#4B5563"
WARNA_SPINE = "#E5E7EB"
