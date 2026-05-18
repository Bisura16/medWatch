---
title: Product Requirements Document (PRD) MedWatch
version: 1.0
owner: Kelompok B5, D4 Teknik Informatika Politeknik Negeri Bandung
date: 18-05-2026
status: AS-BUILT setelah Wave 1 (fix B01-B11, akuisisi data openFDA, modul NewestVisualization)
audience: Dosen pengampu Proyek 1 PPLD, tim kelompok B5, reviewer eksternal
---

# Product Requirements Document MedWatch

## 0. Header dan Metadata

- Nama produk: MedWatch, Sistem Monitoring Keamanan Obat dan Manajemen Klinik Faskes 1.
- Mata kuliah: Proyek 1 Pengembangan Perangkat Lunak Desktop.
- Institusi: D4 Teknik Informatika, Politeknik Negeri Bandung (POLBAN), Kelas 1B-D4.
- Tahun akademik dan semester: TA 2025/2026, Semester 2.
- Kelompok: B5.
- Tanggal dokumen: 18 Mei 2026.
- Tanggal penyerahan dosen: 25 Mei 2026.
- Versi dokumen: 1.0 (AS-BUILT pasca Wave 1).

### Tim penulis

| Nama | NIM | Peran utama | Modul Python |
|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader / Team Coordinator | `anggota1` (scraping dan akuisisi openFDA) |
| Bimo Surya Anggara | 251524040 | Quality Assurance | `anggota2` (CRUD pasien SOAP) |
| Alia Ardani | 251524035 | System Analyst | `anggota3` (visualisasi) |
| Muhammad Iqbal | 251524057 | Programmer | `anggota4` (drug safety check) |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | `anggota5` (PDF export dan autentikasi) |

### Dosen pendamping

- Aprianti Nanda Sari (Project Manager mata kuliah)
- Ade Chandra Nugraha
- Ardhian Ekawijana

### Dokumen terkait (cross-link)

- `docs/SRS.md` (Software Requirements Specification, IEEE 830-1998 dan ISO/IEC/IEEE 29148:2018).
- `docs/SDD.md` (Software Design Description, IEEE 1016-2009).
- `docs/API.md` (kontrak HTTP REST per endpoint).
- `docs/DATA-DICTIONARY.md` (kamus data lintas modul).
- `docs/INSTALL.md` (panduan instalasi, deploy, dan dev).
- `docs/SECURITY.md` (model ancaman OWASP Top 10 dan STRIDE).
- `docs/AS-BUILT.md` (sintesis akhir 19-section ISO/IEC/IEEE 15289:2019).
- `docs/USER-MANUAL.md` (panduan pengguna ISO/IEC/IEEE 26514).
- `docs/adr/` (ADR set dengan template MADR).
- `docs/diagrams/` (sumber Mermaid/PlantUML dan PNG yang dirender, mengacu model C4).

---

## 1. Ringkasan Eksekutif

MedWatch adalah sistem desktop modular untuk bidan di Fasilitas Kesehatan Tingkat 1 (Faskes 1, contohnya puskesmas dan klinik kecil) yang menggabungkan lima kapabilitas operasional: pencatatan rekam medis pasien dengan format SOAP, pengecekan keamanan dan interaksi obat, akuisisi data keamanan obat dari sumber publik (openFDA), visualisasi tren kunjungan dan efek samping, serta ekspor laporan PDF. Implementasi modular dikerjakan oleh lima anggota Kelompok B5 di folder `anggota1/` sampai `anggota5/`, lalu diintegrasikan melalui lapisan REST API Flask di `api/` dan lapisan presentasi web Next.js 15 yang berfungsi sebagai showcase. Pasca Wave 1 (sebelas perbaikan defek B01-B11, modul visualisasi tambahan `anggota3/NewestVisualization/`, akuisisi data nyata openFDA dengan 74 rekord obat plus 6000 rekord recall), MedWatch siap diserahkan kepada dosen pada 25 Mei 2026 sebagai realisasi end-to-end dari spesifikasi awal mata kuliah.

---

## 2. Latar Belakang dan Masalah

### 2.1 Konteks pengguna

Bidan di Faskes 1 (puskesmas, polindes, klinik bersalin kecil) menjalankan beban kerja sehari-hari yang mencakup pemeriksaan kehamilan, KB, imunisasi, dan keluhan umum. Pencatatan masih sering manual atau setengah-digital dengan buku kohort, kartu pasien, dan spreadsheet ad-hoc. Sistem terintegrasi yang berbasis SOAP (Subjective, Objective, Assessment, Plan) tersedia di rumah sakit besar, namun jarang menjangkau Faskes 1 secara terjangkau.

### 2.2 Masalah konkret yang dialami

