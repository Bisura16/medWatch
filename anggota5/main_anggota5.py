# main_anggota5.py

from ambil_data import ambil_seluruh_data_pasien
from export_pdf import buat_laporan_pdf

def jalankan_fitur_anggota_5():
    print("=== Menjalankan Modul Anggota 5 ===")
    # ==========================================
    # FITUR : EXPORT PDF REKAM MEDIS
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