<<<<<<< HEAD
import os
from fpdf import FPDF

# 1. CLASS DEFINITION
class MedWatchPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'REKAM MEDIS PASIEN - MEDWATCH', align='C', ln=True)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', align='C')

# 2. FUNGSI PEMBANTU UNTUK MENCETAK BAGIAN (SECTION)
def tulis_section(pdf, judul_section, data_content):
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 8, f" {judul_section}", ln=True, fill=True)
    pdf.ln(2)
    
    # JIKA DATA ADALAH DICTIONARY (Contoh: Identitas)
    if isinstance(data_content, dict):
        for key, value in data_content.items():
            current_y = pdf.get_y()
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_xy(10, current_y)
            pdf.cell(50, 6, f"{key}")
            
            pdf.set_font('helvetica', '', 10)
            pdf.set_xy(60, current_y)
            pdf.multi_cell(130, 6, f": {value}")
            
    # JIKA DATA ADALAH STRING (Contoh: Anamnesis / Pemeriksaan)
    elif isinstance(data_content, str):
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, data_content)
    
    pdf.ln(4)

# 3. FUNGSI UTAMA EKSPOR (Dengan parameter opsional 'id_pasien_terpilih')
def buat_laporan_pdf(data_pasien, output_filename="Laporan_MedWatch.pdf", id_pasien_terpilih=None):
    pdf = MedWatchPDF() 
    
    # === PROSES FILTERING ===
    data_yang_akan_dicetak = []
    
    if id_pasien_terpilih:
        # Cari pasien berdasarkan ID
        for pasien in data_pasien:
            # Mengambil ID dari dictionary identitas yang sudah di-mapping
            id_sekarang = pasien.get("identitas", {}).get("ID Pasien")
            
            if str(id_sekarang) == str(id_pasien_terpilih):
                data_yang_akan_dicetak.append(pasien)
                break # Hentikan pencarian jika sudah ketemu (asumsi ID unik)
                
        if not data_yang_akan_dicetak:
            print(f"[!] Pasien dengan ID '{id_pasien_terpilih}' tidak ditemukan.")
            return # Keluar dari fungsi jika data tidak ada
    else:
        # Jika id_pasien_terpilih kosong, cetak semua data
        data_yang_akan_dicetak = data_pasien
    # ========================

    # Buat halaman PDF untuk data yang sudah disaring
    for pasien in data_yang_akan_dicetak:
        pdf.add_page()
        
        tulis_section(pdf, "1. IDENTITAS PASIEN", pasien.get("identitas", {}))
        tulis_section(pdf, "2. ANAMNESIS (SUBJEKTIF)", pasien.get("anamnesis", "-"))
        tulis_section(pdf, "3. PEMERIKSAAN FISIK (OBJEKTIF)", pasien.get("pemeriksaan", "-"))
        tulis_section(pdf, "4. DIAGNOSIS DAN TINDAKAN", pasien.get("diagnosis_tindakan", "-"))
        
        # --- Bagian Tanda Tangan ---
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 10)
        current_y_ttd = pdf.get_y()
        
        pdf.set_xy(10, current_y_ttd)
        pdf.cell(90, 6, "Pasien / Keluarga Pasien,", align='C')
        pdf.set_xy(110, current_y_ttd)
        pdf.cell(90, 6, "Bidan / Dokter Pemeriksa,", align='C')
        
        pdf.ln(20)
        current_y_nama = pdf.get_y()
        nama_pasien = pasien.get("identitas", {}).get("Nama Pasien", "(.......................................)")
        
        pdf.set_font('helvetica', 'U', 10)
        pdf.set_xy(10, current_y_nama)
        pdf.cell(90, 6, nama_pasien, align='C')
        pdf.set_xy(110, current_y_nama)
        pdf.cell(90, 6, "(.......................................)", align='C')
        
    pdf.output(output_filename)
    print(f"\n[+] Sukses! Laporan PDF berhasil disimpan: {output_filename}")
