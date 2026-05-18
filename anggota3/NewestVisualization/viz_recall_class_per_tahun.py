"""viz_recall_class_per_tahun.py
================================
Jumlah penarikan (recall) obat per tahun, dipecah menurut klasifikasi
keparahan FDA (Class I, Class II, Class III) dari data
`anggota1/data/drug_recalls.json`.

Tampilan stacked bar:
  - Sumbu X: tahun (parsing prefix 4 digit dari `recall_date`).
  - Sumbu Y: jumlah recall.
  - Segmen warna: Class I (merah), Class II (oranye), Class III (hijau),
    serta segmen abu untuk "Not Yet Classified" jika datanya ada.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FDA Enforcement openFDA oleh anggota1 (T1-DATA).
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
    load_drug_recalls,
    path_output,
)


CLASS_ORDER = ["Class I", "Class II", "Class III"]
CLASS_FALLBACK = "Not Yet Classified"


def _parse_tahun(tanggal: str | None) -> str | None:
    if not tanggal or not isinstance(tanggal, str) or len(tanggal) < 4:
        return None
    prefix = tanggal[:4]
    return prefix if prefix.isdigit() else None


def _agregasi(rekord: list[dict]) -> tuple[list[str], dict[str, np.ndarray]]:
    """Hitung jumlah recall per (tahun, class).

    Returns:
        Tuple (tahun_terurut, matriks_per_class)
    """
    tabel: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rekord:
        tahun = _parse_tahun(r.get("recall_date"))
        if tahun is None:
            continue
        cls = r.get("severity_class") or CLASS_FALLBACK
        if cls not in CLASS_ORDER and cls != CLASS_FALLBACK:
            cls = CLASS_FALLBACK
        tabel[tahun][cls] += 1
    tahun_terurut = sorted(tabel.keys())
    classes = CLASS_ORDER + (
        [CLASS_FALLBACK]
        if any(tabel[t].get(CLASS_FALLBACK, 0) > 0 for t in tahun_terurut)
        else []
    )
    matriks: dict[str, np.ndarray] = {
        cls: np.array([tabel[t].get(cls, 0) for t in tahun_terurut], dtype=float)
        for cls in classes
    }
    return tahun_terurut, matriks


def buat_grafik(output_path: str) -> str | None:
    """Render the recall-per-year stacked bar chart split by Class.

    Args:
        output_path: Absolute path for the resulting PNG.

    Returns:
        ``output_path`` on success, ``None`` when the recalls
        dataset is empty or no year could be parsed.
    """
    rekord = load_drug_recalls()
    if not rekord:
        print("[skip] drug_recalls.json kosong; chart tidak dibuat.")
        return None

    tahun, matriks = _agregasi(rekord)
    if not tahun:
        print("[skip] tidak ada tahun valid pada drug_recalls.json")
        return None

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    fig.patch.set_facecolor(palette.LATAR_FIGUR)

    x = np.arange(len(tahun))
    bottom = np.zeros(len(tahun))
    warna = palette.WARNA_RECALL_CLASS

    classes_present = list(matriks.keys())
    for cls in classes_present:
        nilai = matriks[cls]
        bars = ax.bar(
            x,
            nilai,
            width=0.62,
            bottom=bottom,
            color=warna.get(cls, palette.WARNA_TIDAK_DIKETAHUI),
            label=cls,
            edgecolor="white",
            linewidth=0.8,
        )
        for i, bar in enumerate(bars):
            v = nilai[i]
            if v > 0 and bar.get_height() / max(bottom.max() + nilai.max(), 1) > 0.04:
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
        bottom = bottom + nilai

    total = bottom
    max_val = float(total.max()) if total.size else 1.0
    offset = max_val * 0.02
    for xi, tot in zip(x, total):
        ax.text(
            xi,
            tot + offset,
            f"{int(tot)}",
            ha="center",
            va="bottom",
            fontsize=9,
            color=palette.WARNA_LABEL_SEDANG,
            fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(tahun, fontsize=10)
    ax.set_xlabel("Tahun penarikan", fontsize=10, color=palette.WARNA_TICK)
    ax.set_ylabel("Jumlah recall (rekord)", fontsize=10, color=palette.WARNA_TICK)
    ax.set_ylim(0, max_val * 1.18)
    ax.set_title(
        "Tren Recall Obat FDA per Tahun Berdasarkan Klasifikasi Keparahan",
        fontsize=13,
        fontweight="bold",
        pad=14,
        color=palette.WARNA_LABEL_GELAP,
    )
    ax.set_facecolor(palette.LATAR_AXES)
    ax.grid(axis="y", color=palette.WARNA_GRID, linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=palette.WARNA_TICK)
    for spine in ax.spines.values():
        spine.set_edgecolor(palette.WARNA_SPINE)

    handles = [
        Patch(color=warna.get(cls, palette.WARNA_TIDAK_DIKETAHUI), label=cls)
        for cls in classes_present
    ]
    ax.legend(
        handles=handles,
        title="Klasifikasi recall FDA",
        fontsize=9,
        title_fontsize=9.5,
        framealpha=0.9,
        loc="upper left",
    )

    fig.text(
        0.01,
        -0.02,
        "Sumber: FDA Enforcement Reports via openFDA (anggota1 T1-DATA). "
        "Class I = bahaya tinggi (potensi cedera serius), Class II = "
        "menengah, Class III = ringan. Tahun diparsing dari prefix 4 digit "
        "field recall_date.",
        fontsize=8,
        color=palette.WARNA_LABEL_SEDANG,
        wrap=True,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    target = path_output("viz_recall_class_per_tahun.png")
    hasil = buat_grafik(target)
    if hasil:
        print(f"[ok] {hasil}")
    else:
        print("[gagal] tidak ada data untuk recall per tahun")
