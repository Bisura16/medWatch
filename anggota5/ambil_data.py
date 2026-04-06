# ambil_data.py

from utils.json_handler_dummy import get_dummy_patient_data

def ambil_seluruh_data_pasien():
    """
    Modul khusus untuk mengambil dan menyiapkan data pasien.
    Nantinya akan dihubungkan dengan file data_pasien.json yang dikelola anggota 2.
    """
    print("[AmbilData] Sedang mengambil data rekam medis pasien...")
    
    # Ambil data mentah
    data_mentah = get_dummy_patient_data()
    
    # Di sini Anda bisa menambahkan logika tambahan di masa depan
    # Contoh: mengurutkan data berdasarkan abjad, atau memfilter data kosong
    data_siap_proses = data_mentah 
    
    print(f"[AmbilData] Berhasil mengambil {len(data_siap_proses)} data pasien.")
    return data_siap_proses