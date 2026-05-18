# MedWatch Backend - Flask API + Modul Anggota1-5 + openFDA Acquisition

> Sistem informasi kesehatan untuk Faskes 1 yang menggabungkan modul desktop Python (CustomTkinter) dengan layer integrasi REST API berbasis Flask. Dideploy ke Google Cloud Run dan dipasangkan dengan frontend Next.js di Vercel.

| Metadata | Nilai |
|---|---|
| Mata kuliah | Proyek 1 Pengembangan Perangkat Lunak Desktop |
| Institusi | Politeknik Negeri Bandung, D4 Teknik Informatika, Kelas 1B-D4 |
| Tahun Akademik | Semester 2, TA 2025/2026 |
| Kelompok | B5 |
| Submission | 25 Mei 2026 |
| Live frontend | https://medwatch-frontend.vercel.app |
| Live backend | https://medwatch-api-517694123086.asia-southeast1.run.app |
| Frontend repo | https://github.com/Finerium/FrontendMedwatch |

---

## 1. Apa Itu MedWatch

MedWatch adalah aplikasi sistem informasi kesehatan yang membantu fasilitas kesehatan tingkat pertama (Faskes 1) dalam dua hal utama: (1) mengelola rekam medis pasien dengan skema SOAP, dan (2) memantau keamanan obat melalui data adverse event dan recall yang diambil dari openFDA. Sistem terdiri dari lima modul Python (anggota1 sampai anggota5) yang dirakit menjadi satu aplikasi desktop CLI di folder `integrasi/`, dan sebuah layer integrasi Flask di folder `api/` yang membungkus kelima modul tersebut menjadi REST endpoint untuk frontend Next.js.

Aplikasi ini bersifat offline-first untuk layer desktop, dengan layer web sebagai showcase tambahan yang memperlihatkan modul yang sama lewat antarmuka berbasis browser. Detail lengkap arsitektur dan posisi setiap modul tersedia di [`docs/AS-BUILT.md`](./docs/AS-BUILT.md).

---

## 2. Tim Pengembang

| Nama | NIM | Peran | Modul | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader, Team Coordinator | anggota1 (scraping + openFDA acquisition) | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi matplotlib + NewestVisualization) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | anggota5 (PDF export fpdf2 + auth) | Heimdall |

Dosen pendamping: Aprianti Nanda Sari (Project Manager), Ade Chandra Nugraha, Ardhian Ekawijana.

---

## 3. Fitur Utama

Daftar fitur disusun mengikuti ID requirement dari [`docs/SRS.md`](./docs/SRS.md). ID requirement (FR-NNN) dapat ditelusuri kembali ke baris implementasi di repo via Requirements Traceability Matrix di SRS.

1. **Autentikasi peran tiga jenis** (FR-001 sampai FR-008): login JWT bertanda tangan HMAC-SHA256, role-based access control untuk `tenaga_kesehatan`, `masyarakat`, dan `admin`, plus middleware defense-in-depth di sisi backend dan frontend.
2. **CRUD pasien SOAP** (FR-010 sampai FR-019): rekam medis dengan field S/O/A/P (Subjective, Objective, Assessment, Plan), pengurutan newest-first dengan parser tanggal `DD-MM-YYYY`, validasi range klinis pada field numerik medis di server dan client.
3. **Katalog dan pencarian obat** (FR-020 sampai FR-024): daftar obat lengkap dari `anggota4/data/drug_database.json`, pencarian berbasis kata kunci dengan dukungan alias, profil keamanan per obat.
4. **Pengecekan keamanan obat** (FR-030 sampai FR-039): analisis interaksi multi-obat dengan skor severitas 0-100, penggabungan obat aktif pasien dari `P.resep`, panel edukasi cara membaca verdict.
5. **Visualisasi data kesehatan** (FR-040 sampai FR-049): tren kunjungan 12 bulan, distribusi kategori keluhan, top-10 efek samping, heatmap obat x efek dengan skala warna kontinu 5-stop.
6. **Ekspor PDF** (FR-050 sampai FR-054): rekam medis per pasien, laporan kunjungan bulanan, laporan efek samping ter-ranked, laporan inventaris obat dengan distribusi per kategori farmakologi.
7. **Admin tooling** (FR-060 sampai FR-069): trigger scraper, manajemen pengguna dengan hash bcrypt cost 12, statistik sistem, proteksi penghapusan admin terakhir.
8. **Akuisisi data openFDA** (lihat seksi 11): pengambilan real adverse event reports dan FDA recall pages dengan polite delay, exponential backoff, dan rate-limit handling.

