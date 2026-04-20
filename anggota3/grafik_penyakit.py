"""
grafik_penyakit.py
==================
File entry-point untuk grafik Distribusi Keluhan / Penyakit.

Grafik yang ditampilkan:
  A. Pie Chart      – proporsi keluhan keseluruhan
  B. Horizontal Bar – distribusi per rentang umur
                      (Anak-Anak | Dewasa | Lansia)

Semua logika ada di TampilGrafik.py dan BacaData.py.
"""

from TampilGrafik import visgrafikkeluhan

if __name__ == "__main__":
    print("[grafik_penyakit] Menampilkan Pie Chart distribusi keluhan...")
    print("[grafik_penyakit] Menampilkan Horizontal Bar per rentang umur...")
    visgrafikkeluhan()
    print("[grafik_penyakit] Selesai.")
