"""
========================
grafik_kunjungan_line.py
========================
File entry-point untuk grafik Tren Kunjungan Pasien per Bulan (Line Chart).

Grafik yang ditampilkan:
    Line Chart – 2 garis berdampingan:
    • Total Kunjungan  (ungu, garis solid)
    • Pasien Baru      (ungu muda, garis putus-putus)

Ditampilkan di: Dashboard
"""

from TampilGrafik import visgrafikKunjunganDashboard

if __name__ == "__main__":
    print("[grafik_kunjungan_line] Menampilkan Line Chart Tren Kunjungan Bulanan...")
    visgrafikKunjunganDashboard()
    print("[grafik_kunjungan_line] Selesai.")