Daftar requirement non-functional (performance, security, usability, accessibility) lengkap di [`docs/SRS.md`](./docs/SRS.md) bagian 4.

---

## 4. Tech Stack

### Layer integrasi `api/` (Python 3.11 runtime di Cloud Run)

Sumber versi: [`api/requirements.txt`](./api/requirements.txt).

| Library | Versi | Kegunaan |
|---|---|---|
| Flask | 3.1.3 | HTTP server |
| Flask-Cors | 6.0.0 | CORS allowlist untuk domain Vercel |
| PyJWT | 2.12.0 | Issuance dan verifikasi token JWT |
| bcrypt | 4.2.1 | Hash password dengan cost 12 |
| google-cloud-storage | 2.18.2 | Persistensi state ke GCS bucket |
| gunicorn | 23.0.0 | Production WSGI server |
| requests | 2.33.0 | HTTP client untuk openFDA |
| beautifulsoup4 | 4.12.3 | HTML parsing (legacy anggota1) |
| matplotlib | 3.9.2 | Visualisasi chart (terpakai oleh anggota3) |
| numpy | 1.26.4 | Numerical support |
| fpdf2 | 2.8.1 | PDF generation untuk laporan |

### Modul desktop `anggota1/`-`anggota5/`

Modul Python murni dengan dependency CustomTkinter, Pillow, matplotlib, fpdf2, requests, dan beautifulsoup4 (sesuai pemakaian per-modul). Lihat detail tools desktop di [`docs/SDD.md`](./docs/SDD.md) seksi modul.

---

## 5. Arsitektur

### Diagram C4 Level 1 (System Context)

![C4 Level 1 Context: aktor tenaga kesehatan, masyarakat, admin terhubung ke MedWatch melalui Vercel frontend; MedWatch terkoneksi ke openFDA API dan GCS state bucket](./docs/diagrams/png/c4-l1-context.png)

Sistem MedWatch berinteraksi dengan tiga aktor (tenaga kesehatan, masyarakat, admin) melalui frontend Vercel yang memproksi semua request ke backend Cloud Run. Sumber data eksternal adalah openFDA REST API (untuk efek samping dan recall obat) sementara state persistensi disimpan di Google Cloud Storage.

### Diagram C4 Level 2 (Container)

![C4 Level 2 Container: container Next.js (Vercel) memproksi ke container Flask (Cloud Run) yang membaca-tulis container GCS dan memanggil container openFDA eksternal](./docs/diagrams/png/c4-l2-container.png)

Sistem terdiri dari empat container utama: (a) Frontend Next.js di Vercel dengan proxy API route, (b) Backend Flask di Cloud Run yang menjalankan WSGI server gunicorn, (c) Bucket GCS `medwatch-polban-2026-state` untuk penyimpanan JSON pasien dan users, (d) openFDA REST API sebagai data source eksternal. Detail justifikasi pemilihan arsitektur ini ada di [`docs/adr/0001-vercel-cloud-run-security-pattern.md`](./docs/adr/0001-vercel-cloud-run-security-pattern.md).

### Diagram Deployment

![Deployment diagram: browser klien terkoneksi ke Vercel CDN edge, lalu Vercel function memanggil Cloud Run service di asia-southeast1 yang mengakses GCS bucket dan Secret Manager](./docs/diagrams/png/deployment.png)

