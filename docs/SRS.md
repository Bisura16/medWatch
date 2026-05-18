---
title: Software Requirements Specification (SRS / SKPL) - MedWatch
version: 1.0
owner: Kelompok B5 - 1B-D4 Teknik Informatika, Politeknik Negeri Bandung
date: 2026-05-18
status: AS-BUILT (pasca Wave 1)
standards: IEEE 830-1998, ISO/IEC/IEEE 29148:2018
---

# Spesifikasi Kebutuhan Perangkat Lunak (SRS) MedWatch

Dokumen ini disusun mengikuti struktur Software Requirements Specification yang
direkomendasikan oleh IEEE 830-1998 dan dengan terminologi yang diselaraskan
terhadap ISO/IEC/IEEE 29148:2018 (Systems and software engineering -- Life
cycle processes -- Requirements engineering). SRS ini mendeskripsikan sistem
MedWatch sebagaimana terbangun (as-built) setelah perbaikan Wave 1 (bug B01
sampai B11), bukan rancangan awal sebelum integrasi.

Penomoran bab mengikuti template IEEE 830-1998 bab 5 (Specific Requirements
Recommended Outline). Identifier persyaratan menggunakan pola `FR-XXX` untuk
fungsional dan `NFR-<area>` untuk non-fungsional sesuai praktik umum
requirement engineering ISO/IEC/IEEE 29148:2018 klausa 7.

---

## 1. Pendahuluan

### 1.1 Tujuan SRS

Dokumen ini menetapkan kebutuhan fungsional dan non-fungsional dari sistem
informasi MedWatch versi presentasi (Semester 2 TA 2025/2026) untuk
keperluan submission mata kuliah Proyek 1 Pengembangan Perangkat Lunak
Desktop pada D4 Teknik Informatika Politeknik Negeri Bandung. SRS menjadi
acuan bagi:

1. Tim pengembang Kelompok B5 untuk validasi cakupan fitur sebelum demo.
2. Dosen pendamping (Aprianti Nanda Sari sebagai PM, Ade Chandra Nugraha,
   Ardhian Ekawijana) untuk menilai keselarasan implementasi terhadap
   kebutuhan.
3. Tim Quality Assurance (Bimo Surya Anggara, NIM 251524040) untuk
   merancang skenario uji kotak-hitam (black-box testing) dan matriks
   keterunutan (Requirements Traceability Matrix).
4. Pemangku kepentingan eksternal (mitra Faskes 1, bidan praktik mandiri)
   yang berperan sebagai end user dari aplikasi desktop CustomTkinter
   serta penyangga web Cloud Run + Vercel.

SRS ini disusun dalam Bahasa Indonesia formal sesuai ketentuan submission
dosen. Identifier kode, nama field schema, dan rujukan standar dipertahankan
dalam Bahasa Inggris untuk menjaga keterunutan terhadap kode sumber dan
dokumentasi rujukan internasional.

### 1.2 Lingkup Produk

MedWatch berfungsi sebagai sistem pendukung manajemen klinik Fasilitas
Kesehatan Tingkat Pertama (Faskes 1) dengan penekanan pada pemantauan
keamanan obat. Sistem MedWatch sebagaimana dikirim terdiri dari tiga tier:

1. **Aplikasi Desktop CustomTkinter (utama)**. Berkas Python modular pada
   direktori `anggota1/` hingga `anggota5/` di repositori backend. Mode
   submission resmi mata kuliah adalah aplikasi desktop ini, dirakit
   melalui titik masuk `main.py` (lihat
   `/Users/ghaisan/Documents/MedWatchIntegration/medWatch/main.py:1`).
2. **Backend HTTP Flask (penyangga web)**. Layer `api/` membungkus modul
   anggota1 sampai anggota5 menjadi REST API yang siap dipanggil oleh
   frontend. Titik masuk Flask berada di `api/app.py:27` (`create_app()`)
   dengan registrasi 8 blueprint pada `api/app.py:36-43` yang
   mengekspos total 27 endpoint HTTP.
3. **Frontend Web Next.js (penyangga showcase)**. Repositori
   `FrontendMedWatch/` berisi aplikasi Next.js 16 App Router yang
   memproxy permintaan ke backend Cloud Run melalui pola Next.js API
   route. Frontend dideploy ke Vercel Hobby tier pada URL
   `https://medwatch-frontend.vercel.app`.

Aplikasi melayani tiga peran pengguna (`tenaga_kesehatan`, `masyarakat`,
`admin`) dengan kontrol akses berbasis peran (RBAC). Domain fungsionalnya
meliputi pendaftaran dan rekam medis SOAP pasien, katalog dan pencarian
obat, pengecekan interaksi serta keamanan obat (drug safety check) dengan
konteks pasien, visualisasi data klinis dan keamanan obat, eksport laporan
PDF (rekam medis, laporan bulanan, efek samping, inventaris obat),
serta administrasi sistem (pemicuan scraper, manajemen pengguna, statistik
sistem, log aktivitas).

Yang tidak termasuk lingkup MedWatch versi presentasi: penyimpanan data
rekam medis pada server pusat berskala produksi, integrasi pembayaran,
sinkronisasi SATUSEHAT, billing kapitasi BPJS, modul rujukan online ke
rumah sakit, atau sertifikasi WHO/Kemenkes. Pertimbangan tersebut
didokumentasikan secara terpisah pada `docs/ProductionGrade-ImplementationPlan/`.

### 1.3 Definisi, Akronim, dan Singkatan

| Istilah | Definisi |
|---|---|
| Faskes 1 | Fasilitas Kesehatan Tingkat Pertama (puskesmas, klinik pratama, praktik bidan mandiri). |
| SOAP | Subjective, Objective, Assessment, Plan; format pencatatan klinis standar. |
| Bidan | Tenaga kesehatan dengan kewenangan asuhan kehamilan, KB, imunisasi, dan kebidanan dasar di Faskes 1. |
| RBAC | Role-Based Access Control, pengendalian akses berbasis peran. |
| JWT | JSON Web Token (RFC 7519), token bertanda tangan untuk otentikasi sesi. |
| bcrypt | Algoritma key-stretching untuk hashing kata sandi (Provos and Mazieres 1999). |
| openFDA | Layanan API publik gratis dari US Food and Drug Administration yang mengekspos data farmakovigilans (FAERS) dan recall obat. |
| FAERS | FDA Adverse Event Reporting System. |
| CORS | Cross-Origin Resource Sharing (W3C Recommendation). |
| Cloud Run | Layanan komputasi serverless dari Google Cloud Platform untuk container HTTP. |
| GCS | Google Cloud Storage. |
| Vercel Hobby | Tier gratis dari layanan Vercel untuk hosting aplikasi Next.js. |
| FR | Functional Requirement (kebutuhan fungsional) sebagaimana ISO/IEC/IEEE 29148:2018. |
| NFR | Non-Functional Requirement (kebutuhan non-fungsional). |
| MoSCoW | Skema prioritisasi Must / Should / Could / Won't (Clegg dan Barker 1994). |
| BPOM | Badan Pengawas Obat dan Makanan Republik Indonesia. |
| WIB | Waktu Indonesia Barat (UTC+07:00). |

### 1.4 Referensi

Standar dan dokumen rujukan disitir dengan nomor identifikasinya:

1. **IEEE 830-1998**. IEEE Recommended Practice for Software Requirements
   Specifications. Institute of Electrical and Electronics Engineers,
   New York, 1998. ISBN 0-7381-0332-2.
2. **ISO/IEC/IEEE 29148:2018**. Systems and software engineering --
   Life cycle processes -- Requirements engineering. International
   Organization for Standardization, 2018.
3. **IEEE 1016-2009**. IEEE Standard for Information Technology --
   Systems Design -- Software Design Descriptions. Dirujuk melalui SDD
   pada `docs/SDD.md`.
4. **ISO/IEC/IEEE 26514**. Systems and software engineering --
   Requirements for designers and developers of user documentation.
   Dirujuk melalui `docs/USER-MANUAL.md`.
5. **OWASP Top 10 (2021)**. Open Web Application Security Project.
   Dirujuk melalui `docs/SECURITY.md`.
6. **WCAG 2.1 Level AA**. Web Content Accessibility Guidelines.
   W3C Recommendation, 2018.
7. **RFC 7519 (JSON Web Token)** dan **RFC 6749 (OAuth 2.0)** untuk
   skema otentikasi.
8. **Dokumen internal MedWatch**: `docs/PRD.md` (Product Requirements
   Document), `docs/SDD.md` (Software Design Description),
   `docs/DATA-DICTIONARY.md` (kamus data), `docs/API.md` (spesifikasi
   API), `docs/SECURITY.md` (threat model), `docs/AS-BUILT.md`
   (deskripsi as-built dengan tabel deviasi).

### 1.5 Tinjauan Dokumen

Sisa dokumen dibagi menjadi tiga bab utama sesuai IEEE 830-1998:

- Bab 2 menjelaskan deskripsi umum (perspektif produk, fungsi utama,
  karakteristik pengguna, batasan, asumsi).
- Bab 3 memuat persyaratan spesifik: fungsional (3.1), antarmuka
  eksternal (3.2), non-fungsional (3.3), dan basis data (3.4).
- Lampiran A dan B memuat daftar aktor dan indeks use case.

---

## 2. Deskripsi Umum

### 2.1 Perspektif Produk

MedWatch versi submission adalah produk komposit tiga tier:

1. **Tier Desktop (utama)**. Aplikasi CustomTkinter monolitik berbasis
   Python 3.13 yang dijalankan secara lokal di laptop bidan. Modul
   modular dipecah per anggota tim (`anggota1/` scraping, `anggota2/`
   CRUD pasien, `anggota3/` visualisasi, `anggota4/` drug safety check,
   `anggota5/` PDF export dan otentikasi). Modul-modul ini adalah
   sumber otoritatif dari logika domain.
