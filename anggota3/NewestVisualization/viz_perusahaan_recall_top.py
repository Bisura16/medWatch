"""viz_perusahaan_recall_top.py
================================
Top 20 perusahaan farmasi dengan jumlah recall obat terbanyak menurut
data FDA Enforcement (`anggota1/data/drug_recalls.json`).

Grafik horizontal bar. Warna batang memakai gradient ungu MedWatch
(`PALET_UNGU_SEKUENSIAL`) dengan intensitas mengikuti jumlah recall:
semakin gelap = semakin banyak recall.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FDA Enforcement openFDA oleh anggota1 (T1-DATA).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

if __package__ in (None, ""):
    _akar = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _akar not in sys.path:
        sys.path.insert(0, _akar)

import matplotlib

matplotlib.use("Agg")

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable

from anggota3.NewestVisualization import palette
from anggota3.NewestVisualization.data_loader import (
    load_drug_recalls,
    path_output,
)


TOP_N = 20
MAX_NAMA = 42  # batas karakter agar label tidak menutup grafik


def _potong_nama(nama: str) -> str:
    if len(nama) <= MAX_NAMA:
        return nama
    return nama[: MAX_NAMA - 1].rstrip() + "..."


def _agregasi(rekord: list[dict]) -> tuple[list[str], list[int]]:
    counter: Counter[str] = Counter()
    for r in rekord:
        perusahaan = r.get("company")
        if isinstance(perusahaan, str) and perusahaan.strip():
            counter[perusahaan.strip()] += 1
    teratas = counter.most_common(TOP_N)
    if not teratas:
        return [], []
    # Urutan ascending untuk barh agar terbesar di puncak.
    teratas.reverse()
    nama = [_potong_nama(n) for n, _ in teratas]
    jumlah = [j for _, j in teratas]
    return nama, jumlah


def buat_grafik(output_path: str) -> str | None:
    rekord = load_drug_recalls()
    if not rekord:
        print("[skip] drug_recalls.json kosong; chart tidak dibuat.")
        return None

    nama, jumlah = _agregasi(rekord)
    if not nama:
        print("[skip] tidak ada perusahaan valid untuk Top 20 recall.")
        return None

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "medwatch_ungu",
        palette.PALET_UNGU_SEKUENSIAL,
        N=256,
    )
    max_val = max(jumlah)
    norm = mcolors.Normalize(vmin=0, vmax=max_val)
    warna_batang = [cmap(norm(v)) for v in jumlah]

    fig, ax = plt.subplots(figsize=(8.0, 8.5))
    fig.patch.set_facecolor(palette.LATAR_FIGUR)

    y = np.arange(len(nama))
    bars = ax.barh(
        y,
        jumlah,
        color=warna_batang,
        edgecolor="white",
        linewidth=0.7,
        height=0.72,
    )

    offset = max_val * 0.012
    for bar, val in zip(bars, jumlah):
        ax.text(
            bar.get_width() + offset,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center",
            ha="left",
            fontsize=9,
            color=palette.WARNA_LABEL_SEDANG,
            fontweight="bold",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(nama, fontsize=8.5)
    ax.set_xlim(0, max_val * 1.16)
    ax.set_xlabel(
        "Jumlah recall (rekord)",
        fontsize=10,
        color=palette.WARNA_TICK,
    )
    ax.set_ylabel(
        "Perusahaan farmasi", fontsize=10, color=palette.WARNA_TICK
    )
    ax.set_title(
        f"Top {TOP_N} Perusahaan dengan Recall Obat Terbanyak (FDA)",
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

    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.035, pad=0.04)
    cbar.set_label(
        "Intensitas warna = jumlah recall",
        fontsize=8.5,
        color=palette.WARNA_LABEL_SEDANG,
        labelpad=8,
        fontweight="bold",
    )
    cbar.ax.tick_params(labelsize=8, colors=palette.WARNA_TICK)

    fig.text(
        0.01,
        -0.02,
        "Sumber: FDA Enforcement via openFDA (anggota1 T1-DATA). "
        "Nama perusahaan dipotong pada 42 karakter; gradien ungu mengikuti "
        "frekuensi recall (terang = sedikit, gelap = banyak).",
        fontsize=8,
        color=palette.WARNA_LABEL_SEDANG,
        wrap=True,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    target = path_output("viz_perusahaan_recall_top.png")
    hasil = buat_grafik(target)
    if hasil:
        print(f"[ok] {hasil}")
    else:
        print("[gagal] tidak ada data untuk Top 20 perusahaan")