Frontend dijalankan di Vercel Hobby tier dengan domain `medwatch-frontend.vercel.app`. Backend dideploy ke region Cloud Run `asia-southeast1`. JWT secret disimpan di Google Secret Manager. State bucket dan service account memiliki akses terbatas (Storage Object Admin pada bucket state saja). Detail lengkap ada di [`docs/INSTALL.md`](./docs/INSTALL.md) bagian Deploy.

### Diagram alur sequence (Login)

![Sequence diagram login: browser POST credentials ke Vercel API route, route forward ke Flask login, Flask verifikasi bcrypt dan terbitkan JWT, route set httpOnly cookie](./docs/diagrams/png/seq-login.png)

Daftar lengkap diagram (use case, class, activity, state machine, ERD Chen, ERD Crow's Foot, sequence safety check, sequence PDF) tersedia di folder [`docs/diagrams/png/`](./docs/diagrams/png/) beserta source Mermaid di [`docs/diagrams/src/`](./docs/diagrams/src/). Setiap diagram memiliki file `.legend.md` pendamping yang menjelaskan notasi.

Cetak biru desain detail dan keputusan arsitektur ada di [`docs/SDD.md`](./docs/SDD.md) dan folder [`docs/adr/`](./docs/adr/) (10 ADR mengikuti template MADR).

---

## 6. Prasyarat

### Untuk menjalankan layer desktop dan layer `api/` di local

- Python 3.13 untuk pengembangan local (Cloud Run runtime tetap di Python 3.11).
- pip 24+.
- Git 2.40+.
- Akses internet untuk pip install dan opsional untuk regenerasi data openFDA.

### Untuk menjalankan frontend di local (lihat repo frontend untuk detail)

- Node.js 22 LTS direkomendasikan. Node.js 25 baru saja dirilis dan menghasilkan warning kompatibilitas (`B-WAVE1-BUILD-1`), namun build dan dev server tetap berjalan. Detail mitigasi ada di [`docs/AS-BUILT.md`](./docs/AS-BUILT.md) bagian Known Issues.
- npm 10+.

### Untuk regenerasi data openFDA

- Variabel environment `OPENFDA_API_KEY` (key gratis dari https://open.fda.gov/apis/authentication/).

Daftar lengkap prerequisites termasuk gcloud CLI dan vercel CLI ada di [`docs/INSTALL.md`](./docs/INSTALL.md).

---

## 7. Instalasi

```bash
# 1. Clone repo backend
git clone https://github.com/Bisura16/medWatch.git
cd medWatch

# 2. Buat virtual environment dan install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt

# 3. Jalankan layer API Flask di port 8080
export JWT_SECRET=dev-only-replace-in-prod
export OPENFDA_API_KEY=<your-key-here>
python -m flask --app api.app run --port 8080

# 4. (Opsional) jalankan desktop CLI yang merangkai semua modul
python integrasi/app_terpadu.py
```

Panduan lengkap (termasuk Docker build, deploy ke Cloud Run, dan setup Secret Manager) ada di [`docs/INSTALL.md`](./docs/INSTALL.md).

---

## 8. Konfigurasi

Variabel environment yang dibaca oleh backend. Semua nilai dummy hanya untuk dokumentasi; jangan commit nilai produksi.

| Nama | Wajib | Default | Kegunaan |
|---|---|---|---|
| `JWT_SECRET` | ya (di Cloud Run) | string kosong di dev | Kunci HMAC-SHA256 untuk tanda tangan JWT. Di produksi diambil dari Secret Manager `medwatch-jwt-secret`. |
| `OPENFDA_API_KEY` | opsional | string kosong | Naikkan rate limit openFDA dari 1.000/hari menjadi 120.000/hari. Tanpa key tetap berfungsi, hanya throttled. |
| `GCS_BUCKET` | ya (di Cloud Run) | tidak ada | Nama bucket GCS untuk persistensi `users.json` dan `patients.json`. Resource name: `medwatch-polban-2026-state`. |
| `PORT` | tidak | 8080 | Port HTTP. Cloud Run inject otomatis. |
| `ALLOWED_ORIGINS` | tidak | hardcoded allowlist | Daftar origin Vercel + localhost. Lihat [`api/config.py`](./api/config.py). |

Tidak ada nilai kredensial pernah dicommit ke repo. Mitigasi anti-leak per-commit menggunakan secret-scan hook. Daftar lengkap di [`docs/SECURITY.md`](./docs/SECURITY.md).

---

## 9. Penggunaan

### Menjalankan smoke test backend

```bash
cd api/tests
python smoke_test.py http://localhost:8080
```

Smoke test memeriksa 12 endpoint inti (auth, patients CRUD, safety check, drug catalog, visualizations, PDF generation, admin endpoints) dan mengeluarkan ringkasan pass/fail.

### Menjalankan desktop CLI

```bash
python integrasi/app_terpadu.py
# Login demo:
#   admin1 / admin123     (admin)
#   bidan1 / bidan123     (tenaga_kesehatan)
```

### Endpoint utama

| Method | Path | Peran | Kegunaan |
|---|---|---|---|
| POST | `/api/auth/login` | semua | Login dengan username + password |
| GET | `/api/patients` | tenaga_kesehatan, admin | Daftar pasien terurut newest-first |
| POST | `/api/patients` | tenaga_kesehatan, admin | Tambah rekam pasien baru |
| GET | `/api/drugs/search?q=<kata>` | semua | Pencarian obat dengan alias |
| POST | `/api/safety/check` | semua | Analisis interaksi multi-obat |
| GET | `/api/visualizations/heatmap-efek` | semua terotentikasi | Matriks obat x efek samping |
| POST | `/api/pdf/generate-rekam-medis` | tenaga_kesehatan, admin | PDF rekam medis per pasien |
| POST | `/api/admin/scrape` | admin | Trigger scraper (mocked) |

Daftar lengkap 30+ endpoint dengan request/response shape ada di [`docs/API.md`](./docs/API.md).

---

## 10. Sumber Data dan Teknis Scraping

> Section ini menggantikan strategi scraping awal anggota1 yang berbasis drugs.com dengan pivot ke openFDA REST API. Modul `anggota1/anggota1.py` tetap dipertahankan untuk audit trail dan tidak dimodifikasi (read-only sesuai aturan kepemilikan modul tim).

### Riwayat sumber data

Sumber data efek samping dan recall obat di MedWatch berubah selama proyek berlangsung. Decision lengkap didokumentasikan di [`docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md`](./docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md).

1. **Versi awal (Maret 2026):** `anggota1/anggota1.py` melakukan scraping HTML dari `https://www.drugs.com/sfx/<obat>-side-effects.html` dan `https://www.drugs.com/fda-recalls/`.
2. **Mei 2026:** drugs.com migrasi ke proteksi Akamai edge dengan TLS fingerprinting dan header challenge yang memblokir setiap request dari script Python standar dengan HTTP 403 Forbidden. Kutipan langsung dari [`anggota1/scraper.log`](./anggota1/scraper.log):

   ```
   [1/2] scraping efek samping (64 obat)
     [1/64] ibuprofen
       status 403
     [2/64] paracetamol
       status 403
     [3/64] aspirin
       status 403
   ```

   Sekitar 64 dari 64 URL yang dicoba semua mengembalikan 403. Tidak ada satu obat pun yang berhasil di-scrape via path lama. File `anggota1/data/drug_safety_data.json` dan `anggota1/data/drug_recalls.json` di-populate dengan fixture sementara dari WHO Essential Medicines monograph agar consumer downstream tidak rusak.
3. **Wave 1 (Mei 2026):** pengganti aditif `anggota1/openfda/` dibuat. Modul ini memakai openFDA REST API untuk real large-scale data acquisition. File `anggota1.py` tetap dipertahankan untuk audit trail dan tidak dimodifikasi.

### Endpoint openFDA yang digunakan

| Endpoint | Kegunaan |
|---|---|
| `https://api.fda.gov/drug/event.json` | FDA Adverse Event Reporting System (FAERS). Diakses per-obat dengan parameter `search=patient.drug.medicinalproduct:"<nama>"` dan `count=patient.reaction.reactionmeddrapt.exact` untuk top reaksi, ditambah `count=serious` dan `count=seriousnessdeath` untuk derivasi severity. |
| `https://api.fda.gov/drug/enforcement.json` | FDA Recall / Enforcement Reports. Diakses dengan pagination `skip` dan `limit=1000` (max per request), diurut `recall_initiation_date:desc`. |

### Dasar legal

openFDA adalah layanan publik gratis yang dioperasikan oleh U.S. Food and Drug Administration. Konsumsi programmatic dengan API key diizinkan untuk penelitian, integrasi sistem informasi kesehatan, dan publikasi (Terms of Service: https://open.fda.gov/license/). Data FAERS dan Enforcement Reports tidak mengandung PII pasien; FDA sudah melakukan de-identifikasi sebelum dipublikasikan. Tidak ada bypass anti-bot, captcha, atau ToS-restricted resource yang dilakukan di pipeline ini.

### Rate-limit handling

- Tanpa API key: 1.000 request / 24 jam per IP, 240 / menit.
- Dengan API key (`OPENFDA_API_KEY` di env, dikirim sebagai query param `api_key`): 120.000 request / 24 jam per IP, 240 / menit.
- Modul memakai polite delay 250 ms antar request dan exponential backoff dengan jitter pada HTTP 429 dan 5xx (maksimum 5 retry; backoff 0,5s lalu 1s lalu 2s lalu 4s lalu 8s plus jitter).
- HTTP 404 dianggap empty result, lanjut ke obat berikutnya.

### Anti-leak

Nilai `OPENFDA_API_KEY` tidak pernah ditulis ke file disk, log, atau output. Setiap `source_url` di file JSON menampilkan placeholder `&api_key=<redacted>`. Konstanta `OPENFDA_API_KEY` di [`api/config.py`](./api/config.py) hanya membaca dari environment dengan default string kosong; tidak ada nilai hard-coded. Aturan anti-leak menyeluruh dijelaskan di [`docs/SECURITY.md`](./docs/SECURITY.md).

### Cara regenerasi data openFDA

```bash
cd /path/to/medWatch
export OPENFDA_API_KEY=<your-key-here>
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
```

Hasil ditulis ke `anggota1/data/drug_safety_data.json` dan `anggota1/data/drug_recalls.json` dengan schema yang sama dengan fixture sebelumnya (consumer downstream tidak perlu diubah).

### Hasil yang dicapai

Run Wave 1 pada 18 Mei 2026 menghasilkan:

- **1.850 reaction-term occurrences** terdistribusi pada **74 baris adverse event** (74 obat).
- **6.000 baris recall** dari endpoint enforcement (6 halaman x 1.000 baris).

Untuk run yang lebih besar, naikkan `--max-recall-pages` hingga 26 (mencapai sekitar 17.643 record). Detail teknis lengkap, mapping severity, dan flag CLI tambahan ada di [`anggota1/openfda/README.md`](./anggota1/openfda/README.md).

---

## 11. CRUD dan Data Model

MedWatch mengelola enam entitas inti yang skema lengkapnya didokumentasikan di [`docs/DATA-DICTIONARY.md`](./docs/DATA-DICTIONARY.md). Endpoint CRUD lengkap dengan request/response shape ada di [`docs/API.md`](./docs/API.md).

| Entitas | Sumber kebenaran skema | File data |
|---|---|---|
| User auth | `api/data/users.json` schema bcrypt | `api/data/users.json` |
| Pasien (SOAP) | `anggota2/pasien_helper.py` | `api/data/patients.json` (web), `anggota2/Pasien.json` (desktop) |
| Drug catalog | `anggota4/data/drug_database.json` | sama, read-only |
| Side effect dictionary | `anggota4/data/effect_database.json` | sama, read-only |
| Adverse event report | openFDA FAERS | `anggota1/data/drug_safety_data.json` |
| Drug recall | openFDA Enforcement | `anggota1/data/drug_recalls.json` |

Skema pasien SOAP mengikuti format Bimo (`anggota2/pasien_helper.py`):

- `id` (format `P001`-`P999`)
- `tanggal_kunjungan` (DD-MM-YYYY)
- `nama`, `umur`, `alamat`, `kategori`
- `S` (Subjective): keluhan, riwayat
- `O` (Objective): tekanan_darah, nadi, suhu_c, respirasi, bb_kg, tb_cm, lila_cm, catatan
- `A` (Assessment): diagnosa
- `P` (Plan): tindakan, resep, jadwal_kontrol

Visualisasi diagram ERD lengkap ada di [`docs/diagrams/png/erd-crowsfoot.png`](./docs/diagrams/png/erd-crowsfoot.png) dengan versi Chen di [`docs/diagrams/png/erd-chen.png`](./docs/diagrams/png/erd-chen.png).

![ERD Crow's Foot menampilkan relasi User, Patient, Visit, Drug, Recall, AdverseEvent dengan kardinalitas](./docs/diagrams/png/erd-crowsfoot.png)

---

## 12. Struktur Proyek

```
medWatch/
├── anggota1/                    # Ghaisan: scraping legacy + openFDA acquisition baru
│   ├── anggota1.py              # legacy drugs.com scraper (deprecated, audit trail)
│   ├── openfda/                 # NEW: openFDA REST acquisition pipeline
│   ├── data/                    # drug_safety_data.json, drug_recalls.json
│   └── scraper.log              # bukti HTTP 403 Akamai block
├── anggota2/                    # Bimo: CRUD pasien SOAP
├── anggota3/                    # Alia: visualisasi matplotlib + NewestVisualization
├── anggota4/                    # Iqbal: drug safety check, severity scoring
├── anggota5/                    # Abhidal: PDF export fpdf2 + auth desktop
├── api/                         # Ghaisan: integration layer Flask REST
│   ├── routes/                  # auth, patient, drug, safety, viz, pdf, admin
│   ├── data/                    # users.json, patients.json (web copy)
│   ├── tests/smoke_test.py      # 12-endpoint smoke check
│   └── README.md                # API reference, demo credentials
├── integrasi/                   # Ghaisan: desktop CLI yang merangkai anggota1-5
├── docs/                        # Wave 2 documentation set
│   ├── adr/                     # 10 ADR mengikuti MADR
│   ├── diagrams/                # source Mermaid + PNG render
│   ├── API.md, SRS.md, SDD.md, AS-BUILT.md, ...
│   └── INSTALL.md, SECURITY.md, USER-MANUAL.md
├── ProductionGrade-ImplementationPlan/   # forward-looking production plan
├── main.py                      # entrypoint Cloud Run yang re-export api.app
├── Dockerfile                   # container build untuk Cloud Run
└── README.md                    # file ini
```

Output sederhana dari `tree -L 2 -I 'node_modules|.next|.venv|__pycache__'` di repo root.

---

## 13. Testing

### Smoke test backend

`api/tests/smoke_test.py` adalah suite cek minimal yang mengonfirmasi setiap endpoint utama merespons dengan status dan shape yang benar. Jalankan terhadap deployment local atau Cloud Run:

```bash
python api/tests/smoke_test.py http://localhost:8080
# atau
python api/tests/smoke_test.py https://medwatch-api-517694123086.asia-southeast1.run.app
```

Suite telah diperluas di Wave 5 W5-FIX-CRITICAL dengan assertion baru yang memverifikasi gating role pada endpoint `POST /api/safety/check`: sebagai `umum_budi` (role `masyarakat`), supply `pasien_id=P001` harus mengembalikan `pasien_context: null` dan `pasien_active_meds: []`; sebagai `bidan_siti` (role `tenaga_kesehatan`), supply `pasien_id=P001` harus tetap mengembalikan field tersebut terisi. Sumber: closure H07-1 W4-HUNT.

### Pengujian Black-Box Formal (Wave 5)

Dokumentasi pengujian black-box mengikuti standar IEEE 829 dan ISO/IEC/IEEE 29119 (Software Testing) di-tulis di Wave 5 mission (12-18 Mei 2026) dan tersedia di [`docs/testing/`](./docs/testing/):

| Berkas | Deskripsi |
|---|---|
| [`docs/testing/test-plan.md`](./docs/testing/test-plan.md) | Master test plan: scope, strategy, environment, schedule 12-18 Mei 2026, exit criteria, role-based tester assignment. |
| [`docs/testing/test-cases.md`](./docs/testing/test-cases.md) | TC-MOD-NNN test cases (>=50) covering AUTH, PASIEN, SAFETY, DRUG, VIZ, PDF, ADMIN, SCRAPE, HEATMAP, SCREEN modules. Setiap kasus memuat ID, modul, fitur, technique (EP/BVA/Decision Table/State Transition/Use Case/Error Guessing), prasyarat, langkah, data input, hasil yang diharapkan, hasil aktual, status (Pass/Fail/Blocked), tester (NIM + nama), tanggal eksekusi. |
| [`docs/testing/rtm.md`](./docs/testing/rtm.md) | Requirement Traceability Matrix menghubungkan SRS FR-ID ke TC-MOD-NNN ID. |
| [`docs/testing/defect-log.md`](./docs/testing/defect-log.md) | Defect log eksekusi Wave 5 termasuk W4-HUNT H-ID sebagai entri historis dan W5-RT-NNN entri baru. |
| [`docs/testing/test-summary.md`](./docs/testing/test-summary.md) | Test summary dengan formula `Persentase Validasi = (Sum pass / Sum total) * 100%` plus verdikt Arikunto scale (86-100 sangat baik, 71-85 baik, 56-70 cukup, 41-55 kurang, <=40 sangat kurang). |

Versi `.docx` masing-masing tersedia di [`docs/deliverable/`](./docs/deliverable/) sebagai deliverable submission dosen.

Tester attribution lintas anggota tim:

- Bimo Surya Anggara (NIM 251524040, QA): master plan owner + AUTH/PASIEN execution.
- Alia Ardani (NIM 251524035, System Analyst): RTM + VIZ/HEATMAP execution.
- Muhammad Iqbal (NIM 251524057, Programmer): SAFETY/DRUG execution.
- Abhidal Muhammad Gazza (NIM 251524032, UI/UX): PDF/SCREEN execution.
- Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader): SCRAPE/ADMIN execution.

Real execution evidence disimpan di `docs/testing/evidence/` per TC-ID (transcript curl untuk endpoint, screenshot Playwright untuk UI saat tersedia). Status `Blocked` dieksposisikan eksplisit dengan rujukan ke open blocker (mis. B-WAVE1-BUILD-1 untuk klikthrough SSR).

---

## 14. Deployment

Backend dideploy ke Google Cloud Run di region `asia-southeast1` lewat Cloud Build dari [`api/Dockerfile`](./api/Dockerfile). Frontend dideploy ke Vercel dari repo `Finerium/FrontendMedwatch`. Panduan langkah demi langkah, termasuk setup Secret Manager, GCS bucket, dan environment variable di Vercel, ada di [`docs/INSTALL.md`](./docs/INSTALL.md) bagian Deploy.

---

## 15. Kontribusi Tim

Bagian ini menyimpan kontribusi awal dari teammate dan pemilik repo (Bimo, sebagai pemilik repository `Bisura16/medWatch` dan author asli README). Konten di bawah ini di-restructure dari README sebelumnya untuk integrasi dengan section industri-standar di atas, namun tidak menghilangkan teks asli.

### Aplikasi MedWatch (versi awal, oleh Bimo Surya Anggara)

MedWatch merupakan aplikasi sistem informasi kesehatan berbasis desktop yang dirancang untuk membantu fasilitas kesehatan tingkat pertama (Faskes 1) dalam mengelola data pasien serta melakukan monitoring keamanan obat. Aplikasi ini mengintegrasikan fitur rekam medis digital, pengecekan keamanan obat, visualisasi data kesehatan, dan ekspor laporan dalam satu platform berbasis Python dengan konsep offline-first.

MedWatch memanfaatkan web scraping dari sumber farmasi terpercaya untuk menyediakan informasi efek samping, recall obat, dan peringatan keamanan obat sehingga dapat membantu tenaga kesehatan maupun masyarakat dalam memperoleh informasi kesehatan yang lebih cepat, terstruktur, dan mudah diakses.

### Sistem untuk menjalankan aplikasi desktop (oleh Bimo Surya Anggara)

- **Python** digunakan sebagai bahasa pemrograman utama untuk membangun dan menjalankan seluruh fungsi aplikasi.
- **CustomTkinter** digunakan untuk membuat antarmuka grafis (GUI) modern sehingga pengguna dapat berinteraksi dengan aplikasi dengan tampilan yang lebih interaktif.
- **Requests** digunakan untuk mengambil data halaman web melalui HTTP request dalam proses web scraping.
- **BeautifulSoup4** digunakan untuk memproses dan mengekstrak informasi dari struktur HTML halaman web.
- **Matplotlib** digunakan untuk membuat visualisasi data kesehatan seperti grafik tren kunjungan pasien dan distribusi keluhan.
- **FPDF2** digunakan untuk membuat dan mengekspor laporan dalam format PDF.
- **Pillow** digunakan untuk pengolahan gambar seperti ikon dan elemen antarmuka aplikasi.
- **JSON Module** digunakan untuk membaca dan menyimpan data lokal dalam format JSON. Modul ini merupakan modul bawaan Python sehingga tidak memerlukan instalasi tambahan.
- **OS dan Datetime Module** digunakan untuk pengelolaan file sistem dan pengolahan tanggal/waktu pada aplikasi. Modul ini juga merupakan modul bawaan Python.

### Integration layer `api/` (oleh Ghaisan Khoirul Badruzaman)

Folder `api/` di root repo ini adalah integration layer Flask yang membungkus modul anggota1-5 menjadi REST endpoint, dideploy ke GCP Cloud Run, dan dikoneksikan ke frontend Next.js di Vercel. Detail integrasi tersedia di [`api/README.md`](./api/README.md) dan [`docs/INTEGRATION_GUIDE.md`](./docs/INTEGRATION_GUIDE.md).

### Merge layer `integrasi/` (oleh Ghaisan Khoirul Badruzaman)

Folder `integrasi/` adalah desktop CLI app yang menyusun anggota1-5 jadi satu entry point dengan role-based menu, tanpa memodifikasi file anggota satu pun:

```bash
python integrasi/app_terpadu.py
# Login: admin1 / admin123  (admin)
# Login: bidan1 / bidan123  (tenaga_kesehatan)
```

Lihat [`integrasi/README.md`](./integrasi/README.md) untuk detail.

### Sumber data dan teknis scraping (oleh Ghaisan Khoirul Badruzaman)

Detail openFDA acquisition pipeline yang menggantikan scraping drugs.com (akibat Akamai block 11 Mei 2026) dipindahkan ke seksi 10 di bagian utama README ini.

---

## 16. Cross-Link Repository

| Repo | Kegunaan | URL |
|---|---|---|
| Backend (THIS repo) | Modul anggota1-5 plus integration layer Flask plus desktop CLI | https://github.com/Bisura16/medWatch |
| Frontend showcase | Next.js 15 plus Tailwind v4 plus shadcn glassmorphism, dideploy ke Vercel | https://github.com/Finerium/FrontendMedwatch |

README frontend memiliki section navigasi, route map, RBAC matrix, dan demo credentials yang melengkapi dokumentasi backend ini.

---

## 17. Lisensi

Lisensi MIT. Lihat [`LICENSE`](./LICENSE) untuk teks lengkap.
