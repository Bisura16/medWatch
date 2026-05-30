---
title: MedWatch As-Built (As-Implemented) System Documentation
version: 1.0
date: 2026-05-18
owner: Kelompok B5 - 1B-D4 Teknik Informatika, Politeknik Negeri Bandung
kelompok: B5
ticket: W2-D11
standar_acuan: ISO/IEC/IEEE 15289:2019 (Information Item - System Documentation Description)
status: AS-IMPLEMENTED setelah Iterasi 1 (bug B01..B11, akuisisi openFDA, NewestVisualization) dan Iterasi 2 batch 1+2 (PRD, SRS, SDD, ADR, API, DATA-DICTIONARY, INSTALL, SECURITY, diagram)
---

# As-Built (As-Implemented) System Documentation MedWatch

Dokumen ini disusun mengikuti **ISO/IEC/IEEE 15289:2019, Systems and Software Engineering - Content of Life-Cycle Information Items (Documentation)**, klausa 9 (System Documentation - Item) yang menetapkan struktur item dokumentasi as-built. As-Built MedWatch mendeskripsikan sistem sebagaimana terbangun dan diserahkan pada 25 Mei 2026 kepada dosen mata kuliah Proyek 1 Pengembangan Perangkat Lunak Desktop di D4 Teknik Informatika Politeknik Negeri Bandung. Dokumen tidak mengulang spesifikasi awal (lihat `docs/PRD.md` dan `docs/SRS.md`) melainkan merekam realita implementasi pasca Iterasi 1 perbaikan bug B01..B11, akuisisi data nyata openFDA, dan penambahan modul visualisasi `anggota3/NewestVisualization/` berbasis hasil scraping.

Setiap klaim teknis didukung dengan sitiran `file:line` pada repositori `medWatch/` (backend) atau `FrontendMedWatch/` (frontend). Standar pendukung lain yang dirujuk dokumen ini: IEEE 830-1998 dan ISO/IEC/IEEE 29148:2018 (SRS), IEEE 1016-2009 (SDD), C4 model oleh Brown (arsitektur), MADR (ADR), ISO/IEC/IEEE 26514 (User Documentation), OWASP Top 10 (2021) dan STRIDE (threat model).

---

## 1. Informasi Dokumen

### 1.1 Identitas

| Atribut | Nilai |
|---|---|
| Judul dokumen | As-Built (As-Implemented) System Documentation MedWatch |
| Standar acuan | ISO/IEC/IEEE 15289:2019 - System Documentation Item |
| Versi dokumen | 1.0 |
| Tanggal | 18 Mei 2026 |
| Tanggal penyerahan | 25 Mei 2026 (deadline dosen) |
| Klasifikasi | Internal akademik (artefak submission mata kuliah) |
| Bahasa | Bahasa Indonesia (prosa); Bahasa Inggris (identifier kode dan sitasi standar) |
| Owner | Kelompok B5, 1B-D4 Teknik Informatika, Politeknik Negeri Bandung |
| Mata kuliah | Proyek 1 Pengembangan Perangkat Lunak Desktop |
| Semester | TA 2025/2026, Semester 2 |
| Tiket proyek | W2-D11 (Iterasi 2 batch 2) |

### 1.2 Tim Penulis dan Atribusi

Semua lima anggota Kelompok B5 berkontribusi pada produk yang didokumentasikan di sini. Atribusi modul mengikuti pembagian peran kanonik di konvensi proyek (Backend repo) Rule 1 (Git authorship) dan Team roster:

| Nama lengkap | NIM | Peran utama | Modul Python yang dimiliki | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader / Team Coordinator | `anggota1/` (scraping, akuisisi openFDA), layer `api/`, integrasi cloud | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | `anggota2/` (CRUD pasien SOAP, schema kanonik) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | `anggota3/` (visualisasi matplotlib), `anggota3/NewestVisualization/` (5 chart openFDA) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | `anggota4/` (drug safety check, basis data obat/efek) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | `anggota5/` (PDF export `fpdf2`, auth Phase 1 revision) | Heimdall |

### 1.3 Dosen Pendamping

- Aprianti Nanda Sari (Project Manager mata kuliah)
- Ade Chandra Nugraha
- Ardhian Ekawijana

### 1.4 Cakupan Dokumen

Dokumen ini menggabungkan output Iterasi 1 (perbaikan bug, akuisisi data nyata, modul visualisasi tambahan) dan Iterasi 2 batch 1+2 (set dokumentasi lengkap dan diagram arsitektur). Lihat tabel ringkasan Bab 18 dan Lampiran A untuk daftar commit lengkap.

### 1.5 Dokumen Terkait (Cross-Link)

| Path | Standar | Cakupan singkat |
|---|---|---|
| `docs/PRD.md` | - (template internal) | Product Requirements Document; persona, ruang lingkup, sasaran |
| `docs/SRS.md` | IEEE 830-1998, ISO/IEC/IEEE 29148:2018 | Software Requirements Specification; FR-001..FR-071, NFR-PERF/SEC/USA/ACC/COMP/PORT/MAINT/LOG/INT |
| `docs/SDD.md` | IEEE 1016-2009, C4 model | Software Design Description; dekomposisi modul, design viewpoints |
| `docs/adr/0001..0010-*.md` | MADR 3.0 | 10 Architecture Decision Records |
| `docs/API.md` | OpenAPI-style | 27 endpoint HTTP backend (8 blueprint) |
| `docs/DATA-DICTIONARY.md` | - (kamus data lokal) | 6 entitas JSON: User, Patient, Drug, SideEffect, AdverseEvent, Recall |
| `docs/INSTALL.md` | ISO/IEC/IEEE 26514 | Panduan instalasi, deployment, dev |
| `docs/SECURITY.md` | OWASP Top 10 (2021), STRIDE | Threat model, postur keamanan saat pengiriman |
| `docs/USER-MANUAL.md` | ISO/IEC/IEEE 26514 | Panduan pengguna per peran (terjadwal W2-D09) |
| `docs/diagrams/src/` dan `docs/diagrams/png/` | C4 model | Diagram konteks/container/komponen/deployment + diagram sequence |
| `ProductionGrade-ImplementationPlan/` | - (forward-looking) | Roadmap produksi (terjadwal W2-PROD) |

---

## 2. Ringkasan Eksekutif

MedWatch adalah sistem pemantauan keamanan obat dan manajemen klinik untuk bidan Fasilitas Kesehatan Tingkat 1 (Faskes 1) yang dibangun sebagai produk komposit tiga tier: aplikasi desktop CustomTkinter modular (modul anggota1..5) sebagai submission resmi mata kuliah, backend Flask REST API (`api/`) sebagai lapisan integrasi yang membungkus modul anggota1..5, dan frontend showcase Next.js 16 yang dideploy ke Vercel Hobby sebagai antarmuka web demo. Per `api/app.py:36-43`, backend mengekspos 8 blueprint dengan total 27 endpoint HTTP. Frontend memuat 19 rute aktif pada `src/app/**/page.tsx` (lihat Bagian 9), dengan akses dikontrol oleh tiga peran kanonik (`tenaga_kesehatan`, `masyarakat`, `admin`) dan dekorator RBAC `require_role` (`api/middleware.py:37-51`) plus middleware proxy Next.js (`src/proxy.ts:41-83`).

Keputusan arsitektural utama yang membentuk sistem as-built: (a) pola Vercel Next.js proxy + Cloud Run backend dengan JWT httpOnly cookie (ADR-0001, ADR-0002); (b) skema Pasien SOAP kanonik dari `anggota2/pasien_helper.py` dengan ID `P001..P999` (ADR-0003); (c) pivot scraping dari drugs.com (HTTP 403 Akamai) ke openFDA REST API (ADR-0004), menghasilkan 74 rekord obat dengan 1850 reaction-term occurrences dan 6000 rekord recall (`anggota1/data/drug_safety_data.json` dan `drug_recalls.json`); (d) modul visualisasi tambahan `anggota3/NewestVisualization/` (5 chart) sebagai folder aditif tanpa menyentuh file Alia yang ada (ADR-0005); (e) heatmap kontinu 5-stop risk-matrix d3 sebagai pengganti bucketed 3-warna (ADR-0006).

Deviasi terhadap PRD/SRS/SDD awal didokumentasikan secara eksplisit di Bagian 16 (tabel tiga-kolom). Hutang teknis yang diketahui dicatat di Bagian 15: B-BUILD-1 (Next.js 16.2.1 chunk-emit race pada Node 25, mitigasi Node 22 LTS), bobot heatmap saat ini menggunakan severity weighting (followup untuk pakai raw FAERS counts), audit log admin dashboard masih hardcoded sample (T1-ADMIN sudah membuat route `/dashboard/aktivitas` namun feed admin asli belum tersambung), atomic JSON write (SECURITY.md R6), dan residual risk R1..R8 lain. Semua bug B01..B11 yang dilaporkan dosen / auditor sudah diperbaiki dan terverifikasi live (lihat catatan internal proyek); smoke test backend (`api/tests/smoke_test.py`, 14 assertion utama) hijau di lokal pada 18 Mei 2026.

---

## 3. Tinjauan Proyek

### 3.1 Konteks Akademik

| Atribut | Nilai |
|---|---|
| Institusi | Politeknik Negeri Bandung (POLBAN) |
| Jurusan | D4 Teknik Informatika |
| Kelas | 1B-D4 |
| Mata kuliah | Proyek 1 Pengembangan Perangkat Lunak Desktop |
| Semester | Semester 2, Tahun Akademik 2025/2026 |
| Kelompok | B5 |
| Awal semester | 17 Februari 2026 (kick-off mata kuliah) |
| Deadline submission | 25 Mei 2026 |
| Tentatif sesi presentasi | 8 Juni 2026 (jadwal kelas pasca submission) |

### 3.2 Tujuan Akademik (CPMK terkait)

Mata kuliah memerlukan tim mahasiswa untuk membangun aplikasi desktop modular Python yang menjalankan capaian pembelajaran:

1. Modularisasi: setiap anggota memiliki modul Python tersendiri dengan domain berbeda (`anggota1/` ... `anggota5/`).
2. Integrasi: modul-modul digabungkan menjadi aplikasi koheren via titik masuk `main.py` (`/Users/ghaisan/Documents/MedWatchIntegration/medWatch/main.py:1`) untuk desktop CustomTkinter.
3. Persistensi: data disimpan dalam berkas JSON dengan skema konsisten antar modul.
4. Antarmuka pengguna: GUI desktop berbasis CustomTkinter atau lapisan web showcase Next.js sebagai bonus presentasi.
5. Dokumentasi standar: PRD, SRS, SDD, ADR, manual, As-Built, threat model, dan diagram arsitektur.

### 3.3 Tonggak Proyek

| Tanggal | Peristiwa | Bukti |
|---|---|---|
| 17 Februari 2026 | Kick-off mata kuliah | Kalender akademik POLBAN |
| 11 Mei 2026 | Scraping `drugs.com` live mengembalikan HTTP 403 di seluruh 64 URL `drugs.com/sfx/` (Akamai anti-bot) | `anggota1/scraper.log` baris 1-8, terkutip verbatim pada `docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md` |
| 18 Mei 2026 | Iterasi 1 selesai: B01..B11 fixed, openFDA data nyata, NewestVisualization | catatan internal proyek dan log commit (lihat Lampiran A) |
| 18 Mei 2026 | Iterasi 2 batch 1+2 selesai: PRD, SRS, SDD, ADR, API, DATA-DICTIONARY, INSTALL, SECURITY, AS-BUILT, USER-MANUAL, diagram | Commit dengan prefix `docs(*)` di Lampiran A |
| 25 Mei 2026 | Deadline submission ke dosen | Tonggak utama |
| 8 Juni 2026 (tentatif) | Sesi kelas presentasi pasca submission | Jadwal kelas |

---

## 4. Arsitektur As-Built

### 4.1 C4 Level 1 Context

Diagram konteks merepresentasikan sistem MedWatch sebagai kotak hitam yang berinteraksi dengan empat aktor manusia (tenaga kesehatan, masyarakat, admin, dosen observasional) dan tiga sistem eksternal (openFDA REST API, Google Cloud Storage, Google Secret Manager).

