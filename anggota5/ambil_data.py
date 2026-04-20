import json
import os

def ambil_seluruh_data_pasien(filepath="data/Pasien.json"):
    lokasi_sekarang = os.path.dirname(os.path.abspath(__file__))
    path_absolut = os.path.join(lokasi_sekarang, "data", "Pasien.json")

    if not os.path.exists(path_absolut):
        print(f"Peringatan: File {path_absolut} tidak ditemukan.")
        return []

    try:
        with open(path_absolut, 'r', encoding='utf-8') as file:
            data_mentah = json.load(file)
    except json.JSONDecodeError:
        return []

    data_siap_proses = []
    for data in data_mentah:
        S = data.get("S", {})
        O = data.get("O", {})
        A = data.get("A", {})
        P = data.get("P", {})
        
        pasien_terformat = {
            "identitas": {
                "ID Pasien": data.get("id", "-"),
                "Nama Pasien": data.get("nama", "-"),
                "Umur": str(data.get("umur", "-")) + " Tahun",
                "Tanggal Kunjungan": data.get("tanggal_kunjungan", "-")
            },
            "anamnesis": f"Keluhan Utama : {S.get('keluhan', '-')}\nRiwayat Sakit : {S.get('riwayat', '-')}",
            "pemeriksaan": f"Tekanan Darah : {O.get('tekanan_darah', '-')} mmHg\nNadi : {O.get('nadi', '-')} x/menit\nSuhu Tubuh : {O.get('suhu_c', '-')} °C\nCatatan Lain : {O.get('catatan', '-')}",
            "diagnosis_tindakan": f"DIAGNOSA (A) :\n{A.get('diagnosa', '-')}\n\nTINDAKAN (P) :\n{P.get('tindakan', '-')}\n\nRESEP OBAT : {P.get('resep', '-')}"
        }
        data_siap_proses.append(pasien_terformat)

    return data_siap_proses