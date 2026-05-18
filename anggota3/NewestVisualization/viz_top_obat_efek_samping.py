"""viz_top_obat_efek_samping.py
==============================
Top 15 obat dengan beban efek samping terbesar berdasarkan jumlah total
laporan FAERS (Adverse Event Reports) openFDA, diparse dari field
`warnings` rekord scraping (`anggota1/data/drug_safety_data.json`).

Mengapa dipilih total laporan FAERS, bukan jumlah jenis efek samping?
openFDA mengembalikan maksimum `count=25` jenis efek samping per obat
sehingga setiap obat punya nilai 25 (flat). Total laporan FAERS lebih
menggambarkan beban keamanan obat di dunia nyata.

Grafik horizontal bar; warna setiap batang ditentukan oleh field
`severity_level` (ringan / sedang / serius). Label angka di sisi kanan
batang menampilkan total laporan dengan separator ribuan.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FAERS openFDA oleh anggota1 (Ghaisan, T1-DATA).
"""
from __future__ import annotations

import os
import re
import sys

# Saat dijalankan langsung (`python anggota3/.../viz_xxx.py`) butuh
# memasukkan akar repo ke sys.path agar import paket berhasil.
if __package__ in (None, ""):
    _akar = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _akar not in sys.path:
        sys.path.insert(0, _akar)

import matplotlib

# Hindari ketergantungan ke server GUI pada lingkungan headless.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from anggota3.NewestVisualization import palette
from anggota3.NewestVisualization.data_loader import (
    load_drug_safety,
    path_output,
)


TOP_N = 15

# Regex hasil parsing field warnings:
#   "Berdasarkan 111361 laporan FAERS untuk paracetamol, fraksi laporan
#    serius 96%, fraksi laporan kematian 14.1%."
RE_TOTAL = re.compile(r"(\d[\d,]*)\s+laporan FAERS", re.IGNORECASE)


def _ekstrak_total(warnings: str | None) -> int | None:
    if not warnings:
        return None
    m = RE_TOTAL.search(warnings)
    if not m:
        return None
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _siapkan_data(rekord: list[dict]):
    """Urutkan rekord menurut total laporan FAERS dan ambil Top N.

    Returns:
        Tuple (nama_obat, total_laporan, severity, jumlah_efek_unik) -
        list ascending agar barh tampil terbesar di puncak.
    """
    diperkaya = []
    for r in rekord:
        nama = r.get("drug_name")
        side = r.get("side_effects") or []
        if not nama or not isinstance(side, list):
            continue
        total = _ekstrak_total(r.get("warnings"))
        if total is None:
            continue
        sev = (r.get("severity_level") or "tidak diketahui").lower()
        diperkaya.append({
            "nama": nama,
            "total": total,
            "severity": sev,
            "jumlah_efek": len(side),
        })
    diperkaya.sort(key=lambda r: r["total"], reverse=True)
    diperkaya = diperkaya[:TOP_N]
    diperkaya.sort(key=lambda r: r["total"])  # ascending untuk barh
    return (
        [r["nama"] for r in diperkaya],
        [r["total"] for r in diperkaya],
        [r["severity"] for r in diperkaya],
        [r["jumlah_efek"] for r in diperkaya],
    )


def _format_ribuan(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def buat_grafik(output_path: str) -> str | None:
    """Render the top-15 drugs by FAERS report volume.

    Args:
        output_path: Absolute path for the resulting PNG.

    Returns:
        ``output_path`` on success, ``None`` when no record carries
        a valid FAERS total in its ``warnings`` field.
    """
    rekord = load_drug_safety()
    if not rekord:
        print("[skip] drug_safety_data.json kosong; chart tidak dibuat.")
        return None

    nama_obat, total_laporan, severity, jumlah_efek = _siapkan_data(rekord)
    if not nama_obat:
        print("[skip] tidak ada rekord valid untuk Top 15 obat.")
        return None

    warna = [
        palette.WARNA_KEPARAHAN.get(s, palette.WARNA_TIDAK_DIKETAHUI)
        for s in severity
    ]

    fig, ax = plt.subplots(figsize=(8.4, 7.5))
    fig.patch.set_facecolor(palette.LATAR_FIGUR)

    y = np.arange(len(nama_obat))
    bars = ax.barh(
        y,
        total_laporan,
        color=warna,
        edgecolor="white",
        linewidth=0.8,
        height=0.7,
    )

    max_val = max(total_laporan)
    offset = max_val * 0.012
    for bar, total, jefek in zip(bars, total_laporan, jumlah_efek):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{_format_ribuan(total)}  ({jefek} efek)",
            va="center",
            ha="left",
            fontsize=8.5,
            color=palette.WARNA_LABEL_SEDANG,
            fontweight="bold",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(nama_obat, fontsize=9.5)
    ax.set_xlim(0, max_val * 1.32)
    ax.set_xlabel(
        "Jumlah total laporan FAERS (skala lebih besar = beban lebih tinggi)",
        fontsize=10,
        color=palette.WARNA_TICK,
    )
    ax.set_ylabel("Nama obat", fontsize=10, color=palette.WARNA_TICK)
    ax.set_title(
        f"Top {TOP_N} Obat dengan Beban Laporan Efek Samping Terbesar",
        fontsize=13,
        fontweight="bold",
        pad=14,
        color=palette.WARNA_LABEL_GELAP,
    )
    ax.set_facecolor(palette.LATAR_AXES)
    ax.grid(axis="x", color=palette.WARNA_GRID, linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=palette.WARNA_TICK)
    for spine in ax.spines.values():
        spine.set_edgecolor(palette.WARNA_SPINE)

    # Format sumbu X dengan separator ribuan
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda v, _pos: _format_ribuan(int(v)))
    )

    # Legend keparahan
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(color=palette.WARNA_RINGAN, label="Ringan"),
        Patch(color=palette.WARNA_SEDANG, label="Sedang"),
        Patch(color=palette.WARNA_SERIUS, label="Serius"),
    ]
    ax.legend(
        handles=legend_handles,
        title="Tingkat keparahan",
        fontsize=9,
        title_fontsize=9.5,
        framealpha=0.9,
        loc="lower right",
    )

    fig.text(
        0.01,
        -0.02,
        "Sumber: FAERS openFDA via anggota1 (T1-DATA). "
        "Panjang batang = total laporan FAERS untuk obat tersebut "
        "(diparse dari field warnings); angka dalam tanda kurung adalah "
        "jumlah jenis efek samping unik yang ditarik (maks 25). "
        "Warna mencerminkan severity_level (ringan / sedang / serius).",
        fontsize=8,
        color=palette.WARNA_LABEL_SEDANG,
        wrap=True,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    target = path_output("viz_top_obat_efek_samping.png")
    hasil = buat_grafik(target)
    if hasil:
        print(f"[ok] {hasil}")
    else:
        print("[gagal] tidak ada data untuk Top 15 obat")
