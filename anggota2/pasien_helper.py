"""
  funsi pasien_helper.py
  Deskripsi: Helper internal untuk baca/simpan
             Pasien.json
"""
import json
import os

FILE_PASIEN          = "Pasien.json"
FILE_MEDICAL_RECORDS = "MedicalRecords.json"


def baca_file(nama_file: str = FILE_PASIEN) -> list:
    """Membaca semua data dari file JSON."""
    if not os.path.exists(nama_file):
        return []
    with open(nama_file, "r", encoding="utf-8") as f:
        return json.load(f)


def simpan_file(data: list, nama_file: str = FILE_PASIEN) -> None:
    """Menyimpan list data ke file JSON."""
    with open(nama_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def generate_id(data: list) -> str:
    """Membuat ID pasien otomatis. Format: P001, P002, dst."""
    if not data:
        return "P001"
    nomor_terakhir = max(int(p["id"][1:]) for p in data if p["id"][1:].isdigit())
    return f"P{str(nomor_terakhir + 1).zfill(3)}"


def input_wajib(label: str) -> str:
    """Input yang tidak boleh kosong."""
    while True:
        nilai = input(label).strip()
        if nilai:
            return nilai
        print("  [!] Field ini wajib diisi.")