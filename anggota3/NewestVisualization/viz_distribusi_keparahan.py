"""viz_distribusi_keparahan.py
=============================
Distribusi tingkat keparahan efek samping per kategori obat menurut data
scraping FAERS openFDA (`anggota1/data/drug_safety_data.json`).

Tampilan stacked horizontal bar:
  - Sumbu Y: kategori obat (Analgesik, Antibiotik, ...)
  - Sumbu X: jumlah obat di kategori tersebut
  - Segmen warna setiap batang dipecah menurut severity_level
    (ringan / sedang / serius) memakai palet risk-matrix MedWatch.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FAERS openFDA oleh anggota1 (Ghaisan, T1-DATA).
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

if __package__ in (None, ""):
    _akar = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _akar not in sys.path:
        sys.path.insert(0, _akar)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from anggota3.NewestVisualization import palette
from anggota3.NewestVisualization.data_loader import (
    load_drug_safety,
    path_output,
)


SEVERITY_ORDER = ["ringan", "sedang", "serius"]


def _agregasi(rekord: list[dict]) -> tuple[list[str], dict[str, np.ndarray]]:
    """Hitung jumlah obat per (kategori, severity).

    Returns:
        Tuple (kategori_terurut, matriks_per_severity) di mana
        matriks_per_severity[s] = array sejajar kategori_terurut.
    """
    tabel: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rekord:
        kategori = r.get("category") or "Tidak diketahui"
        severity = (r.get("severity_level") or "tidak diketahui").lower()
        if severity not in SEVERITY_ORDER:
            severity = "tidak diketahui"
        tabel[kategori][severity] += 1

    total_per_kategori = {k: sum(v.values()) for k, v in tabel.items()}
    kategori_terurut = sorted(
        total_per_kategori.keys(),
        key=lambda k: total_per_kategori[k],
    )

    matriks: dict[str, np.ndarray] = {}
    for sev in SEVERITY_ORDER:
        matriks[sev] = np.array(
            [tabel[k].get(sev, 0) for k in kategori_terurut],
            dtype=float,
        )
    # Tambah baris "tidak diketahui" hanya jika ada nilai > 0
    tidak_dikenal = np.array(
        [tabel[k].get("tidak diketahui", 0) for k in kategori_terurut],
        dtype=float,
    )
    if tidak_dikenal.sum() > 0:
        matriks["tidak diketahui"] = tidak_dikenal
    return kategori_terurut, matriks


def buat_grafik(output_path: str) -> str | None:
    """Render the stacked severity-by-category bar chart.

    Args:
        output_path: Absolute path for the resulting PNG.

    Returns:
        ``output_path`` on success, ``None`` when the source file is
        empty or has no valid category (the caller logs a skip).
    """
    rekord = load_drug_safety()
    if not rekord:
        print("[skip] drug_safety_data.json kosong; chart tidak dibuat.")
        return None

    kategori, matriks = _agregasi(rekord)
    if not kategori:
        print("[skip] tidak ada kategori valid pada drug_safety_data.json")
        return None

    fig, ax = plt.subplots(figsize=(8.0, 6.0))
    fig.patch.set_facecolor(palette.LATAR_FIGUR)

    y = np.arange(len(kategori))
    height = 0.65
    kiri = np.zeros(len(kategori))

    warna_segmen = {
        "ringan": palette.WARNA_RINGAN,
        "sedang": palette.WARNA_SEDANG,
        "serius": palette.WARNA_SERIUS,
        "tidak diketahui": palette.WARNA_TIDAK_DIKETAHUI,
    }
    label_segmen = {
        "ringan": "Ringan",
        "sedang": "Sedang",
        "serius": "Serius",
        "tidak diketahui": "Tidak diketahui",
    }

    urutan_plot = SEVERITY_ORDER + (["tidak diketahui"] if "tidak diketahui" in matriks else [])

    for sev in urutan_plot:
        nilai = matriks[sev]
        bars = ax.barh(
            y,
            nilai,
            height,
            left=kiri,
            color=warna_segmen[sev],
            label=label_segmen[sev],
            edgecolor="white",
            linewidth=0.8,
        )
        for i, bar in enumerate(bars):
            v = nilai[i]
            if v > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(v)}",
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color="white",
                    fontweight="bold",
                )
        kiri = kiri + nilai

    total = kiri
    max_val = float(total.max()) if total.size else 1.0
    offset = max_val * 0.015
    for yi, tot in zip(y, total):
        ax.text(
            tot + offset,
            yi,
            f"total {int(tot)}",
            va="center",
            ha="left",
            fontsize=8.5,
            color=palette.WARNA_LABEL_SEDANG,
            fontweight="bold",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(kategori, fontsize=10)
    ax.set_xlim(0, max_val * 1.22)
    ax.set_xlabel(
        "Jumlah obat (rekord drug_safety_data.json)",
        fontsize=10,
        color=palette.WARNA_TICK,
    )
    ax.set_ylabel("Kategori obat", fontsize=10, color=palette.WARNA_TICK)
    ax.set_title(
        "Distribusi Tingkat Keparahan Efek Samping per Kategori Obat",
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

    handles = [Patch(color=warna_segmen[s], label=label_segmen[s]) for s in urutan_plot]
    ax.legend(
        handles=handles,
        title="Severity level",
        fontsize=9,
        title_fontsize=9.5,
        framealpha=0.9,
        loc="lower right",
    )

    fig.text(
        0.01,
        -0.02,
        "Sumber: FAERS openFDA via anggota1 (T1-DATA). "
        "Tiap batang merupakan kategori obat; segmen warna menunjukkan "
        "berapa banyak obat dalam kategori tersebut yang dilaporkan dengan "
        "severity ringan, sedang, atau serius.",
        fontsize=8,
        color=palette.WARNA_LABEL_SEDANG,
        wrap=True,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    target = path_output("viz_distribusi_keparahan.png")
    hasil = buat_grafik(target)
    if hasil:
        print(f"[ok] {hasil}")
    else:
        print("[gagal] tidak ada data untuk distribusi keparahan")
