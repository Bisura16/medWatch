"""
data_loader.py
==============
Modul pusat untuk membaca database obat dan database efek samping.
Semua modul anggota 4 mengambil data dari file ini agar alurnya modular.
"""

import json
import os
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OBAT_DB = os.path.join(DATA_DIR, "drug_database.json")
EFEK_DB = os.path.join(DATA_DIR, "effect_database.json")


def _baca_json(path: str) -> List[Dict]:
    """Baca file JSON dan kembalikan list kosong bila file bermasalah."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def normalisasi_teks(teks: str) -> str:
    """Samakan format teks agar pencarian dan pencocokan lebih stabil."""
    return " ".join((teks or "").strip().lower().split())


def muat_database_obat() -> List[Dict]:
    """Ambil seluruh data obat dari file database utama."""
    return _baca_json(OBAT_DB)


def muat_database_efek_samping() -> List[Dict]:
    """Ambil seluruh master data efek samping."""
    return _baca_json(EFEK_DB)


def buat_index_efek_samping() -> Dict[str, Dict]:
    """
    Buat index {nama_efek_normalized: data_efek} agar proses cross-reference
    di safety checker lebih cepat dan tidak perlu loop berulang.
    """
    return {
        normalisasi_teks(item.get("nama_efek", "")): item
        for item in muat_database_efek_samping()
        if item.get("nama_efek")
    }


def _kolom_pencarian_obat(obat: Dict) -> List[str]:
    """Gabungkan kolom-kolom yang relevan untuk fitur pencarian obat."""
    bidang = [
        obat.get("nama_obat", ""),
        obat.get("kategori", ""),
        obat.get("dosis_umum", ""),
        obat.get("kehamilan", ""),
    ]
    bidang.extend(obat.get("alias", []))
    bidang.extend(obat.get("bahan_aktif", []))
    bidang.extend(obat.get("indikasi", []))
    return [normalisasi_teks(item) for item in bidang if item]


def _hitung_skor_kecocokan(obat: Dict, keyword_norm: str) -> int:
    """
    Beri skor sederhana agar hasil yang paling relevan muncul lebih dulu.
    Exact match nama obat atau alias diberi bobot paling tinggi.
    """
    nama_obat = normalisasi_teks(obat.get("nama_obat", ""))
    alias = [normalisasi_teks(item) for item in obat.get("alias", [])]

    if keyword_norm == nama_obat or keyword_norm in alias:
        return 100
    if nama_obat.startswith(keyword_norm):
        return 90
    if keyword_norm in nama_obat:
        return 80

    kolom = _kolom_pencarian_obat(obat)
    for nilai in kolom:
        if nilai.startswith(keyword_norm):
            return 70
        if keyword_norm in nilai:
            return 60

    return 0


def cari_obat_dalam_database(kata_kunci: str) -> List[Dict]:
    """Cari obat berdasarkan nama, alias, bahan aktif, kategori, atau indikasi."""
    keyword_norm = normalisasi_teks(kata_kunci)
    if not keyword_norm:
        return []

    hasil = []
    for obat in muat_database_obat():
        skor = _hitung_skor_kecocokan(obat, keyword_norm)
        if skor > 0:
            hasil.append((skor, obat))

    # Urutkan dari skor paling relevan lalu nama obat agar hasil konsisten.
    hasil.sort(key=lambda item: (-item[0], item[1].get("nama_obat", "")))
    return [item[1] for item in hasil]


def ambil_obat_terbaik(kata_kunci: str) -> Optional[Dict]:
    """
    Ambil satu data obat paling relevan.
    Dipakai oleh fitur profil keamanan dan safety checker.
    """
    hasil = cari_obat_dalam_database(kata_kunci)
    return hasil[0] if hasil else None
