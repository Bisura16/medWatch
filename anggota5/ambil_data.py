<<<<<<< HEAD
import json
import os

def ambil_seluruh_data_pasien():
    # 1. Dapatkan lokasi folder anggota5
    lokasi_sekarang = os.path.dirname(os.path.abspath(__file__))
    
    # 2. PERBAIKAN: Naik satu level (..), lalu masuk ke anggota2
    # Kita tidak menggunakan subfolder "data" lagi karena Pasien.json ada di root anggota2
    path_absolut = os.path.normpath(os.path.join(lokasi_sekarang, "..", "anggota2", "Pasien.json"))

    if not os.path.exists(path_absolut):
        print(f"Peringatan: File {path_absolut} tidak ditemukan.")
        return []

    try:
        with open(path_absolut, 'r', encoding='utf-8') as file:
            data_mentah = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    data_siap_proses = []
    for data in data_mentah:
        # Mengambil dictionary S, O, A, P (default {} jika tidak ada)
        S = data.get("S", {})
        O = data.get("O", {})
        A = data.get("A", {})
        P = data.get("P", {})
        
        pasien_terformat = {
            "identitas": {
                "ID Pasien": data.get("id", "-"),
                "Nama Pasien": data.get("nama", "-"),
                "Umur": str(data.get("umur", "-")) + " Tahun",
                "Tanggal Kunjungan": data.get("tanggal_kunjungan", "-"),
                "Alamat": data.get("alamat", "-") # Tambahan agar lebih lengkap
            },
            # Mapping ke format string untuk fungsi tulis_section kamu
            "anamnesis": f"Keluhan Utama : {S.get('keluhan', '-')}\nRiwayat Sakit : {S.get('riwayat', '-')}",
            "pemeriksaan": (
                f"Tekanan Darah : {O.get('tekanan_darah', '-')} mmHg\n"
                f"Nadi : {O.get('nadi', '-')} x/menit\n"
                f"Suhu Tubuh : {O.get('suhu_c', '-')} °C\n"
                f"Berat Badan : {O.get('bb_kg', '-')} kg\n"
                f"Catatan Lain : {O.get('catatan', '-')}"
            ),
            "diagnosis_tindakan": (
                f"DIAGNOSA (A) :\n{A.get('diagnosa', '-')}\n\n"
                f"TINDAKAN (P) :\n{P.get('tindakan', '-')}\n\n"
                f"RESEP OBAT : {P.get('resep', '-')}\n"
                f"JADWAL KONTROL : {P.get('jadwal_kontrol', '-')}"
            )
        }
        data_siap_proses.append(pasien_terformat)

    return data_siap_proses
=======
import json
import os

def ambil_seluruh_data_pasien():
    # 1. Dapatkan lokasi folder anggota5
    lokasi_sekarang = os.path.dirname(os.path.abspath(__file__))
    
    # 2. PERBAIKAN: Naik satu level (..), lalu masuk ke anggota2
    # Kita tidak menggunakan subfolder "data" lagi karena Pasien.json ada di root anggota2
    path_absolut = os.path.normpath(os.path.join(lokasi_sekarang, "..", "anggota2", "Pasien.json"))

    if not os.path.exists(path_absolut):
        print(f"Peringatan: File {path_absolut} tidak ditemukan.")
        return []

    try:
        with open(path_absolut, 'r', encoding='utf-8') as file:
            data_mentah = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    data_siap_proses = []
    for data in data_mentah:
        # Mengambil dictionary S, O, A, P (default {} jika tidak ada)
        S = data.get("S", {})
        O = data.get("O", {})
        A = data.get("A", {})
        P = data.get("P", {})
        
        pasien_terformat = {
            "identitas": {
                "ID Pasien": data.get("id", "-"),
                "Nama Pasien": data.get("nama", "-"),
                "Umur": str(data.get("umur", "-")) + " Tahun",
                "Tanggal Kunjungan": data.get("tanggal_kunjungan", "-"),
                "Alamat": data.get("alamat", "-") # Tambahan agar lebih lengkap
            },
            # Mapping ke format string untuk fungsi tulis_section kamu
            "anamnesis": f"Keluhan Utama : {S.get('keluhan', '-')}\nRiwayat Sakit : {S.get('riwayat', '-')}",
            "pemeriksaan": (
                f"Tekanan Darah : {O.get('tekanan_darah', '-')} mmHg\n"
                f"Nadi : {O.get('nadi', '-')} x/menit\n"
                f"Suhu Tubuh : {O.get('suhu_c', '-')} °C\n"
                f"Berat Badan : {O.get('bb_kg', '-')} kg\n"
                f"Catatan Lain : {O.get('catatan', '-')}"
            ),
            "diagnosis_tindakan": (
                f"DIAGNOSA (A) :\n{A.get('diagnosa', '-')}\n\n"
                f"TINDAKAN (P) :\n{P.get('tindakan', '-')}\n\n"
                f"RESEP OBAT : {P.get('resep', '-')}\n"
                f"JADWAL KONTROL : {P.get('jadwal_kontrol', '-')}"
            )
        }
        data_siap_proses.append(pasien_terformat)

    return data_siap_proses
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