1. Pencatatan rekam medis berbasis kertas atau formulir Excel ad-hoc tidak konsisten, sulit di-rekap, dan rentan hilang. Bidan kesulitan melihat tren kunjungan, distribusi keluhan, atau riwayat per pasien.
2. Saat memberikan resep, bidan tidak punya alat cepat untuk mengecek interaksi obat berdasarkan basis data lokal Indonesia, padahal kombinasi obat (mis. obat hipertensi dengan NSAID) berisiko serius. Sumber daring berbahasa Inggris dan tidak selalu relevan untuk konteks formularium lokal.
3. Tidak ada cara cepat memantau data keselamatan obat (efek samping terlapor, recall) dari sumber otoritatif. Sumber komersial (mis. `drugs.com`) tidak menyediakan API publik dan secara aktif memblokir scraping otomatis melalui Akamai (HTTP 403, lihat ADR-004).
4. Saat dosen atau kepala puskesmas meminta laporan bulanan, bidan harus merangkum ulang manual dari catatan SOAP. Tidak ada generator laporan PDF satu-klik.
5. Visualisasi tren kunjungan, distribusi keluhan, dan distribusi keparahan efek samping memerlukan keahlian Excel/spreadsheet yang tidak setiap bidan miliki.

### 2.3 Mengapa membangun MedWatch sekarang

Mata kuliah Proyek 1 PPLD memberi kerangka akademik untuk membangun aplikasi desktop modular Python yang dapat menjawab kelima masalah di atas dalam ruang lingkup proyek mahasiswa. Selain memenuhi capaian pembelajaran (CPMK pemrograman terstruktur, modularisasi, integrasi), MedWatch juga menjadi prototipe awal yang berpotensi dilanjutkan menjadi produk operasional bagi Faskes 1.

---

## 3. Pengguna dan Persona

MedWatch melayani tiga persona dengan kebutuhan yang berbeda. Nomenklatur peran yang dipakai oleh kode adalah `tenaga_kesehatan`, `masyarakat`, dan `admin` (lihat aturan kanonik di `.md` bagian "Role nomenclature"). Label antarmuka dapat menampilkan "Bidan" atau "Pasien" agar ramah pengguna.

### 3.1 Persona 1: Tenaga Kesehatan (bidan Faskes 1)

- Identitas: bidan koordinator atau bidan pelaksana di puskesmas / polindes / klinik bersalin kecil.
- Konteks teknis: PC desktop / laptop sederhana dengan Windows atau Linux, koneksi internet tidak selalu stabil, jam kerja shift, beban administratif tinggi.
- Tujuan utama:
  1. Mencatat kunjungan pasien dengan format SOAP yang konsisten dan terstruktur (skema kanonik di `api/routes/patient_routes.py:1-30`, ID pasien `P001..P999` sesuai konvensi anggota2).
  2. Melakukan cek interaksi obat sebelum menulis resep, dengan keluaran yang menjelaskan obat aktif pasien dari rekam SOAP terkini (lihat fitur `pasien_active_meds` di `api/routes/safety_routes.py:43-62`).
  3. Mencetak laporan rekam medis pasien sebagai PDF saat dimintai dosen pembimbing atau saat rujukan.
- Pain points: input numerik (BB, TB, LILA, tekanan darah) sebelumnya menerima huruf tanpa validasi (defek B03, kini divalidasi server-side di `api/routes/patient_routes.py:56-99`); daftar pasien tampil dari terlama (B07 sebelumnya, kini sudah descending di `api/routes/patient_routes.py:135-146`).

### 3.2 Persona 2: Masyarakat (warga umum)

- Identitas: warga (atau pasien) yang ingin akses informasi keamanan obat tanpa perlu pelatihan klinis.
- Konteks teknis: pengakses web melalui browser di laptop atau ponsel.
- Tujuan utama:
  1. Mencari informasi profil keamanan obat (efek samping, kontraindikasi, peringatan kehamilan) lewat `frontend /drug-search` yang memanggil `GET /api/drugs/search` (lihat `api/routes/drug_routes.py:31-40`).
  2. Memeriksa apakah dua obat memiliki potensi interaksi melalui `frontend /safety-checker` yang memanggil `POST /api/safety/check` (lihat `api/routes/safety_routes.py:16-72`).
- Pain points: tidak semua sumber daring berbahasa Indonesia; MedWatch menampilkan label dan peringatan dalam Bahasa Indonesia formal.

### 3.3 Persona 3: Admin (manajer sistem)

- Identitas: admin yang mewakili kepala puskesmas atau koordinator tim untuk pengelolaan akun pengguna dan trigger akuisisi data obat.
- Konteks teknis: web dashboard pada `frontend /admin/dashboard`, memerlukan login.
- Tujuan utama:
  1. Memantau metrik sistem nyata (pengguna aktif per peran, jumlah pasien, jumlah obat di katalog, uptime proses) yang diserve oleh `GET /api/admin/system-stats` di `api/routes/admin_routes.py:106-127`.
  2. Memicu sinkronisasi katalog obat (mocked scraper, dengan path produksi mengarah ke modul akuisisi openFDA real) lewat `POST /api/admin/scrape` di `api/routes/admin_routes.py:21-38`.
  3. Mengelola akun pengguna melalui `GET/POST/DELETE /api/admin/users` di `api/routes/admin_routes.py:41-103`.
