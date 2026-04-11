"""
PerbandinganObat.py
===================
Modul algoritma pemrosesan data perbandingan efek samping obat.

Dipanggil oleh : TampilGrafik.py
Membaca data dari : BacaData.get_data_perbandingan_obat()

Tugas modul ini:
  - Normalisasi matriks frekuensi → skala 0-100%
  - Menghitung skor risiko tiap obat
  - Mengurutkan obat berdasarkan skor risiko
  - Menyiapkan data final siap diplot heatmap
"""

import numpy as np
from BacaData import get_data_perbandingan_obat


def _normalisasi_matriks(matriks: list[list]) -> np.ndarray:
    """
    Normalisasi nilai tiap kolom ke skala 0-100
    relatif terhadap nilai maksimum kolom tersebut.

    Contoh: kolom Mual max=60 → nilai 30 jadi 50%
    """
    arr     = np.array(matriks, dtype=float)
    col_max = arr.max(axis=0)
    col_max[col_max == 0] = 1          # hindari pembagian nol
    return (arr / col_max) * 100


def hitung_skor_risiko(matriks_pct: np.ndarray) -> np.ndarray:
    """
    Hitung skor risiko tiap obat dari rata-rata baris matriks (%).
    Obat dengan skor lebih tinggi = profil efek samping lebih berat.

    Return: array 1D skor per obat
    """
    return matriks_pct.mean(axis=1)


def urutkan_obat_by_risiko(obat: list, matriks_pct: np.ndarray) -> tuple:
    """
    Urutkan obat dari skor risiko tertinggi ke terendah.

    Return: (obat_sorted, matriks_sorted)
    """
    skor = hitung_skor_risiko(matriks_pct)
    idx  = np.argsort(skor)[::-1]         # descending
    return [obat[i] for i in idx], matriks_pct[idx]


def siapkan_data_heatmap(urutkan: bool = True) -> dict:
    """
    Pipeline lengkap:
      1. Ambil data dari BacaData
      2. Normalisasi matriks
      3. Opsional urutkan obat berdasarkan skor risiko

    Dipanggil oleh TampilGrafik.tampil_heatmap_efek_samping()

    Return:
        {
          "obat"       : ["Aspirin", ...],
          "efek"       : ["Mual", ...],
          "matriks_pct": np.ndarray shape (n_obat, n_efek),
          "skor_risiko": np.ndarray shape (n_obat,),
        }
    """
    raw          = get_data_perbandingan_obat()
    obat         = raw["obat"]
    efek         = raw["efek"]
    matriks_pct  = _normalisasi_matriks(raw["matriks"])

    if urutkan:
        obat, matriks_pct = urutkan_obat_by_risiko(obat, matriks_pct)

    skor = hitung_skor_risiko(matriks_pct)

    return {
        "obat"       : obat,
        "efek"       : efek,
        "matriks_pct": matriks_pct,
        "skor_risiko": skor,
    }