2. **Tier Backend (penyangga)**. Layer Flask `api/` membungkus modul
   anggota1 sampai anggota5 dengan adapter dan adapter tipis (schema
   translation, JWT issuance, RBAC middleware). Backend disiapkan untuk
   penyebaran ke Google Cloud Run di region `asia-southeast1` dengan
   container image dibangun dari `api/Dockerfile`. Storage persisten
   menggunakan GCS bucket `medwatch-polban-2026-state`; konfigurasi
   `USE_CLOUD_STORAGE` di `api/config.py:29` mengaktifkan path GCS
   ketika true, atau menyimpan ke filesystem `api/data/` ketika false.
3. **Tier Frontend (showcase)**. Aplikasi Next.js 16 App Router pada
   repositori `FrontendMedWatch/` yang dideploy ke Vercel Hobby tier
   sebagai showcase. Frontend memuat berbagai rute (lihat tabel pada
   bagian 3.2.1) dan memproxy permintaan ke backend melalui Next.js API
   route. Pola proksi ini menjaga URL backend Cloud Run agar tidak
   pernah terekspos pada browser klien (lihat `docs/adr/0001-vercel-cloudrun-split.md`).

Diagram konteks (C4 Level 1) berada di `docs/diagrams/png/c4-l1-context.png`;
sumber Mermaid pada `docs/diagrams/src/c4-l1-context.mmd`.

### 2.2 Fungsi Produk

Dalam tingkat fitur utama, MedWatch mendukung:

1. **Otentikasi dan otorisasi**. Login manual dengan password, demo
   login satu-klik untuk tiga peran, logout, RBAC tiga peran
   (`tenaga_kesehatan`, `masyarakat`, `admin`).
2. **CRUD pasien dengan schema SOAP**. Pembuatan, pembacaan, perubahan,
   dan penghapusan rekam pasien lengkap dengan validasi numerik medis
   per field dan urutan list newest-first.
3. **Katalog dan pencarian obat**. Daftar obat dengan filter kategori,
   pencarian berbasis kata kunci (alias), dan pembacaan profil keamanan
   lengkap suatu obat.
4. **Pengecekan keamanan dan interaksi obat (safety check)**. Agregasi
   risiko per obat dengan skor numerik (`severity_score` 0..100) dan
   label (`severity_level` low/medium/high), pengayaan dengan obat aktif
   pasien yang sedang dirawat (B05).
5. **Eksport laporan PDF**. Rekam medis SOAP per pasien, laporan
   kunjungan bulanan, laporan efek samping, dan inventaris obat (B04).
6. **Visualisasi**. Tren kunjungan bulanan, distribusi keluhan, top-10
   efek samping, dan matriks heatmap obat versus efek dengan skala
   warna kontinu (B11).
7. **Administrasi sistem**. Pemicuan scraper (mock di sisi server),
   CRUD pengguna terbatas admin, statistik sistem real-time (B10),
   feed log aktivitas (B02), tombol cepat menuju panel scraper di
   dashboard admin (B01).

### 2.3 Karakteristik Pengguna

MedWatch melayani tiga persona dengan profil sebagai berikut.

| Persona | Role string | Kemampuan teknis | Akses fitur utama |
|---|---|---|---|
| Tenaga kesehatan (bidan, perawat Faskes 1) | `tenaga_kesehatan` | Komputer dasar (familiar Microsoft Office, browser). Tidak terbiasa terminal. | CRUD pasien (Create, Read, Update), safety check, lihat visualisasi, generate PDF rekam medis dan laporan bulanan. Tidak bisa hapus pasien atau memicu scraper. |
| Masyarakat umum (pasien sendiri, keluarga) | `masyarakat` | Pengguna awam smartphone. | Lihat profil sendiri, pencarian obat OTC, safety-check obat dari resep yang diberikan bidan. Tidak bisa melihat daftar pasien lain. |
| Admin sistem (Project Leader Kelompok B5) | `admin` | Mahasiswa D4 Teknik Informatika, terbiasa terminal dan deploy. | Semua kemampuan tenaga kesehatan + delete pasien + manajemen pengguna (CRUD user) + pemicuan scraper + statistik sistem + log aktivitas. |

Persona admin merupakan ekstensi melampaui PRD asli (yang mengeluarkan
otentikasi dari scope), sehingga keberadaannya didokumentasikan sebagai
suplemen presentasi pada `docs/adr/0002-jwt-bcrypt-httpcookie.md` dan
diakui sebagai deviasi pada tabel deviasi `docs/AS-BUILT.md`.

### 2.4 Batasan

1. Aplikasi MedWatch dirancang untuk skala submission mata kuliah,
   bukan beban produksi puskesmas berskala kabupaten.
2. Semua sumber daya infrastruktur harus tetap berada pada free tier:
   openFDA tanpa biaya, Vercel Hobby, GCP free trial credit
   (USD 300, tanpa kartu produksi).
3. Frontend Next.js 16 dijalankan pada Node 22 LTS sebagaimana
   didokumentasikan pada `docs/INSTALL.md`. Node 25 (terbaru, belum
   LTS) tidak kompatibel dengan turbopack production build saat tulisan
   ini (lihat blocker B-WAVE1-BUILD-1 di
   `docs/AS-BUILT.md` bagian Known Issues).
4. Tidak ada lisensi proprietary; seluruh perpustakaan adalah open
   source dengan lisensi permissive (MIT, BSD-3, Apache-2.0).
5. Tidak ada peneribitan API publik di luar lingkup demo dosen; CORS
   dibatasi pada origin Vercel showcase dan localhost pengembang.
6. Kebijakan tanpa em dash dan tanpa emoji berlaku pada seluruh teks
   user-facing dan dokumen internal.

### 2.5 Asumsi dan Ketergantungan

1. Pengguna desktop memiliki Python 3.13 atau lebih baru, terinstal
   pada Windows 10/11, macOS 12+, atau Ubuntu 22.04+.
2. Pengguna web menggunakan browser modern dengan dukungan
   ES2022 (Chrome >= 120, Firefox >= 120, Edge >= 120, Safari >= 17).
3. Konektivitas internet tersedia untuk fungsi safety check yang
   memerlukan database obat ter-update dan untuk akses showcase web.
4. Variabel lingkungan `OPENFDA_API_KEY` tersedia bila scraper data
   real openFDA dijalankan; lihat `api/config.py:34`.
5. Akun GCP `medwatch-polban-2026` dengan service account default
   tersedia ketika frontend showcase di-deploy ulang.
6. Schema kanonikal data pasien mengikuti `anggota2/pasien_helper.py`
   dengan ID format `P001..P999` (lihat `.md` Rule 3 di repositori).
7. Browser JavaScript runtime di sisi frontend memiliki kemampuan
   menyimpan dan mengirim cookie httpOnly (semua browser modern
   mendukung).

---

## 3. Persyaratan Spesifik