- Catatan PRD: peran `admin` adalah ekstensi presentasi di luar PRD asli mata kuliah yang menyatakan autentikasi sebagai out-of-scope (`.md`, bagian "PRD scope tension awareness"). Admin di MedWatch hadir sebagai supplementary demo, bukan sebagai pengganti modul desktop CustomTkinter anggota1-5.

---

## 4. Ruang Lingkup dan Batasan

### 4.1 In-scope (fitur inti MVP)

| ID | Fitur | Modul Owner | Endpoint backend / Rute frontend |
|---|---|---|---|
| FR-001 | Autentikasi pengguna multi-peran (tenaga_kesehatan, masyarakat, admin) | anggota5 + `api/` | `POST /api/auth/login` (`api/routes/auth_routes.py:13-40`), `GET /api/auth/me` (`api/routes/auth_routes.py:43-46`), `POST /api/auth/logout` (`api/routes/auth_routes.py:49-51`), frontend `src/app/login/` |
| FR-002 | CRUD pasien SOAP dengan validasi rentang medis dan urutan terbaru di atas | anggota2 + `api/` | `GET/POST /api/patients`, `GET/PUT/DELETE /api/patients/<id>` (`api/routes/patient_routes.py:135-218`), frontend `src/app/pasien/`, `src/app/patients/` |
| FR-003 | Pencarian dan profil keamanan obat | anggota4 + `api/` | `GET /api/drugs`, `GET /api/drugs/search`, `GET /api/drugs/<nama>` (`api/routes/drug_routes.py:19-51`), frontend `src/app/drug-search/`, `src/app/drug-comparison/` |
| FR-004 | Cek interaksi obat dengan konteks pasien dan tampilan obat aktif pasien | anggota4 + `api/` | `POST /api/safety/check` (`api/routes/safety_routes.py:16-72`), frontend `src/app/safety-checker/` |
| FR-005 | Visualisasi tren kunjungan, distribusi keluhan, top efek samping, heatmap | anggota3 + `api/` | `GET /api/visualizations/kunjungan-trend`, `keluhan-distribution`, `top-efek-samping`, `heatmap-efek` (`api/routes/visualization_routes.py:54-138`), frontend `src/app/visualization/`, `src/app/heatmap/` |
| FR-006 | Ekspor PDF rekam medis, laporan bulanan, efek samping, inventaris obat | anggota5 + `api/` | `POST /api/pdf/generate-rekam-medis`, `generate-laporan-bulanan`, `generate-efek-samping`, `generate-inventaris` (`api/routes/pdf_routes.py:169-511`), frontend `src/app/export-pdf/`, `src/app/export/` |
| FR-007 | Akuisisi data keamanan obat dari sumber otoritatif openFDA | anggota1 + `api/` | Modul `anggota1/openfda/`, output `anggota1/data/drug_safety_data.json` (74 rekord) dan `anggota1/data/drug_recalls.json` (6000 rekord) |
| FR-008 | Dashboard admin dengan metrik nyata (uptime proses, jumlah pengguna per peran, jumlah pasien, jumlah obat) dan CTA scraper | `api/` + frontend | `GET /api/admin/system-stats` (`api/routes/admin_routes.py:106-127`), frontend `src/app/admin/dashboard/` |
| FR-009 | Manajemen pengguna oleh admin (list, create, delete) | `api/` + frontend | `GET/POST /api/admin/users`, `DELETE /api/admin/users/<username>` (`api/routes/admin_routes.py:41-103`), frontend `src/app/admin/users/` |
| FR-010 | Visualisasi baru berbasis data openFDA (5 chart) di `anggota3/NewestVisualization/` | anggota3 | Script Python: `viz_top_obat_efek_samping.py`, `viz_distribusi_keparahan.py`, `viz_recall_class_per_tahun.py`, `viz_perusahaan_recall_top.py`, `viz_heatmap_obat_efek.py` |

### 4.2 Out-of-scope (tidak termasuk MVP 25 Mei 2026)

1. Custom domain (gunakan default `.vercel.app` dan `.run.app`).
2. Layanan berbayar (Auth0, SendGrid, Sentry paid tier, Cloudflare paid).
3. Sinkronisasi real-time multi-Faskes (mis. WebSocket, replikasi kluster).
4. Aplikasi mobile native (iOS / Android).
5. Modul keuangan (BPJS klaim, billing).
6. Integrasi dengan sistem rekam medis nasional (SatuSehat, integrasi PCare).
7. Notifikasi push, email otomatis ke pasien.
8. Bypass mekanisme anti-bot `drugs.com` (lihat ADR-004 untuk pivot ke openFDA).

