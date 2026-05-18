# NewestVisualization

Modul visualisasi tambahan MedWatch berbasis data scraping openFDA.
Folder ini bersifat **additive**; berkas asli milik Alia di
`anggota3/` (BacaData.py, TampilGrafik.py, dst) tidak diubah sama sekali.

## Atribusi

| Peran | Nama | NIM | Modul |
|---|---|---|---|
| Penulis dokumenter | **Alia Ardani** | **251524035** | anggota3 - System Analyst (visualisasi) |
| Sumber data scraping | Ghaisan Khoirul Badruzaman | 251524048 | anggota1 - Project Leader (T1-DATA) |

Git commit dilakukan oleh identitas Ghaisan (Project Leader) sesuai aturan
mission. Atribusi dokumenter tetap pada Alia Ardani sebagai pemilik
folder `anggota3/`.

## Sumber data

Modul ini membaca dua berkas JSON hasil scraping di repo `anggota1/data/`:

| Berkas | Skema | Sumber |
|---|---|---|
| `anggota1/data/drug_safety_data.json` | `{drug_name, category, side_effects[], severity_level, warnings, source_url}` | openFDA Adverse Events (FAERS) |
| `anggota1/data/drug_recalls.json` | `{product_name, reason, recall_date, severity_class, company}` | openFDA FDA Enforcement Reports |

Pemuat tunggal `data_loader.py` membungkus pembacaan kedua file dan
menjaga toleransi terhadap kondisi berkas tidak ditemukan atau corrupt.
Modul ini **tidak** meng-import paket `anggota1` atau `anggota4`.

## Palet warna

Konstanta HEX di `palette.py` direplikasi langsung dari
`anggota3/TampilGrafik.py` agar gaya visual selaras dengan modul Alia
yang sudah ada:

- `#A78BFA` ungu muda (anak-anak)
- `#7C3AED` ungu utama brand (dewasa)
- `#1E1B4B` slate gelap (lansia)
- `#3B82F6` biru (laki-laki)
- `#EC4899` pink (perempuan)
- Palet ungu sekuensial `#EDE9FE -> #4C1D95` untuk gradient
- Warna keparahan risk-matrix: ringan `#A6D96A`, sedang `#FDAE61`,
  serius `#D7191C`, tidak diketahui `#9CA3AF` (selaras dengan keputusan
  T1-HEATMAP)

## Daftar visualisasi

| Skrip | Output PNG | Apa yang ditampilkan |
|---|---|---|
| `viz_top_obat_efek_samping.py` | `output/viz_top_obat_efek_samping.png` | Top 15 obat dengan beban laporan FAERS terbesar; warna batang per severity. |
| `viz_distribusi_keparahan.py` | `output/viz_distribusi_keparahan.png` | Distribusi jumlah obat per kategori (Analgesik, Antibiotik, dll) dipecah segmen severity. |
| `viz_recall_class_per_tahun.py` | `output/viz_recall_class_per_tahun.png` | Stacked bar jumlah recall FDA per tahun, dipecah Class I / II / III. |
| `viz_perusahaan_recall_top.py` | `output/viz_perusahaan_recall_top.png` | Top 20 perusahaan farmasi dengan recall terbanyak; gradient ungu MedWatch. |
| `viz_heatmap_obat_efek.py` | `output/viz_heatmap_obat_efek.png` | Heatmap obat x kategori efek samping; skala kontinu YlOrRd, sumbu disortir menurun. |

Setiap skrip menulis PNG dengan lebar minimal 1600 px, dpi 200, dan
`bbox_inches="tight"`. Setiap chart memiliki judul, label sumbu dengan
satuan, legend yang menjelaskan encoding warna, plus caption sumber data
dalam Bahasa Indonesia.

## Cara meregenerasi

Dari akar repo `medWatch/` dengan virtual environment yang punya
matplotlib + numpy (Python 3.13 ada di `.venv/`):

```bash
# Semua chart sekaligus
.venv/bin/python -m anggota3.NewestVisualization.generate_all

# Per chart (boleh)
.venv/bin/python anggota3/NewestVisualization/viz_top_obat_efek_samping.py
.venv/bin/python anggota3/NewestVisualization/viz_distribusi_keparahan.py
.venv/bin/python anggota3/NewestVisualization/viz_recall_class_per_tahun.py
.venv/bin/python anggota3/NewestVisualization/viz_perusahaan_recall_top.py
.venv/bin/python anggota3/NewestVisualization/viz_heatmap_obat_efek.py
```

Hasil PNG disimpan ke `anggota3/NewestVisualization/output/`.

## Catatan integritas

- Folder ini hanya menambahkan berkas baru di bawah
  `anggota3/NewestVisualization/`. Tidak ada perubahan, hapus, atau edit
  pada berkas lain milik Alia.
- Tidak menggunakan em dash dan tidak menggunakan emoji di kode, output,
  README, ataupun caption chart.
- Semua label dan caption ditulis dalam Bahasa Indonesia sesuai pedoman
  i18n MedWatch.
