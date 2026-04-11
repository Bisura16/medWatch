"""
grafik_top_efek.py
==================
File entry-point untuk grafik Top 10 Efek Samping Obat.

Grafik yang ditampilkan:
  Bar Chart vertikal – 10 efek samping paling sering dilaporkan,
  gradasi warna ungu, disertai garis rata-rata.

Semua logika ada di TampilGrafik.py dan BacaData.py.
"""

from TampilGrafik import Vgrafik10topEfek

if __name__ == "__main__":
    print("[grafik_top_efek] Menampilkan Top 10 Efek Samping Obat...")
    Vgrafik10topEfek()
    print("[grafik_top_efek] Selesai.")