### 4.3 Catatan tegangan dengan PRD asli

PRD asli mata kuliah (`MedWatch_PRD.pdf`) menyatakan dua butir berikut sebagai out-of-scope: "Fitur login atau multi-user dengan autentikasi" dan "Deployment ke platform web atau mobile". Misi integrasi mata kuliah menambahkan keduanya sebagai supplementary demo (lihat `.md` bagian "PRD scope tension awareness"). Naratif kepada dosen: aplikasi desktop modular CustomTkinter anggota1-5 tetap submission utama; lapisan REST Flask (`api/`) di Cloud Run plus Next.js 15 di Vercel adalah lapisan presentasi yang menyajikan fitur yang sama dalam form factor web demo. PRD ini mendokumentasikan AS-BUILT termasuk supplementary auth, tanpa memodifikasi PRD asli secara retroaktif.

### 4.4 Asumsi

1. Penggunaan tunggal-Faskes: setiap instalasi MedWatch melayani satu klinik / puskesmas. Multi-tenant tidak didukung.
2. Bahasa pengguna: Bahasa Indonesia formal untuk seluruh UI dan dokumentasi.
3. Lokal Indonesia: tanggal dd-MM-yyyy, Rupiah saat menampilkan biaya (bila ada), zona waktu WIB.
4. Resource gratis: deploy demo memanfaatkan free tier GCP (`medwatch-polban-2026`) dan Vercel Hobby. Tidak ada layanan berbayar.

---

## 5. Sasaran dan Tujuan

| Kode | Sasaran | Pernyataan singkat |
|---|---|---|
| G-01 | Konsistensi rekam medis | Bidan dapat mencatat kunjungan pasien dalam format SOAP yang divalidasi server-side untuk rentang medis. |
| G-02 | Keselamatan farmakologi | Bidan dapat memeriksa interaksi obat sebelum meresepkan, dengan konteks obat aktif pasien dari rekam SOAP terakhir. |
| G-03 | Sumber data otoritatif | Data keamanan obat (efek samping, recall) bersumber dari openFDA, tidak fabrikatif, dan reproducible. |
| G-04 | Transparansi metrik | Dashboard admin hanya menampilkan angka yang dihitung dari data nyata (jumlah pengguna, pasien, obat, uptime proses), tanpa nilai placeholder. |
| G-05 | Output siap dosen | Laporan PDF (rekam medis, laporan bulanan, efek samping, inventaris) dapat diunduh dalam satu klik untuk presentasi. |
| G-06 | Pemahaman cepat tren | Visualisasi tren kunjungan, distribusi keluhan, top efek samping, dan heatmap dapat dilihat tanpa keahlian spreadsheet. |
| G-07 | Pemeliharaan aman | Tidak ada nilai kredensial yang masuk ke repo; resource name (project, bucket, secret) yang publik di dokumen tetap aman dibagikan ke dosen. |

---

## 6. Fitur Utama (Tabel FR-Level)

Tabel ini ringkasan; rincian acceptance criteria dan kontrak data ada di `docs/SRS.md`, `docs/API.md`, dan `docs/DATA-DICTIONARY.md`.

| ID | Fitur | Persona target | Modul Python / Folder | Endpoint utama |
|---|---|---|---|---|
| FR-001 | Autentikasi login multi-peran dengan JWT httpOnly cookie | tenaga_kesehatan, masyarakat, admin | `anggota5/auth.py` + `api/auth.py` | `POST /api/auth/login` (`api/routes/auth_routes.py:13-40`) |
| FR-002 | CRUD pasien SOAP, validasi rentang medis, ID `P001..P999`, urutan tanggal terbaru di atas | tenaga_kesehatan, admin | `anggota2/pasien_helper.py` + `api/routes/patient_routes.py` | `GET/POST/PUT/DELETE /api/patients` |
| FR-003 | Katalog dan profil obat (cari, list, detail, perbandingan) | masyarakat, tenaga_kesehatan | `anggota4/data_loader.py`, `anggota4/pencarian_obat.py` | `GET /api/drugs`, `GET /api/drugs/search`, `GET /api/drugs/<nama>` |
| FR-004 | Cek interaksi obat dengan opsi konteks pasien dan keluaran `pasien_active_meds` | tenaga_kesehatan | `anggota4/safety_checker.py` + `api/helpers.py:parse_resep_to_meds` | `POST /api/safety/check` (`api/routes/safety_routes.py:16-72`) |
| FR-005 | Visualisasi (4 endpoint) | tenaga_kesehatan, admin | `api/routes/visualization_routes.py` + `anggota4/data_loader.py` | `GET /api/visualizations/...` |
| FR-006 | Ekspor PDF (4 jenis: rekam medis, laporan bulanan, efek samping, inventaris) | tenaga_kesehatan, admin | `anggota5/export_pdf.py` (rekam medis dan bulanan), `api/routes/pdf_routes.py` (efek samping, inventaris) | `POST /api/pdf/generate-...` |
| FR-007 | Akuisisi data nyata openFDA (`drug/event` dan `drug/enforcement`) | (pipeline) | `anggota1/openfda/` | CLI `python -m anggota1.openfda.fetch` |
| FR-008 | Dashboard admin metrik nyata dengan CTA scraper | admin | `api/routes/admin_routes.py` | `GET /api/admin/system-stats` (`api/routes/admin_routes.py:106-127`), `POST /api/admin/scrape` (`api/routes/admin_routes.py:21-38`) |
| FR-009 | Manajemen pengguna oleh admin (list, create, delete) | admin | `api/routes/admin_routes.py` | `GET/POST /api/admin/users`, `DELETE /api/admin/users/<username>` (`api/routes/admin_routes.py:41-103`) |
| FR-010 | Visualisasi tambahan `NewestVisualization/` (5 chart) | (pipeline) | `anggota3/NewestVisualization/` | Output PNG di `anggota3/NewestVisualization/output/` |

