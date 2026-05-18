"""viz_heatmap_obat_efek.py
============================
Heatmap obat x kategori efek samping dari data scraping FAERS openFDA
(`anggota1/data/drug_safety_data.json`).

Setiap sel pada heatmap menyatakan banyaknya kali kategori efek samping
tersebut muncul pada list `side_effects` masing-masing obat. Karena
side_effects bersifat kategorikal (string) maka setiap kemunculan
dihitung sebagai satu. Sel kosong tetap diwarnai sebagai tint paling
terang (bukan dibiarkan putih) sesuai pedoman MedWatch.

Fitur:
  - Skala warna kontinu `YlOrRd` (kuning -> oranye -> merah).
  - Sel bernilai 0 ditampilkan dengan tint paling terang (kuning pucat).
  - Sumbu X dan Y diurutkan berdasarkan total kolom/baris menurun.
  - Anotasi numerik di setiap sel; warna teks otomatis kontras.
  - Colorbar gradient dengan tick min / mid / max.
  - Caption dalam Bahasa Indonesia menjelaskan encoding warna.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
Sumber data: scraping FAERS openFDA oleh anggota1 (T1-DATA).
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

if __package__ in (None, ""):
    _akar = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _akar not in sys.path:
        sys.path.insert(0, _akar)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from anggota3.NewestVisualization import palette
from anggota3.NewestVisualization.data_loader import (
    load_drug_safety,
    path_output,
)


TOP_OBAT = 20
TOP_EFEK = 18

# Pengelompokan kasar istilah FAERS ke kategori bermakna untuk bidan.
# Kategori dipilih supaya nilainya jadi padat (heatmap bukan sparse).
KATEGORI_EFEK = [
    ("Saluran cerna", ["nausea", "vomit", "diarrh", "abdomin", "constipation", "dyspepsia", "gastritis"]),
    ("Nyeri umum", ["pain", "headache", "arthralgia", "myalgia", "back pain", "neck pain"]),
    ("Sistem saraf pusat", ["dizziness", "somnolence", "tremor", "confus", "syncope", "seizure", "paraesthesia", "neuropathy"]),
    ("Saluran napas", ["dyspnoea", "cough", "asthma", "pneumonia", "wheezing", "bronch"]),
    ("Reaksi kulit", ["rash", "pruritus", "urticaria", "erythema", "alopecia", "dermatitis"]),
    ("Kardiovaskular", ["hypotension", "hypertension", "tachycardia", "bradycardia", "palpitation", "arrhythmia", "atrial"]),
    ("Hematologi", ["anaemia", "leukopenia", "neutropenia", "thrombocytopenia", "bleeding", "haemorrhage"]),
    ("Metabolik / endokrin", ["hyperglycaem", "hypoglycaem", "weight", "diabetes", "thyroid"]),
    ("Ginjal & saluran kemih", ["renal", "kidney", "urin", "dysuria"]),
    ("Hati", ["hepat", "liver", "jaundice"]),
    ("Psikiatri", ["anxiety", "depression", "insomnia", "agitation", "emotional", "suicidal"]),
    ("Umum / sistemik", ["fatigue", "asthenia", "malaise", "pyrexia", "oedema", "off label use", "drug ineffective", "fall", "overdose"]),
]


def _klasifikasi(efek: str) -> str | None:
    """Kembalikan kategori efek samping berdasar substring; None jika tidak cocok."""
    if not isinstance(efek, str):
        return None
    teks = efek.lower()
    for nama_kategori, pola in KATEGORI_EFEK:
        for p in pola:
            if p in teks:
                return nama_kategori
    return None


def _bangun_matriks(rekord: list[dict]) -> tuple[list[str], list[str], np.ndarray]:
    """Hitung matriks frekuensi obat x kategori efek samping."""
    hitung: dict[str, Counter] = defaultdict(Counter)
    untuk_obat = {}
    for r in rekord:
        nama = r.get("drug_name")
        side = r.get("side_effects") or []
        if not nama or not isinstance(side, list):
            continue
        untuk_obat.setdefault(nama, 0)
        untuk_obat[nama] += len(side)
        for s in side:
            kat = _klasifikasi(s)
            if kat is None:
                continue
            hitung[nama][kat] += 1

    # Pilih TOP_OBAT obat dengan total kemunculan terbesar
    nama_terurut = sorted(
        hitung.keys(),
        key=lambda n: sum(hitung[n].values()),
        reverse=True,
    )[:TOP_OBAT]
    # Pilih kategori dengan total kemunculan tertinggi (di antara TOP_OBAT)
    total_kategori: Counter = Counter()
    for n in nama_terurut:
        for k, v in hitung[n].items():
            total_kategori[k] += v
    kategori_terurut = [
        k for k, _ in total_kategori.most_common(TOP_EFEK)
    ]
    # Susun matriks
    matriks = np.zeros((len(nama_terurut), len(kategori_terurut)), dtype=float)
    for i, n in enumerate(nama_terurut):
        for j, k in enumerate(kategori_terurut):
            matriks[i, j] = hitung[n].get(k, 0)
    # Urutkan akhir: baris by row-sum desc, kolom by col-sum desc
    row_sum = matriks.sum(axis=1)
    col_sum = matriks.sum(axis=0)
    row_order = np.argsort(-row_sum)
    col_order = np.argsort(-col_sum)
    matriks = matriks[row_order][:, col_order]
    nama_terurut = [nama_terurut[i] for i in row_order]
    kategori_terurut = [kategori_terurut[j] for j in col_order]
    return nama_terurut, kategori_terurut, matriks


def _warna_teks_kontras(value_norm: float) -> str:
    """Pilih warna teks (gelap/putih) menurut intensitas sel."""
    # value_norm di range [0, 1]; ambang 0.6 cocok untuk YlOrRd
    return "white" if value_norm > 0.6 else palette.WARNA_LABEL_SEDANG


def buat_grafik(output_path: str) -> str | None:
    """Render the drug x effect-category heatmap.

    Args:
        output_path: Absolute path for the resulting PNG.

    Returns:
        ``output_path`` on success, ``None`` when there are no valid
        drug-category pairs or every cell is zero (uninformative).
    """
    rekord = load_drug_safety()
    if not rekord:
        print("[skip] drug_safety_data.json kosong; heatmap tidak dibuat.")
        return None

    nama_obat, kategori, matriks = _bangun_matriks(rekord)
    if matriks.size == 0 or not nama_obat or not kategori:
        print("[skip] tidak ada pasangan obat-kategori valid untuk heatmap.")
        return None

    max_val = float(matriks.max()) if matriks.size else 1.0
    if max_val <= 0:
        print("[skip] semua sel heatmap bernilai nol; tidak informatif.")
        return None
    mid_val = max_val / 2

    n_baris, n_kolom = matriks.shape
    fig_w = max(9.0, n_kolom * 0.65)
    fig_h = max(6.0, n_baris * 0.42) + 1.8

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(palette.LATAR_FIGUR)

    cmap = plt.get_cmap("YlOrRd")
    im = ax.imshow(matriks, aspect="auto", cmap=cmap, vmin=0, vmax=max_val)

    # Anotasi sel
    for i in range(n_baris):
        for j in range(n_kolom):
            val = matriks[i, j]
            norm = val / max_val if max_val > 0 else 0.0
            txt = f"{int(val)}" if val > 0 else "0"
            ax.text(
                j,
                i,
                txt,
                ha="center",
                va="center",
                fontsize=8.5,
                fontweight="bold",
                color=_warna_teks_kontras(norm),
            )

    ax.set_xticks(range(n_kolom))
    ax.set_xticklabels(kategori, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(n_baris))
    ax.set_yticklabels(nama_obat, fontsize=9.5)

    # Grid antar sel (putih tipis)
    ax.set_xticks(np.arange(-0.5, n_kolom, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_baris, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(which="major", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        "Heatmap Frekuensi Kategori Efek Samping per Obat",
        fontsize=13,
        fontweight="bold",
        pad=14,
        color=palette.WARNA_LABEL_GELAP,
    )
    ax.set_xlabel(
        "Kategori efek samping (klasifikasi MedWatch dari MedDRA)",
        fontsize=10,
        color=palette.WARNA_TICK,
        labelpad=8,
    )
    ax.set_ylabel(
        "Nama obat (Top 20 menurut total kemunculan)",
        fontsize=10,
        color=palette.WARNA_TICK,
    )

    cbar = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.032, pad=0.03)
    cbar.set_label(
        "Frekuensi kemunculan efek samping (laporan FAERS)",
        fontsize=9,
        color=palette.WARNA_LABEL_SEDANG,
        labelpad=10,
        fontweight="bold",
    )
    cbar.set_ticks([0, mid_val, max_val])
    cbar.set_ticklabels([
        "0 (terang)",
        f"{int(mid_val)} (menengah)",
        f"{int(max_val)} (gelap)",
    ])
    cbar.ax.tick_params(labelsize=8, colors=palette.WARNA_TICK)

    fig.text(
        0.01,
        0.005,
        "Sumber: FAERS openFDA via anggota1 (T1-DATA). "
        "Setiap sel menghitung berapa kali nama efek samping pada list "
        "side_effects obat (baris) cocok dengan substring pengenal "
        "kategori (kolom). Warna kontinu YlOrRd: kuning terang = 0, "
        "merah pekat = nilai maksimum. Baris dan kolom diurut menurut "
        "total menurun.",
        fontsize=8,
        color=palette.WARNA_LABEL_SEDANG,
        wrap=True,
    )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    target = path_output("viz_heatmap_obat_efek.png")
    hasil = buat_grafik(target)
    if hasil:
        print(f"[ok] {hasil}")
    else:
        print("[gagal] tidak ada data untuk heatmap obat x efek")
