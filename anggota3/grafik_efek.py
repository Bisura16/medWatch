"""
grafik_efek.py
==============
File entry-point untuk grafik Perbandingan Efek Samping Obat.

Grafik yang ditampilkan:
  Heatmap – baris = obat, kolom = efek samping,
             warna = intensitas frekuensi (0% → 100%)

Semua logika ada di TampilGrafik.py, PerbandinganObat.py, dan BacaData.py.
"""

from TampilGrafik import visgrafikEfek

if __name__ == "__main__":
    print("[grafik_efek] Menampilkan Heatmap Perbandingan Efek Samping Obat...")
    visgrafikEfek()
    print("[grafik_efek] Selesai.")