---

## 7. Persyaratan Non-Fungsional (Ringkas)

Rincian lengkap, kuantifikasi, dan acceptance criteria dipindahkan ke `docs/SRS.md` (mengacu IEEE 830-1998 dan ISO/IEC/IEEE 29148:2018). Ringkasan ada di sini untuk konteks PRD.

### 7.1 Kinerja

- Endpoint pencarian obat (`GET /api/drugs/search`) target waktu respons p95 di bawah 500 ms untuk dataset 74 obat lokal di Cloud Run min-instance-0 cold start kecil.
- Pembuatan PDF rekam medis target di bawah 2 detik per pasien tunggal pada Cloud Run free tier.
- Halaman utama Next.js (`/`) target Largest Contentful Paint di bawah 2.5 detik pada koneksi 3G simulasi.

### 7.2 Keamanan

- Hashing password dengan bcrypt cost 12 (lihat `api/auth.py`).
- JWT signing dengan secret di Secret Manager `medwatch-jwt-secret`, tidak pernah di-commit. Token disimpan sebagai httpOnly cookie SameSite=Lax (security pattern B Vercel proxy).
- CORS allowlist di backend (lihat `api/config.py CORS_ORIGINS` dan registrasi di `api/app.py:30-34`).
- Tidak ada nilai kredensial pernah ditulis ke repo, log, atau dokumen. Resource NAMES (project `medwatch-polban-2026`, bucket `medwatch-polban-2026-state`, service `medwatch-api`, secret `medwatch-jwt-secret`) boleh dibagikan ke dosen.

### 7.3 Usability

- Bahasa antarmuka: Bahasa Indonesia formal.
- Tema gelap dan terang (Next.js `next-themes`) dengan warna mengikuti palet ungu kanonik anggota3 (`anggota3/NewestVisualization/palette.py`).
- Login menampilkan kredensial demo di bawah form (perbaikan B09, lihat `src/app/login/page.tsx`) untuk memudahkan dosen mencoba.

### 7.4 Aksesibilitas

- Kontras warna teks utama memenuhi WCAG AA pada dua tema.
- Komponen form punya label eksplisit; tombol punya `data-testid` untuk uji otomatis (lihat fix B01 dan B02 dengan `data-testid="cta-scraper"` dan `data-testid="lihat-semua-aktivitas"`).

### 7.5 Internasionalisasi dan Lokalisasi

- Locale tunggal: id-ID, register formal.
- Format tanggal: dd-MM-yyyy (mis. `tanggal_kunjungan: "28-02-2026"`); parser di `api/routes/patient_routes.py:30-45`.
- Format mata uang Rupiah saat menampilkan biaya (Rp 1.000 dengan titik ribuan, koma desimal). Tidak ada modul keuangan dalam MVP.

---

## 8. Sumber Data

### 8.1 Sumber yang dipakai

- openFDA `drug/event.json` (FDA Adverse Event Reporting System / FAERS) untuk daftar efek samping per obat. Output: `anggota1/data/drug_safety_data.json`, 74 rekord obat, 1850 kemunculan istilah efek samping total (`anggota1/openfda/fetch.py` ringkasan stdout pada T1-DATA mission run, 18 Mei 2026).
- openFDA `drug/enforcement.json` (FDA Recall Enterprise System) untuk recall obat. Output: `anggota1/data/drug_recalls.json`, 6000 rekord recall, distribusi kelas Class II=4946, Class I=552, Class III=501, Not Yet Classified=1.
- Basis data lokal `anggota4/data/drug_database.json` (obat formularium lokal, owner Iqbal) dan `anggota4/data/effect_database.json` (efek samping terklasifikasi: ringan / sedang / serius).
- Basis data lokal `anggota2/Pasien.json` (skema kanonik pasien SOAP, owner Bimo).
- API key openFDA dibaca dari env `OPENFDA_API_KEY` (lihat `api/config.py`); nilainya tidak pernah di-commit. Kunci ini menaikkan kuota dari 1.000/hari/IP menjadi 120.000/hari/akun. URL dasar openFDA publik: `https://open.fda.gov`.

