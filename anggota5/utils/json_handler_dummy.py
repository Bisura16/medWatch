# utils/json_handler_dummy.py

def get_dummy_patient_data():
    return [
        {
            "identitas": {
                "Nama Lengkap": "Budi Santoso",
                "Nomor Rekam Medis (RM)": "RM-2026-04-001",
                "Tanggal Lahir/Usia": "15 Mei 1980 / 45 Tahun",
                "Jenis Kelamin": "Laki-laki",
                "Alamat & Kontak": "Jl. Gegerkalong Hilir No. 47 / 081234567890"
            },
            "anamnesis": {
                "Keluhan Utama": "Sakit kepala hebat dan dada terasa berat sejak 2 hari yang lalu.",
                "Riwayat Penyakit Sekarang": "Nyeri berdenyut di bagian tengkuk, disertai mual tapi tidak muntah.",
                "Riwayat Penyakit Dahulu": "Memiliki riwayat hipertensi sejak 5 tahun lalu, jarang kontrol rutin.",
                "Riwayat Alergi": "Tidak ada alergi obat atau makanan."
            },
            "pemeriksaan": {
                "Tanda Vital": "TD: 160/100 mmHg, Nadi: 88x/mnt, Suhu: 36.5°C, RR: 20x/mnt",
                "Hasil Pemeriksaan Fisik": "Pasien tampak menahan sakit, kesadaran compos mentis.",
                "Hasil Lab/Radiologi": "Kolesterol total: 240 mg/dL, Gula Darah Sewaktu: 110 mg/dL"
            },
            "diagnosis_tindakan": {
                "Diagnosis Medis": "Hipertensi Emergency Ringan (I10)",
                "Tindakan/Pengobatan": "Pemberian Amlodipine 10mg (1x1), Paracetamol 500mg (kalo perlu). Edukasi diet rendah garam.",
                "Rencana Tindak Lanjut": "Kontrol ulang 3 hari ke depan atau segera ke IGD jika nyeri dada memburuk."
            },
            "penanggung_jawab": {
                "Nama Dokter Pemeriksa": "dr. Andi Wijaya",
                "Nama Penanggung Jawab": "Siti Aminah (Istri)"
            }
        }
    ]

def get_dummy_drug_data():
    # Tetap sama untuk kebutuhan fitur visualisasi
    return {
        "obat": ["Amlodipine", "Captopril", "Lisinopril"],
        "efek_samping_ringan": [12, 15, 8],
        "efek_samping_sedang": [4, 7, 3],
        "efek_samping_berat": [1, 2, 0]
    }
