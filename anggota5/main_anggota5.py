# main_anggota5.py

from ambil_data import ambil_seluruh_data_pasien
from export_pdf import buat_laporan_pdf
from visualisasi import buat_grafik_perbandingan
from utils.json_handler_dummy import get_dummy_drug_data

def jalankan_fitur_anggota_5():
    print("=== Menjalankan Modul Anggota 5 ===")
    
    # ==========================================
    # FITUR 1: VISUALISASI OBAT
    # ==========================================
    data_obat = get_dummy_drug_data()
    path_grafik = buat_grafik_perbandingan(data_obat, output_filename='grafik_obat_temp.png')
    print(f"[OK] Grafik berhasil dibuat: {path_grafik}")
    
    # ==========================================
    # FITUR 2: EXPORT PDF REKAM MEDIS
    # ==========================================
    # Langkah A: Modul Ambil Data
    data_pasien = ambil_seluruh_data_pasien()
    
    # Langkah B: Modul Export PDF
    nama_file_pdf = "Laporan_RM_MedWatch.pdf"
    print(f"[ExportPDF] Sedang menyusun dokumen {nama_file_pdf}...")
    buat_laporan_pdf(data_pasien, output_filename=nama_file_pdf)
    print(f"[OK] Laporan PDF berhasil diekspor!")

if __name__ == "__main__":
    jalankan_fitur_anggota_5()