### 8.2 Pivot drugs.com ke openFDA (ringkas)

Awalnya `anggota1/anggota1.py` melakukan scraping `drugs.com/sfx/<nama>` untuk daftar efek samping. Per 11 Mei 2026 saat run scraping live, seluruh 64 URL `drugs.com/sfx/` mengembalikan HTTP 403 (Akamai anti-bot, bukti verbatim di `anggota1/scraper.log` baris 1-8). Tidak ada upaya bypass anti-bot yang dilakukan (sesuai etika riset dan ToS). Mitigasi: pivot ke openFDA REST API publik via modul aditif `anggota1/openfda/` (preserve file lama untuk audit trail). Rincian keputusan ada di ADR-004 (`docs/adr/0004-openfda-pivot.md`).

### 8.3 Update dan refresh strategy

- Modul `anggota1/openfda/fetch.py` dirancang re-runnable. Output dapat diregenerasi kapan pun via `python -m anggota1.openfda.fetch --max-recall-pages 6`.
- Schema output disengaja identik dengan fixture sebelumnya supaya konsumen downstream (`api/routes/drug_routes.py`, `api/routes/safety_routes.py`, modul visualisasi `anggota3/`, dan frontend) tidak perlu modifikasi.

---

## 9. Metrik Sukses (Acceptance KPIs)

| Kode | Metrik | Target | Status saat ini (Wave 1) |
|---|---|---|---|
| M-01 | Defek B01-B11 terverifikasi live (Playwright atau curl + ferry-back) | 11/11 fix lulus verifikasi dosen | 11/11 (lihat `findings/bugs/T1-*.md`) |
| M-02 | Rekord adverse-event openFDA real | >= 1000 kemunculan istilah efek samping | 1850 kemunculan, 74 rekord obat |
| M-03 | Rekord recall openFDA real | >= 5000 rekord | 6000 rekord |
| M-04 | Visualisasi baru di `anggota3/NewestVisualization/` | >= 4 chart informatif | 5 chart (top obat efek, distribusi keparahan, recall per tahun, perusahaan recall top, heatmap) |
| M-05 | ID pasien sesuai format `P001..P999` | 100% format kanonik | 100% (validasi di `api/routes/patient_routes.py:102-112`) |
| M-06 | Tidak ada nilai kredensial di repo / dokumen | nol leak | nol (per-commit secret-scan `./scripts/secret-scan.sh`) |
| M-07 | Dashboard admin uptime nyata (bukan hardcoded) | KPI uptime dihitung dari `process_started_at` | Lulus (lihat `api/routes/admin_routes.py:106-127`) |
| M-08 | Heatmap continuous color scale 5-stop risk | non-binary | Lulus per ADR-006 (`docs/adr/0006-heatmap-color-scale.md`) |
| M-09 | Daftar pasien sort descending tanggal | Terbaru paling atas | Lulus (`api/routes/patient_routes.py:135-146`) |
| M-10 | Tipe PDF tersedia | >= 4 (rekam medis, laporan bulanan, efek samping, inventaris) | 4/4 (`api/routes/pdf_routes.py`) |
| M-11 | Dokumentasi standar dikutip | PRD, SRS, SDD, ADR, API, As-Built, USER-MANUAL ada | Sedang dibangun di Wave 2 |
| M-12 | Mesin build Frontend dan Backend lulus | Build OK, lint OK | Lulus dengan catatan B-WAVE1-BUILD-1 (Node 22 LTS direkomendasikan, Node 25 punya bug) |

---

## 10. Risiko dan Mitigasi