Bagian ini mengikuti struktur IEEE 830-1998 klausa 5.3, dengan
pengelompokan menurut tipe persyaratan (fungsional di 3.1, antarmuka di
3.2, non-fungsional di 3.3, database di 3.4). Setiap kebutuhan diberi
identifier unik. Prioritas menggunakan MoSCoW: M (Must), S (Should), C
(Could), W (Won't this iteration).

### 3.1 Persyaratan Fungsional

#### 3.1.1 Otentikasi dan Otorisasi

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-001 | Sistem MUST menerima login manual dengan kombinasi `username` dan `password`. Sistem MUST menerbitkan token JWT bertanda tangan HMAC-SHA256 dengan `iss=medwatch-api` saat kredensial cocok, dan MUST menolak dengan HTTP 401 `{"error":"invalid credentials"}` bila tidak cocok. | tenaga_kesehatan, masyarakat, admin | Login dengan `bidan_siti / siti2026` mengembalikan token dan objek user dengan `role="tenaga_kesehatan"`. Login dengan password salah mengembalikan 401. | `POST /api/auth/login` (`api/routes/auth_routes.py:13`) | M |
| FR-002 | Sistem MUST memvalidasi token JWT (issuer dan exp) pada setiap endpoint terlindung melalui dekorator `require_auth`. Token tidak valid menghasilkan HTTP 401 `{"error":"missing or invalid token"}`. | semua peran | curl tanpa header `Authorization: Bearer ...` ke `GET /api/patients` menghasilkan HTTP 401. | Middleware `api/middleware.py:17-34`; primitif JWT `api/auth.py:35-39` | M |
| FR-003 | Sistem MUST menampilkan tiga preset demo login pada halaman `/login` dengan label "Demo Bidan", "Demo Masyarakat", "Demo Admin"; tiap tombol MUST memperlihatkan format `username / password` yang akan diisikan ke form (B09). Tombol mengisi form, tetapi pengguna tetap MUST menekan submit atau Enter untuk masuk. | masyarakat, tenaga_kesehatan, admin | Klik tombol "Demo Bidan" mengisi input `bidan_siti` dan `siti2026`; klik Masuk berhasil. Teks `bidan_siti / siti2026` tampak pada UI. | Route `/login` (`src/app/login/page.tsx:18-43, 80-109`) | M |
| FR-004 | Sistem MUST membaca nilai submit dari `FormData` instans `<form>` untuk menghindari kondisi balapan controlled-input pada browser autofill atau password manager. Sistem MUST menolak submit kosong dengan pesan "Username dan password wajib diisi." dalam Bahasa Indonesia. | tenaga_kesehatan, masyarakat, admin | Mengisi input dengan password manager lalu klik Masuk berhasil menghasilkan POST dengan payload yang benar. | `src/app/login/page.tsx:80-98` | M |
| FR-005 | Sistem MUST menerapkan kontrol akses berbasis peran (RBAC) pada endpoint terlindung melalui dekorator `require_role`. Peran yang tidak diizinkan harus menerima HTTP 403 `{"error":"forbidden"}` tanpa kebocoran skema. | semua peran | Login sebagai `bidan_siti` lalu GET `/api/admin/system-stats` mengembalikan 403. | Middleware `api/middleware.py:37-51` | M |
| FR-006 | Sistem MUST menyediakan endpoint logout yang mengirimkan respons 200 sehingga frontend dapat menghapus cookie httpOnly. | semua peran | POST `/api/auth/logout` mengembalikan 200 `{"status":"logged_out"}`. | `POST /api/auth/logout` (`api/routes/auth_routes.py:49`) | S |
| FR-007 | Sistem MUST menyediakan endpoint introspeksi sesi yang mengembalikan profil pengguna saat ini dari klaim token. | semua peran | GET `/api/auth/me` dengan token valid mengembalikan `{"username","role","name"}`. | `GET /api/auth/me` (`api/routes/auth_routes.py:43`) | M |
| FR-008 | Frontend MUST melakukan defense-in-depth dengan middleware Next.js yang me-redirect pengguna tanpa cookie sesi ke `/login` dan pengguna non-admin yang mengakses `/admin/*` ke landing role-nya. | semua peran | curl `/admin/scraper` tanpa cookie mendapat 307 ke `/login`; sebagai bidan mendapat 307 ke `/dashboard`. | `src/middleware.ts:35-67` (lihat T1-VERIFY check C3 dan C4) | M |

#### 3.1.2 CRUD Pasien (Schema SOAP)

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-010 | Sistem MUST mengembalikan daftar ringkas pasien terurut newest-first menggunakan parser tanggal `DD-MM-YYYY` pada `tanggal_kunjungan` dan tiebreak menurun pada numeric tail id (`P003` mendahului `P001` jika tanggal sama). (B07) | tenaga_kesehatan, admin | GET `/api/patients` mengembalikan array dengan elemen pertama bertanggal kunjungan terbaru; respon T1-PASIEN menunjukkan `P010 (18-05-2026)` di posisi pertama. | `GET /api/patients` (`api/routes/patient_routes.py:135-146`) | M |
| FR-011 | Sistem MUST membuat rekam pasien baru dengan ID berformat `P` + tiga digit (`P001`..`P999`). ID dihasilkan dari `anggota2.pasien_helper.generate_id` (jika modul tersedia) atau fallback inline. | tenaga_kesehatan, admin | POST `/api/patients` mengembalikan 201 dengan body berisi `id` baru yang unik. | `POST /api/patients` (`api/routes/patient_routes.py:162-187`) | M |
| FR-012 | Sistem MUST memvalidasi empat field wajib: `nama`, `S.keluhan`, `A.diagnosa`, `P.tindakan`. Ketidakhadiran field wajib menghasilkan HTTP 400 `{"error":"<field> required"}`. | tenaga_kesehatan, admin | POST tanpa `S.keluhan` mengembalikan 400 dengan pesan "S.keluhan required". | `api/routes/patient_routes.py:166-173` | M |
| FR-013 | Sistem MUST memvalidasi seluruh field numerik medis terhadap range klinis di sisi server (B03). Pelanggaran menghasilkan HTTP 400 dengan body `{"error":"Validasi gagal","fields":[...]}` dan pesan Bahasa Indonesia per field. Range yang diterapkan: BB `1..300 kg`, TB `30..300 cm`, LILA `8..60 cm`, Nadi `30..220 x/menit`, Suhu `30..44 C`, Respirasi `5..80 x/menit`, tekanan darah komposit dengan sistolik `60..250 mmHg` dan diastolik `30..160 mmHg` mengikuti pola `\d{1,3}/\d{1,3}`. | tenaga_kesehatan, admin | POST dengan `O.bb_kg="abc"` mengembalikan 400 dengan pesan "BB (kg) harus berupa angka.". POST dengan `O.tekanan_darah="999/80"` mengembalikan 400 dengan pesan sistolik out-of-range. | `api/routes/patient_routes.py:17-99` | M |
| FR-014 | Frontend MUST melakukan validasi mirror sisi klien pada blur dan submit dengan mesin yang sama (range, tipe). Field invalid harus menampilkan inline error berperan `role="alert"` di bawah input dalam Bahasa Indonesia. | tenaga_kesehatan, admin | Ketik `abc` pada input BB di `/patients/new`, blur input, error "BB (kg) harus berupa angka." muncul di bawah. | `src/lib/patient-validation.ts`; `src/app/patients/new/page.tsx` (`new/page.tsx`) | M |
| FR-015 | Sistem MUST mengembalikan detail satu rekam pasien lengkap. Peran `masyarakat` MUST hanya boleh mengakses rekam miliknya sendiri (cek `owner_username`); pelanggaran menghasilkan HTTP 403. | tenaga_kesehatan, admin, masyarakat | GET `/api/patients/P001` sebagai bidan_siti mengembalikan 200 dengan SOAP lengkap; sebagai umum_budi (bukan owner) mengembalikan 403. | `GET /api/patients/<pid>` (`api/routes/patient_routes.py:149-159`) | M |
| FR-016 | Sistem MUST melakukan deep-merge body PUT ke dalam rekam pasien yang ada, mempertahankan `id` semula dan mempertahankan field nested S/O/A/P yang tidak disertakan dalam body. Validasi range FR-013 berlaku juga pada PUT. | tenaga_kesehatan, admin | PUT `/api/patients/P001` dengan body parsial `{"O":{"tekanan_darah":"120/80"}}` mempertahankan field lain di `O`. | `PUT /api/patients/<pid>` (`api/routes/patient_routes.py:190-205`) | M |
| FR-017 | Sistem MUST membatasi penghapusan rekam pasien hanya untuk peran `admin`. | admin | DELETE `/api/patients/P001` sebagai admin mengembalikan 204; sebagai bidan_siti mengembalikan 403. | `DELETE /api/patients/<pid>` (`api/routes/patient_routes.py:208-217`) | S |

#### 3.1.3 Katalog dan Pencarian Obat

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-020 | Sistem MUST mengembalikan daftar obat dari katalog `anggota4/data/drug_database.json`. Parameter query `category` (case-insensitive) MUST memfilter berdasarkan field `kategori`. | semua peran (tidak memerlukan auth) | GET `/api/drugs?category=analgesik dan antipiretik` mengembalikan hanya Paracetamol dan Ibuprofen. | `GET /api/drugs` (`api/routes/drug_routes.py:19-28`) | M |
| FR-021 | Sistem MUST menyediakan pencarian obat berbasis kata kunci yang mendelegasikan ke `anggota4.pencarian_obat.cari_obat`. Pencarian harus mempertimbangkan field `alias` (misalnya "Acetaminophen" mencari Paracetamol). | semua peran (tidak memerlukan auth) | GET `/api/drugs/search?q=paracetamol` mengembalikan minimal entri Paracetamol. | `GET /api/drugs/search` (`api/routes/drug_routes.py:31-40`) | M |
| FR-022 | Sistem MUST mengembalikan profil keamanan lengkap satu obat berdasarkan nama, atau HTTP 404 jika tidak ditemukan. | semua peran | GET `/api/drugs/Paracetamol` mengembalikan profil; GET `/api/drugs/ObatYangTidakAda` mengembalikan 404. | `GET /api/drugs/<nama_obat>` (`api/routes/drug_routes.py:43-51`) | S |

#### 3.1.4 Cek Interaksi dan Keamanan Obat

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-030 | Sistem MUST menerima daftar obat (`drugs: string[]`) yang minimal berisi satu obat dan opsional `pasien_id`. Sistem MUST mendelegasikan analisis ke `anggota4.safety_checker.cek_keamanan_obat` dan mengagregasi hasil. | tenaga_kesehatan, masyarakat, admin | POST `/api/safety/check` dengan `{"drugs":["paracetamol","ibuprofen"]}` mengembalikan 200 dengan field `drugs`, `interactions`, `severity_score`, `severity_level`. | `POST /api/safety/check` (`api/routes/safety_routes.py:16-72`) | M |
| FR-031 | Sistem MUST menghitung `severity_score` sebagai bilangan bulat 0..100 (round dari maksimum skor per obat) dan `severity_level` sebagai `low`/`medium`/`high` hasil pemetaan dari label Bahasa Indonesia `rendah`/`sedang`/`tinggi` dengan pemilihan label tertinggi di antara obat-obat yang diperiksa. | tenaga_kesehatan, admin | Cek `paracetamol + ibuprofen` mengembalikan `severity_score=60` dan `severity_level="medium"` (lihat smoke test pada T1-PASIEN). | `api/routes/safety_routes.py:34-42, 63-71` | M |
| FR-032 | Sistem MUST mengembalikan daftar obat aktif pasien (`pasien_active_meds`) ketika `pasien_id` disertakan dalam request. Daftar didapat dari parsing field `P.resep` pasien yang sedang dirawat melalui `parse_resep_to_meds`. (B05) | tenaga_kesehatan, masyarakat (untuk dirinya), admin | POST `/api/safety/check` dengan `pasien_id=P001` mengembalikan `pasien_active_meds:["Asam folat","Amoxicillin"]`. | `api/routes/safety_routes.py:44-61`; parser `api/helpers.py:47-96` | M |
| FR-033 | Frontend MUST otomatis menggabungkan `pasien_active_meds` ke dalam daftar obat input pengecekan, dengan deduplikasi case-insensitive; pengguna tetap dapat menambah atau menghapus chip obat secara manual. | tenaga_kesehatan, masyarakat, admin | Pilih pasien P001 di `/safety-checker`, chip "Asam folat" dan "Amoxicillin" muncul; chip dapat dihapus. | `src/app/safety-checker/page.tsx` (`safety-checker/page.tsx`) | M |
| FR-034 | Frontend MUST menyediakan panel collapsible "Cara membaca verdikt dan obat aktif" yang menjelaskan konsep obat aktif, formula skor severitas (`total_bobot / (jumlah_efek * 4) * 100`, dengan bobot ringan=1, sedang=2, serius=4), threshold label, dan rasional munculnya banyak kartu. (B08) | masyarakat, tenaga_kesehatan | Panel default tertutup, klik header menampilkan tiga seksi penjelas dalam Bahasa Indonesia. | `src/app/safety-checker/page.tsx`; lihat T1-SAFETY bagian 4. | M |

#### 3.1.5 Visualisasi

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-040 | Sistem MUST mengembalikan tren kunjungan 12 bulan dengan kunci bulan Bahasa Indonesia singkat. Jika tidak ada data pasien, sistem MUST mengembalikan baseline dummy yang konsisten supaya UI tidak kosong saat demo. | tenaga_kesehatan, admin | GET `/api/visualizations/kunjungan-trend` mengembalikan array 12 elemen `{month,count}`. | `GET /api/visualizations/kunjungan-trend` (`api/routes/visualization_routes.py:54-66`) | S |
| FR-041 | Sistem MUST mengembalikan distribusi kategori keluhan dari rekam pasien atau fallback dummy bila kosong. | tenaga_kesehatan, admin | GET `/api/visualizations/keluhan-distribution` mengembalikan array `{kategori,count}` terurut desc. | `GET /api/visualizations/keluhan-distribution` (`api/routes/visualization_routes.py:69-80`) | S |
| FR-042 | Sistem MUST mengembalikan top-10 efek samping ter-frekuent berdasarkan banyak obat yang melaporkan efek tersebut, lengkap dengan `tingkat_keparahan`. | semua peran terotentikasi | GET `/api/visualizations/top-efek-samping` mengembalikan array <=10 elemen `{nama_efek,count,kategori,tingkat_keparahan}`. | `GET /api/visualizations/top-efek-samping` (`api/routes/visualization_routes.py:83-110`) | S |
| FR-043 | Sistem MUST mengembalikan matriks heatmap obat x efek samping dengan nilai biner presence. | semua peran terotentikasi | GET `/api/visualizations/heatmap-efek` mengembalikan `{drugs[],effects[],values[][]}`. | `GET /api/visualizations/heatmap-efek` (`api/routes/visualization_routes.py:113-138`) | S |
| FR-044 | Frontend `/heatmap` MUST merender setiap sel dengan warna kontinu sequential 5-stop ramp risk-matrix (green to red) yang dipetakan oleh `d3-scale.scaleLinear` clamped pada `[min,max]`. Sel dengan v=0 MUST tetap diwarnai (lightest tint), bukan latar belakang halaman. Sel NaN/undefined MUST ditampilkan dengan pola hatch dan label "N/A". (B11) | tenaga_kesehatan, masyarakat, admin | Setiap dari 102 sel pada dataset 6x17 memiliki warna terdefinisi dan aria-label berisi nilai numerik (T1-HEATMAP evidence). | `src/app/heatmap/page.tsx`; util `src/lib/heatmap-colors.ts` | M |
| FR-045 | Frontend heatmap MUST menampilkan legend gradient swatch 14 px dengan tiga tick (`min`, `mid`, `max`) dan caption Bahasa Indonesia yang menjelaskan bahwa nilai sel adalah presence x bobot keparahan. | tenaga_kesehatan, masyarakat, admin | Legend block menampilkan "Skala intensitas", "rendah > tinggi", swatch gradient, tick 0/2/4, dan caption sumber data. | `src/app/heatmap/page.tsx` legend section | M |
| FR-046 | Frontend heatmap MUST mengurutkan baris dan kolom secara descending berdasarkan total bobot baris dan kolom (bukan alfabet). | tenaga_kesehatan, masyarakat, admin | Pada dataset 6x17, baris teratas adalah obat dengan total bobot tertinggi (Ibuprofen 12), kolom pertama adalah efek dengan total bobot tertinggi. | `src/app/heatmap/page.tsx` sorted useMemo | S |

#### 3.1.6 Eksport PDF

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-050 | Sistem MUST membangkitkan PDF rekam medis SOAP per pasien dengan delegasi ke `anggota5.export_pdf.buat_laporan_pdf` setelah translasi schema flat Bimo ke nested Abhidal. PDF MUST `Content-Type: application/pdf` berukuran >=2 KB. (B04 sub-1) | tenaga_kesehatan, admin | POST `/api/pdf/generate-rekam-medis` dengan `{"pasien_id":"P001"}` mengembalikan PDF 2.0 KB minimum. | `POST /api/pdf/generate-rekam-medis` (`api/routes/pdf_routes.py:169-202`) | M |
| FR-051 | Sistem MUST membangkitkan PDF laporan kunjungan bulanan agregat. Filter bulan `YYYY-MM` harus benar membandingkan suffix `MM-YYYY` dari `tanggal_kunjungan` (perbaikan T1-PDF dari bug suffix). Endpoint terbatas peran `admin`. | admin | POST dengan `{"month":"2026-04"}` mengembalikan PDF berisi pasien dengan tanggal April 2026. | `POST /api/pdf/generate-laporan-bulanan` (`api/routes/pdf_routes.py:205-238`) | M |
| FR-052 | Sistem MUST membangkitkan PDF laporan efek samping yang menggabungkan frekuensi obat dalam `P.resep` seluruh pasien dengan `anggota1/data/drug_safety_data.json` untuk menghasilkan ranking top-25 efek samping tertimbang dan tabel severitas per obat. Fallback weight 1 per obat ketika tidak ada pasien sehingga PDF tidak pernah kosong. (B04 sub-2) | tenaga_kesehatan, admin | POST `/api/pdf/generate-efek-samping` mengembalikan PDF >=4 KB dengan tabel top-25 efek. | `POST /api/pdf/generate-efek-samping` (`api/routes/pdf_routes.py:241-385`) | M |
| FR-053 | Sistem MUST membangkitkan PDF laporan inventaris obat berisi distribusi per kategori farmakologi, daftar obat dengan kategori-indikasi-kehamilan, dan detail dosis serta peringatan per obat. (B04 sub-3) | tenaga_kesehatan, admin | POST `/api/pdf/generate-inventaris` mengembalikan PDF >=3 KB. | `POST /api/pdf/generate-inventaris` (`api/routes/pdf_routes.py:388-511`) | M |
| FR-054 | Frontend `/export-pdf` MUST menyediakan empat pilihan jenis laporan dan UI step-2 yang berbeda per tipe (pasien picker untuk rekam medis, date-range untuk bulanan, cakupan statis untuk efek samping dan inventaris). Setiap pilihan harus memanggil endpoint backend yang benar. | tenaga_kesehatan, admin | Memilih "Inventaris obat" dan klik Generate menghasilkan unduhan PDF dari `/api/pdf/generate-inventaris`. | `src/app/export-pdf/page.tsx` | M |

#### 3.1.7 Administrasi Sistem

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-060 | Sistem MUST menyediakan endpoint pemicu scraper (mocked dengan sleep 3 detik, mengembalikan timestamp dan jumlah obat terkini). Akses terbatas peran `admin`. Implementasi production-grade akan memanggil `anggota1` melalui worker queue (didokumentasikan di `docs/ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md`). | admin | POST `/api/admin/scrape` sebagai admin mengembalikan `{status:"completed", drugs_updated, recalls_added, timestamp}`. | `POST /api/admin/scrape` (`api/routes/admin_routes.py:21-38`) | M |
| FR-061 | Sistem MUST mengembalikan daftar pengguna dengan password yang sudah ter-strip (`password_hash`, `password_plain`, `password` dihapus dari respon). | admin | GET `/api/admin/users` mengembalikan array user tanpa field `password_hash`. | `GET /api/admin/users` (`api/routes/admin_routes.py:41-45`) | M |
| FR-062 | Sistem MUST menciptakan user baru dengan role valid `tenaga_kesehatan|masyarakat|admin`. Password MUST di-hash bcrypt cost 12. Username unik (HTTP 409 jika duplikat). Bila username tidak diberikan, sistem dapat membentuk dari kombinasi `<name>+<phone[-4:]>`. | admin | POST `/api/admin/users` dengan `{username,password,role,name,phone}` valid mengembalikan 201 dengan field user (tanpa password_hash). | `POST /api/admin/users` (`api/routes/admin_routes.py:48-85`) | M |
| FR-063 | Sistem MUST mencegah penghapusan admin terakhir (mengembalikan 400 "cannot delete last admin"). | admin | DELETE admin satu-satunya yang tersisa mengembalikan HTTP 400. | `DELETE /api/admin/users/<username>` (`api/routes/admin_routes.py:88-103`) | M |
| FR-064 | Sistem MUST mengembalikan statistik sistem real-time: `users_count`, `patients_count`, `drugs_count`, breakdown `users_by_role`, `last_scrape`, `process_started_at`, dan `uptime_seconds`. Tidak ada nilai hardcoded (B10). | admin | GET `/api/admin/system-stats` mengembalikan nilai yang berubah sesuai data file dan uptime. | `GET /api/admin/system-stats` (`api/routes/admin_routes.py:106-127`) | M |
| FR-065 | Frontend dashboard admin MUST merender keempat KPI (Pengguna aktif, Pasien terdaftar, Obat di katalog, Uptime API) dari respon `/api/admin/system-stats`, tanpa angka hardcoded. Helper `formatUptime(seconds)` mengonversi detik menjadi label kompak (`5m`, `3j 12m`, `2h 4j`). (B10) | admin | grep pada repo frontend untuk literal `1.247`, `1,247`, `99.94`, `99,94` mengembalikan zero matches; KPI di `/admin/dashboard` berubah ketika `users.json` berubah. | `src/app/admin/dashboard/page.tsx:43-81`; T1-VERIFY check C5-C7 | M |
| FR-066 | Frontend dashboard admin MUST memuat CTA prominen "Jalankan Scraper Obat" yang link ke `/admin/scraper` dengan `data-testid="cta-scraper"` (B01). | admin | Snapshot `/admin/dashboard` memperlihatkan card dengan link `Buka panel scraper` ke `/admin/scraper`. | `src/app/admin/dashboard/page.tsx:170-226` | M |
| FR-067 | Frontend dashboard pengguna MUST memiliki tombol "Lihat semua" pada panel "Aktivitas terbaru" yang link ke `/dashboard/aktivitas` dengan `data-testid="lihat-semua-aktivitas"` (B02). | tenaga_kesehatan, masyarakat, admin | Klik "Lihat semua" pada `/dashboard` navigasi ke `/dashboard/aktivitas` yang menampilkan feed lengkap. | `src/app/dashboard/page.tsx` line ~442; route `src/app/dashboard/aktivitas/page.tsx` | M |

#### 3.1.8 Endpoint Pendukung (Health dan Info)

| ID | Deskripsi | Persona | Acceptance Criteria | Endpoint atau Route | Prioritas |
|---|---|---|---|---|---|
| FR-070 | Sistem MUST mengekspos endpoint health-check tak terlindung yang mengembalikan status, versi, dan timestamp ISO-8601. | semua peran (public) | GET `/api/health` mengembalikan 200 `{"status":"ok","version":"1.0.0","time":...}`. | `GET /api/health` (`api/routes/health.py:12-18`) | M |
| FR-071 | Sistem MUST menyediakan endpoint info modul yang menunjukkan modul anggota mana yang berhasil ter-load dan apakah cloud storage aktif. | semua peran | GET `/api/info` mengembalikan dictionary `modules_loaded` dengan boolean per modul. | `GET /api/info` (`api/routes/health.py:21-36`) | S |

Total persyaratan fungsional: 40 ID (FR-001 sampai FR-071 dengan
nomor selektif). Semua endpoint disurvei lengkap (27 endpoint HTTP)
dengan acuan file:line pada implementasi backend dan frontend.

#### 3.1.9 Bentuk Payload Request dan Response (Ringkasan)

Bagian ini melengkapi acceptance criteria di atas dengan bentuk
payload utama yang harus dipenuhi implementasi. Spesifikasi terperinci
per endpoint berada pada `docs/API.md`. Schema data dijelaskan pada
`docs/DATA-DICTIONARY.md`.

Login (FR-001).

Request body:

```
{
  "username": "string (1..64 char)",
  "password": "string (1..128 char)"
}
```

Response sukses (200):

```
{
  "token": "<JWT HS256>",
  "user": { "username": "string", "role": "tenaga_kesehatan|masyarakat|admin", "name": "string" }
}
```

Response gagal (401): `{"error":"invalid credentials"}`.

Create patient (FR-011, FR-012, FR-013).

Request body (contoh sesuai schema kanonikal pasien, lihat
`api/data/patients.json` baris 2-30 untuk contoh nyata):

```
{
  "tanggal_kunjungan": "DD-MM-YYYY",
  "nama": "string (wajib)",
  "umur": "string",
  "alamat": "string",
  "kategori": "string",
  "S": {"keluhan": "string (wajib)", "riwayat": "string"},
  "O": {
    "tekanan_darah": "120/80",
    "nadi": "82",
    "suhu_c": "36.8",
    "respirasi": "18",
    "bb_kg": "60",
    "tb_cm": "165",
    "lila_cm": "24",
    "catatan": "string"
  },
  "A": {"diagnosa": "string (wajib)"},
  "P": {"tindakan": "string (wajib)", "resep": "string multi-baris", "jadwal_kontrol": "string"}
}
```

Response sukses (201): objek pasien lengkap dengan `id` baru.

Response validasi gagal (400):

```
{
  "error": "Validasi gagal",
  "fields": ["BB (kg) harus antara 1 dan 300.", "..."]
}
```

Safety check (FR-030..FR-032).

Request body:

```
{ "drugs": ["paracetamol", "ibuprofen"], "pasien_id": "P001 (opsional)" }
```

Response sukses (200):

```
{
  "drugs": [ <object hasil_obat dari anggota4.safety_checker> ],
  "interactions": [ {"nama_efek": "...", "obat_terkait": [...], "tingkat_tertinggi": "ringan|sedang|serius"} ],
  "severity_score": 60,
  "severity_level": "low|medium|high",
  "warnings": ["..."],
  "obat_tidak_ditemukan": ["..."],
  "pasien_context": { "id", "nama", "kategori", "diagnosa", "kondisi_umum" } | null,
  "pasien_active_meds": ["Asam folat", "Amoxicillin"]
}
```

System stats (FR-064).

Response sukses (200):

```
{
  "users_count": 6,
  "patients_count": 11,
  "drugs_count": 6,
  "last_scrape": null | {"status", "drugs_updated", "recalls_added", "source", "timestamp"},
  "users_by_role": {"tenaga_kesehatan": 2, "masyarakat": 2, "admin": 2},
  "process_started_at": "ISO-8601",
  "uptime_seconds": 3188
}
```

Heatmap data (FR-043).

Response sukses (200):

```
{
  "drugs": ["Paracetamol", "Ibuprofen", "Amoxicillin", "Captopril", "Cetirizine", "Metformin"],
  "effects": ["Mual", "Pusing", "Ruam kulit", ...],
  "values": [[0, 1, 0, ...], ...]
}
```

#### 3.1.10 Matriks Keterunutan Bug Register ke FR-ID

Tabel ini menghubungkan setiap bug yang ditangani Wave 1 dengan
persyaratan fungsional yang dipengaruhi dan bukti perbaikan
(lihat `.mission/findings/bugs/T1-*.md`):

| Bug ID | Deskripsi singkat | FR yang terkait | Bukti perbaikan |
|---|---|---|---|
| B01 | Tidak ada CTA admin scraper di dashboard | FR-066 | `src/app/admin/dashboard/page.tsx:170-226`; T1-ADMIN section 4.2 |
| B02 | Tombol "Lihat semua" inert | FR-067 | `src/app/dashboard/page.tsx ~442-444`; new route `dashboard/aktivitas/page.tsx`; T1-ADMIN section 4.3-4.4 |
| B03 | Form pasien menerima huruf pada field numerik | FR-013, FR-014 | `api/routes/patient_routes.py:17-99`; `src/lib/patient-validation.ts`; T1-PASIEN |
| B04 | Eksport PDF hanya SOAP | FR-050, FR-051, FR-052, FR-053, FR-054 | `api/routes/pdf_routes.py:241-511`; `src/app/export-pdf/page.tsx`; T1-PDF |
| B05 | Safety check tidak menampilkan obat aktif pasien | FR-032, FR-033 | `api/routes/safety_routes.py:44-71`; `src/app/safety-checker/page.tsx`; T1-SAFETY |
| B06 | KPI dashboard admin self-resolving dari clean state | FR-064, FR-065 | `api/routes/admin_routes.py:106-127`; T1-VERIFY |
| B07 | List pasien sort newest-at-bottom | FR-010 | `api/routes/patient_routes.py:135-146`; T1-PASIEN |
| B08 | Tidak ada penjelasan inline verdikt safety | FR-034 | `src/app/safety-checker/page.tsx` collapsible panel; T1-SAFETY section 4 |
| B09 | Manual login gagal, demo creds tidak tampak | FR-003, FR-004 | `src/app/login/page.tsx:18-43, 80-109`; T1-LOGIN |
| B10 | KPI uptime admin hardcoded | FR-064, FR-065 | `api/routes/admin_routes.py:18, 106-127`; `src/app/admin/dashboard/page.tsx`; T1-ADMIN section 4.1 |
| B11 | Heatmap tidak kontinu | FR-044, FR-045, FR-046 | `src/lib/heatmap-colors.ts` (new); `src/app/heatmap/page.tsx` rewrite; T1-HEATMAP |

#### 3.1.11 Aturan Bisnis Tambahan

| ID | Aturan |
|---|---|
| BR-001 | Pasien diidentifikasi unik dengan ID format `P` + 3 digit (`P001`..`P999`) per `.md` Rule 3 schema source-of-truth. Tidak ada migrasi ke `PSN-001` (draf Abhidal non-kanonikal). |
| BR-002 | Tanggal kunjungan disimpan dalam format `DD-MM-YYYY` (literal hyphen). Tanggal yang tidak parse-able dipertahankan tetapi diurutkan ke bawah pada list newest-first. |
| BR-003 | Field `O.nadi`, `O.suhu_c`, `O.respirasi` dianggap optional karena bidan tidak selalu mengukurnya; field wajib hanya `nama`, `S.keluhan`, `A.diagnosa`, `P.tindakan` (sesuai workflow bidan di Faskes 1). |
| BR-004 | Bobot keparahan efek samping mengikuti `anggota4.safety_checker.BOBOT_KEPARAHAN`: `ringan=1`, `sedang=2`, `serius=4`. Threshold label aggregate mengikuti `_label_risiko` di modul yang sama. |
| BR-005 | Format severitas dalam respon API safety check menggunakan label Inggris (`low/medium/high`) demi konsistensi pada UI internasional-friendly, sementara label internal Bahasa Indonesia (`rendah/sedang/tinggi`) dipertahankan pada modul anggota4. |
| BR-006 | Penghapusan admin terakhir dilarang sistem untuk mempertahankan ketersediaan jalur administrasi (lihat NFR-SEC-007). |
| BR-007 | Field `P.resep` di-parse oleh `parse_resep_to_meds` dengan toleransi dosage hint (`3x500mg`, `1x1 sehari`), parenthetical note, dan latin frequency tokens (`prn`, `bid`, `qd`, `tid`, `qid`). Daftar yang dihasilkan tidak mengubah file asli. |
| BR-008 | Token JWT memiliki masa hidup 12 jam (`JWT_EXPIRY_HOURS=12` pada `api/config.py:19`) yang mencerminkan satu sesi shift bidan. |

### 3.2 Persyaratan Antarmuka Eksternal

#### 3.2.1 Antarmuka Pengguna (User Interface)

Aplikasi web Next.js mengekspos antarmuka berikut. Semua route bersifat
client-rendered (`"use client"`) atau hybrid dengan dynamic = "force-dynamic".

| Route | Berkas | Persona yang Dapat Mengakses | Fungsi |
|---|---|---|---|
| `/` | `src/app/page.tsx` | semua | Redirect ke `/dashboard`. |
| `/login` | `src/app/login/page.tsx` | publik | Halaman login dengan 3 preset demo. |
| `/dashboard` | `src/app/dashboard/page.tsx` | tenaga_kesehatan, masyarakat, admin | Dashboard utama berisi KPI, aktivitas terbaru, dan link cepat. |
| `/dashboard/aktivitas` | `src/app/dashboard/aktivitas/page.tsx` | tenaga_kesehatan, masyarakat, admin | Feed aktivitas penuh tanpa pagination (B02). |
| `/patients` | `src/app/patients/page.tsx` | tenaga_kesehatan, admin | Daftar pasien dengan urut newest-first (B07). |
| `/patients/new` | `src/app/patients/new/page.tsx` | tenaga_kesehatan, admin | Form input pasien dengan validasi range numerik (B03). |
| `/patients/[id]` | `src/app/patients/[id]/page.tsx` | tenaga_kesehatan, admin | Edit rekam pasien tertentu, mirror validasi sama. |
| `/pasien/profile` | `src/app/pasien/profile/page.tsx` | masyarakat | Profil ringkas pengguna masyarakat. |
| `/drug-search` | `src/app/drug-search/page.tsx` | semua peran | Pencarian dan filter daftar obat. |
| `/drug-comparison` | `src/app/drug-comparison/page.tsx` | semua peran | Membandingkan profil hingga 3 obat berdampingan. |
| `/safety-checker` | `src/app/safety-checker/page.tsx` | semua peran | Pengecekan keamanan dan interaksi obat dengan konteks pasien (B05, B08). |
| `/visualization` | `src/app/visualization/page.tsx` | tenaga_kesehatan, admin | Dashboard visualisasi (Recharts). |
| `/heatmap` | `src/app/heatmap/page.tsx` | semua peran | Heatmap kontinu obat x efek (B11). |
| `/export` | `src/app/export/page.tsx` | tenaga_kesehatan, admin | Legacy export PDF (rekam medis + bulanan). |
| `/export-pdf` | `src/app/export-pdf/page.tsx` | tenaga_kesehatan, admin | Eksport empat tipe PDF (B04). |
| `/admin/dashboard` | `src/app/admin/dashboard/page.tsx` | admin | Dashboard admin dengan KPI real (B10) dan CTA scraper (B01). |
| `/admin/scraper` | `src/app/admin/scraper/page.tsx` | admin | Panel pemicu scraper. |
| `/admin/users` | `src/app/admin/users/page.tsx` | admin | Manajemen pengguna (list + create + delete). |

UI menggunakan palette MedWatch yang terkonsolidasi pada
`src/app/globals.css` dengan token semantik `--safe`, `--warn`, `--crit`.
Header dan sidebar layout dibungkus pada `src/components/layout/Sidebar.tsx`
(`Sidebar.tsx:53-70` mengatur RBAC navigasi).

#### 3.2.2 Antarmuka Perangkat Keras

MedWatch tidak menggunakan perangkat keras khusus. Persyaratan
operasional minimum bagi pengguna:

| Tier | Requirement |
|---|---|
| Desktop CustomTkinter (utama) | CPU x86-64 atau Apple Silicon, RAM >= 4 GB, ruang disk 500 MB untuk Python venv. |
| Web client | Browser modern (Chrome >= 120, Firefox >= 120, Edge >= 120, Safari >= 17). Resolusi minimum 360 x 640 (smartphone) hingga 1920 x 1080 (desktop). |
| Backend host | Cloud Run instance 512 MiB RAM, 1 vCPU on-demand, region `asia-southeast1`. |

#### 3.2.3 Antarmuka Perangkat Lunak

| Komponen | Versi | Sumber |
|---|---|---|
| Python | 3.13 (Cloud Run runtime di Dockerfile menggunakan Python 3.11 fallback) | `api/requirements.txt`, `api/Dockerfile` |
| Flask | 3.0+ | `api/requirements.txt` |
| Flask-CORS | 4.0+ | `api/requirements.txt` |
| PyJWT | 2.x | `api/auth.py:2` |
| bcrypt | 4.x | `api/auth.py:1, 11` |
| fpdf2 | 2.7+ | `api/routes/pdf_routes.py:22` |
| matplotlib | 3.9+ (untuk modul anggota3) | `anggota3/TampilGrafik.py` |
| google-cloud-storage | 2.x (opsional, hanya bila USE_CLOUD_STORAGE=true) | `api/storage.py:25` |
| Node.js | 22 LTS (Vercel Hobby) | `package.json`, lihat blocker B-WAVE1-BUILD-1 untuk Node 25 incompatibility |
| Next.js | 16.x App Router | `package.json` |
| TypeScript | 5.x strict mode | `tsconfig.json` |
| Tailwind CSS | v4 | `tailwind.config.ts` |
| d3-scale, d3-interpolate | 4.x / 3.x | `package.json` (digunakan di `src/lib/heatmap-colors.ts`) |

#### 3.2.4 Antarmuka Komunikasi

1. **HTTP/HTTPS**. Browser klien terhadap Vercel frontend menggunakan
   HTTPS dengan sertifikat default Vercel. Backend Cloud Run juga
   mengekspos HTTPS dengan sertifikat default `*.run.app`.
2. **JWT**. Sesi otentikasi disimpan sebagai cookie httpOnly +
   SameSite=Lax + Secure. Token dikeluarkan dengan klaim `sub`,
   `role`, `name`, `iat`, `exp`, `iss="medwatch-api"` (lihat
   `api/auth.py:22-32`). Verifikasi mengikat issuer di
   `api/auth.py:37`.
3. **CORS**. Allowlist origin dibatasi pada
   `https://medwatch-frontend.vercel.app`,
   `http://localhost:3000`, dan `http://localhost:5173` (lihat
   `api/config.py:21-25`). `supports_credentials=True` di
   `api/app.py:30-34` memungkinkan cookie httpOnly cross-origin.
4. **Content negotiation**. Endpoint API mengembalikan JSON
   (`application/json`); endpoint PDF mengembalikan
   `application/pdf` dengan header `Content-Disposition: attachment`.

### 3.3 Persyaratan Non-Fungsional

Penomoran NFR mengikuti area ISO/IEC 25010 (Software product quality
characteristics) sebagaimana direferensikan oleh ISO/IEC/IEEE 29148:2018
Annex B.

#### 3.3.1 NFR-PERF (Performansi)

| ID | Persyaratan | Pengukuran |
|---|---|---|
| NFR-PERF-001 | Endpoint list (`GET /api/patients`, `GET /api/drugs`) MUST merespon dalam < 2 detik p95 dengan dataset realistik (200 pasien, 500 obat). | Diukur dengan curl `--write-out time_total`. |
| NFR-PERF-002 | Pembangkitan PDF rekam medis MUST selesai dalam < 5 detik untuk satu rekam SOAP. | Diukur via timestamp respon backend di `pdf_routes.py`. |
| NFR-PERF-003 | Heatmap halaman MUST melakukan render awal dalam < 1.5 detik setelah respon API tersedia, pada dataset 6x17 yang ada. | Diukur via React DevTools Profiler atau Playwright timing. |
| NFR-PERF-004 | Backend Flask MUST tahan terhadap minimal 30 request per detik pada Cloud Run instance dasar (1 vCPU, 512 MiB) untuk endpoint read-only. | Diukur dengan `wrk` atau Apache `ab` setelah deploy. |

#### 3.3.2 NFR-SEC (Keamanan)

| ID | Persyaratan | Standar Acuan |
|---|---|---|
| NFR-SEC-001 | Sistem MUST mengikuti OWASP Top 10 (2021): A01 Broken Access Control diatasi via `require_role`; A02 Cryptographic Failures diatasi via bcrypt cost 12; A03 Injection dilindungi melalui parameterized JSON parsing; A05 Security Misconfiguration ditangani via header strip-server dan CORS allowlist; A07 Identification and Authentication Failures ditangani via JWT bertanda tangan dengan exp dan iss. | OWASP Top 10 (2021) |
| NFR-SEC-002 | Password MUST di-hash dengan bcrypt cost factor 12 (default kuat). Password mentah TIDAK boleh disimpan persisten; helper `_ensure_users_hashed` mengkonversi `password_plain` ke `password_hash` saat first load. | `api/auth.py:11-12`; `api/storage.py:90-98` |
| NFR-SEC-003 | JWT MUST diterbitkan dengan klaim `iss="medwatch-api"` dan diverifikasi dengan parameter `issuer` agar token dari sistem lain ditolak. | `api/auth.py:30, 37` |
| NFR-SEC-004 | JWT MUST disimpan pada cookie httpOnly + Secure + SameSite=Lax di sisi frontend Next.js, tidak pada localStorage. | Pola proksi Vercel API route, lihat `docs/SECURITY.md` |
| NFR-SEC-005 | Tidak ada service account key JSON yang di-commit ke repositori. Cloud Run menggunakan identity-bound default service account. | Tinjauan tree dan history pada Wave 4 |
| NFR-SEC-006 | CORS allowlist MUST membatasi origin pada URL Vercel showcase dan localhost pengembang. Tidak ada wildcard `*`. | `api/config.py:21-25` |
| NFR-SEC-007 | Endpoint admin MUST mencegah penghapusan admin terakhir untuk menjaga ketersediaan jalur administratif. | `api/routes/admin_routes.py:93-98` |
| NFR-SEC-008 | Field `password_hash`, `password_plain`, `password` MUST di-strip dari setiap respon yang berisi data user. | `api/helpers.py:16-18`; digunakan di `admin_routes.py:45, 85` |
| NFR-SEC-009 | Tidak ada nilai kredensial (token, password, secret) yang ditulis ke dokumen mana pun, termasuk SRS ini. Nama resource (project, bucket, service, secret name) diizinkan. | Per-commit `secret-scan.sh` pada mission protocol |
| NFR-SEC-010 | Header `Server` Flask MUST dihapus dari respon (`strip_server_headers` after_request) untuk mengurangi information disclosure. | `api/app.py:58-61` |

#### 3.3.3 NFR-USA (Usability)

| ID | Persyaratan |
|---|---|
| NFR-USA-001 | Semua teks user-facing MUST dalam Bahasa Indonesia register formal (sapaan, perintah, label, error). Identifier kode dan nama standar tetap dalam Bahasa Inggris. |
| NFR-USA-002 | Tanggal MUST diformat `DD-MM-YYYY` di seluruh UI dan storage agar konsisten dengan praktik klinis Indonesia. |
| NFR-USA-003 | Nilai moneter (bila muncul, misalnya pada laporan inventaris yang akan datang) MUST diformat sebagai Rupiah (`Rp ...`). |
| NFR-USA-004 | UI MUST responsive pada lebar viewport 360 px hingga 1920 px tanpa kerusakan layout. Heatmap mengaktifkan horizontal scroll pada lebar < 820 px. |
| NFR-USA-005 | Error UI MUST ditampilkan inline di dekat field yang bermasalah dengan `role="alert"`, bukan hanya banner global. |
| NFR-USA-006 | UI MUST bebas em dash dan bebas emoji. |
| NFR-USA-007 | Tombol demo login MUST mempertontonkan kredensial yang akan diisikan agar dosen pemeriksa dapat memahami akses contoh tanpa membaca dokumen. |

#### 3.3.4 NFR-ACC (Accessibility)

| ID | Persyaratan | Standar Acuan |
|---|---|---|
| NFR-ACC-001 | UI MUST menargetkan kepatuhan dasar WCAG 2.1 Level AA: kontras teks minimal 4.5:1 untuk teks normal dan 3:1 untuk teks besar. | WCAG 2.1 SC 1.4.3 |
| NFR-ACC-002 | Setiap input form MUST memiliki `<label>` terkait dengan `for=`. | WCAG 2.1 SC 1.3.1, 3.3.2 |
| NFR-ACC-003 | Elemen interaktif MUST memiliki focus ring yang terlihat dan dapat dinavigasi melalui keyboard (Tab, Shift+Tab, Enter, Space). | WCAG 2.1 SC 2.4.7, 2.1.1 |
| NFR-ACC-004 | Sel heatmap MUST membawa `aria-label` yang menyebutkan kombinasi obat x efek dan nilai numeriknya agar dapat dipindai screen reader. | WCAG 2.1 SC 1.1.1 |
| NFR-ACC-005 | Header tabel MUST menggunakan `<th>` dengan `scope=` yang sesuai. | WCAG 2.1 SC 1.3.1 |

#### 3.3.5 NFR-COMP (Compatibility dan Constraints)

| ID | Persyaratan |
|---|---|
| NFR-COMP-001 | Seluruh infrastruktur MUST menggunakan free tier: openFDA, Vercel Hobby plan, Google Cloud Platform free trial credit. |
| NFR-COMP-002 | Sistem MUST tetap fungsional saat openFDA tidak tersedia, dengan fallback ke data cache lokal pada `anggota1/data/`. |
| NFR-COMP-003 | Backend Cloud Run MUST mendukung cold start < 5 detik agar UX showcase tidak terdegradasi. |
| NFR-COMP-004 | Frontend MUST dapat di-build di Node 22 LTS. Node 25 nightlies tidak didukung (lihat blocker B-WAVE1-BUILD-1). |

#### 3.3.6 NFR-PORT (Portability dan Konsistensi Lintas-Platform)

| ID | Persyaratan |
|---|---|
| NFR-PORT-001 | Schema entitas (Pasien, Drug, Side effect, User) MUST identik antara aplikasi desktop CustomTkinter dan web showcase. Kanonikalisasi diatur pada `.md` Rule 3. |
| NFR-PORT-002 | Backend MUST mendukung penyimpanan ganda: lokal JSON (`api/data/`) untuk pengembang dan GCS bucket (`medwatch-polban-2026-state`) untuk produksi, dipilih via env `USE_CLOUD_STORAGE`. |
| NFR-PORT-003 | Modul anggota1..5 MUST tetap dapat dijalankan terisolasi sebagai aplikasi desktop CustomTkinter melalui `main.py`. |

#### 3.3.7 NFR-MAINT (Maintainability)

| ID | Persyaratan |
|---|---|
| NFR-MAINT-001 | Setiap commit MUST mengikuti Conventional Commits (Cox dan Vorontsov 2017): `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `perf:`. |
| NFR-MAINT-002 | Setiap modul Python pada layer `api/` MUST memiliki docstring level modul yang menjelaskan tujuan; tiap fungsi publik MUST memiliki docstring deskriptif. |
| NFR-MAINT-003 | Keputusan arsitektural MUST dicatat sebagai ADR (Architecture Decision Record) pada `docs/adr/` mengikuti template MADR. |
| NFR-MAINT-004 | Tidak ada `eval()`, `exec()`, atau shell injection vector di codebase. Semua data pasien di-sanitize sebelum render SOAP. |
| NFR-MAINT-005 | Tidak ada `console.log` di kode TypeScript yang ter-commit pada main, kecuali di dalam blok dev-only yang jelas. Tidak ada `print()` Python di production path. |
| NFR-MAINT-006 | Tidak ada TODO tanpa referensi tiket atau follow-up yang terdokumentasi. |

### 3.4 Persyaratan Database (Persistensi Data)

Sistem MedWatch versi presentasi tidak menggunakan basis data relasional;
semua state disimpan dalam berkas JSON. Pilihan ini didokumentasikan
sebagai ADR (`docs/adr/0007-json-storage.md`). Sumber-truth dan layout
field dijelaskan terperinci dalam `docs/DATA-DICTIONARY.md`. Ringkasan
penyimpanan:

| Entitas | Lokasi (Desktop) | Lokasi (Backend) | Source-of-truth |
|---|---|---|---|
| Pasien | `anggota2/Pasien.json` | `api/data/patients.json` atau `gs://medwatch-polban-2026-state/patients.json` | `anggota2/pasien_helper.py` |
| User | `anggota5/data/users.json` (legacy) | `api/data/users.json` atau `gs://medwatch-polban-2026-state/users.json` | `api/data/users.json` (canonical) |
| Drug | `anggota4/data/drug_database.json` | sama (read-only) | `anggota4/data/drug_database.json` |
| Side effect | `anggota4/data/effect_database.json` | sama (read-only) | `anggota4/data/effect_database.json` |
| Drug safety (FAERS) | `anggota1/data/drug_safety_data.json` | sama (read-only) | scraped from openFDA |
| Drug recall | `anggota1/data/drug_recalls.json` | sama (read-only) | scraped from openFDA |

Persyaratan persistensi:

| ID | Persyaratan |
|---|---|
| FR-DB-001 | Sistem MUST menulis `users.json` dan `patients.json` dengan encoding UTF-8 dan `ensure_ascii=false` sehingga karakter Indonesia tetap terbaca manusia. |
| FR-DB-002 | Sistem MUST memuat `users.json` saat boot pertama dan meng-hash field `password_plain` apa pun yang ditemukan (perlindungan dari seed data plaintext yang tertinggal di repo). |
| FR-DB-003 | Saat `USE_CLOUD_STORAGE=true` dan file GCS belum ada, sistem MUST melakukan seed dari `api/data/` lokal ke bucket. |
| FR-DB-004 | Tidak ada ID pasien yang boleh dihapus permanen tanpa intervensi role admin; soft-delete tidak diperlukan untuk versi presentasi. |

---

#### 3.3.8 NFR-LOG (Logging dan Observability)

| ID | Persyaratan |
|---|---|
| NFR-LOG-001 | Setiap proses login berhasil MUST tercatat dengan level `INFO` (`api/routes/auth_routes.py:27`). Setiap login gagal MUST tercatat dengan level `WARNING` lengkap username yang mencoba (`api/routes/auth_routes.py:36, 39`). |
| NFR-LOG-002 | Penolakan otentikasi MUST tercatat dengan path yang ditolak agar dapat dipantau oleh admin (`api/middleware.py:21, 26`). |
| NFR-LOG-003 | Penolakan role MUST tercatat dengan informasi username dan role yang mencoba serta role yang diizinkan (`api/middleware.py:45-48`). |
| NFR-LOG-004 | Aksi mutatif admin (pembuatan user, penghapusan user, pemicuan scraper) MUST tercatat dengan identitas yang melakukan (`api/routes/admin_routes.py:26, 84, 101`). |
| NFR-LOG-005 | Tidak ada kredensial atau token JWT yang ditulis ke log; password failure hanya mencatat username (bukan password) untuk audit trail. |

#### 3.3.9 NFR-INT (Internationalization)

| ID | Persyaratan |
|---|---|
| NFR-INT-001 | Default locale aplikasi adalah `id-ID` (Bahasa Indonesia, Indonesia). |
| NFR-INT-002 | Format angka MUST menggunakan separator titik untuk ribuan dan koma untuk desimal (per kaidah BIPM untuk regio Indonesia). Penerapan: `stats.users_count.toLocaleString("id-ID")` di `src/app/admin/dashboard/page.tsx:64`. |
| NFR-INT-003 | Encoding berkas teks MUST UTF-8 tanpa BOM. JSON diserialisasi dengan `ensure_ascii=false`. |
| NFR-INT-004 | Zona waktu untuk timestamp tampil ke pengguna MUST WIB (UTC+07:00). Implementasi: konstanta `_WIB = timezone(timedelta(hours=7))` di `api/routes/pdf_routes.py:35`. Timestamp internal API tetap dalam ISO-8601 UTC. |

## 4. Asumsi Verifikasi dan Strategi Pengujian

SRS ini bertindak sebagai dasar test plan kotak-hitam yang disusun
secara terpisah pada `docs/TEST-PLAN.md` (Wave 5). Pengelompokan test
case mengikuti urutan FR-ID. Strategi pengujian ringkas:

1. **Test atomic per endpoint backend**. Setiap endpoint diuji untuk
   happy path (200/201/204), missing/invalid payload (400), missing
   auth (401), role mismatch (403), dan resource not found (404).
   Skrip terotomatisasi pada `api/tests/smoke_test.py` menjalankan
   suite 14 assertion utama.
2. **Test UI per route frontend**. Untuk setiap route pada bagian
   3.2.1 dijalankan Playwright scenario: berhasil render, RBAC
   enforce (redirect 307 atau forbidden card), interaksi utama
   memberikan respon yang diharapkan.
3. **Test integrasi B01..B11**. Setiap bug Wave 1 memiliki tiket
   T1-* yang menyimpan transcript curl, snapshot Playwright, atau
   screenshot sebagai bukti perbaikan. Lihat tabel di 3.1.10.
4. **Test cek skema data**. JSON pasien dan user diverifikasi
   terhadap schema kanonikal melalui pemeriksaan field wajib pada
   layer storage (`api/storage.py`).
5. **Test perilaku batas range numerik**. Sembilan field numerik
   medis (BB, TB, LILA, Nadi, Suhu, Respirasi, sistolik, diastolik,
   komposit TD) diuji pada lima titik: lower bound -1, lower bound,
   nilai valid tengah, upper bound, upper bound +1.

Setiap test case akan ditautkan kembali ke FR-ID atau NFR-ID melalui
Requirements Traceability Matrix (RTM) yang disusun oleh System
Analyst (Alia Ardani, NIM 251524035) pada Wave 5.

### 4.1 Lingkungan Verifikasi

| Lingkungan | Komponen | Versi | URL/Pelabuhan |
|---|---|---|---|
| Backend lokal | Flask via gunicorn / `flask run` | Python 3.13 | `http://127.0.0.1:8080` |
| Frontend lokal | Next.js dev (`npm run dev`) | Node 22 LTS | `http://localhost:3000` |
| Backend cloud | Cloud Run service `medwatch-api` | container Python 3.11 | `https://medwatch-api-XXXXX-as.a.run.app` |
| Frontend cloud | Vercel Hobby | Node 22 LTS runtime | `https://medwatch-frontend.vercel.app` |
| Storage lokal | filesystem `api/data/*.json` | n/a | n/a |
| Storage cloud | GCS bucket `medwatch-polban-2026-state` | n/a | n/a |

### 4.2 Kriteria Selesai Verifikasi (Definition of Done)

Suatu FR dianggap memenuhi definition-of-done bila:

1. Implementasi tersedia di kode (file:line dirujuk pada SRS).
2. Acceptance criteria pada tabel masing-masing terlewati melalui
   skenario test dokumentasi (smoke test, Playwright, atau curl).
3. Bukti tersimpan: file `T1-*.md` pada `.mission/findings/bugs/` atau
   transcript verifikasi pada `.mission/findings/audits/`.
4. Tidak terdapat regresi pada smoke test backend
   (`api/tests/smoke_test.py`).
5. Auditor Wave 2 memberikan status PASS untuk tiket terkait.

### 4.3 Risiko Implementasi yang Diketahui

| ID | Risiko | Mitigasi |
|---|---|---|
| RISK-001 | Next.js 16.2.1 build artifact gagal merender route klien (`InvariantError: client reference manifest...`) ketika dibuild dengan Node 25 nightly. | Mengunci versi Node ke 22 LTS dan menyusun ulang `.next` setelah `rm -rf node_modules/.cache`; didokumentasikan pada B-WAVE1-BUILD-1. |
| RISK-002 | Turbopack cache race condition di macOS saat banyak subagent berjalan paralel dengan `rm -rf .next`. | Disertasikan pada laporan T1-PASIEN; mitigasi: gunakan `npm run build && npm run start` urutan setelah agen lain selesai. |
| RISK-003 | openFDA API tidak responsif pada saat demo. | Sistem memiliki fallback cache lokal pada `anggota1/data/`, sehingga safety check tetap berfungsi dengan dataset terakhir. |
| RISK-004 | GCS bucket region berbeda dari Cloud Run region menyebabkan latency. | Bucket dan service ditetapkan keduanya pada `asia-southeast1`. |
| RISK-005 | Token JWT bocor melalui XSS bila disimpan di localStorage. | Sistem menyimpan token pada cookie httpOnly + SameSite=Lax + Secure (NFR-SEC-004). |

---

## Lampiran A: Daftar Aktor

Mengikuti notasi use case UML (OMG 2017):

| Aktor | Tipe | Deskripsi singkat |
|---|---|---|
| Tenaga Kesehatan (Bidan) | Primary | Memasukkan rekam SOAP, menjalankan safety check, mencetak rekam medis, melihat visualisasi. |
| Masyarakat | Primary | Melihat profil sendiri, mengecek interaksi obat berdasarkan resep, mencari profil obat. |
| Administrator Sistem | Primary | Memicu scraper, memanajemen pengguna, memantau statistik dan log aktivitas. |
| Sistem openFDA | Secondary | Sumber eksternal data efek samping dan recall obat. |
| Sistem Cloud Run | Secondary | Lingkungan host backend Flask. |
| Sistem Vercel | Secondary | Lingkungan host frontend Next.js. |

## Lampiran B: Indeks Use Case

Daftar lengkap use case mengacu pada diagram use case (`docs/diagrams/png/use-case.png`,
sumber `docs/diagrams/src/use-case.mmd`):

1. UC-01 Login (FR-001..FR-004, FR-007)
2. UC-02 Logout (FR-006)
3. UC-03 Melihat dashboard (FR-064, FR-065, FR-066, FR-067)
4. UC-04 Membuat rekam pasien SOAP (FR-011..FR-014)
5. UC-05 Mengubah rekam pasien (FR-016 + FR-013)
6. UC-06 Menghapus rekam pasien (FR-017)
7. UC-07 Melihat daftar pasien (FR-010)
8. UC-08 Mencari obat (FR-020, FR-021)
9. UC-09 Melihat profil keamanan obat (FR-022)
10. UC-10 Membandingkan obat (FR-021)
11. UC-11 Mengecek interaksi obat (FR-030, FR-031, FR-032, FR-033, FR-034)
12. UC-12 Melihat visualisasi kunjungan (FR-040, FR-041)
13. UC-13 Melihat heatmap obat-efek (FR-043, FR-044, FR-045, FR-046)
14. UC-14 Mengekspor rekam medis PDF (FR-050)
15. UC-15 Mengekspor laporan bulanan PDF (FR-051)
16. UC-16 Mengekspor laporan efek samping PDF (FR-052)
17. UC-17 Mengekspor inventaris obat PDF (FR-053)
18. UC-18 Memicu scraper obat (FR-060)
19. UC-19 Mengelola pengguna (FR-061, FR-062, FR-063)
20. UC-20 Memantau statistik sistem (FR-064, FR-065)
21. UC-21 Melihat log aktivitas (FR-067)

---

## Riwayat Revisi

| Versi | Tanggal | Penulis | Catatan |
|---|---|---|---|
| 0.1 | 2026-04-30 | Bimo Surya Anggara (QA) | Draf awal pre-integrasi mengikuti PRD asli (tanpa otentikasi, tanpa web tier). |
| 1.0 | 2026-05-18 | Ghaisan Khoirul Badruzaman (Project Leader) | Revisi as-built pasca Wave 1, menambahkan tier web showcase, RBAC, dan dokumentasi tiap perbaikan B01..B11. Dicocokkan dengan kode aktual baris per baris. |

Dokumen ini adalah artefak submission Wave 2 (W2-D02) dari mission MedWatch
Kelompok B5 untuk presentasi 25 Mei 2026.
