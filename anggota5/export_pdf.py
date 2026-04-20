from fpdf import FPDF

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

def tulis_section(pdf, judul_section, data_content):
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 8, f" {judul_section}", ln=True, fill=True)
    pdf.ln(2)
    
    if isinstance(data_content, dict):
        for key, value in data_content.items():
            current_y = pdf.get_y()
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_xy(10, current_y)
            pdf.cell(50, 6, f"{key}")
            
            pdf.set_font('helvetica', '', 10)
            pdf.set_xy(60, current_y)
            pdf.multi_cell(130, 6, f": {value}")
    elif isinstance(data_content, str):
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 6, data_content)
    pdf.ln(4)

def buat_laporan_pdf(data_pasien, output_filename="Laporan_MedWatch.pdf"):
    pdf = MedWatchPDF()
    for pasien in data_pasien:
        pdf.add_page()
        tulis_section(pdf, "1. IDENTITAS PASIEN", pasien.get("identitas", {}))
        tulis_section(pdf, "2. ANAMNESIS (SUBJEKTIF)", pasien.get("anamnesis", "-"))
        tulis_section(pdf, "3. PEMERIKSAAN FISIK (OBJEKTIF)", pasien.get("pemeriksaan", "-"))
        tulis_section(pdf, "4. DIAGNOSIS DAN TINDAKAN", pasien.get("diagnosis_tindakan", "-"))
        
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