| Kode | Risiko | Kemungkinan | Dampak | Mitigasi |
|---|---|---|---|---|
| R-01 | Sumber `drugs.com` diblokir Akamai (HTTP 403) | Tinggi (sudah terjadi) | Tinggi | Pivot ke openFDA, ADR-004, modul aditif `anggota1/openfda/`. Tidak ada bypass anti-bot. |
| R-02 | Kuota openFDA API harian | Sedang | Sedang | Pakai `OPENFDA_API_KEY` (120.000/hari) di env, jangan commit value. |
| R-03 | Node 25 punya bug `EBADF` saat run `next build` di lingkungan dev Ghaisan | Pasti (sudah teramati) | Rendah-Sedang | Lingkungan submission dosen rekomendasi Node 22 LTS; dokumentasi di `docs/INSTALL.md` dan As-Built `Known Issues / Technical Debt`. |
| R-04 | Cloud Run cold start menambah latensi pertama | Sedang | Rendah | min-instances=0 dipilih untuk biaya; first-request latency dijelaskan ke dosen sebagai trade-off free tier. |
| R-05 | Vercel free tier punya batas function execution | Rendah | Rendah | Proxy `app/api/[...slug]/route.ts` ringan; semua kerja berat ada di backend. |
| R-06 | Schema teammate (`anggota2/Pasien.json`) berubah saat merge ke main | Rendah | Sedang | Read-only contract di `.md` Rule 2; canonical schema dikunci di `docs/DATA-DICTIONARY.md`. |
| R-07 | API key openFDA bocor ke repo | Rendah | Tinggi | Per-commit secret-scan `./scripts/secret-scan.sh` blokir pola `api_key=...`, env-only loading di `api/config.py`. |
| R-08 | PDF gagal untuk karakter non-Latin-1 (helvetica fpdf2) | Sedang | Rendah | `_safe()` di `api/routes/pdf_routes.py:42-45` mengencode ulang ke Latin-1 dengan replacement char. |
| R-09 | Bidan menulis data SOAP semi-terstruktur (mis. "tespek positif") yang tidak masuk struktur ketat | Tinggi (sudah dipahami) | Rendah | Field `O.catatan` sebagai catch-all (lihat `.md`, "Bidan workflow reality"). |
| R-10 | Dosen menjalankan kode di mesin tanpa Python 3.13 | Rendah | Rendah | `docs/INSTALL.md` mengarahkan Python 3.11+ (Cloud Run runtime 3.11), venv terdokumentasi. |

---

## 11. Tim dan Peran

| Nama | NIM | Peran utama | Tanggung jawab teknis pada AS-BUILT |
|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader / Team Coordinator | Modul `anggota1` (scraping); modul aditif `anggota1/openfda/`; lapisan integrasi `api/`; lapisan frontend `FrontendMedwatch`; orchestration mission. |
| Bimo Surya Anggara | 251524040 | Quality Assurance | Modul `anggota2` (CRUD pasien SOAP); schema kanonik pasien; QA test plan dan eksekusi mayoritas test case. |
| Alia Ardani | 251524035 | System Analyst | Modul `anggota3` (visualisasi); folder baru `anggota3/NewestVisualization/` dengan 5 chart berbasis openFDA. |
| Muhammad Iqbal | 251524057 | Programmer | Modul `anggota4` (drug safety check); basis data obat dan efek samping lokal. |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | Modul `anggota5` (PDF export, autentikasi); revisi anggota5 untuk role-based auth (lihat Phase 1 exception di `.md`). |

### Atribusi tester

Test plan dan eksekusi didistribusikan lintas anggota:

- Bimo: master test plan dan eksekusi mayoritas.
- Alia: traceability requirement dan tes visualisasi.
- Iqbal: tes logika drug-safety.
- Abhidal: tes autentikasi, PDF, usability.
- Ghaisan: tes scraping dan tes integrasi end-to-end.

---

## 12. Tanggal Penting dan Tonggak

| Tanggal | Peristiwa | Catatan |
|---|---|---|
| 17 Februari 2026 | Awal Semester 2 TA 2025/2026 | Kick-off mata kuliah Proyek 1 PPLD. |
| 11 Mei 2026 | Scraping live `drugs.com` mengembalikan HTTP 403 | Pivot dimulai (ADR-004). |
| 18 Mei 2026 | Wave 1 selesai: B01-B11 fixed, openFDA data nyata, NewestVisualization | Dokumen PRD versi 1.0 dirilis (file ini). |
| 25 Mei 2026 | Submission deadline ke dosen | Tonggak utama. |
| 8 Juni 2026 | Kemungkinan kelas presentasi pasca-submission | Tentatif. |

---

## 13. Daftar Istilah / Glosarium

