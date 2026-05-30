# ADR-0005: anggota3/NewestVisualization/ sebagai modul aditif untuk Alia

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Project Iterasi 1 mensyaratkan visualisasi tambahan berbasis data
scraping openFDA (1850 entri efek samping + 6000 recall). Modul
existing milik Alia (`anggota3/BacaData.py`, `anggota3/TampilGrafik.py`,
`anggota3/PerbandinganObat.py`, plus skrip grafik per topik) sudah
selesai dan diuji terhadap data lama. Mengedit file-file ini akan
melanggar mandat read-only untuk modul anggota dan dapat menabrak QA
yang sudah dilakukan Alia.

## Decision Drivers

- konvensi proyek menyatakan modul `anggota1/`..`anggota5/` read-only,
  dengan pengecualian satu kali Iterasi 1 anggota5 yang tidak relevan di
  sini.
- Visualisasi baru harus terlihat sebagai pekerjaan Alia (peran
  System Analyst) untuk menjaga peran kontribusi tim tetap akurat.
- Output skrip harus selaras secara visual dengan palet dan style yang
  sudah dipakai modul `anggota3/` agar tidak tampak seperti project
  terpisah.

## Considered Options

- Edit file existing milik Alia untuk menambah visualisasi baru.
- Buat folder sibling baru `anggota3/NewestVisualization/` yang berisi
  data loader sendiri, palet sendiri, dan skrip per chart.
- Letakkan visualisasi baru di repo frontend (Recharts/D3).

## Decision Outcome

Chosen option: "Folder sibling aditif `anggota3/NewestVisualization/`",
karena memuaskan kontrak read-only, menjaga atribusi kepemilikan Alia,
dan memberikan deliverable berupa PNG yang dapat disertakan ke laporan
dosen tanpa bergantung pada layer frontend.

### Consequences

- Good: Tidak ada file Alia yang berubah; QA terhadap modul lama tetap
  valid.
- Good: Atribusi tetap jelas: README folder menyatakan secara
  eksplisit bahwa Alia Ardani (251524035, System Analyst) adalah
  penulis dokumenter, sementara data scraping bersumber dari Ghaisan
  (anggota1 / T1-DATA).
- Good: Skrip dapat dijalankan offline (matplotlib + numpy) dan
  menghasilkan PNG yang langsung tertanam ke laporan/README.
- Good: Palet warna disalin verbatim dari `anggota3/TampilGrafik.py`
  agar visualisasi baru terlihat menyatu dengan visualisasi lama.
- Bad: Ada duplikasi konstanta palet di dua tempat (`anggota3/TampilGrafik.py`
  dan `anggota3/NewestVisualization/palette.py`); harus disinkronkan
  manual jika Alia mengubah palet utama.
- Bad: Pengguna yang mencari visualisasi MedWatch harus tahu ada dua
  folder; sebagian risiko ini dikurangi via README utama dan As-Built
  (Iterasi 2 D11).

### Confirmation

- Atribusi: `anggota3/NewestVisualization/README.md:9-16` mendaftarkan
  Alia Ardani (251524035) sebagai penulis dokumenter dan menyatakan
  "Git commit dilakukan oleh identitas Ghaisan (Project Leader)
  sesuai aturan project. Atribusi dokumenter tetap pada Alia Ardani."
- Daftar visualisasi: `anggota3/NewestVisualization/README.md:48-56`
  mendaftarkan lima skrip (`viz_top_obat_efek_samping.py`,
  `viz_distribusi_keparahan.py`, `viz_recall_class_per_tahun.py`,
  `viz_perusahaan_recall_top.py`, `viz_heatmap_obat_efek.py`) dengan
  output PNG di subfolder `output/`.
- Catatan integritas: `anggota3/NewestVisualization/README.md:82-90`
  menyatakan "Folder ini hanya menambahkan berkas baru di bawah
  `anggota3/NewestVisualization/`. Tidak ada perubahan, hapus, atau
  edit pada berkas lain milik Alia."
- Palet aligned: `anggota3/NewestVisualization/README.md:36-46`
  mereplikasi konstanta HEX `#A78BFA`, `#7C3AED`, `#1E1B4B`, `#3B82F6`,
  `#EC4899` plus palet ungu sekuensial sesuai gaya modul Alia.
- Sumber data: `anggota3/NewestVisualization/README.md:20-30` membaca
  `anggota1/data/drug_safety_data.json` dan
  `anggota1/data/drug_recalls.json` tanpa meng-import paket anggota1
  atau anggota4.

## More Information

- ADR-0004 menjelaskan asal data openFDA yang dikonsumsi modul ini.
- ADR-0006 menjelaskan keputusan warna heatmap yang juga dipakai oleh
  `viz_heatmap_obat_efek.py`.