=======
import os
from fpdf import FPDF

# 1. CLASS DEFINITION
class MedWatchPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'REKAM MEDIS PASIEN - MEDWATCH', align='C', ln=True)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', align='C')

# 2. FUNGSI PEMBANTU UNTUK MENCETAK BAGIAN (SECTION)
def tulis_section(pdf, judul_section, data_content):
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 8, f" {judul_section}", ln=True, fill=True)
    pdf.ln(2)
    
    # JIKA DATA ADALAH DICTIONARY (Contoh: Identitas)
    if isinstance(data_content, dict):
        for key, value in data_content.items():
            current_y = pdf.get_y()
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_xy(10, current_y)
            pdf.cell(50, 6, f"{key}")
            
            pdf.set_font('helvetica', '', 10)
            pdf.set_xy(60, current_y)
            pdf.multi_cell(130, 6, f": {value}")
            
    # JIKA DATA ADALAH STRING (Contoh: Anamnesis / Pemeriksaan)
    elif isinstance(data_content, str):
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, data_content)
    
    pdf.ln(4)

# 3. FUNGSI UTAMA EKSPOR (Dengan parameter opsional 'id_pasien_terpilih')
def buat_laporan_pdf(data_pasien, output_filename="Laporan_MedWatch.pdf", id_pasien_terpilih=None):
    pdf = MedWatchPDF() 
    
    # === PROSES FILTERING ===
    data_yang_akan_dicetak = []
    
    if id_pasien_terpilih:
        # Cari pasien berdasarkan ID
        for pasien in data_pasien:
            # Mengambil ID dari dictionary identitas yang sudah di-mapping
            id_sekarang = pasien.get("identitas", {}).get("ID Pasien")
            
            if str(id_sekarang) == str(id_pasien_terpilih):
                data_yang_akan_dicetak.append(pasien)
                break # Hentikan pencarian jika sudah ketemu (asumsi ID unik)
                
        if not data_yang_akan_dicetak:
            print(f"[!] Pasien dengan ID '{id_pasien_terpilih}' tidak ditemukan.")
            return # Keluar dari fungsi jika data tidak ada
    else:
        # Jika id_pasien_terpilih kosong, cetak semua data
        data_yang_akan_dicetak = data_pasien
    # ========================

    # Buat halaman PDF untuk data yang sudah disaring
    for pasien in data_yang_akan_dicetak:
        pdf.add_page()
        
        tulis_section(pdf, "1. IDENTITAS PASIEN", pasien.get("identitas", {}))
        tulis_section(pdf, "2. ANAMNESIS (SUBJEKTIF)", pasien.get("anamnesis", "-"))
        tulis_section(pdf, "3. PEMERIKSAAN FISIK (OBJEKTIF)", pasien.get("pemeriksaan", "-"))
        tulis_section(pdf, "4. DIAGNOSIS DAN TINDAKAN", pasien.get("diagnosis_tindakan", "-"))
        
        # --- Bagian Tanda Tangan ---
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 10)
        current_y_ttd = pdf.get_y()
        
        pdf.set_xy(10, current_y_ttd)
        pdf.cell(90, 6, "Pasien / Keluarga Pasien,", align='C')
        pdf.set_xy(110, current_y_ttd)
        pdf.cell(90, 6, "Bidan / Dokter Pemeriksa,", align='C')
        
        pdf.ln(20)
        current_y_nama = pdf.get_y()
        nama_pasien = pasien.get("identitas", {}).get("Nama Pasien", "(.......................................)")
        
        pdf.set_font('helvetica', 'U', 10)
        pdf.set_xy(10, current_y_nama)
        pdf.cell(90, 6, nama_pasien, align='C')
        pdf.set_xy(110, current_y_nama)
        pdf.cell(90, 6, "(.......................................)", align='C')
        
    pdf.output(output_filename)
    print(f"\n[+] Sukses! Laporan PDF berhasil disimpan: {output_filename}")
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
