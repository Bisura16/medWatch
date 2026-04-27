"""
=======================
grafik_kunjungan_bar.py
=======================
File entry-point untuk grafik Tren Kunjungan Pasien per Bulan (Bar Chart Gender).

Grafik yang ditampilkan:
    Grouped Bar Chart – setiap bulan punya 2 bar berdampingan:
    • Laki-Laki  (Biru  #3B82F6)
    • Perempuan  (Pink  #EC4899)
    + Garis tipis total per bulan sebagai referensi.

Ditampilkan di: Bagian Visualisasi

Semua logika ada di TampilGrafik.py dan BacaData.py.
"""

from TampilGrafik import visgrafikKunjunganGender

if __name__ == "__main__":
    print("[grafik_kunjungan_bar] Menampilkan Bar Chart Kunjungan per Gender...")
    visgrafikKunjunganGender()
    print("[grafik_kunjungan_bar] Selesai.")
