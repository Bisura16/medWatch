"""generate_all.py
==================
Jalankan kelima skrip visualisasi NewestVisualization secara berurutan
dan cetak path PNG hasilnya beserta ukuran berkas.

Eksekusi (dari akar medWatch):
    .venv/bin/python -m anggota3.NewestVisualization.generate_all

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FAERS dan FDA Enforcement openFDA oleh anggota1.
"""
from __future__ import annotations

import os

from anggota3.NewestVisualization import (
    viz_distribusi_keparahan,
    viz_heatmap_obat_efek,
    viz_perusahaan_recall_top,
    viz_recall_class_per_tahun,
    viz_top_obat_efek_samping,
)
from anggota3.NewestVisualization.data_loader import path_output


URUTAN_VIZ = [
    ("Top obat dengan efek samping terbanyak", viz_top_obat_efek_samping, "viz_top_obat_efek_samping.png"),
    ("Distribusi keparahan per kategori obat", viz_distribusi_keparahan, "viz_distribusi_keparahan.png"),
    ("Recall per tahun per Class", viz_recall_class_per_tahun, "viz_recall_class_per_tahun.png"),
    ("Top perusahaan recall", viz_perusahaan_recall_top, "viz_perusahaan_recall_top.png"),
    ("Heatmap obat x kategori efek samping", viz_heatmap_obat_efek, "viz_heatmap_obat_efek.png"),
]


def _format_ukuran(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def main() -> int:
    print("[NewestVisualization] mulai generate seluruh PNG")
    sukses = 0
    gagal = 0
    for label, modul, nama_file in URUTAN_VIZ:
        target = path_output(nama_file)
        try:
            hasil = modul.buat_grafik(target)
        except Exception as exc:  # noqa: BLE001 - report all failures
            print(f"  [error] {label}: {exc!r}")
            gagal += 1
            continue
        if hasil and os.path.exists(hasil):
            ukuran = os.path.getsize(hasil)
            print(f"  [ok] {label}\n        -> {hasil} ({_format_ukuran(ukuran)})")
            sukses += 1
        else:
            print(f"  [skip] {label}: tidak ada output")
            gagal += 1
    print(f"[NewestVisualization] selesai. sukses={sukses}, gagal={gagal}")
    return 0 if gagal == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