| Istilah | Definisi |
|---|---|
| SOAP | Subjective, Objective, Assessment, Plan. Format standar rekam medis berbasis catatan, dipakai oleh skema pasien MedWatch (`api/routes/patient_routes.py:1-30`, schema kanonik di `.md` bagian "Schema source of truth"). |
| Faskes 1 | Fasilitas Kesehatan Tingkat 1, mencakup puskesmas, polindes, klinik bersalin kecil. Sasaran utama pengguna MedWatch. |
| openFDA | API publik U.S. Food and Drug Administration di `https://open.fda.gov`. Sumber utama data efek samping (`drug/event`) dan recall (`drug/enforcement`) pada MedWatch pasca pivot. |
| FAERS | FDA Adverse Event Reporting System, basis data yang diekspos oleh openFDA endpoint `drug/event`. |
| MedDRA | Medical Dictionary for Regulatory Activities, ontologi medis yang dipakai openFDA sebagai `patient.reaction.reactionmeddrapt`. |
| JWT | JSON Web Token (RFC 7519), token signed untuk autentikasi MedWatch (issued di `api/auth.py`, diverifikasi di middleware `api/middleware.py`). |
| RBAC | Role-Based Access Control. MedWatch punya tiga peran: `tenaga_kesehatan`, `masyarakat`, `admin`. Decorator `@require_role` dipakai di route Flask (mis. `api/routes/patient_routes.py:136`). |
| Tenaga Kesehatan | Peran backend untuk bidan Faskes 1 (string value `tenaga_kesehatan`). Akses penuh CRUD pasien dan cek interaksi obat. |
| Masyarakat | Peran backend untuk warga umum (string value `masyarakat`). Akses read-only katalog obat dan safety checker tanpa konteks pasien. |
| Akamai | Layanan CDN / WAF yang dipakai `drugs.com`, memblokir traffic scraping otomatis dengan HTTP 403. Bukti di `anggota1/scraper.log`. |
| Cloud Run | Layanan serverless GCP untuk deploy backend Flask MedWatch (service name `medwatch-api`, region `asia-southeast1`). |
| GCS bucket | Google Cloud Storage. Bucket `medwatch-polban-2026-state` dipakai untuk persistensi `users.json` dan `patients.json` di lingkungan demo cloud. |
| Vercel proxy | Pola "security pattern B": browser hanya melihat domain Vercel, panggilan ke `/api/[...slug]` di-proxy server-side ke `BACKEND_API_URL` (Cloud Run) dengan header JWT dari cookie httpOnly. |
| Faskes | Singkatan Fasilitas Kesehatan. |
| LILA | Lingkar Lengan Atas, parameter antropometri ibu hamil. Diakomodasi di field `O.lila_cm` dengan rentang 8-60 cm (`api/routes/patient_routes.py:17-24`). |

---

## 14. Lampiran: Referensi

### 14.1 Repositori dan resource

- Backend repo (Bisura16/medWatch): `https://github.com/Bisura16/medWatch`, branch integrasi `ghaisan-APIIntegration`.
- Frontend repo (Finerium/FrontendMedwatch): `https://github.com/Finerium/FrontendMedwatch`, branch integrasi `ghaisan-APIIntegration`.
- openFDA API publik: `https://open.fda.gov`, endpoint `drug/event` dan `drug/enforcement` (lihat juga ADR-004 dan README repo backend bagian "Sumber Data").
- GCP project name (resource name, bukan kredensial): `medwatch-polban-2026`, region `asia-southeast1`.
- GCS bucket: `medwatch-polban-2026-state`.
- Cloud Run service: `medwatch-api`.
- Secret Manager: `medwatch-jwt-secret`.

### 14.2 Standar yang dikutip oleh dokumen turunan PRD

- IEEE 830-1998 / ISO/IEC/IEEE 29148:2018 dipakai di `docs/SRS.md` untuk struktur SRS.
- IEEE 1016-2009 dipakai di `docs/SDD.md` untuk Software Design Description.
- ISO/IEC/IEEE 26514 dipakai di `docs/USER-MANUAL.md`.
- ISO/IEC/IEEE 15289:2019 dipakai di `docs/AS-BUILT.md` untuk struktur 19-section.
- MADR (Markdown Architecture Decision Records) dipakai di `docs/adr/`.
- C4 model (Simon Brown) dipakai di `docs/diagrams/` untuk diagram L1, L2, L3, dan Deployment.
- OWASP Top 10 + STRIDE dipakai di `docs/SECURITY.md` untuk threat model.

### 14.3 Dokumen turunan internal (lihat juga)

- `docs/SRS.md` (Software Requirements Specification)
- `docs/SDD.md` (Software Design Description)
- `docs/API.md` (Endpoint kontrak HTTP)
- `docs/DATA-DICTIONARY.md`
- `docs/INSTALL.md`
- `docs/SECURITY.md`
- `docs/AS-BUILT.md`
- `docs/USER-MANUAL.md`
- `docs/adr/0001-vercel-cloudrun-split.md` (security pattern B)
- `docs/adr/0002-jwt-bcrypt-cookie.md`
- `docs/adr/0003-pasien-soap-schema.md`
- `docs/adr/0004-openfda-pivot.md`
- `docs/adr/0005-newest-visualization-additive.md`
- `docs/adr/0006-heatmap-color-scale.md`
- `docs/adr/0007-patient-list-sort.md`
- `docs/adr/0008-pdf-fpdf2-inprocess.md`

---

## 15. Riwayat Revisi

| Versi | Tanggal | Penulis | Ringkasan perubahan |
|---|---|---|---|
| 1.0 | 18-05-2026 | Kelompok B5 (Ghaisan koordinator) | Revisi AS-BUILT setelah Wave 1: bug B01-B11 fixed, openFDA data nyata, `anggota3/NewestVisualization/` ditambahkan; struktur PRD selaras dengan misi penyerahan dosen 25-05-2026. |