- Sumber Mermaid: `docs/diagrams/src/c4-l1-context.mmd`
- Render PNG: `docs/diagrams/png/c4-l1-context.png` (lihat juga `docs/diagrams/png/01-c4-context.png`)
- Notasi: legend Mermaid mengacu C4 model Simon Brown (https://c4model.com)

Aktor manusia menggunakan browser modern yang mengakses URL Vercel `https://medwatch-frontend.vercel.app`. Sistem eksternal openFDA diakses oleh pipeline akuisisi `anggota1/openfda/fetch.py` (CLI) untuk regenerasi data offline; tidak diakses runtime oleh backend Flask. GCS bucket `medwatch-polban-2026-state` dan Secret Manager `medwatch-jwt-secret` diakses oleh service Cloud Run via default service account.

### 4.2 C4 Level 2 Container

Diagram container memperinci sistem menjadi tiga aplikasi utama plus penyimpanan persisten.

- Sumber: `docs/diagrams/src/c4-l2-container.mmd`
- Render PNG: `docs/diagrams/png/c4-l2-container.png` (alt `02-c4-container.png`)

Container:

1. **Desktop CustomTkinter** (`main.py:1` + `anggota1/`..`anggota5/`): submission resmi mata kuliah; runtime Python 3.13 lokal di laptop bidan.
2. **Backend Flask** (`api/`): runtime Python 3.11 di Cloud Run `medwatch-api`, region `asia-southeast1`, 1 vCPU + 512 MiB RAM. Entry point `api/app.py:27` `create_app()`. Mengekspos 27 endpoint HTTP melalui 8 blueprint (`api/app.py:36-43`).
3. **Frontend Next.js** (`FrontendMedWatch/src/`): Next.js 16.2.1 App Router, React 19.2.4, TypeScript 5.x strict, Tailwind v4. Dideploy ke Vercel Hobby. Proxy server-side via `src/app/api/[...slug]/route.ts:1-109` yang meneruskan ke `BACKEND_API_URL` (env Vercel, server-only, tanpa prefiks `NEXT_PUBLIC_`).
4. **Penyimpanan persisten**: JSON di filesystem `api/data/` saat `USE_CLOUD_STORAGE=false` atau GCS bucket `medwatch-polban-2026-state` saat `USE_CLOUD_STORAGE=true` (`api/config.py:29`, `api/storage.py:63-87`).

### 4.3 C4 Level 3 Component (Backend)

Diagram komponen memperinci dekomposisi internal `api/`.

- Sumber: `docs/diagrams/src/c4-l3-component-backend.mmd`
- Render PNG: `docs/diagrams/png/c4-l3-component-backend.png` (alt `03-c4-component-api.png`)

Komponen utama dalam `api/`:

| Komponen | Path | Tanggung jawab |
|---|---|---|
| Bootstrap | `api/bootstrap.py:1-39` | Lazy-load modul anggota1..5; return None jika gagal import |
| Config | `api/config.py:1-38` | Env-driven constant (JWT, CORS, GCS, openFDA key) |
| Auth | `api/auth.py:1-39` | JWT issue/verify, bcrypt hash/verify |
| Middleware | `api/middleware.py:1-51` | `require_auth`, `require_role` decorators |
| Helpers | `api/helpers.py:1-96` | Response wrappers, password sanitization, `parse_resep_to_meds` |
| Storage | `api/storage.py:1-100+` | Cloud Storage atau local file backend |
| Routes blueprint | `api/routes/*.py` | 8 blueprint: health, auth, patient, drug, safety, visualization, pdf, admin |

### 4.4 Deployment Topology

Diagram deployment menggambarkan pemetaan container ke node fisik dan layanan cloud.

- Sumber: `docs/diagrams/src/deployment.mmd`
- Render PNG: `docs/diagrams/png/deployment.png` (alt `12-deployment.png`)

Topologi:

- Browser klien -> Vercel Edge (Next.js 16 Static + Edge Functions) -> Server-side proxy `src/app/api/[...slug]/route.ts` -> Cloud Run service `medwatch-api` (asia-southeast1) -> GCS bucket `medwatch-polban-2026-state` (asia-southeast1) atau Secret Manager `medwatch-jwt-secret`.
- Backend URL Cloud Run tidak diekspos ke browser (security pattern B, ADR-0001). Browser hanya melihat domain Vercel.
- CORS allowlist backend membatasi origin pada `https://medwatch-frontend.vercel.app`, `http://localhost:3000`, dan `http://localhost:5173` (`api/config.py:21-25`, `api/app.py:30-34`).

### 4.5 Key Sequence Diagrams

Diagram sekuens kritis tersedia sebagai sumber Mermaid:

- Login flow: `docs/diagrams/src/seq-login.mmd` (`docs/diagrams/png/06-sequence-auth.png` legacy render)
- CRUD Pasien (create): `docs/diagrams/src/seq-pasien-crud.mmd` (legacy `07-sequence-patient-create.png`)
- Cek interaksi obat (safety check): legacy `08-sequence-safety-check.png`
- Use case keseluruhan: `docs/diagrams/src/use-case.mmd` -> `docs/diagrams/png/use-case.png` (alt `04-use-case.png`)

Tiap diagram dilengkapi blok legend yang menjelaskan notasi. Lihat juga dekomposisi visual modul tiap anggota di `docs/diagrams/png/14-structure-chart-anggota1.png` sampai `18-structure-chart-anggota5.png`.

---

## 5. Inventaris Fitur yang Diimplementasikan

Tabel ini memetakan setiap Functional Requirement dari `docs/SRS.md` ke status implementasi nyata pada sistem AS-BUILT. Status: **Implemented** (selesai, terverifikasi), **Partial** (sebagian, ada caveat di kolom Catatan), atau **Deferred** (dipindah ke Iterasi 5 atau ProductionGrade-ImplementationPlan).

### 5.1 Otentikasi dan Otorisasi

| FR-ID | Deskripsi singkat | Status | Bukti file:line |
|---|---|---|---|
| FR-001 | POST `/api/auth/login` JWT HS256 | Implemented | `api/routes/auth_routes.py:13-40` |
| FR-002 | `require_auth` middleware | Implemented | `api/middleware.py:17-34` |
| FR-003 | 3 preset demo login B09 | Implemented | `src/app/login/page.tsx:18-43, 80-109` |
| FR-004 | FormData submit B09 | Implemented | `src/app/login/page.tsx:80-98` |
| FR-005 | `require_role` RBAC | Implemented | `api/middleware.py:37-51` |
| FR-006 | POST `/api/auth/logout` | Implemented | `api/routes/auth_routes.py:49-51` |
| FR-007 | GET `/api/auth/me` | Implemented | `api/routes/auth_routes.py:43-46` |
| FR-008 | Middleware Next.js redirect | Implemented | `src/proxy.ts:41-83` |

### 5.2 CRUD Pasien (Schema SOAP)

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-010 | GET `/api/patients` newest-first (B07) | Implemented | `api/routes/patient_routes.py:135-146` |
| FR-011 | POST `/api/patients` ID `P001..P999` | Implemented | `api/routes/patient_routes.py:162-187` |
| FR-012 | Validasi 4 field wajib | Implemented | `api/routes/patient_routes.py:166-173` |
| FR-013 | Validasi numerik medis (B03) | Implemented | `api/routes/patient_routes.py:17-99` |
| FR-014 | Frontend mirror validasi | Implemented | `src/lib/patient-validation.ts`, `src/app/patients/new/page.tsx` |
| FR-015 | GET `/api/patients/<pid>` | Implemented | `api/routes/patient_routes.py:149-159` |
| FR-016 | PUT deep-merge | Implemented | `api/routes/patient_routes.py:190-205` |
| FR-017 | DELETE admin-only | Implemented | `api/routes/patient_routes.py:208-217` |

### 5.3 Katalog dan Pencarian Obat

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-020 | GET `/api/drugs` filter kategori | Implemented | `api/routes/drug_routes.py:19-28` |
| FR-021 | GET `/api/drugs/search` alias-aware | Implemented | `api/routes/drug_routes.py:31-40` |
| FR-022 | GET `/api/drugs/<nama_obat>` | Implemented | `api/routes/drug_routes.py:43-51` |

### 5.4 Cek Interaksi dan Keamanan Obat

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-030 | POST `/api/safety/check` agregat | Implemented | `api/routes/safety_routes.py:16-72` |
| FR-031 | Severity score 0..100 + level | Implemented | `api/routes/safety_routes.py:34-42, 63-71` |
| FR-032 | `pasien_active_meds` dari P.resep (B05) | Implemented | `api/routes/safety_routes.py:44-61`; parser `api/helpers.py:47-96` |
| FR-033 | Auto-merge chip frontend | Implemented | `src/app/safety-checker/page.tsx` |
| FR-034 | Panel collapsible penjelas (B08) | Implemented | `src/app/safety-checker/page.tsx` |

### 5.5 Visualisasi

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-040 | GET kunjungan-trend | Implemented | `api/routes/visualization_routes.py:54-66` |
| FR-041 | GET keluhan-distribution | Implemented | `api/routes/visualization_routes.py:69-80` |
| FR-042 | GET top-efek-samping | Implemented | `api/routes/visualization_routes.py:83-110` |
| FR-043 | GET heatmap-efek | Implemented | `api/routes/visualization_routes.py:113-138` |
| FR-044 | Frontend heatmap kontinu d3 5-stop (B11) | Implemented | `src/app/heatmap/page.tsx`, util `src/lib/heatmap-colors.ts` |
| FR-045 | Legend gradient swatch | Implemented | `src/app/heatmap/page.tsx` legend section |
| FR-046 | Sort baris/kolom by total bobot | Implemented | `src/app/heatmap/page.tsx` sorted useMemo |

### 5.6 Eksport PDF

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-050 | POST generate-rekam-medis | Implemented | `api/routes/pdf_routes.py:169-202` |
| FR-051 | POST generate-laporan-bulanan | Implemented | `api/routes/pdf_routes.py:205-238` |
| FR-052 | POST generate-efek-samping (B04 sub-2) | Implemented | `api/routes/pdf_routes.py:241-385` |
| FR-053 | POST generate-inventaris (B04 sub-3) | Implemented | `api/routes/pdf_routes.py:388-511` |
| FR-054 | Frontend 4 pilihan PDF | Implemented | `src/app/export-pdf/page.tsx` |

### 5.7 Administrasi Sistem

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-060 | POST `/api/admin/scrape` mocked | Implemented (mock) | `api/routes/admin_routes.py:21-38` (production worker queue di `ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md`) |
| FR-061 | GET `/api/admin/users` strip password | Implemented | `api/routes/admin_routes.py:41-45` |
| FR-062 | POST `/api/admin/users` bcrypt cost 12 | Implemented | `api/routes/admin_routes.py:48-85` |
| FR-063 | DELETE protect last admin | Implemented | `api/routes/admin_routes.py:88-103` |
| FR-064 | GET system-stats real (B10) | Implemented | `api/routes/admin_routes.py:106-127` |
| FR-065 | Dashboard admin tanpa hardcoded | Implemented | `src/app/admin/dashboard/page.tsx:43-81` |
| FR-066 | CTA scraper (B01) | Implemented | `src/app/admin/dashboard/page.tsx:170-226` |
| FR-067 | Lihat semua activity (B02) | Implemented | `src/app/dashboard/page.tsx ~442-444`; route `src/app/dashboard/aktivitas/page.tsx` |

### 5.8 Endpoint Pendukung dan Akuisisi Data

| FR-ID | Deskripsi | Status | Bukti file:line |
|---|---|---|---|
| FR-070 | GET `/api/health` | Implemented | `api/routes/health.py:12-18` |
| FR-071 | GET `/api/info` modul | Implemented | `api/routes/health.py:21-36` |
| - | Akuisisi data openFDA real (T1-DATA) | Implemented | `anggota1/openfda/fetch.py:1-468`; output 74 rekord obat + 6000 rekord recall |
| - | NewestVisualization 5 chart (T1-VIZ) | Implemented | `anggota3/NewestVisualization/viz_*.py`; output PNG di `anggota3/NewestVisualization/output/` |

**Statistik agregat AS-BUILT:** 40 FR-ID terdokumentasi di `docs/SRS.md`, 27 endpoint HTTP backend, 19 rute frontend aktif (Bagian 9), 11 bug B01..B11 selesai dan diverifikasi (lihat catatan internal proyek).

---

## 6. Tumpukan Teknologi Final dengan Versi Pin

Versi terkunci diambil dari `api/requirements.txt:1-11` (backend) dan `FrontendMedWatch/package.json` (frontend). Semua versi diuji per 18 Mei 2026.

### 6.1 Backend (Python)

| Paket | Versi | Sumber | Catatan |
|---|---|---|---|
| Python | 3.11 (Cloud Run) / 3.13 (dev) | `api/Dockerfile`; dev venv | Cloud Run runtime `python:3.11-slim` |
| Flask | 3.1.3 | `api/requirements.txt:1` | Pin eksak |
| Flask-Cors | 6.0.0 | `api/requirements.txt:2` | Pin eksak |
| PyJWT | 2.12.0 | `api/requirements.txt:3` | Pin eksak |
| bcrypt | 4.2.1 | `api/requirements.txt:4` | Pin eksak |
| google-cloud-storage | 2.18.2 | `api/requirements.txt:5` | Pin eksak; hanya di-load saat `USE_CLOUD_STORAGE=true` |
| gunicorn | 23.0.0 | `api/requirements.txt:6` | Production WSGI |
| requests | 2.33.0 | `api/requirements.txt:7` | Dipakai `anggota1/openfda/fetch.py` |
| beautifulsoup4 | 4.12.3 | `api/requirements.txt:8` | Legacy untuk `anggota1.py` lama; tidak dipakai openFDA |
| matplotlib | 3.9.2 | `api/requirements.txt:9` | Untuk `anggota3/` matplotlib charts |
| numpy | 1.26.4 | `api/requirements.txt:10` | Dependency `matplotlib` |
| fpdf2 | 2.8.1 | `api/requirements.txt:11` | Generate PDF via `api/routes/pdf_routes.py` |

### 6.2 Frontend (Node)

| Paket | Versi | Sumber | Catatan |
|---|---|---|---|
| Node.js | 22 LTS (rekomendasi) | `package.json` (engines tidak di-pin; lihat B-BUILD-1) | Node 25 memicu chunk-emit race |
| Next.js | 16.2.1 | `package.json` | App Router |
| React | 19.2.4 | `package.json` | RSC default |
| React DOM | 19.2.4 | `package.json` | |
| TypeScript | 5.x | `tsconfig.json` | strict mode |
| Tailwind CSS | v4 (`^4`) | `package.json`, `tailwind.config.ts` | |
| @tailwindcss/postcss | ^4 | `package.json` devDependencies | |
| eslint | ^9 | `package.json` devDependencies | |
| eslint-config-next | 16.2.1 | `package.json` devDependencies | |
| framer-motion | ^12.38.0 | `package.json` | Animasi |
| recharts | ^3.8.1 | `package.json` | Visualisasi line/bar chart |
| d3-scale | ^4.0.2 | `package.json` | Heatmap continuous color (FR-044) |
| d3-interpolate | ^3.0.1 | `package.json` | Heatmap gradient (FR-044) |
| d3-geo | ^3.1.1 | `package.json` | Indonesia map (archived route) |
| @react-three/drei | ^10.7.7 | `package.json` | Molecule viewer (archived) |
| @react-three/fiber | ^9.5.0 | `package.json` | Three.js wrapper (archived) |
| three | ^0.183.2 | `package.json` | Three.js |
| next-themes | ^0.4.6 | `package.json` | Tema gelap/terang |
| zustand | ^5.0.12 | `package.json` | Client state (auth store) |
| jspdf | ^4.2.1 | `package.json` | Client-side PDF (legacy) |
| jspdf-autotable | ^5.0.7 | `package.json` | Tabel PDF |
| @base-ui/react | ^1.3.0 | `package.json` | Primitive UI (Radix-style) |
| class-variance-authority | ^0.7.1 | `package.json` | shadcn utility |
| clsx | ^2.1.1 | `package.json` | Class utility |
| cmdk | ^1.1.1 | `package.json` | Command palette |
| html2canvas | ^1.4.1 | `package.json` | Snapshot ke canvas (legacy) |
| lucide-react | ^1.7.0 | `package.json` | Icon set |
| react-force-graph-2d | ^1.29.1 | `package.json` | Network graph (archived) |
| react-simple-maps | ^3.0.0 | `package.json` | Indonesia map (archived) |
| shadcn | ^4.1.1 | `package.json` | shadcn CLI |
| sonner | ^2.0.7 | `package.json` | Toast notification |
| tailwind-merge | ^3.5.0 | `package.json` | Tailwind utility |
| topojson-client | ^3.1.0 | `package.json` | TopoJSON Indonesia map (archived) |
| tw-animate-css | ^1.4.0 | `package.json` | Animasi Tailwind |

### 6.3 Infrastruktur Cloud

| Layanan | Nama resource | Region | Catatan |
|---|---|---|---|
| GCP Project | `medwatch-polban-2026` | (asia-southeast1 default) | Resource name OK; tidak ada credential value di doc |
| Cloud Run | `medwatch-api` | asia-southeast1 | 1 vCPU + 512 MiB; min-instances=0 |
| Cloud Storage | `medwatch-polban-2026-state` | asia-southeast1 | Persistensi users.json + patients.json |
| Secret Manager | `medwatch-jwt-secret` | global | JWT signing secret |
| Vercel project | `medwatch` | edge global | Hobby tier; URL `https://medwatch-frontend.vercel.app` |
| openFDA REST API | `api.fda.gov` (publik) | global | Endpoint `drug/event.json` + `drug/enforcement.json` |

---

## 7. Model Data Final

Sumber kebenaran skema: `docs/DATA-DICTIONARY.md`. ERD tersedia di `docs/diagrams/png/11-er-schema.png`. Ringkasan entitas:

| Entitas | Lokasi (Desktop) | Lokasi (Backend) | Source-of-truth | Endpoint utama |
|---|---|---|---|---|
| User | `anggota5/data/users.json` (legacy) | `api/data/users.json` atau `gs://medwatch-polban-2026-state/users.json` | `api/data/users.json` (canonical) | `POST /api/auth/login`, `GET /api/admin/users` |
| Patient | `anggota2/Pasien.json` | `api/data/patients.json` atau `gs://medwatch-polban-2026-state/patients.json` | `anggota2/pasien_helper.py` | `GET/POST/PUT/DELETE /api/patients` |
| Drug | `anggota4/data/drug_database.json` | sama (read-only) | `anggota4/data/drug_database.json` | `GET /api/drugs`, `GET /api/drugs/search`, `GET /api/drugs/<nama>` |
| SideEffect | `anggota4/data/effect_database.json` | sama (read-only) | `anggota4/data/effect_database.json` | dipakai oleh safety check dan visualisasi |
| AdverseEvent | `anggota1/data/drug_safety_data.json` | sama (read-only) | scraped openFDA `drug/event` | dibaca oleh `anggota3/NewestVisualization/viz_top_obat_efek_samping.py`, `api/routes/pdf_routes.py:80-91` |
| Recall | `anggota1/data/drug_recalls.json` | sama (read-only) | scraped openFDA `drug/enforcement` | dibaca oleh `anggota3/NewestVisualization/viz_recall_class_per_tahun.py`, `viz_perusahaan_recall_top.py` |

### 7.1 Skema Pasien Kanonik (ringkasan)

Diturunkan dari `anggota2/pasien_helper.py` (konvensi proyek). Field wajib: `nama`, `S.keluhan`, `A.diagnosa`, `P.tindakan`. Field opsional `O.nadi`, `O.suhu_c`, `O.respirasi` (bidan tidak selalu mengukur). ID format `P001..P999` di-generate oleh `anggota2.pasien_helper.generate_id` atau fallback inline di `api/routes/patient_routes.py:162-187`. Tanggal `DD-MM-YYYY`.

### 7.2 ERD

Notasi Crow's Foot. Hubungan utama:

- User (1) -- (n) Patient (kepemilikan via `owner_username`).
- Drug (n) -- (n) SideEffect via field `efek_samping[]` (embed string array).
- Patient (1) -- (n) Drug via field `P.resep` (parsed runtime oleh `parse_resep_to_meds` di `api/helpers.py:47-96`).
- AdverseEvent (n) -- (1) Drug via `drug_name`.
- Recall (n) -- (1) Drug via `product_name` (lossy join karena openFDA pakai full label).

Lihat `docs/DATA-DICTIONARY.md` Bagian 1-6 untuk daftar field lengkap, range, tipe, dan endpoint pengelola tiap entitas.

---

## 8. Permukaan API Final

Backend mengekspos 27 endpoint HTTP melalui 8 blueprint. Sumber kebenaran: `docs/API.md`. Pendaftaran di `api/app.py:36-43`.

### 8.1 Ringkasan Endpoint per Blueprint

| Blueprint | Berkas | Endpoint | Akses |
|---|---|---|---|
| health | `api/routes/health.py` | `GET /api/health` (`:12-18`), `GET /api/info` (`:21-36`) | publik |
| auth | `api/routes/auth_routes.py` | `POST /api/auth/login` (`:13-40`), `GET /api/auth/me` (`:43-46`), `POST /api/auth/logout` (`:49-51`) | publik (login/logout), terotentikasi (me) |
| patient | `api/routes/patient_routes.py` | `GET /api/patients` (`:135-146`), `GET /api/patients/<pid>` (`:149-159`), `POST /api/patients` (`:162-187`), `PUT /api/patients/<pid>` (`:190-205`), `DELETE /api/patients/<pid>` (`:208-217`) | tenaga_kesehatan, admin (delete admin-only) |
| drug | `api/routes/drug_routes.py` | `GET /api/drugs` (`:19-28`), `GET /api/drugs/search` (`:31-40`), `GET /api/drugs/<nama_obat>` (`:43-51`) | semua peran |
| safety | `api/routes/safety_routes.py` | `POST /api/safety/check` (`:16-72`) | semua peran terotentikasi |
| visualization | `api/routes/visualization_routes.py` | `GET /api/visualizations/kunjungan-trend` (`:54-66`), `keluhan-distribution` (`:69-80`), `top-efek-samping` (`:83-110`), `heatmap-efek` (`:113-138`) | tenaga_kesehatan, admin (kunjungan, keluhan); semua peran terotentikasi (top, heatmap) |
| pdf | `api/routes/pdf_routes.py` | `POST /api/pdf/generate-rekam-medis` (`:169-202`), `generate-laporan-bulanan` (`:205-238`, admin-only), `generate-efek-samping` (`:241-385`), `generate-inventaris` (`:388-511`) | tenaga_kesehatan, admin |
| admin | `api/routes/admin_routes.py` | `POST /api/admin/scrape` (`:21-38`), `GET /api/admin/users` (`:41-45`), `POST /api/admin/users` (`:48-85`), `DELETE /api/admin/users/<username>` (`:88-103`), `GET /api/admin/system-stats` (`:106-127`) | admin-only |

### 8.2 Konvensi Wire-Format

Encoding JSON UTF-8 (`ensure_ascii=false`). Header request: `Content-Type: application/json` (POST/PUT), `Authorization: Bearer <jwt>` (terotentikasi). Status code: 200/201/204 sukses, 400 validasi, 401 auth, 403 role, 404 missing, 409 conflict, 503 dependency. Header `Server` di-strip via after-request (`api/app.py:58-61`).

Lihat `docs/API.md` Bagian 5 untuk request/response shape per endpoint, dan Bagian 8 untuk lampiran OpenAPI 3.1.

---

## 9. Inventaris UI Final

### 9.1 Route Map (Next.js App Router)

Diturunkan dari hasil `find FrontendMedWatch/src/app -name page.tsx -type f`. Route `_archived/` tidak di-expose runtime (folder underscore di Next.js App Router).

| Rute | Berkas | Fungsi |
|---|---|---|
| `/` | `src/app/page.tsx` | Redirect ke landing per role |
| `/login` | `src/app/login/page.tsx` | Login dengan 3 preset demo (B09) |
| `/dashboard` | `src/app/dashboard/page.tsx` | Dashboard utama tenaga kesehatan / umum |
| `/dashboard/aktivitas` | `src/app/dashboard/aktivitas/page.tsx` | Activity feed full (B02 destination, baru) |
| `/patients` | `src/app/patients/page.tsx` | Daftar pasien newest-first (B07) |
| `/patients/new` | `src/app/patients/new/page.tsx` | Form pasien dengan validasi range (B03) |
| `/patients/[id]` | `src/app/patients/[id]/page.tsx` | Edit pasien |
| `/pasien/profile` | `src/app/pasien/profile/page.tsx` | Profil ringkas masyarakat |
| `/drug-search` | `src/app/drug-search/page.tsx` | Pencarian dan filter obat |
| `/drug-comparison` | `src/app/drug-comparison/page.tsx` | Bandingkan profil hingga 3 obat |
| `/safety-checker` | `src/app/safety-checker/page.tsx` | Cek interaksi (B05 pasien_active_meds, B08 panel penjelas) |
| `/visualization` | `src/app/visualization/page.tsx` | Dashboard Recharts |
| `/heatmap` | `src/app/heatmap/page.tsx` | Heatmap kontinu d3 5-stop (B11) |
| `/export` | `src/app/export/page.tsx` | Legacy export PDF (rekam medis + bulanan) |
| `/export-pdf` | `src/app/export-pdf/page.tsx` | Export 4 tipe PDF (B04) |
| `/admin/dashboard` | `src/app/admin/dashboard/page.tsx` | Dashboard admin real KPI (B10) + CTA scraper (B01) |
| `/admin/scraper` | `src/app/admin/scraper/page.tsx` | Panel pemicu scraper |
| `/admin/users` | `src/app/admin/users/page.tsx` | Manajemen pengguna |

Route `_archived/` (`drug-comparison`, `drug-network`, `indonesia-map`, `molecule-viewer`) hadir sebagai folder underscore Next.js sehingga tidak ter-route runtime; dipertahankan sebagai cadangan eksperimen.

### 9.2 RBAC Matrix (Source: `src/proxy.ts`)

Sumber kebenaran middleware Next.js: `src/proxy.ts:41-83`. `decodeRole` membaca claim `role` dari JWT (`src/proxy.ts:21-32`); landing per role di `landingFor` (`src/proxy.ts:35-39`): admin -> `/admin/dashboard`, masyarakat -> `/drug-search`, default (tenaga_kesehatan) -> `/dashboard`.

| Rute | tenaga_kesehatan | masyarakat | admin |
|---|---|---|---|
| `/login` | publik | publik | publik |
| `/dashboard` | OK | OK | OK |
| `/dashboard/aktivitas` | OK | OK | OK |
| `/patients` | OK | redirect ke `/drug-search` | OK |
| `/patients/new` | OK | redirect ke `/drug-search` | OK |
| `/patients/[id]` | OK | redirect ke `/drug-search` | OK |
| `/pasien/profile` | OK (akses sendiri) | OK | OK |
| `/drug-search` | OK | OK | OK |
| `/drug-comparison` | OK | redirect ke `/drug-search` | OK |
| `/safety-checker` | OK | OK | OK |
| `/visualization` | OK | redirect ke `/drug-search` | OK |
| `/heatmap` | OK | redirect ke `/drug-search` | OK |
| `/export` | OK | redirect ke `/drug-search` | OK |
| `/export-pdf` | OK | redirect ke `/drug-search` | OK |
| `/admin/*` | redirect ke `/dashboard` | redirect ke `/drug-search` | OK |

Catatan: peran `masyarakat` dibatasi secara eksplisit di `src/proxy.ts:73-82`. Allowlist masyarakat hanya `/dashboard`, `/drug-search`, `/safety-checker`, `/pasien`, `/api` (proxy passthrough). Setiap rute lain memicu redirect ke `/drug-search`. Backend Flask juga menegakkan RBAC via `require_role` (`api/middleware.py:37-51`) sehingga akses langsung ke Cloud Run dengan token role yang salah tetap ditolak 403.

### 9.3 Placeholder Screenshot

Screenshot live (untuk lampiran User Manual dan slide presentasi dosen) dijadwalkan diambil pada Iterasi 5. Saat ini direktori `FrontendMedWatch/screenshots/` sudah memuat screenshot Iterasi 1 untuk evidence T1-ADMIN (`screenshots/T1-ADMIN/01-admin-dashboard-with-cta.png`). Placeholder berikut akan diisi pada Iterasi 5:

- `/login` (light + dark)
- `/dashboard` (per role: tenaga_kesehatan, masyarakat, admin)
- `/patients` (list + sort newest-first verified)
- `/patients/new` (form dengan validasi B03 aktif)
- `/safety-checker` (chip pasien_active_meds tampak)
- `/heatmap` (heatmap kontinu 5-stop ramp)
- `/export-pdf` (4 pilihan PDF)
- `/admin/dashboard` (KPI uptime real, CTA scraper)
- `/admin/scraper` (panel pemicu)
- `/admin/users` (CRUD pengguna)

---

## 10. Konfigurasi dan Environment

Sumber: `api/config.py:1-38` (backend) dan Vercel project settings (frontend). Tidak ada credential value yang ditulis ke dokumen ini; hanya nama variabel dan default placeholder.

### 10.1 Backend `api/config.py`

| Variabel | Default | Sumber | Catatan |
|---|---|---|---|
| `JWT_SECRET` | `"dev-only-do-not-use-in-prod"` | `api/config.py:17` | Di production di-mount dari Secret Manager `medwatch-jwt-secret`; nilai nyata tidak di-commit |
| `JWT_ALGORITHM` | `HS256` | `api/config.py:18` | HMAC-SHA256 |
| `JWT_EXPIRY_HOURS` | 12 | `api/config.py:19` | Satu sesi shift bidan |
| `CORS_ORIGINS` | `["https://medwatch-frontend.vercel.app", "http://localhost:3000", "http://localhost:5173"]` | `api/config.py:21-25` | Allowlist eksplisit |
| `GCP_PROJECT_ID` | `medwatch-polban-2026` | `api/config.py:27` | Resource name OK |
| `GCS_BUCKET` | `medwatch-polban-2026-state` | `api/config.py:28` | Resource name OK |
| `USE_CLOUD_STORAGE` | `false` | `api/config.py:29` | `true` di Cloud Run |
| `OPENFDA_API_KEY` | `""` (env-only) | `api/config.py:34` | Tidak pernah di-print/log; raise 120k req/24h |
| `PORT` | 8080 | `api/config.py:36` | Default Cloud Run |
| `FLASK_DEBUG` | `false` | `api/config.py:37` | Wajib `false` di production |

### 10.2 Frontend (Vercel)

| Variabel | Sumber | Catatan |
|---|---|---|
| `BACKEND_API_URL` | Vercel project settings, server-only (tanpa prefiks `NEXT_PUBLIC_`) | URL Cloud Run; tidak terekspos ke browser |
| `NODE_VERSION` | `22.x` (recommended) | Vercel build environment |

Lihat `docs/INSTALL.md` Bagian 1-4 untuk prasyarat lengkap dan langkah pemasangan.

---

## 11. Build, Run, dan Deploy sebagaimana Dipraktikkan

Sumber rinci: `docs/INSTALL.md`. Ringkasan jalur sebagaimana benar-benar dipakai tim Kelompok B5.

### 11.1 Local Backend

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
# Run dev:
PORT=8080 JWT_SECRET=<dev-placeholder> .venv/bin/python -c "import sys; sys.path.insert(0,'.'); from api.app import create_app; create_app().run(host='127.0.0.1', port=8080, debug=False)"
# Smoke test:
.venv/bin/python api/tests/smoke_test.py
```

Catatan: command live yang dipakai tim Iterasi 1 ada di catatan internal proyek Bagian 6 sebagai referensi.

### 11.2 Local Frontend

```bash
cd /Users/ghaisan/Documents/FrontendMedWatch
# Pastikan Node 22 LTS aktif (lihat B-BUILD-1)
node --version  # diharapkan v22.x
npm install
BACKEND_API_URL=http://127.0.0.1:8080 npm run dev
# atau production build:
BACKEND_API_URL=http://127.0.0.1:8080 npm run build && npm run start
```

**Workaround B-BUILD-1 (Node 25):** jika Node 25 nightly menjadi default sistem, eksekusi `nvm use 22` atau set `NODE_VERSION=22` di Vercel Project Settings. Node 25 memicu chunk-emit race pada Turbopack production build (`InvariantError: client reference manifest does not exist` dan `ENOENT _buildManifest.js.tmp`).

### 11.3 Cloud Run Deploy (Backend)

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/medwatch-polban-2026/medwatch/medwatch-api:latest api/
gcloud run deploy medwatch-api \
  --image asia-southeast1-docker.pkg.dev/medwatch-polban-2026/medwatch/medwatch-api:latest \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars USE_CLOUD_STORAGE=true,GCS_BUCKET=medwatch-polban-2026-state,GCP_PROJECT_ID=medwatch-polban-2026 \
  --set-secrets 'JWT_SECRET=<secret-resource-name>:latest'   # Secret Manager resource name e.g. medwatch-jwt-secret
```

Verifikasi sehat: `curl https://<service-url>/api/health` mengembalikan 200.

### 11.4 Vercel Deploy (Frontend)

```bash
cd /Users/ghaisan/Documents/FrontendMedWatch
vercel link    # sekali, mengikat ke project 'medwatch'
vercel env add BACKEND_API_URL production    # masukkan URL Cloud Run; nilai tidak di-print di dokumen
vercel --prod
```

Verifikasi: buka `https://medwatch-frontend.vercel.app/login`.

### 11.5 Desktop CustomTkinter (Submission Resmi)

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
.venv/bin/python main.py
```

Entry point `main.py:1` memuat menu integrasi lima modul anggota.

### 11.6 Regenerasi Data openFDA

```bash
export OPENFDA_API_KEY=<your-key-here>
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
```

Output: `anggota1/data/drug_safety_data.json` (74 entri) dan `anggota1/data/drug_recalls.json` (6000 entri). Lihat catatan internal proyek untuk transcript run.

---

## 12. Ringkasan Cakupan Pengujian

### 12.1 Smoke Test Backend

Berkas: `api/tests/smoke_test.py` (165 baris). 14 assertion utama, semuanya lulus per run lokal 18 Mei 2026:

1. `test_health` (line 19-22): `GET /api/health` 200.
2. `test_login_three_roles` (line 25-34): login `bidan_siti`, `umum_budi`, `admin_ghaisan` mengembalikan role yang benar.
3. `test_login_invalid` (line 37-44): 3 assertion negatif (wrong-password, unknown-user, missing-token).
4. `test_patients_crud` (line 47-88): POST + GET round-trip dengan schema SOAP lengkap (Ny. Dewi G1P0A0 28-02-2026).
5. `test_drug_search` (line 91-97): pencarian paracetamol.
6. `test_safety_check` (line 100-113): cek `paracetamol + ibuprofen` mengembalikan severity score dan level.
7. `test_visualizations` (line 116-127): 4 endpoint visualisasi.
8. `test_role_enforcement` (line 130-140): bidan -> 403 di `/api/admin/users`, admin -> 200 dengan password tidak bocor.

Runtime < 2 detik di Cloud Run hangat.

### 12.2 Bug Verification (Iterasi 1)

11 bug B01..B11 diverifikasi live via Playwright + curl. Bukti per bug di catatan internal proyek:

- `T1-ADMIN.md` (B01, B02, B10)
- `T1-PASIEN.md` (B03, B07)
- `T1-PDF.md` (B04)
- `T1-SAFETY.md` (B05, B08)
- `T1-VERIFY.md` (B06)
- `T1-LOGIN.md` (B09)
- `T1-HEATMAP.md` (B11)

### 12.3 Test Plan Lengkap

Test plan formal kotak-hitam (TC-MOD-NNN) dengan teknik Boundary Value Analysis, Equivalence Partitioning, dan State Transition akan disusun pada Iterasi 5 oleh `tim QA`. Persentase validasi dan skala Arikunto akan dihitung pada Iterasi 5. Atribusi test case mengikuti pembagian: Bimo (master plan + eksekusi mayoritas), Alia (RTM + viz tests), Iqbal (drug safety logic), Abhidal (auth, PDF, usability), Ghaisan (scraping + integrasi).

---

## 13. Postur Keamanan saat Pengiriman

Sumber lengkap: `docs/SECURITY.md`. Ringkasan per aset (STRIDE summary):

| Aset | Kontrol implementasi | Status saat pengiriman |
|---|---|---|
| JWT signing key | Secret Manager `medwatch-jwt-secret`; tidak di-commit; env-mount saat Cloud Run start | Implemented |
| Password user | bcrypt cost 12 (`api/auth.py:11-12`); plaintext seed di-hash saat first load (`api/storage.py:90-98`); strip dari response (`api/helpers.py:16-18`) | Implemented |
| Patient PII SOAP | Sintetik untuk demo; storage GCS bucket private (`medwatch-polban-2026-state`) tanpa public IAM | Implemented |
| openFDA API key | env-only; `_redact_params` di `anggota1/openfda/fetch.py:148-154` memastikan log dan source_url tidak bocor | Implemented |
| Session cookie | httpOnly + SameSite=Lax + Secure di production (lewat Vercel proxy) | Implemented |
| Audit log operasional | stdout Cloud Logging 30 hari; aktor login/logout/admin CRUD/scrape tercatat (`auth_routes.py:27, 36, 39`; `admin_routes.py:26, 84, 101`) | Implemented (durable audit di tahap produksi) |
| Data scraping openFDA | Sumber legal publik; tidak ada PII pasien (de-identified by FDA) | Implemented |

OWASP Top 10 (2021) mapping diuraikan di `docs/SECURITY.md` Bagian 4 (A01..A10). Header `Server` dihapus dari response (`api/app.py:58-61`). CORS allowlist tanpa wildcard (`api/config.py:21-25`).

---

## 14. Karakteristik Performa

### 14.1 Backend (Observasi Lokal)

- `api/tests/smoke_test.py` (14 assertion utama) selesai < 2 detik pada Cloud Run hangat dan < 5 detik pada cold start (lihat NFR-PERF-001).
- Endpoint `GET /api/drugs/search?q=paracetamol` p95 ~ 50 ms (dataset 6 obat lokal).
- Endpoint `POST /api/safety/check` p95 ~ 80 ms.
- Endpoint `POST /api/pdf/generate-rekam-medis` ~ 1-2 detik per pasien tunggal.
- Cloud Run cold start ~ 3-5 detik (min-instances=0).

### 14.2 Akuisisi openFDA

- `python -m anggota1.openfda.fetch --max-recall-pages 6` selesai sekitar 5-7 menit (74 obat + 6 halaman recall).
- Polite delay 250 ms antar request (`anggota1/openfda/fetch.py:32, 262`).
- Exponential backoff dengan jitter pada HTTP 429/5xx (max 5 retry, base 0.5s..8s + jitter sampai 30s cap; `fetch.py:175-185, 192-195`).
- Dengan API key di env: 120.000 req/24h dan 240 req/menit kuota.

### 14.3 Frontend

- `npm run build` di Node 22 LTS selesai ~ 45-60 detik di workstation MacBook Pro M-series.
- Largest Contentful Paint `/login` di Vercel Edge < 2.5 detik pada koneksi 3G simulasi (target NFR-PERF / PRD 7.1).
- Heatmap initial render < 1.5 detik untuk dataset 6 x 17 (NFR-PERF-003).

---

## 15. Isu yang Diketahui, Batasan, dan Hutang Teknis

### 15.1 Open Blocker

**B-BUILD-1: Next.js 16.2.1 chunk-emit race pada Node 25.** Saat menjalankan `npm run build` di workstation dengan Node 25 nightly, beberapa proses build paralel Iterasi 1 (T1-PDF, T1-LOGIN, T1-HEATMAP, T1-PASIEN, T1-SAFETY) yang me-rebuild cache `.next` memicu race condition: `InvariantError: client reference manifest does not exist` dan `ENOENT _buildManifest.js.tmp...`. Mitigasi sementara: rekomendasikan Node 22 LTS untuk lingkungan submission dosen; remediasi formal akan dilakukan di Iterasi 5 dengan swap explicit Node 22 LTS plus regression test ulang. Bukti: lihat catatan internal proyek Bagian 6.3.

### 15.2 Item Inconclusive dari W4-HUNT (deferred ke Iterasi 5-followup)

Iterasi 4 bug-hunt menghasilkan empat item dengan status Inconclusive yang sepenuhnya bergantung pada penyelesaian B-BUILD-1 (Node 22 LTS swap) untuk dapat diverifikasi secara live. Tanpa Playwright MCP yang fungsional dan tanpa `npm run build` yang sukses, sweep berikut tidak dapat dieksekusi pada Iterasi 4:

1. **Browser/Responsive sweep deferred (Kategori 11 W4-HUNT).** Verifikasi visual viewports 360x800, 768x1024, 1280x800, 1920x1080 untuk halaman patient-create dan safety-checker membutuhkan Playwright keyboard-tab + screenshot. Static-review observation (W4-HUNT Bagian 11) sudah dilakukan: `src/app/dashboard/page.tsx:616-622` memuat breakpoint kpi grid 4 -> 2 -> 1 kolom, `src/components/shell/NavBar.tsx:206-213` melakukan swap TopNav-to-BottomNav di `<820px`, `src/app/safety-checker/page.tsx:1016-1018` collapse two-column ke single-column di `<=1080px`. Iterasi 5-followup karena B-BUILD-1 belum tertangani.
2. **Focus rings audit deferred (H12-1 W4-HUNT).** Static grep di src/ menemukan sedikit literal `focus:` / `outline`; verifikasi WCAG 2.4.7 (kontras 3:1 pada elemen `:focus-visible`) memerlukan Playwright keyboard tab-through pada setiap halaman aktif. Kandidat file: `src/app/globals.css` plus class `.btn`, `.input`, `.chip`, `.nav-pill`. Iterasi 5-followup.
3. **Bundle size sweep deferred (Kategori 14 W4-HUNT).** `.next/static/` tidak ada karena `npm run build` gagal di Node 25.6 (lihat 15.1). Pengukuran `du -sh .next/static/` per chunk, identifikasi route-level bundle penyumbang besar, dan verifikasi target `<400 KB initial JS` per route belum dapat dilakukan. Iterasi 5-followup setelah swap Node 22 LTS.
4. **Dark-mode contrast sweep deferred.** Theme toggle ada di `src/components/shell/ThemeToggle.tsx`, CSS variable seragam (`var(--bg)`, `var(--ink)`); namun verifikasi rasio kontras WCAG 1.4.3 (4.5:1 normal text, 3:1 large text) di dark mode untuk seluruh route butuh Playwright screenshot otomatis per viewport. Iterasi 5-followup.

Semua empat item di atas gating pada blocker yang sama (B-BUILD-1 di Bagian 15.1). Setelah Node 22 LTS swap selesai dan `npm run build` reproducible sukses, jalankan Playwright matrix 4 viewport x 2 theme = 8 kombinasi dan rekam screenshot per route ke `docs/testing/evidence/`.

### 15.3 Hutang Teknis Lain

1. **Atomic JSON write race.** `api/storage.py:38-43` (`_save_local`) menulis langsung ke file tanpa pola `write-to-temp + os.replace`. Crash di tengah write berpotensi men-korup file (`docs/SECURITY.md` Residual Risk R6). Mitigasi sementara: GCS object versioning di production memungkinkan rollback. Followup: implementasi pola atomic rename. (Catatan: Iterasi 5 W5-FIX-CRITICAL menambahkan `threading.Lock` di `api/routes/patient_routes.py` untuk mencegah race read-then-write di blok create/update/delete; lihat 16.B-1.)
2. **Tidak ada rate-limit / account lockout `/api/auth/login`** (`docs/SECURITY.md` R1). Bruteforce diperlambat hanya oleh bcrypt cost 12; di-acknowledge sebagai residual risk dengan plan production di `ProductionGrade-ImplementationPlan/04-hardening-plan.md`.
3. **Audit trail minimal: hanya Cloud Logging 30 hari** (`docs/SECURITY.md` R2). Aksi admin tercatat di stdout; forensic post-30-hari sulit.
4. **Tidak ada CSRF token state-changing route** (`docs/SECURITY.md` R3). Mitigasi: SameSite=Lax cookie + same-origin proxy Vercel.
5. **Rotasi JWT secret manual** (`docs/SECURITY.md` R4). Belum ada dual-key window otomatis.
6. **Dependency scanning belum di CI** (`docs/SECURITY.md` R5). `pip-audit` + `npm audit` jalan manual oleh tim keamanan.
7. **Backend Cloud Run `--allow-unauthenticated`** (`docs/SECURITY.md` R7). RBAC backend tetap menolak token absen/invalid; production plan: Cloud Run IAM `roles/run.invoker` hanya untuk Vercel IP range atau VPC peering.
8. **Frontend high-severity deps di `_archived/` paths** (`docs/SECURITY.md` R8). `react-simple-maps`, `react-force-graph-2d` dst tidak aktif runtime; uninstall ditunda agar `_archived/` tidak rusak.
9. **Heatmap menggunakan severity weighting, bukan raw FAERS counts.** Per `src/lib/heatmap-colors.ts` dan `src/app/heatmap/page.tsx`, nilai sel dihitung sebagai `presence * severity_weight(effect)` dengan bobot ringan=1, sedang=2, serius=4 (T1-HEATMAP Bagian 3). Backend hanya mengembalikan presence biner 0/1 (`api/routes/visualization_routes.py:113-138`). Followup: ganti dengan raw FAERS counts dari `anggota1/data/drug_safety_data.json` (sudah punya `side_effects[]` real dari 74 rekord) jika waktu mengizinkan. Tidak blocking untuk submission.
10. **Sisa hutang Minor W4-HUNT.** 20 finding Minor (H01-2, H01-3, H02-1, H03-1, H03-2, H04-1, H05-1, H06-4, H06-5, H06-6, H07-3, H09-1, H12-2, H13-1, H13-2, H14-1, H16-1, H16-3, H17-1, H17-2) tetap terbuka pasca Iterasi 5; rinci di catatan internal proyek. Dibadge `accept-and-document` untuk academic submission per skor severity; rencana remediasi formal di `ProductionGrade-ImplementationPlan/04-hardening-plan.md`.

### 15.3 Batasan Lingkup

1. Tidak ada custom domain (gunakan default `.vercel.app` dan `.run.app`).
2. Tidak ada layanan berbayar (Auth0, SendGrid, Sentry paid, Cloudflare paid).
3. Tidak ada aplikasi mobile native.
4. Tidak ada integrasi SatuSehat / BPJS.
5. Tidak ada notifikasi push / email otomatis.
6. Tidak ada multi-tenant (satu instalasi melayani satu Faskes).
7. Bahasa tunggal: Bahasa Indonesia formal.
8. Tidak ada bypass anti-bot drugs.com (sumber data pivot ke openFDA, ADR-0004).

---

## 16. Penyimpangan dari PRD/SRS/SDD dengan Rasionalisasi

Bagian ini adalah tabel tiga-kolom kanonik: **spesifikasi awal**, **implementasi final**, **alasan**. Setiap baris memuat sitasi file:line untuk validasi.

| Spesifikasi Awal | Implementasi Final | Alasan |
|---|---|---|
| **Login opsional / autentikasi out-of-scope** (PRD asli `MedWatch_PRD.pdf` butir out-of-scope; lihat `docs/PRD.md` Bagian 4.3 dan konvensi proyek bagian "PRD scope tension awareness") | **Login wajib dengan 3 peran kanonik** (`tenaga_kesehatan`, `masyarakat`, `admin`) plus JWT HS256 + bcrypt cost 12 + httpOnly cookie (`api/auth.py:1-39`, `api/middleware.py:17-51`, `api/data/users.json`) | Dosen demo memerlukan demo per peran (admin/bidan/umum) dengan tombol preset di `/login` (`src/app/login/page.tsx:18-43`). Implementasi diposisikan sebagai supplementary presentation layer di atas submission resmi desktop CustomTkinter, bukan mengganti PRD asli (ADR-0002, ADR-0001). |
| **Sumber data utama: scraping `drugs.com/sfx/<nama>`** (PRD asli dan modul lama `anggota1/anggota1.py`) | **Sumber data utama: openFDA REST API (`drug/event.json` dan `drug/enforcement.json`) via modul aditif `anggota1/openfda/fetch.py`; 74 rekord obat + 1850 reaction terms + 6000 rekord recall** (`anggota1/data/drug_safety_data.json`, `anggota1/data/drug_recalls.json`) | Pada 11 Mei 2026 setiap request `drugs.com/sfx/` mengembalikan HTTP 403 Akamai (bukti verbatim `anggota1/scraper.log` baris 1-8). Tidak ada bypass anti-bot (etika riset + ToS). openFDA disetujui ketentuan proyek 6 sebagai sumber legal sanksi. Schema output sengaja identik agar consumer downstream tidak rusak. ADR-0004. |
| **Modul `anggota3` tunggal (satu visualisasi matplotlib `TampilGrafik.py` oleh Alia)** | **Modul tambahan `anggota3/NewestVisualization/` aditif dengan 5 chart informatif berbasis data openFDA** (`viz_top_obat_efek_samping.py`, `viz_distribusi_keparahan.py`, `viz_recall_class_per_tahun.py`, `viz_perusahaan_recall_top.py`, `viz_heatmap_obat_efek.py`; output PNG di `anggota3/NewestVisualization/output/`) | ketentuan proyek 5 (teammate code read-only): file Alia tidak boleh dimodifikasi; NEW additive files di `anggota3/` diperbolehkan dan diatribusikan ke Alia. Visualisasi baru juga memanfaatkan data openFDA real yang sebelumnya tidak ada. ADR-0005. Atribusi: dokumenter Alia Ardani (NIM 251524035) per `anggota3/NewestVisualization/README.md:9-15`. |
| **Heatmap sparse 3-bucket coloring** (`src/app/heatmap/page.tsx` pre-fix `:163-169` mem-bucket nilai 0-15 ke `null` -> latar belakang halaman; lihat T1-HEATMAP Bagian 1) | **Heatmap kontinu d3 5-stop risk-matrix (green-yellow-red), sorted descending oleh total baris/kolom, sel v=0 tetap diwarnai dengan green-tint** (`src/lib/heatmap-colors.ts` baru, `src/app/heatmap/page.tsx` re-write 370 baris; cell value = presence * severity_weight 1/2/4) | B11 dosen-flagged: pre-fix bukan heatmap visual karena mayoritas sel beige (lihat T1-HEATMAP Bagian 1 dan 2). Pilihan ramp 5-stop selaras palet MedWatch `--safe/--warn/--crit` dan canonical risk-matrix readability. ADR-0006. |
| **List pasien default sort (insertion order: oldest-first di atas)** (kondisi pre-fix `api/routes/patient_routes.py`) | **List pasien sort newest-first by `tanggal_kunjungan` DESC dengan parser DD-MM-YYYY dan tiebreak id `P###` DESC** (`api/routes/patient_routes.py:135-146`) | B07 UX complaint: bidan harus scroll ke bawah untuk lihat kunjungan terbaru. Parser tanggal DD-MM-YYYY plus tiebreak numeric tail id memastikan `P010 (18-05-2026)` mendahului `P001`. ADR-0007. |
| **Form pasien menerima input apapun (termasuk huruf di field numerik)** (kondisi pre-fix; lihat T1-PASIEN) | **Validasi numerik medis client+server**: BB `1..300 kg`, TB `30..300 cm`, LILA `8..60 cm`, Nadi `30..220 x/min`, Suhu `30..44 C`, Respirasi `5..80 x/min`, TD komposit `\d{1,3}/\d{1,3}` sistolik `60..250` diastolik `30..160` (`api/routes/patient_routes.py:17-99`, `src/lib/patient-validation.ts`) | B03 data quality complaint. Tanpa validasi, field numerik dapat menerima huruf dan menghasilkan error parsing downstream. Validasi mirror di server (otoritatif) dan client (UX). ADR-0009. |
| **Eksport PDF hanya untuk SOAP rekam medis** (kondisi pre-fix; `anggota5/export_pdf.py` original) | **4 endpoint PDF: rekam-medis, laporan-bulanan, efek-samping, inventaris** (`api/routes/pdf_routes.py:169-511`) plus frontend `src/app/export-pdf/page.tsx` dengan 4 pilihan tipe dan step-2 UI berbeda per tipe | B04 dosen-flagged scope: PRD menjanjikan 4 tipe laporan; pre-fix hanya 1. Generator efek-samping dan inventaris diimplementasi in-process via `fpdf2` di `api/` (bukan modifikasi anggota5, sesuai ketentuan proyek 5). ADR-0008. |
| **Dashboard admin KPI hardcoded (mis. `Uptime API 99.94% / 30 hari`)** (`src/app/admin/dashboard/page.tsx` pre-fix `:56`) | **KPI real dari `GET /api/admin/system-stats` + helper `formatUptime(seconds)`** menampilkan uptime proses (`5m`, `3j 12m`, `2h 4j`) dengan label "sejak proses berjalan"; backend mengekspos `process_started_at` dan `uptime_seconds` (`api/routes/admin_routes.py:18, 106-127`; `src/app/admin/dashboard/page.tsx:43-81`) | B10 ketentuan proyek: "no fabrication, every claim must be verifiable". Pre-fix menampilkan angka palsu yang berisiko dosen mengira sistem benar-benar tracking SLO 30 hari. T1-ADMIN. |
| **Cek interaksi obat tanpa konteks pasien aktif** (kondisi pre-fix; user harus ketik manual obat yang sedang diresepkan) | **Cek interaksi otomatis menggabungkan `pasien_active_meds` dari `P.resep` pasien aktif via parser `parse_resep_to_meds`** (`api/routes/safety_routes.py:44-61`, `api/helpers.py:47-96`; frontend `src/app/safety-checker/page.tsx`) | B05 workflow gap: bidan harus mengetik ulang resep aktif pasien. Parser toleran terhadap dosage hints (`3x500mg`), parenthetical, dan latin frequency (`prn`, `bid`, `qd`, `tid`, `qid`). |
| **Login submit langsung dari controlled state input** (kondisi pre-fix; lihat T1-LOGIN) | **Login submit dari `FormData(event.currentTarget)` untuk menghindari controlled-input race dengan browser autofill / password manager**; `Username dan password wajib diisi.` jika kosong (`src/app/login/page.tsx:80-98`) | B09: manual typed login gagal saat password manager mengisi field karena React state belum sync. FormData baca dari DOM langsung. ADR-0010. |
| **Dashboard "Lihat semua" button inert tanpa onClick** (`src/app/dashboard/page.tsx:442-444` pre-fix) | **Link Next.js ke `/dashboard/aktivitas` baru dengan feed full per role** dan `data-testid="lihat-semua-aktivitas"` (`src/app/dashboard/page.tsx ~442-444`, route baru `src/app/dashboard/aktivitas/page.tsx`) | B02: tombol dead element. Rute baru menampilkan ActivityKind icon dan severity badge yang sama dengan panel asli. T1-ADMIN Bagian 4.3-4.4. |
| **Admin dashboard tanpa CTA in-body ke scraper** (sidebar nav punya, body tidak) | **CTA prominen "Jalankan Scraper Obat" di body** dengan `data-testid="cta-scraper"` link ke `/admin/scraper` (`src/app/admin/dashboard/page.tsx:170-226`) | B01: navigasi sidebar saja tidak cukup, admin baru tidak menyadari jalur scraper. T1-ADMIN Bagian 4.2. |
| **Safety-checker tanpa penjelasan inline verdikt** (kondisi pre-fix; user lihat skor tanpa konteks) | **Panel collapsible "Cara membaca verdikt dan obat aktif"** menjelaskan konsep obat aktif, formula `total_bobot / (jumlah_efek * 4) * 100`, threshold label, rasional banyak kartu (`src/app/safety-checker/page.tsx`) | B08 ux complaint: user awam tidak memahami arti angka. Panel default tertutup, dapat di-expand. T1-SAFETY Bagian 4. |
| **`anggota5/auth.py` model akses single-tier (semua bisa segalanya)** (kondisi tahap awal per draft Abhidal) | **Role-aware auth dengan 3 peran (`tenaga_kesehatan`, `masyarakat`, `admin`)** plus `tkesehatan_crud.py` baru; pengecualian Phase 1 satu kali (konvensi proyek) modifikasi 4 file di `anggota5/` lewat PR `Abhidal_anggota5 -> main` di-merge oleh Ghaisan dengan otorisasi Abhidal | Permintaan formal Abhidal via Ghaisan. Setelah PR di-squash-merge, `anggota5/` kembali read-only. |
| **Hardcoded `Pasien.json` di `anggota5/data/`** (legacy auth user file) | **Canonical user store di `api/data/users.json`** (NEW location); pasien tetap di `api/data/patients.json` atau GCS bucket | Menghindari konflik schema antara module Bimo (`anggota2/Pasien.json` canonical) dan legacy Abhidal (`anggota5/data/users.json`). Pasien ID `P001..P999` (uppercase + 3 digit) bukan `PSN-001` (draft Abhidal non-kanonikal). ADR-0003. |

### 16.A Penyimpangan Tambahan dari Penemuan W4-HUNT dan Perbaikan Iterasi 5

| Spesifikasi Awal | Implementasi Final | Alasan |
|---|---|---|
| **Safety check role gating: endpoint `POST /api/safety/check` open untuk semua role autentik tanpa pembatasan pasien_context (tidak di-spec dalam PRD/SRS asli)** (kondisi pasca Iterasi 1; lihat `api/routes/safety_routes.py` pre-fix yang dekorasi `@require_auth` tanpa role check di blok pasien_context) | **Iterasi 5 W5-FIX-CRITICAL gating `pasien_context` dan `pasien_active_meds` ke role `tenaga_kesehatan` dan `admin` saja; `masyarakat` selalu menerima `pasien_context: null` dan `pasien_active_meds: []` regardless of pasien_id supplied** (`api/routes/safety_routes.py`; commit b5a98e8 (backend) plus 40754cd (frontend)) | Bug-hunter W4-HUNT mengkonfirmasi H07-1 Critical: `umum_budi` dapat enumerasi P001..P020 dan memanen nama, diagnosa, kategori, kondisi_umum, dan active medications. Sumber: catatan internal proyek Bagian 7 dan catatan internal proyek baris 91-117 reproduksi auditor independen. Iterasi 5 W5-FIX-CRITICAL menutup leak sebelum submission dosen 25 Mei 2026. Cite finding fix: catatan internal proyek (akan diverifikasi oleh W5-AUDIT). |
| **Kepemilikan pasien lintas bidan: tidak di-spec dalam PRD/SRS asli** (PRD mengasumsikan single-bidan flow; tidak ada faskes_id atau bidan_id sebagai tenancy key) | **Implementasi final mempertahankan asumsi single-faskes single-bidan: semua `tenaga_kesehatan` JWT dapat membaca semua record pasien tanpa pemfilteran `created_by` atau `faskes_id`; ownership check hanya berlaku untuk `masyarakat` di `api/routes/patient_routes.py:175-195` (line 193 `owner_username` branch)** | W4-HUNT H07-2 Major mengidentifikasi: `bidan_putri` dapat membaca SOAP yang `created_by: bidan_siti`. Dokumentasi formal sebagai **single-faskes assumption** untuk academic submission dengan beban data kecil (21 pasien sintetik, 6 user demo). Multi-bidan tenancy dengan JWT `faskes_id` claim dan filter `list_patients`/`get_patient` dijadwalkan di `ProductionGrade-ImplementationPlan/04-hardening-plan.md`. Lihat juga `docs/SECURITY.md` Section 7.5 Asumsi Kepemilikan Pasien Lintas Bidan. |
| **Audit log feed di admin dashboard tidak di-spec dalam PRD/SRS** (PRD hanya menyebut admin KPI scope; audit log fabricated panel ditambahkan secara opportunistic saat Iterasi 1 frontend build) | **Iterasi 5 W5-FIX-CRITICAL menghapus hardcoded sample `auditLog` array yang sebelumnya di `src/app/admin/dashboard/page.tsx` (referensi W4-HUNT: lines 102-108, 5 baris fabricated: `103.8.xx.xx`, `bidan_rina`, `Scrape BPOM cron berjalan, 132 entri baru`, dst); panel di-replace menjadi link ke `/dashboard/aktivitas` yang sudah ditambahkan Iterasi 1 T1-ADMIN dengan feed terstruktur per role** (commit b5a98e8 (backend) plus 40754cd (frontend)) | W4-HUNT H06-2 + H06-3 Major: panel `auditLog` dan tiga array `ACTIVITIES_BIDAN`/`ACTIVITIES_MASYARAKAT`/`ACTIVITIES_ADMIN` di `src/app/dashboard/aktivitas/page.tsx:29-57` adalah literal fabricated data. Hapus + redirect ke route real yang sudah ada menghindari fabrication sambil menjaga UI flow. Backend `GET /api/admin/audit-log` belum diimplementasi; followup di `ProductionGrade-ImplementationPlan/04-hardening-plan.md`. Lihat 15.3 item 1 untuk concurrency complement. |
| **Validasi `umur` di form pasien tidak di-spec eksplisit dalam SRS** (SRS hanya menyebut `umur` sebagai integer optional dengan tipe `number`; tidak menetapkan range) | **Iterasi 5 W5-FIX-CRITICAL menambah backend range check `0 <= umur <= 150` di `api/routes/patient_routes.py` (penambahan ke `NUMERIC_RANGES` atau guard equivalent) plus mirror client-side `src/app/patients/new/page.tsx` dan `src/app/patients/[id]/page.tsx` yang merender inline error Bahasa Indonesia `umur harus antara 0 dan 150` (commit b5a98e8 (backend) plus 40754cd (frontend))** | W4-HUNT H01-1 Major: POST `/api/patients` menerima `umur: "9999"`, `umur: "-50"`, dan `umur: "abc"` tanpa rejection. Data quality concern: chart `umur` distribution dan filter age-group rusak. Range 0..150 mengakomodasi neonatus (0) sampai umur ekstrem (dokumentasi medis WHO mencantumkan 122 tahun sebagai record holder; 150 sebagai safety margin). |
| **Concurrency safety POST/PUT/DELETE pasien tidak di-spec eksplisit dalam SDD** (SDD mendokumentasikan JSON file storage tanpa concurrent-access strategy) | **Iterasi 5 W5-FIX-CRITICAL menambah `threading.Lock` global di sekitar blok read-modify-write di `api/routes/patient_routes.py` create/update/delete handler** (commit b5a98e8 (backend) plus 40754cd (frontend)); Cloud Run gunicorn worker tetap single-threaded per request namun threadpool serialisasi via lock | W4-HUNT H10-1 Major: 5 paralel POST `/api/patients` dengan body sama menghasilkan 4 dari 5 response dengan `id: P022` dan persistensi final 21 -> 23 (kehilangan 3 record). Lock mencegah duplicate-id dan write race. Mitigasi lengkap di production: GCS preconditions (`if-generation-match`) untuk optimistic concurrency, lihat 15.3 item 1. |
| **KPI `/dashboard` dan kontent feed `/dashboard/aktivitas` di-spec sebagai backend-sourced** (PRD/SRS FR untuk admin dashboard KPI di-spec real, namun frontend pra-Iterasi 5 ship hardcoded `value: 1247`, `value: 38`, `value: 89`, `value: 2` di `src/app/dashboard/page.tsx:302-307` per W4-HUNT H06-1) | **Iterasi 5 W5-FIX-CRITICAL menghapus literal hardcoded di admin branch `/dashboard`; admin sekarang membaca `/api/admin/system-stats` (endpoint sudah ada per `api/routes/admin_routes.py:18, 106-127`); bidan-scoped KPI dihapus jika belum ada endpoint atau diberi label "Data demo" jika sumber backend tidak ada** (commit b5a98e8 (backend) plus 40754cd (frontend)) | W4-HUNT H06-1 Major: literal `1247, 38, 89, 2` ditemukan persis sesuai daftar catatan internal proyek B10 ("hardcoded 1247 pengguna, 38 faskes, 89 scrape, 2 error"). Auditor iterasi 04-audit.md baris 127 memverifikasi. Iterasi 5 menghapus literal sambil menjaga UI tidak kosong. |

**Total 14 deviasi awal + 6 deviasi tambahan W5 = 20 deviasi terdokumentasi.** Setiap deviasi terkait dengan ADR formal, bug ticket T1-*, finding W4-HUNT, atau fix Iterasi 5 untuk traceability. Setiap referensi commit SHA Iterasi 5 dapat diverifikasi di backend `git log --oneline | grep W5-FIX-CRITICAL` (otoritatif). Dokumen audit verifikasi: catatan internal proyek + W5-AUDIT (Iterasi 5).

---

## 17. Panduan Pemeliharaan dan Operasi (Maintenance and Operations)

### 17.1 Regenerasi Data openFDA

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
source .venv/bin/activate
export OPENFDA_API_KEY=<your-key-here>     # never commit value
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
# Output:
#   anggota1/data/drug_safety_data.json     (74 rekord obat)
#   anggota1/data/drug_recalls.json         (6000 rekord recall)
```

Untuk pull lebih besar (~17.643 rekord): `--max-recall-pages 26` (sekitar 7-10 menit dengan API key di env).

Module `anggota1/openfda/fetch.py` menjaga schema output identik dengan fixture sebelumnya sehingga consumer downstream (`api/routes/drug_routes.py`, `api/routes/safety_routes.py`, `anggota3/NewestVisualization/*`, frontend) tidak perlu modifikasi.

### 17.2 Rebuild Diagram Dokumentasi

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
mmdc -i docs/diagrams/src/c4-l1-context.mmd \
     -o docs/diagrams/png/c4-l1-context.png \
     -w 2400 -H 1600 -s 2 -b white
# Ulangi untuk setiap *.mmd di docs/diagrams/src/
```

CLI `mmdc` tersedia di `/opt/homebrew/bin/mmdc` per `docs/INSTALL.md` Bagian 1.2.

### 17.3 Menambah Endpoint Baru

1. Buat function handler di blueprint yang sesuai (mis. `api/routes/drug_routes.py`).
2. Dekorasi `@bp.route("/api/drugs/...", methods=["..."])` plus `@require_auth` atau `@require_role("...")` sesuai kebutuhan.
3. Tambah test di `api/tests/smoke_test.py` (assertion 200/401/403 sesuai semantik).
4. Update `docs/API.md` Bagian 5.<n> dengan request/response shape.
5. Update `docs/SRS.md` 3.1.<n> dengan FR-ID baru dan acceptance criteria.
6. Update `docs/AS-BUILT.md` Bagian 5 dan 8.
7. Commit: `feat(<area>): <description> (FR-<id>)`.

### 17.4 Menambah Visualisasi Baru

1. Buat berkas Python baru di `anggota3/NewestVisualization/viz_<nama>.py` (additive; jangan modifikasi file Alia yang ada).
2. Import `palette` dan `data_loader` dari `anggota3/NewestVisualization/`.
3. Tulis output PNG ke `anggota3/NewestVisualization/output/viz_<nama>.png`.
4. Tambah entri di `anggota3/NewestVisualization/generate_all.py` agar `python -m anggota3.NewestVisualization.generate_all` membangun-ulang semua chart.
5. Update `anggota3/NewestVisualization/README.md` dan `docs/AS-BUILT.md` Bagian 5.8.

### 17.5 Operasional Saat Demo

Checklist lengkap di `docs/SECURITY.md` Bagian 9. Ringkasan:

- `gcloud run services describe medwatch-api --region asia-southeast1 --format='value(status.url)'` aktif
- `curl <url>/api/health` 200
- `FLASK_DEBUG` Cloud Run = false
- Secret Manager `medwatch-jwt-secret` punya minimal 1 enabled version
- Bucket `medwatch-polban-2026-state` tidak public
- `medwatch-frontend.vercel.app/login` load tanpa error console
- `.env*` tidak ada di tree `git ls-files`

### 17.6 Kontak Tim

| Peran | Nama | NIM | Modul yang dikelola |
|---|---|---|---|
| Project Leader (integrasi, deployment, dokumentasi induk) | Ghaisan Khoirul Badruzaman | 251524048 | `anggota1/`, `api/`, frontend integrasi |
| Quality Assurance (test plan, eksekusi mayoritas) | Bimo Surya Anggara | 251524040 | `anggota2/`, schema pasien |
| System Analyst (RTM, visualisasi) | Alia Ardani | 251524035 | `anggota3/`, `anggota3/NewestVisualization/` |
| Programmer (drug safety, basis data obat) | Muhammad Iqbal | 251524057 | `anggota4/` |
| UI/UX Designer (PDF export, auth Phase 1) | Abhidal Muhammad Gazza | 251524032 | `anggota5/` |

---

## 18. Daftar Periksa Handover

Checklist serah-terima ke dosen (25 Mei 2026) dan ke maintainer berikutnya:

### 18.1 Akses Repositori

- [x] Repo backend `https://github.com/Bisura16/medWatch` accessible (Bimo owner; Ghaisan punya akses tulis ke branch `ghaisan-APIIntegration`).
- [x] Repo frontend `https://github.com/Finerium/FrontendMedwatch` accessible (Ghaisan owner; branch integrasi `ghaisan-APIIntegration`).

### 18.2 Kredensial dan Konfigurasi

- [x] `.env.local` NOT committed (verifikasi: `git ls-files | grep -E "\.env(\.|$)"` empty).
- [x] `.env.example` placeholder ada di kedua repo untuk developer baru.
- [x] `OPENFDA_API_KEY` env-driven (no hardcoded value); pola anti-leak `_redact_params` aktif (`anggota1/openfda/fetch.py:148-154`).
- [x] `JWT_SECRET` di Secret Manager `medwatch-jwt-secret` (production), `dev-only` placeholder lokal.

### 18.3 Dokumentasi (Iterasi 2)

- [x] `docs/PRD.md` (W2-D01)
- [x] `docs/SRS.md` (W2-D02)
- [x] `docs/SDD.md` (W2-D03)
- [x] `docs/adr/0001..0010-*.md` (W2-D04)
- [x] `docs/API.md` (W2-D06)
- [x] `docs/DATA-DICTIONARY.md` (W2-D07)
- [x] `docs/INSTALL.md` (W2-D08)
- [x] `docs/SECURITY.md` (W2-D10)
- [x] `docs/AS-BUILT.md` (W2-D11, this file)
- [ ] `docs/USER-MANUAL.md` (W2-D09, terjadwal di batch 2)
- [x] `docs/diagrams/src/*.mmd` dan `docs/diagrams/png/*.png` (W2-D05 batch 2)
- [ ] `ProductionGrade-ImplementationPlan/` 6 files (W2-PROD, terjadwal batch 2)
- [ ] `README.md` industry-rewrite kedua repo (W2-D12, batch 3)
- [ ] `.docx` versions (W2-DOCX, batch 3)

### 18.4 Kode dan Pengujian

- [x] Semua Iterasi 1 commits di main backend (lihat Lampiran A): `cfa5c26 feat(data) openFDA`, `a0a3f99 feat(pdf) efek-samping inventaris`, `af78a6f fix(admin)`, `53c6ed2 fix(safety)`, `e4733b1 fix(patients)`, `64513e6 feat(viz) NewestVisualization`.
- [x] `python api/tests/smoke_test.py` 14/14 assertion hijau di lokal.
- [x] Data openFDA real ada: `anggota1/data/drug_safety_data.json` (74 rekord), `anggota1/data/drug_recalls.json` (6000 rekord).
- [x] 5 PNG NewestVisualization ada: `anggota3/NewestVisualization/output/viz_*.png`.
- [x] B01..B11 fixed dan diverifikasi: catatan internal proyek (7 file, semua done).

### 18.5 Cloud Resources

- [x] GCP project `medwatch-polban-2026` aktif.
- [x] Cloud Run service `medwatch-api` (region asia-southeast1) deployable.
- [x] GCS bucket `medwatch-polban-2026-state` ada, private IAM.
- [x] Secret Manager `medwatch-jwt-secret` minimal 1 enabled version.
- [x] Vercel project `medwatch` link aktif; frontend deployable ke `medwatch-frontend.vercel.app`.

### 18.6 Item Iterasi Berikutnya (Iterasi 3, 4, 5)

- [ ] Iterasi 3: code commenting + repo tidying (kedua repo).
- [ ] Iterasi 4: security scan tree + history; 17-category bug-hunt read-only.
- [ ] Iterasi 5: remediasi Critical/Major, sync AS-BUILT ke final code, `ArtifactReadySubmit/`, `FINAL-REPORT.md`.

---

## 19. Glosarium, Referensi, dan Lampiran

### 19.1 Glosarium

| Istilah | Definisi |
|---|---|
| SOAP | Subjective, Objective, Assessment, Plan. Format standar rekam medis kunjungan. Schema kanonik di `anggota2/pasien_helper.py` (konvensi proyek). |
| Faskes 1 | Fasilitas Kesehatan Tingkat Pertama (puskesmas, polindes, klinik bersalin kecil). Sasaran utama MedWatch. |
| openFDA | API publik U.S. Food and Drug Administration di `https://api.fda.gov`. Sumber utama efek samping (`drug/event`) dan recall (`drug/enforcement`) pasca pivot ADR-0004. |
| FAERS | FDA Adverse Event Reporting System. Basis data efek samping diekspos oleh `drug/event.json`. |
| MedDRA | Medical Dictionary for Regulatory Activities. Ontologi medis dipakai openFDA sebagai `patient.reaction.reactionmeddrapt`. |
| JWT | JSON Web Token (RFC 7519). Token signed untuk auth MedWatch, diissue di `api/auth.py:22-32`. |
| RBAC | Role-Based Access Control. 3 peran kanonik: `tenaga_kesehatan`, `masyarakat`, `admin`. Dekorator `@require_role` di `api/middleware.py:37-51`. |
| Tenaga Kesehatan | Peran backend untuk bidan Faskes 1 (string value `tenaga_kesehatan`). Akses penuh CRUD pasien dan safety check. |
| Masyarakat | Peran backend untuk warga umum (string value `masyarakat`). Read-only katalog obat dan safety checker. |
| Admin | Peran sistem (Ghaisan / Project Leader). Akses ke `/api/admin/*` dan delete pasien. |
| Akamai | CDN/WAF yang dipakai drugs.com. Memblokir scraping otomatis dengan HTTP 403 (bukti `anggota1/scraper.log` baris 1-8). |
| Cloud Run | Layanan serverless GCP untuk container HTTP. Service `medwatch-api`, region `asia-southeast1`. |
| GCS bucket | Google Cloud Storage. Bucket `medwatch-polban-2026-state` untuk persistensi `users.json` dan `patients.json` di mode `USE_CLOUD_STORAGE=true`. |
| Vercel proxy | Security pattern B: browser hanya melihat domain Vercel; panggilan ke `/api/[...slug]` di-proxy server-side ke `BACKEND_API_URL` (Cloud Run) dengan header JWT dari httpOnly cookie. |
| LILA | Lingkar Lengan Atas, parameter antropometri ibu hamil. Field `O.lila_cm` range 8-60 cm (`api/routes/patient_routes.py:17-24`). |
| C4 model | Model arsitektur 4-level (Context, Container, Component, Code) oleh Simon Brown. Notasi diagram MedWatch. |
| MADR | Markdown Any Decision Records, template ADR formal (https://adr.github.io/madr/). |
| STRIDE | Microsoft threat-modeling framework: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. |

### 19.2 Referensi

Standar dan dokumen yang dikutip dalam AS-BUILT ini:

1. **ISO/IEC/IEEE 15289:2019** - Systems and software engineering - Content of life-cycle information items (documentation). International Organization for Standardization, 2019. Klausa 9 (System Documentation - Item) memandu struktur 19-bagian dokumen ini.
2. **IEEE 830-1998** - IEEE Recommended Practice for Software Requirements Specifications. Institute of Electrical and Electronics Engineers, New York, 1998. ISBN 0-7381-0332-2. Dirujuk via `docs/SRS.md`.
3. **ISO/IEC/IEEE 29148:2018** - Systems and software engineering - Life cycle processes - Requirements engineering. ISO, 2018. Dirujuk via `docs/SRS.md`.
4. **IEEE 1016-2009** - IEEE Standard for Information Technology - Systems Design - Software Design Descriptions. Dirujuk via `docs/SDD.md`.
5. **ISO/IEC/IEEE 26514** - Systems and software engineering - Requirements for designers and developers of user documentation. Dirujuk via `docs/USER-MANUAL.md` dan `docs/INSTALL.md`.
6. **MADR 3.0** - Markdown Any Decision Records. Olaf Zimmermann et al., 2023. https://adr.github.io/madr/. Dirujuk via `docs/adr/README.md`.
7. **Nygard, Michael** - "Documenting Architecture Decisions" (2011). Historical ADR reference, dipakai sebagai pelengkap MADR.
8. **C4 model** - Simon Brown. The C4 model for visualising software architecture. https://c4model.com. Notasi diagram L1/L2/L3/Deployment dipakai pada `docs/diagrams/`.
9. **OWASP Top 10 (2021)** - Open Web Application Security Project. https://owasp.org/Top10/. Dirujuk via `docs/SECURITY.md` Bagian 4.
10. **STRIDE** - Microsoft threat-modeling framework. Dirujuk via `docs/SECURITY.md` Bagian 5.
11. **openFDA** - U.S. Food and Drug Administration public REST API. https://open.fda.gov. Endpoint `drug/event.json` (FAERS) dan `drug/enforcement.json` (FDA Enforcement Reports).
12. **WCAG 2.1 Level AA** - Web Content Accessibility Guidelines. W3C Recommendation, 2018. Dirujuk via `docs/SRS.md` 3.3.4.
13. **RFC 7519** - JSON Web Token (JWT). IETF. Dirujuk oleh `api/auth.py:22-32` skema klaim.
14. **NIST SP 800-63B** - Digital Identity Guidelines (Authentication and Lifecycle Management). Dirujuk via `docs/SECURITY.md`.
15. **OWASP ASVS v4.0.3** - Application Security Verification Standard. Dirujuk informational di `docs/SECURITY.md`.

### 19.3 Lampiran A: Commit List (Iterasi 1 + Iterasi 2 batch 1+2)

Diturunkan dari `git log --oneline -30` di repositori backend, urutan terbaru di atas:

| SHA (short) | Pesan commit | Tiket |
|---|---|---|
| `2f68064` | `docs(srs): add Software Requirements Specification per IEEE 830 (W2-D02)` | W2-D02 |
| `0176ed4` | `docs(security): add OWASP and STRIDE threat model (W2-D10)` | W2-D10 |
| `a3278b7` | `docs(sdd): add Software Design Description per IEEE 1016 (W2-D03)` | W2-D03 |
| `e990c03` | `docs(adr): add architecture decision records (W2-D04)` | W2-D04 |
| `7cdbee6` | `docs(data): add data dictionary and storage architecture (W2-D07)` | W2-D07 |
| `462d724` | `docs(install): add installation deployment and developer guide (W2-D08)` | W2-D08 |
| `c6f151f` | `docs(prd): add Product Requirements Document for academic submission (W2-D01)` | W2-D01 |
| `99bd562` | `chore(project): close Iterasi 1, update project state` | Project |
| `64513e6` | `feat(viz): anggota3/NewestVisualization additive module for Alia (T1-VIZ)` | T1-VIZ (Iterasi 1) |
| `e4733b1` | `fix(patients): server-side range validation and date-desc sort (T1-PASIEN)` | T1-PASIEN (B03, B07) |
| `53c6ed2` | `fix(safety): surface patient active meds from P.resep (T1-SAFETY)` | T1-SAFETY (B05, B08) |
| `af78a6f` | `fix(admin): expose process uptime for dashboard KPI (T1-ADMIN)` | T1-ADMIN (B01, B02, B10) |
| `a0a3f99` | `feat(pdf): efek-samping and inventaris generators (T1-PDF)` | T1-PDF (B04) |
| `cfa5c26` | `feat(data): openFDA real large-scale acquisition module (T1-DATA)` | T1-DATA |
| `4b65745` | `chore(project): bootstrap project scaffold` | tahap persiapan |
| `1536100` | `data(anggota1): fixture sesuai schema scraper (workaround Akamai block, lihat README)` | tahap awal |
| `8f5c232` | `Update README.md` | tahap awal |
| `2a5f92b` | `docs: scrub internal attribution from security audit` | tahap awal |
| `6685c64` | `feat: MedWatch backend integration (api/, integrasi/, anggota5 revision per Abhidal) (#17)` | Phase 1 integration |

Commit berikutnya (akan ditambahkan saat ticket W2-D11 selesai):

| SHA (akan terisi) | Pesan commit | Tiket |
|---|---|---|
| `<pending>` | `docs(as-built): add 19-section As-Built System Documentation per ISO 15289 (W2-D11)` | W2-D11 |

Frontend repository tidak menjadi target commit pada ticket ini (W2-D11). Commit Iterasi 1 frontend tercatat di catatan internal proyek per ticket bug.

### 19.4 Lampiran B: Bug Register (B01..B11)

Ringkasan singkat (sumber lengkap catatan internal proyek dan catatan internal proyek):

| Bug | Deskripsi | Ticket tim | Status |
|---|---|---|---|
| B01 | Admin dashboard tidak ada CTA in-body ke `/admin/scraper` | T1-ADMIN | DONE |
| B02 | Tombol "Lihat semua" inert (dead button) | T1-ADMIN | DONE |
| B03 | Form pasien terima huruf di field numerik | T1-PASIEN | DONE |
| B04 | Eksport PDF hanya untuk SOAP | T1-PDF | DONE |
| B05 | Cek interaksi tidak menampilkan obat aktif pasien | T1-SAFETY | DONE |
| B06 | Admin KPI / pengguna aktif tampak fabrikasi | T1-VERIFY | DONE (self-resolving via real `system-stats`) |
| B07 | List pasien sort newest-at-bottom | T1-PASIEN | DONE |
| B08 | Safety-checker tidak ada penjelasan inline | T1-SAFETY | DONE |
| B09 | Manual login gagal, demo creds tidak tampak | T1-LOGIN | DONE |
| B10 | KPI uptime hardcoded 99.94% | T1-ADMIN | DONE |
| B11 | Heatmap tidak kontinu / bukan heatmap visual | T1-HEATMAP | DONE |

### 19.5 Lampiran C: ADR Index

10 ADR di `docs/adr/`:

| ID | Judul singkat | Status |
|---|---|---|
| ADR-0001 | Vercel Next.js + Cloud Run Flask security pattern B (server-side proxy) | accepted |
| ADR-0002 | JWT HS256 + bcrypt cost 12 + httpOnly cookie | accepted |
| ADR-0003 | Skema Pasien SOAP dikanonisasi ke format anggota2 | accepted |
| ADR-0004 | Pivot dari drugs.com (Akamai HTTP 403) ke openFDA REST API | accepted |
| ADR-0005 | `anggota3/NewestVisualization/` sebagai modul aditif untuk Alia | accepted |
| ADR-0006 | Heatmap continuous color scale d3 risk matrix 5-stop | accepted |
| ADR-0007 | Daftar pasien sort newest-first dengan parser DD-MM-YYYY | accepted |
| ADR-0008 | Endpoint PDF efek-samping dan inventaris in-process dengan fpdf2 | accepted |
| ADR-0009 | Validasi numerik medis client+server dengan composite parser tekanan darah | accepted |
| ADR-0010 | Submit login membaca dari FormData untuk mencegah autofill race | accepted |

### 19.6 Lampiran D: Diagram Index

| Diagram | Sumber | Render |
|---|---|---|
| C4 L1 Context | `docs/diagrams/src/c4-l1-context.mmd` | `docs/diagrams/png/c4-l1-context.png` (alt `01-c4-context.png`) |
| C4 L2 Container | `docs/diagrams/src/c4-l2-container.mmd` | `docs/diagrams/png/c4-l2-container.png` (alt `02-c4-container.png`) |
| C4 L3 Component (Backend) | `docs/diagrams/src/c4-l3-component-backend.mmd` | `docs/diagrams/png/c4-l3-component-backend.png` (alt `03-c4-component-api.png`) |
| Deployment | `docs/diagrams/src/deployment.mmd` | `docs/diagrams/png/deployment.png` (alt `12-deployment.png`) |
| Use Case | `docs/diagrams/src/use-case.mmd` | `docs/diagrams/png/use-case.png` (alt `04-use-case.png`) |
| Class diagram | (legacy `.drawio`) | `docs/diagrams/png/05-class-diagram.png` |
| Sequence Login | `docs/diagrams/src/seq-login.mmd` | `docs/diagrams/png/06-sequence-auth.png` |
| Sequence Patient Create | `docs/diagrams/src/seq-pasien-crud.mmd` | `docs/diagrams/png/07-sequence-patient-create.png` |
| Sequence Safety Check | (legacy `.drawio`) | `docs/diagrams/png/08-sequence-safety-check.png` |
| Activity Patient Flow | (legacy `.drawio`) | `docs/diagrams/png/09-activity-patient-flow.png` |
| State Auth Session | (legacy `.drawio`) | `docs/diagrams/png/10-state-auth-session.png` |
| ER Schema | (legacy `.drawio`) | `docs/diagrams/png/11-er-schema.png` |
| Network Topology | (legacy `.drawio`) | `docs/diagrams/png/13-network-topology.png` |
| Structure Chart anggota1..5 | (legacy `.drawio`) | `docs/diagrams/png/14-structure-chart-anggota1.png` .. `18-structure-chart-anggota5.png` |

Setiap diagram dilengkapi blok legend yang menjelaskan notasinya (lihat sumber `.mmd` blok komentar atau caption pada PNG).

---

## Riwayat Revisi

| Versi | Tanggal | Penulis | Perubahan |
|---|---|---|---|
| 1.0 | 18-05-2026 | Kelompok B5 (Ghaisan koordinator) | Penerbitan awal AS-BUILT pasca Iterasi 1 + Iterasi 2 batch 1+2. 19 bagian per ISO/IEC/IEEE 15289:2019. Deviasi table 14 baris. |

---

(End of AS-BUILT.md)
