"""data_loader.py
================
Pemuat data scraping untuk modul NewestVisualization.

Membaca dua berkas hasil scraping milik anggota1:
  - `anggota1/data/drug_safety_data.json`
  - `anggota1/data/drug_recalls.json`

Penanganan kegagalan:
  - File tidak ditemukan  -> kembalikan list kosong dan cetak peringatan.
  - File rusak / non-JSON -> raise ValueError dengan pesan jelas.
  - Field tidak lengkap   -> rekord diabaikan oleh masing-masing skrip viz.

Modul ini sengaja membaca berkas JSON langsung, tanpa meng-import paket
`anggota1` atau `anggota4`, agar tidak menambah ketergantungan lintas modul.

Penulis dokumenter: Alia Ardani, NIM 251524035, System Analyst (anggota3).
"""
from __future__ import annotations

import json
import os
from typing import Any

# Akar repo medWatch dihitung relatif dari lokasi berkas ini.
# berkas ini -> anggota3/NewestVisualization/data_loader.py
# parent[2]  -> medWatch/ (akar)
_AKAR_REPO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

PATH_DRUG_SAFETY = os.path.join(
    _AKAR_REPO, "anggota1", "data", "drug_safety_data.json"
)
PATH_DRUG_RECALLS = os.path.join(
    _AKAR_REPO, "anggota1", "data", "drug_recalls.json"
)

# Folder keluaran PNG bersama untuk semua skrip viz
PATH_OUTPUT = os.path.join(
    _AKAR_REPO, "anggota3", "NewestVisualization", "output"
)


def _muat_json(path: str) -> list[dict[str, Any]]:
    """Baca satu berkas JSON dan kembalikan list of dict.

    Args:
        path: path absolut ke berkas JSON.

    Returns:
        List rekord. Kembalikan list kosong bila berkas tidak ada.

    Raises:
        ValueError: berkas ada tetapi gagal di-parse atau strukturnya
                    bukan list.
    """
    if not os.path.exists(path):
        print(f"[peringatan] berkas tidak ditemukan: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gagal mem-parsing JSON dari {path}: {exc.msg} "
            f"(baris {exc.lineno}, kolom {exc.colno})"
        ) from exc
    if not isinstance(data, list):
        raise ValueError(
            f"Struktur JSON tidak valid di {path}: "
            f"diharapkan list, ditemukan {type(data).__name__}"
        )
    return data


def load_drug_safety() -> list[dict[str, Any]]:
    """Kembalikan list rekord efek samping obat.

    Setiap rekord mengikuti skema:
      {drug_name, category, side_effects[], severity_level,
       warnings, source_url}
    """
    return _muat_json(PATH_DRUG_SAFETY)


def load_drug_recalls() -> list[dict[str, Any]]:
    """Kembalikan list rekord penarikan obat (FDA recalls).

    Setiap rekord mengikuti skema:
      {product_name, reason, recall_date, severity_class, company}
    """
    return _muat_json(PATH_DRUG_RECALLS)


def pastikan_folder_output() -> str:
    """Buat folder `output/` bila belum ada, kembalikan path absolutnya."""
    os.makedirs(PATH_OUTPUT, exist_ok=True)
    return PATH_OUTPUT


def path_output(nama_file: str) -> str:
    """Helper untuk menyusun path absolut hasil PNG di folder output."""
    pastikan_folder_output()
    return os.path.join(PATH_OUTPUT, nama_file)
