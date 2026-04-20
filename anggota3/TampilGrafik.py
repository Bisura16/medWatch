"""
TampilGrafik.py
===============
Modul utama visualisasi MedWatch.
Semua fungsi grafik ada di sini.

Menggunakan:
  - BacaData.py          → semua pembacaan data
  - PerbandinganObat.py  → algoritma heatmap efek samping

Fungsi publik (dipanggil file grafik masing-masing):
  visgrafikkeluhan(output_pie, output_hbar)   → Pie + Horizontal Bar
  visgrafikEfek(output_filename)              → Heatmap efek samping
  Vgrafik10topEfek(output_filename)           → Bar Chart Top 10

Library: matplotlib, numpy
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from BacaData        import get_data_distribusi_keluhan, get_data_top10_efek_samping
from PerbandinganObat import siapkan_data_heatmap

# ─────────────────────────────────────────────
# PALET WARNA MEDWATCH
# ─────────────────────────────────────────────
WARNA_ANAK   = "#A78BFA"
WARNA_DEWASA = "#7C3AED"
WARNA_LANSIA = "#1E1B4B"

PALET_PIE = [
    "#7C3AED","#A78BFA","#C4B5FD","#6D28D9",
    "#8B5CF6","#DDD6FE","#4C1D95","#EDE9FE",
]


# ─────────────────────────────────────────────
# HELPER INTERNAL
# ─────────────────────────────────────────────
def _simpan_atau_tampil(fig, output_filename):
    fig.tight_layout()
    if output_filename:
        plt.savefig(output_filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_filename
    plt.show()
    return None


def _style_ax(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14, color="#1C1C2E")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color="#4B5563")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color="#4B5563")
    ax.set_facecolor("#FAFAFA")
    ax.tick_params(colors="#4B5563")
    for spine in ax.spines.values():
        spine.set_edgecolor("#E5E7EB")


# ══════════════════════════════════════════════════════
# GRAFIK 2A – PIE CHART DISTRIBUSI KELUHAN
# ══════════════════════════════════════════════════════
def _tampil_pie_keluhan(output_filename=None):
    data    = get_data_distribusi_keluhan()
    keluhan = data["keluhan"]
    total   = data["total"]

    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor("#FFFFFF")

    wedges, _, autotexts = ax.pie(
        total,
        labels=None,
        colors=PALET_PIE[:len(keluhan)],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.set_title("Distribusi Keluhan Pasien",
                 fontsize=13, fontweight="bold", pad=15, color="#1C1C2E")
    ax.legend(
        wedges,
        [f"{k}  ({t} kasus)" for k, t in zip(keluhan, total)],
        title="Keluhan",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8.5,
        framealpha=0.9,
    )

    return _simpan_atau_tampil(fig, output_filename)


# ══════════════════════════════════════════════════════
# GRAFIK 2B – HORIZONTAL GROUPED BAR (3 RENTANG UMUR)
# ══════════════════════════════════════════════════════
def _tampil_hbar_keluhan_umur(output_filename=None):
    data    = get_data_distribusi_keluhan()
    keluhan = data["keluhan"]
    anak    = np.array(data["anak"],   dtype=float)
    dewasa  = np.array(data["dewasa"], dtype=float)
    lansia  = np.array(data["lansia"], dtype=float)
    total   = np.array(data["total"],  dtype=float)

    # Urutkan ascending → terbanyak paling atas
    idx     = np.argsort(total)
    keluhan = [keluhan[i] for i in idx]
    anak    = anak[idx];  dewasa = dewasa[idx]
    lansia  = lansia[idx]; total  = total[idx]

    n  = len(keluhan)
    y  = np.arange(n)
    h  = 0.26

    fig, ax = plt.subplots(figsize=(11, max(5, n * 0.9)))
    fig.patch.set_facecolor("#FFFFFF")

    b1 = ax.barh(y + h, anak,   h, label="Anak-Anak (0–18 th)",
                 color=WARNA_ANAK,   edgecolor="white", linewidth=0.7)
    b2 = ax.barh(y,     dewasa, h, label="Dewasa (19–59 th)",
                 color=WARNA_DEWASA, edgecolor="white", linewidth=0.7)
    b3 = ax.barh(y - h, lansia, h, label="Lansia (>60 th)",
                 color=WARNA_LANSIA, edgecolor="white", linewidth=0.7)

    max_val = max(anak.max(), dewasa.max(), lansia.max())
    offset  = max_val * 0.012
    for bars in (b1, b2, b3):
        for bar in bars:
            w = bar.get_width()
            if w > 0:
                ax.text(w + offset, bar.get_y() + bar.get_height() / 2,
                        str(int(w)), va="center", ha="left",
                        fontsize=8, color="#374151")

    # Label total kecil di kiri
    for yi, tot in zip(y, total):
        ax.text(-offset * 3, yi, f"({int(tot)})",
                va="center", ha="right", fontsize=7.5, color="#9CA3AF")

    ax.set_yticks(y)
    ax.set_yticklabels(keluhan, fontsize=10)
    ax.set_xlim(0, max_val * 1.2)
    ax.set_ylim(-h * 2, n - 1 + h * 2)
    ax.grid(axis="x", color="#E5E7EB", linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9, framealpha=0.88, loc="lower right")

    _style_ax(ax,
        title="Distribusi Keluhan Pasien per Rentang Umur",
        xlabel="Jumlah Kasus",
        ylabel="Jenis Keluhan / Penyakit",
    )

    return _simpan_atau_tampil(fig, output_filename)


# ══════════════════════════════════════════════════════
# GRAFIK 3 – HEATMAP PERBANDINGAN EFEK SAMPING OBAT
# ══════════════════════════════════════════════════════
def _tampil_heatmap_efek_samping(output_filename=None):
    # Data diproses oleh PerbandinganObat
    data        = siapkan_data_heatmap(urutkan=True)
    obat        = data["obat"]
    efek        = data["efek"]
    matriks_pct = data["matriks_pct"]

    n_obat = len(obat)
    n_efek = len(efek)

    fig_w = max(9,  n_efek * 0.8)
    fig_h = max(5,  n_obat * 0.52) + 1.8

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("#FFFFFF")

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "medwatch",
        ["#EDE9FE", "#A78BFA", "#7C3AED", "#4C1D95"],
        N=256,
    )
    im = ax.imshow(matriks_pct, aspect="auto", cmap=cmap, vmin=0, vmax=100)

    # Anotasi nilai tiap sel
    for i in range(n_obat):
        for j in range(n_efek):
            val = matriks_pct[i, j]
            if val > 0:
                tc = "white" if val > 55 else "#374151"
                ax.text(j, i, f"{val:.0f}",
                        ha="center", va="center",
                        fontsize=7.5, color=tc, fontweight="bold")

    ax.set_xticks(range(n_efek))
    ax.set_xticklabels(efek, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(n_obat))
    ax.set_yticklabels(obat, fontsize=9.5)

    # Grid antar sel
    ax.set_xticks(np.arange(-0.5, n_efek, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_obat, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(which="major", bottom=False, left=False)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title("Perbandingan Profil Efek Samping Obat",
                 fontsize=13, fontweight="bold", pad=14, color="#1C1C2E")

    cbar = fig.colorbar(im, ax=ax, orientation="horizontal",
                        fraction=0.03, pad=0.18, aspect=40)
    cbar.set_label("FREKUENSI EFEK SAMPING",
                   fontsize=8, color="#6B7280", labelpad=6, fontweight="bold")
    cbar.ax.tick_params(labelsize=8)
    cbar.set_ticks([0, 25, 50, 75, 100])
    cbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

    return _simpan_atau_tampil(fig, output_filename)


# ══════════════════════════════════════════════════════
# GRAFIK 4 – BAR CHART TOP 10 EFEK SAMPING
# ══════════════════════════════════════════════════════
def _tampil_bar_top10(output_filename=None):
    data = get_data_top10_efek_samping()
    efek = data["efek_samping"][:10]
    jml  = data["jumlah"][:10]

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor("#FFFFFF")

    norm_vals  = np.array(jml, dtype=float) / max(jml)
    bar_colors = [plt.cm.Purples(0.35 + 0.55 * v) for v in norm_vals]

    bars = ax.bar(efek, jml, color=bar_colors,
                  edgecolor="white", linewidth=0.9, width=0.62)

    for bar, val in zip(bars, jml):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(jml) * 0.012,
                str(val),
                ha="center", va="bottom",
                fontsize=9.5, color="#374151", fontweight="bold")

    rata2 = np.mean(jml)
    ax.axhline(rata2, color="#A78BFA", linestyle="--",
               linewidth=1.3, alpha=0.8, label=f"Rata-rata ({rata2:.1f})")

    ax.set_ylim(0, max(jml) * 1.18)
    ax.grid(axis="y", color="#E5E7EB", linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9, framealpha=0.85)
    plt.xticks(rotation=28, ha="right", fontsize=9.5)

    _style_ax(ax,
        title="Top 10 Efek Samping Obat Paling Sering Dilaporkan",
        xlabel="Jenis Efek Samping",
        ylabel="Jumlah Kasus Dilaporkan",
    )

    return _simpan_atau_tampil(fig, output_filename)


# ══════════════════════════════════════════════════════
# FUNGSI PUBLIK – dipanggil file grafik masing-masing
# ══════════════════════════════════════════════════════
def visgrafikkeluhan(output_pie=None, output_hbar=None):
    """Tampilkan Pie Chart + Horizontal Bar distribusi keluhan."""
    _tampil_pie_keluhan(output_pie)
    _tampil_hbar_keluhan_umur(output_hbar)


def visgrafikEfek(output_filename=None):
    """Tampilkan Heatmap perbandingan efek samping obat."""
    return _tampil_heatmap_efek_samping(output_filename)


def Vgrafik10topEfek(output_filename=None):
    """Tampilkan Bar Chart Top 10 efek samping."""
    return _tampil_bar_top10(output_filename)
