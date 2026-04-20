from ambil_data import ambil_seluruh_data_pasien
# PERBAIKAN: Import fungsi buat_laporan_pdf dari modul export_pdf
from export_pdf import buat_laporan_pdf 

# Catatan: Baris di bawah ini bisa dihapus jika tidak dipakai di file ini
# from utils.json_handler_dummy import get_dummy_drug_data

def jalankan_fitur_anggota_5():
    print("=== Menjalankan Modul Anggota 5 ===")
    
    # ==========================================
    # FITUR 2: EXPORT PDF REKAM MEDIS
    # ==========================================
    # Langkah A: Modul Ambil Data
    data_pasien = ambil_seluruh_data_pasien()
    
    # Langkah B: Modul Export PDF
    nama_file_pdf = "Laporan_RM_MedWatch.pdf"
    print(f"[ExportPDF] Sedang menyusun dokumen {nama_file_pdf}...")
    
    # Fungsi ini sekarang bisa berjalan karena sudah di-import
    buat_laporan_pdf(data_pasien, output_filename=nama_file_pdf)
    print(f"[OK] Laporan PDF berhasil diekspor!")

if __name__ == "__main__":
    jalankan_fitur_anggota_5()