# export_pdf.py

from fpdf import FPDF

class MedWatchPDF(FPDF):
    def header(self):
        # Kop Surat Rekam Medis
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'REKAM MEDIS PASIEN - MEDWATCH', align='C', ln=True)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', align='C')

def tulis_section(pdf, judul_section, data_dict):
    """
    Fungsi bantuan untuk menulis setiap sub-bab ke dalam PDF dengan kordinat absolut.
    """
    # Header Section (Blok abu-abu)
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 8, f" {judul_section}", ln=True, fill=True)
    pdf.ln(2)
    
    # Isi Section
    for key, value in data_dict.items():
        # 1. Simpan posisi vertikal (Y) saat ini
        current_y = pdf.get_y()
        
        # 2. Cetak Kunci (Key) di koordinat X = 10 (margin kiri default)
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_xy(10, current_y)
        pdf.cell(60, 6, f"{key}")
        
        # 3. Cetak Nilai (Value) di koordinat X = 70 (10 margin + 60 lebar key)
        pdf.set_font('helvetica', '', 10)
        pdf.set_xy(70, current_y)
        pdf.multi_cell(130, 6, f": {value}")
        
        # multi_cell otomatis akan menurunkan koordinat Y ke bawah setelah selesai.
        # Jadi baris selanjutnya aman!
    
    pdf.ln(4) # Jarak antar section

def buat_laporan_pdf(data_pasien, output_filename="Laporan_MedWatch.pdf"):
    """
    Membuat dokumen PDF tanpa menyertakan gambar grafik.
    Satu halaman didedikasikan untuk satu pasien.
    """
    pdf = MedWatchPDF()
    
    for pasien in data_pasien:
        pdf.add_page()
        
        tulis_section(pdf, "1. IDENTITAS PASIEN", pasien["identitas"])
        tulis_section(pdf, "2. ANAMNESIS (RIWAYAT PENYAKIT)", pasien["anamnesis"])
        tulis_section(pdf, "3. PEMERIKSAAN FISIK DAN PENUNJANG", pasien["pemeriksaan"])
        tulis_section(pdf, "4. DIAGNOSIS DAN TINDAKAN", pasien["diagnosis_tindakan"])
        
        # Tanda tangan & Penanggung jawab
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 10)
        
        # Gunakan get_y() untuk menyamakan tinggi kolom tanda tangan
        current_y_ttd = pdf.get_y()
        
        pdf.set_xy(10, current_y_ttd)
        pdf.cell(95, 6, "Nama Penanggung Jawab Pasien,", align='C')
        
        pdf.set_xy(105, current_y_ttd)
        pdf.cell(95, 6, "Nama Dokter Pemeriksa,", align='C')
        
        pdf.ln(20) # Jarak kosong untuk coretan tanda tangan
        
        current_y_nama = pdf.get_y()
        
        pdf.set_font('helvetica', 'U', 10)
        pdf.set_xy(10, current_y_nama)
        pdf.cell(95, 6, pasien["penanggung_jawab"]["Nama Penanggung Jawab"], align='C')
        
        pdf.set_xy(105, current_y_nama)
        pdf.cell(95, 6, pasien["penanggung_jawab"]["Nama Dokter Pemeriksa"], align='C')
        
    pdf.output(output_filename)