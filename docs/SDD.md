---
title: Software Design Description (SDD) MedWatch
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048)
date: 2026-05-18
status: As-Built post Wave 1
standar: IEEE 1016-2009
referensi_arsitektur: C4 model (Simon Brown)
---

# Deskripsi Desain Perangkat Lunak (Software Design Description, SDD) MedWatch

Dokumen ini ditulis mengikuti standar **IEEE 1016-2009 (IEEE Standard for Information Technology - Systems Design - Software Design Descriptions)**. Setiap *design viewpoint* yang disebut standar diisi dengan informasi yang mencerminkan keadaan kode setelah Wave 1 selesai (per 18 Mei 2026), bukan asumsi rancangan awal. Untuk *architecture viewpoints* (Context, Container, Component, Deployment) dokumen ini juga merujuk pada **C4 model** karya **Simon Brown** sebagai notasi visual pendamping.

Semua klaim teknis dilengkapi sitiran `file:line`. Tidak ada penemuan kembali dari ingatan: setiap nama route, schema, dan fungsi diverifikasi langsung terhadap kode yang ada di repositori `medWatch/` (backend) dan `FrontendMedWatch/` (frontend).

---

## 1. Pendahuluan

### 1.1 Tujuan SDD

SDD ini menjadi rujukan tunggal mengenai keputusan rancangan internal sistem MedWatch. Tujuannya:

1. Memberi *designer* dan *developer* peta dekomposisi modul agar perubahan dapat dilokalisasi tanpa efek samping silang.
2. Memberi *QA* (Bimo Surya Anggara, 251524040) basis untuk menyusun *test case* berbasis *design viewpoint*.
3. Memberi *sysadmin* yang men-deploy aplikasi (Cloud Run, Vercel, Secret Manager, GCS) gambaran *deployment topology* yang akurat.
4. Memberi *dosen* (Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana) artefak rancangan yang dapat dinilai terhadap kriteria mata kuliah Proyek 1 Pengembangan Perangkat Lunak Desktop.
5. Menjadi dokumen induk yang konsisten dengan PRD (`docs/PRD.md`), SRS (`docs/SRS.md`), dan ADR (`docs/adr/`), sekaligus menjadi dasar untuk As-Built (`docs/AS-BUILT.md`).

SDD ini bukan dokumen perilaku eksternal (itu di SRS) dan bukan dokumen instalasi (itu di `docs/INSTALL.md`). SDD berfokus pada *bagaimana sistem dibangun di dalam*.

### 1.2 Lingkup dan Pemangku Kepentingan

Lingkup teknis yang dibahas:

- Backend Flask di folder `api/` (`api/app.py:27`, `api/routes/`, `api/auth.py`, `api/storage.py`, `api/helpers.py`, `api/middleware.py`, `api/bootstrap.py`, `api/config.py`).
- Lapisan integrasi `integrasi/` yang mengorkestrasi modul anggota1..5 untuk desktop CLI (`integrasi/adapter.py:1-89`, `integrasi/app_terpadu.py:1-116`).
- Modul anggota1..5 yang dipakai oleh `api/` secara *read-only*. Sebagai contoh `anggota4/safety_checker.py:14` mendefinisikan bobot keparahan; `api/` mengimpor namun tidak memodifikasi.
- Frontend Next.js 15+ di folder `src/` (`src/proxy.ts`, `src/app/api/[...slug]/route.ts`, halaman SSR di `src/app/**/page.tsx`, util di `src/lib/`).
- Infrastruktur cloud: Cloud Run (`medwatch-api` di region `asia-southeast1`), Vercel (`medwatch-frontend.vercel.app`), GCS bucket (`medwatch-polban-2026-state`), Secret Manager (`medwatch-jwt-secret`), serta openFDA REST API publik (`https://api.fda.gov`).

Pemangku kepentingan utama:

| Peran | Pemegang | Kepentingan utama |
|---|---|---|
| Project Leader / dev integrasi | Ghaisan Khoirul Badruzaman (251524048) | Konsistensi *cross-module*, ownership `api/` dan `integrasi/`, integrasi cloud. |
| Quality Assurance | Bimo Surya Anggara (251524040) | *Test case design* berdasarkan dekomposisi modul. |
| System Analyst | Alia Ardani (251524035) | *Traceability* dari SRS ke desain. |
| Programmer | Muhammad Iqbal (251524057) | Pemilik `anggota4/` (safety logic), dipanggil oleh `api/routes/safety_routes.py:26-30`. |
| UI/UX Designer | Abhidal Muhammad Gazza (251524032) | Pemilik `anggota5/` (PDF + auth lama). Auth dialihkan ke `api/auth.py` dengan satu kali pengecualian Phase 1. |
| Dosen pendamping | Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana | Penilaian kelengkapan dan ketepatan SDD. |

### 1.3 Referensi

1. IEEE 1016-2009 - IEEE Standard for Information Technology - Systems Design - Software Design Descriptions.
2. Brown, Simon. The C4 model for visualising software architecture. https://c4model.com. Diakses sebagai notasi *Context*, *Container*, *Component*, *Code/Deployment*.
3. PRD MedWatch (`docs/PRD.md`) - sumber kebutuhan dan persona.
4. SRS MedWatch (`docs/SRS.md`) - mengikuti IEEE 830-1998 / ISO/IEC/IEEE 29148:2018.
5. ADR (`docs/adr/0001-*.md` .. `docs/adr/000N-*.md`) - keputusan arsitektural per ADR.
6. As-Built (`docs/AS-BUILT.md`) - mengikuti ISO/IEC/IEEE 15289:2019.
7. Diagram sumber + render (`docs/diagrams/src/*.{mmd,puml}`, `docs/diagrams/png/*.png`).
8. Wave 1 findings: `.mission/findings/bugs/T1-ADMIN.md`, `T1-HEATMAP.md`, `T1-LOGIN.md`, `T1-PASIEN.md`, `T1-PDF.md`, `T1-SAFETY.md`, `T1-VERIFY.md` di repositori frontend.
9. Constitution misi: `~/Documents/FrontendMedWatch/.mission/plan.md`.

### 1.4 Definisi

| Istilah | Penjelasan |
|---|---|
| Faskes 1 | Fasilitas Kesehatan Tingkat Pertama (puskesmas, posyandu, klinik bidan). |
| SOAP | Kerangka pencatatan medis: Subjective, Objective, Assessment, Plan. Skema teks dijabarkan di Bagian 3.5. |
| Tenaga kesehatan | Role pengguna untuk bidan / perawat / tenaga medis lainnya. Nilai literal `tenaga_kesehatan` (CLAUDE.md aturan 4). |
| Masyarakat | Role pengguna umum (pasien). Nilai literal `masyarakat`. |
| Admin | Role pengelola sistem (Ghaisan). Nilai literal `admin`. |
| JWT | JSON Web Token. Diterbitkan oleh `api/auth.py:22-32`, diverifikasi oleh `api/auth.py:35-39`. |
| openFDA | REST API publik FDA (`https://api.fda.gov`) sebagai sumber data adverse event dan recall pasca pivot. |
| Vercel proxy pattern | Pola di mana browser hanya melihat domain Vercel, JWT disimpan di httpOnly cookie, dan Cloud Run URL tidak terekspos ke klien. Implementasi: `src/app/api/[...slug]/route.ts:1-108`. |
| B01..B11 | Bug register yang diperbaiki di Wave 1, lihat `.mission/bugs.md`. |
| C4 L1/L2/L3 | Level 1 (Context), Level 2 (Container), Level 3 (Component) pada model C4 oleh Brown. |

---

## 2. Pertimbangan Desain

### 2.1 Asumsi dan Ketergantungan

Asumsi:

1. Pengguna primer adalah bidan Faskes 1 yang familiar dengan alur pencatatan SOAP tetapi tidak selalu mengisi seluruh kolom (PRD; lihat juga CLAUDE.md "Bidan workflow reality"). Skema desain harus toleran terhadap *field* kosong (lihat `api/routes/patient_routes.py:82-88`).
2. Konteks bahasa user-facing adalah Bahasa Indonesia formal, dengan istilah teknis tetap dalam Inggris di kode dan dokumen rujukan. Locale `dd-MM-yyyy` dan Rupiah dipakai bila relevan.
3. Sumber data obat adalah `anggota4/data/drug_database.json` (Iqbal) dan `anggota4/data/effect_database.json` (Iqbal). Sumber data pasien default adalah `api/data/patients.json` (dibuat fresh oleh `api/`) atau `anggota2/Pasien.json` (Bimo) bila diakses lewat CLI desktop.
4. Klien browser terkini (Chrome/Firefox/Safari versi lalu lintas mayoritas) mendukung `fetch`, `httpOnly` cookies, dan ES2020+. Tidak ada *polyfill* khusus.

Ketergantungan eksternal:

- Python 3.11+ runtime (Cloud Run; lokal venv menggunakan 3.13). `api/requirements.txt` mengunci Flask 3.0+, flask-cors, PyJWT, bcrypt, google-cloud-storage, fpdf2.
- Node.js 22 LTS untuk Next.js 16 (catatan B-WAVE1-BUILD-1 di As-Built mengenai *blocker* dev-server Turbopack).
- openFDA REST API publik (`https://api.fda.gov/drug/event.json`, `https://api.fda.gov/drug/enforcement.json`), kunci API di env `OPENFDA_API_KEY` (dipakai `anggota1/openfda/fetch.py:21,69`).
- GCP project `medwatch-polban-2026` dengan layanan Cloud Run + Cloud Storage + Secret Manager.
- Vercel project untuk hosting frontend (default `.vercel.app` URL).

### 2.2 Batasan Desain

1. **Free tier wajib**. CLAUDE.md aturan 8 menetapkan tidak boleh ada layanan berbayar di luar GCP free trial Ghaisan. Konsekuensi: tidak boleh ada Auth0, SendGrid, Sentry berbayar, Cloudflare berbayar, atau Vercel Pro. Pilihan biner: pakai komponen gratis atau abstain.
2. **Modul anggota1..anggota5 *read-only*** (CLAUDE.md aturan 2). Setiap perbaikan integrasi diimplementasi sebagai *wrapper* di `api/` (contoh: `api/routes/safety_routes.py:30-41` membungkus `anggota4.safety_checker.cek_keamanan_obat`). Pengecualian Phase 1 untuk `anggota5/auth.py` dan `anggota5/main_anggota5.py` sudah ditutup dan tidak dibuka kembali oleh misi ini.
3. **Tanpa em dash dan tanpa emoji** di seluruh kode, komentar, dokumen, dan UI (mission constraint 4).
4. **Tidak ada nilai kredensial dalam dokumen**. Nama resource (project, bucket, service, secret name) diperbolehkan; *value* (kunci, password, JWT secret) tidak (mission constraint 12).
5. **Lokal vs cloud sebagai konfigurasi runtime**: implementasi tidak boleh memaksa salah satu jalur saja. `api/config.py:29` mendefinisikan `USE_CLOUD_STORAGE`; `api/storage.py:63-87` memilih *fallback* berdasarkan flag tersebut.
6. **Scope discipline**: hanya perubahan yang dibutuhkan oleh misi yang diizinkan (constraint 8). Tidak ada refactor spekulatif.
7. **Lokal CRUD tetap berjalan**: implementasi `integrasi/adapter.py:35-44` memanggil `anggota2/PasienCRUD.py` sebagai *subprocess* sehingga modus desktop CLI tidak terganggu pekerjaan integrasi web.

### 2.3 Tujuan dan Petunjuk Desain (*Design Goals & Guidelines*)

1. **Separation of concerns**: tiap modul anggota1..5 tetap menjadi unit *single-responsibility*; integrasi terjadi di lapisan tipis `api/` dan `integrasi/`. Frontend tidak memanggil modul anggota langsung, hanya lewat REST.
2. **Defense in depth untuk auth**: cookie httpOnly + middleware proxy Next.js (`src/proxy.ts:41-83`) + middleware Flask (`api/middleware.py:17-34`) + CORS allowlist (`api/config.py:21-25`). Tiga lapisan independen.
3. **Backend URL tidak pernah bocor ke klien**. Konsekuensi: variabel env `BACKEND_API_URL` di Vercel tidak diawali `NEXT_PUBLIC_`. Akses backend lewat `src/app/api/[...slug]/route.ts:11`.
4. **Skema kanonik tunggal**: ketika dua anggota memakai skema berbeda, dipilih satu sumber kebenaran. Tabel di Bagian 3.5 dan CLAUDE.md aturan 3.
5. **Toleransi *graceful*** terhadap modul yang gagal di-*load*. `api/bootstrap.py:26-39` mengembalikan `None` bila import gagal; pemanggil mengeksekusi *inline fallback* (contoh `api/routes/visualization_routes.py:38-51`).
6. **Resep input bidan adalah free-text** dan harus diparsing oleh logika di backend (`api/helpers.py:47-96`) dan cermin TS di frontend (`src/lib/patient-format.ts` `parseResepToMeds`). Bidan tidak dipaksa memilih dari dropdown.
7. **Tidak ada credential value yang ditulis** di kode, komentar, docs, atau commit. `OPENFDA_API_KEY` dibaca dari env, tidak pernah dicetak (`anggota1/openfda/fetch.py:21`).

---

## 3. Sudut Pandang Desain (IEEE 1016-2009 *Design Viewpoints*)

IEEE 1016-2009 mengatur agar desain dideskripsikan dari beberapa *viewpoint* yang melayani *concern* berbeda. Bagian ini menyajikan 11 *viewpoint* yang relevan untuk MedWatch. Untuk *viewpoint* arsitektural (3.1, 3.2, 3.3, 3.4), notasi C4 oleh Brown dipakai pada diagram pendamping (sumber `docs/diagrams/src/`, render `docs/diagrams/png/`).

### 3.1 Sudut Pandang Konteks (*Context Viewpoint*; C4 L1)

*Concern*: bagaimana sistem berinteraksi dengan dunia luar (aktor, sistem eksternal).

Diagram sumber: `docs/diagrams/src/c4-l1-context.mmd` (render `docs/diagrams/png/c4-l1-context.png`).

Aktor:

- **Tenaga kesehatan / bidan** (role `tenaga_kesehatan`): login lewat browser, mengakses CRUD pasien, safety checker, visualisasi, export PDF.
- **Masyarakat** (role `masyarakat`): login lewat browser, mengakses pencarian obat, safety checker terbatas, profile pasien.
- **Admin** (role `admin`, dipegang Ghaisan): mengakses dashboard admin, manajemen user, trigger scraping, dan semua kemampuan tenaga kesehatan.
- **Dosen / penguji**: persona observasional, mengakses URL publik Vercel untuk demo.

Sistem eksternal:

- **openFDA REST API** (`https://api.fda.gov/drug/event.json`, `https://api.fda.gov/drug/enforcement.json`). Diakses oleh `anggota1/openfda/fetch.py` dengan kunci di env. Acquisitions disimpan ke `anggota1/data/drug_safety_data.json` dan `drug_recalls.json` (dipakai oleh `api/routes/pdf_routes.py:80-91`).
- **Google Cloud Storage** (`medwatch-polban-2026-state` bucket): persistensi `users.json` dan `patients.json` saat `USE_CLOUD_STORAGE=true` (lihat `api/storage.py:45-60`).
- **Google Secret Manager** (`medwatch-jwt-secret`): JWT signing key di-mount sebagai env `JWT_SECRET` saat Cloud Run start (`api/config.py:17`).

Tidak ada integrasi telemetri pihak ketiga, tidak ada SaaS auth, tidak ada layanan berbayar (sesuai batasan 2.2.1).

### 3.2 Sudut Pandang Komposisi (*Composition Viewpoint*; C4 L2 Container)

*Concern*: bagaimana sistem dipecah menjadi *container* eksekusi yang dapat di-deploy independen.

Diagram sumber: `docs/diagrams/src/c4-l2-container.mmd`.

Container:

1. **Browser (Single Page App)**. Next.js 15 app dirender via Vercel Edge. Komponen utama: halaman SSR/RSC di `src/app/**/page.tsx`, *client store* Zustand di `src/lib/auth-store.ts:20-68`, util fetch di `src/lib/api.ts:16-38`. Tidak menyimpan JWT di localStorage; mengandalkan cookie httpOnly.
2. **Vercel Next.js runtime**. Hosting `medwatch-frontend.vercel.app`. Dua tanggung jawab kritis:
   - Server Rendering halaman.
   - **API proxy** di `src/app/api/[...slug]/route.ts:16-108` yang meneruskan request browser ke Cloud Run dan mengelola cookie sesi.
   - **Edge middleware proxy** di `src/proxy.ts:41-83` (file ini menggantikan `middleware.ts` lama; lihat T1-LOGIN dan T1-SAFETY catatan tentang deprecation Next 16) untuk redirect login dan *role gate*.
3. **Cloud Run Flask service (`medwatch-api`)**. Container Python berjalan di `asia-southeast1`. Entry point `api/app.py:27-63`. Blueprint terdaftar: `health`, `auth_routes`, `patient_routes`, `drug_routes`, `safety_routes`, `visualization_routes`, `pdf_routes`, `admin_routes` (`api/app.py:36-43`). Diserve oleh gunicorn (lihat `Dockerfile` dan `Procfile` di root backend).
4. **Google Cloud Storage bucket (`medwatch-polban-2026-state`)**. Penyimpanan persisten untuk `users.json` dan `patients.json` saat mode cloud aktif (`api/storage.py:45-60`).
5. **Google Secret Manager (`medwatch-jwt-secret`)**. Sumber kunci JWT yang dimount sebagai env Cloud Run.
6. **openFDA REST API**. Dependensi eksternal *read-only*, dipakai *offline* via `anggota1/openfda/fetch.py` (bukan oleh request waktu nyata).

Komunikasi antar-container:

- Browser <-> Vercel: HTTPS, same-origin (cookie httpOnly path `/`).
- Vercel proxy -> Cloud Run: HTTPS dengan header `Authorization: Bearer <JWT>` yang disuntik dari cookie (`src/app/api/[...slug]/route.ts:38-42`).
- Cloud Run -> GCS: SDK `google-cloud-storage` via *workload identity* default service account (`api/storage.py:22-27`).
- Cloud Run -> Secret Manager: env injection (Cloud Run --set-secrets, baca via `os.environ.get("JWT_SECRET", ...)` di `api/config.py:17`).
- Operator -> openFDA: HTTPS dengan `api_key` query param (`anggota1/openfda/fetch.py:21-23`), dijalankan saat akuisisi data, bukan saat request user.

### 3.3 Sudut Pandang Logis (*Logical Viewpoint*; C4 L3 Component untuk backend `api/`)

*Concern*: bagaimana container Flask dipecah menjadi komponen logis dan apa tanggung jawab masing-masing.

Diagram sumber: `docs/diagrams/src/c4-l3-component-backend.mmd`.

Komponen di dalam Cloud Run service `medwatch-api`:

| Komponen | File | Tanggung jawab utama |
|---|---|---|
| Application factory | `api/app.py:27-63` | Buat Flask app, daftarkan blueprint, pasang CORS (origin allowlist di `api/config.py:21-25`), pasang error handler 404/500 (`api/app.py:49-56`), strip `Server` header (`api/app.py:58-61`). |
| Configuration | `api/config.py:1-37` | Konstanta path, JWT, GCS, CORS. Membaca env: `JWT_SECRET`, `GCP_PROJECT_ID`, `GCS_BUCKET`, `USE_CLOUD_STORAGE`, `OPENFDA_API_KEY`, `PORT`, `FLASK_DEBUG`. |
| Auth primitives | `api/auth.py:11-39` | `hash_password` (bcrypt cost 12, `api/auth.py:12`), `verify_password` (`api/auth.py:15-19`), `issue_token` (HS256, `iss` = `medwatch-api`, exp 12 jam, `api/auth.py:22-32`), `verify_token` (`api/auth.py:35-39`). |
| Middleware decorators | `api/middleware.py:10-51` | `require_auth` baca `Authorization: Bearer` (`api/middleware.py:10-15`), populasi `g.user`; `require_role(*allowed)` memvalidasi role JWT terhadap allowlist (`api/middleware.py:37-51`). |
| Storage adapter | `api/storage.py:1-122` | `load_users` / `save_users` / `load_patients` / `save_patients`. Auto-fallback antara file lokal `api/data/*.json` dan GCS (`api/storage.py:63-87`). Hashing plaintext password pada *first read* (`api/storage.py:90-98,105-109`). |
| Helpers | `api/helpers.py:1-96` | `ok` / `err` response shaper, `strip_password_fields` (`api/helpers.py:16-18`), `parse_resep_to_meds` (`api/helpers.py:25-96`) untuk parser resep bidan. |
| Bootstrap loader | `api/bootstrap.py:1-39` | Inject path anggota1..5 ke `sys.path` (`api/bootstrap.py:18-23`), lazy import dengan *graceful fallback* `None` saat gagal (`api/bootstrap.py:26-39`). |
| Auth routes | `api/routes/auth_routes.py:13-51` | `POST /api/auth/login` (`auth_routes.py:13`), `GET /api/auth/me` (`auth_routes.py:43`), `POST /api/auth/logout` (`auth_routes.py:49`). |
| Patient routes | `api/routes/patient_routes.py:135-218` | CRUD pasien dengan validasi B03 dan sort B07 (`patient_routes.py:135-146`, `162-188`, `190-205`, `208-217`). |
| Drug routes | `api/routes/drug_routes.py:19-51` | `GET /api/drugs` katalog (`drug_routes.py:19-28`), `GET /api/drugs/search` pencarian (`drug_routes.py:31-40`), `GET /api/drugs/<nama_obat>` profil (`drug_routes.py:43-51`). |
| Safety routes | `api/routes/safety_routes.py:16-72` | `POST /api/safety/check` dengan pasien aktif meds (B05) dan pelabelan severity (B08). |
| Visualization routes | `api/routes/visualization_routes.py:54-138` | Empat endpoint: kunjungan-trend, keluhan-distribution, top-efek-samping, heatmap-efek. |
| PDF routes | `api/routes/pdf_routes.py:169-511` | Rekam medis per pasien, laporan bulanan, efek samping (B04), inventaris obat. Delegasi sebagian ke `anggota5/export_pdf.py` lewat `_to_anggota5_format` (`pdf_routes.py:135-166`). |
| Admin routes | `api/routes/admin_routes.py:21-127` | Trigger scrape (mock; B01), CRUD user, system-stats real (B10). |
| Health routes | `api/routes/health.py:12-37` | `GET /api/health`, `GET /api/info`. |

Diagram L3 menggambarkan dependensi *inbound* dari `app.py` ke setiap blueprint dan *outbound* dari blueprint ke komponen inti (`middleware`, `storage`, `auth`, `bootstrap`, `helpers`).

### 3.4 Sudut Pandang Dependensi (*Dependency Viewpoint*)

*Concern*: graf dependensi internal lintas folder untuk memastikan tidak ada *cyclic import* dan modul *read-only* tidak diubah.

Aturan: `api/` mengimpor `anggota1..5` (read-only). `integrasi/adapter.py` mengimpor anggota1..5 (read-only). Frontend tidak mengimpor `api/` Python apa pun; komunikasi via HTTP.

Dependensi konkret (cite file):

- `api/app.py:14-17` impor `api.config`, blueprint routes.
- `api/routes/safety_routes.py:6-9` impor `api.middleware`, `api.bootstrap`, `api.storage`, `api.helpers` -> kemudian `bootstrap.get_module("anggota4", "safety_checker")` -> import dinamis `anggota4/safety_checker.py:1-12`.
- `api/routes/drug_routes.py:11-16` mengikuti pola yang sama untuk `anggota4.data_loader` dan `anggota4.pencarian_obat`.
- `api/routes/pdf_routes.py:182, 218` mengimpor `anggota5.export_pdf` lewat `bootstrap.get_module`. `anggota5/export_pdf.py` adalah *read-only* milik Abhidal.
- `api/routes/visualization_routes.py:11-13` mengimpor `api.bootstrap`, `api.storage`, `api.helpers`. Catatan: `anggota3/BacaData.py` memiliki SyntaxError tercatat di `api/routes/visualization_routes.py:3-5`; pemulihan terjadi via implementasi *inline equivalent* di sini sehingga `anggota3` tetap *read-only*.
- `integrasi/adapter.py:10-16` memetakan path anggota1..5; `integrasi/app_terpadu.py:18-29` mengimpor `anggota5/auth.py` untuk *desktop CLI login* dan `integrasi/adapter.py` untuk *subprocess dispatch*.
- Frontend: `src/app/api/[...slug]/route.ts:11` membaca `BACKEND_API_URL` (server-only env). `src/proxy.ts:1-89` tidak mengimpor `BACKEND_API_URL`; ia hanya membaca cookie dan melakukan *role gating*. `src/lib/api.ts:16-38` hanya memakai `fetch()` ke path relatif `/api/...` sehingga browser tidak pernah melihat URL backend.

Tidak ada *cyclic import*: `api/config.py` dan `api/auth.py` hanya bergantung pada *standard library* dan dependensi pihak ketiga; modul `api/routes/*` bergantung pada `api/middleware`, `api/storage`, `api/helpers`, `api/bootstrap`, dan modul anggota; tidak ada arah balik.

### 3.5 Sudut Pandang Informasi (*Information Viewpoint*; data model)

*Concern*: struktur entitas data utama dan sumber kebenaran skema.

Sumber kebenaran skema diatur eksplisit di **CLAUDE.md aturan 3**. Ringkasan dengan sitiran:

**Entitas Pasien (kanonik dari Bimo, `anggota2/pasien_helper.py`)**. ID berformat `P001`, `P002`, ... (huruf P + 3 digit). Generator: `api/routes/patient_routes.py:102-112` memanggil `anggota2.pasien_helper.generate_id` bila tersedia; fallback inline. Skema:

```text
{
  "id": "P001",
  "tanggal_kunjungan": "DD-MM-YYYY",
  "nama": "string",
  "umur": "string",
  "alamat": "string",
  "kategori": "Ibu Hamil | KB | Anak | Imunisasi | Umum",
  "S": { "keluhan": "string", "riwayat": "string" },
  "O": {
    "tekanan_darah": "sistolik/diastolik",
    "nadi": "number-string",
    "suhu_c": "number-string",
    "respirasi": "number-string",
    "bb_kg": "number-string",
    "tb_cm": "number-string",
    "lila_cm": "number-string",
    "catatan": "string"
  },
  "A": { "diagnosa": "string" },
  "P": { "tindakan": "multi-line string", "resep": "free-text", "jadwal_kontrol": "string" },
  "created_by": "username",
  "owner_username": "username (opsional, untuk role masyarakat)"
}
```

Validasi numerik diatur di `api/routes/patient_routes.py:17-99` (rentang `NUMERIC_RANGES`, `SYSTOLIC_RANGE`, `DIASTOLIC_RANGE`, `TD_PATTERN`). Pesan error berbahasa Indonesia. Cermin client-side: `src/lib/patient-validation.ts:22-92`.

**Entitas Drug (kanonik dari Iqbal, `anggota4/data/drug_database.json`)**. Skema:

```text
{
  "nama_obat": "string",
  "alias": ["string"],
  "kategori": "string",
  "bahan_aktif": ["string"],
  "indikasi": ["string"],
  "dosis_umum": "string",
  "kehamilan": "string",
  "peringatan": ["string"],
  "kontraindikasi": ["string"],
  "interaksi": ["string"],
  "efek_samping": ["string"]
}
```

Dibaca *read-only* lewat `anggota4/data_loader.py:33-35` (`muat_database_obat`). Diakses oleh `api/routes/drug_routes.py:20-28` dan `api/routes/pdf_routes.py:94-105`.

**Entitas Side Effect (kanonik dari Iqbal, `anggota4/data/effect_database.json`)**. Skema:

```text
{
  "nama_efek": "string",
  "kategori": "string",
  "tingkat_keparahan": "ringan | sedang | serius",
  "rekomendasi": "string"
}
```

Bobot skoring numerik diset di `anggota4/safety_checker.py:14`: `BOBOT_KEPARAHAN = {"ringan": 1, "sedang": 2, "serius": 4}`. Indeks pencarian dibangun di `anggota4/data_loader.py:43-52`.

**Entitas User (lapisan `api/data/users.json`, dikelola oleh `api/storage.py`)**. Skema:

```text
{
  "username": "string",
  "password_hash": "bcrypt $2b$12$...",
  "role": "tenaga_kesehatan | masyarakat | admin",
  "name": "string",
  "phone": "string"
}
```

Hashing dilakukan di `api/storage.py:90-98` saat *first read* bila file seed berisi `password_plain`. Field `password_hash` tidak pernah dikembalikan ke klien karena `helpers.strip_password_fields` (`api/helpers.py:16-18`) dipakai pada semua endpoint admin (`api/routes/admin_routes.py:44-45`).

**Entitas Adverse Event / Recall (sumber openFDA, schema kompatibel mundur)**. `anggota1/data/drug_safety_data.json` berisi list of `{drug_name, severity_level, side_effects}` (lihat `api/routes/pdf_routes.py:271-281`). `anggota1/data/drug_recalls.json` berisi catatan FDA enforcement; akuisisi di `anggota1/openfda/fetch.py:55-99`.

**Data Dictionary lengkap** diatur terpisah di `docs/DATA-DICTIONARY.md`. SDD ini hanya mereferensikan untuk *single source of truth*.

### 3.6 Sudut Pandang Interface (*Interface Viewpoint*)

*Concern*: kontrak interaksi antar komponen yang diumumkan ke luar.

**REST API backend** terdaftar di `api/app.py:36-43`. Endpoint utama (verifikasi langsung ke routes):

| Path | Method | Auth | Route file:line |
|---|---|---|---|
| `/api/health` | GET | none | `routes/health.py:13-18` |
| `/api/info` | GET | none | `routes/health.py:22-36` |
| `/api/auth/login` | POST | none | `routes/auth_routes.py:13-40` |
| `/api/auth/me` | GET | bearer | `routes/auth_routes.py:43-46` |
| `/api/auth/logout` | POST | none | `routes/auth_routes.py:49-51` |
| `/api/patients` | GET | tenaga_kesehatan, admin | `routes/patient_routes.py:135-146` |
| `/api/patients/<pid>` | GET | bearer + ownership | `routes/patient_routes.py:149-159` |
| `/api/patients` | POST | tenaga_kesehatan, admin | `routes/patient_routes.py:162-187` |
| `/api/patients/<pid>` | PUT | tenaga_kesehatan, admin | `routes/patient_routes.py:190-205` |
| `/api/patients/<pid>` | DELETE | admin | `routes/patient_routes.py:208-217` |
| `/api/drugs` | GET | none | `routes/drug_routes.py:19-28` |
| `/api/drugs/search?q=` | GET | none | `routes/drug_routes.py:31-40` |
| `/api/drugs/<nama_obat>` | GET | none | `routes/drug_routes.py:43-51` |
| `/api/safety/check` | POST | bearer | `routes/safety_routes.py:16-72` |
| `/api/visualizations/kunjungan-trend` | GET | tenaga_kesehatan, admin | `routes/visualization_routes.py:54-66` |
| `/api/visualizations/keluhan-distribution` | GET | tenaga_kesehatan, admin | `routes/visualization_routes.py:69-80` |
| `/api/visualizations/top-efek-samping` | GET | bearer | `routes/visualization_routes.py:83-110` |
| `/api/visualizations/heatmap-efek` | GET | bearer | `routes/visualization_routes.py:113-138` |
| `/api/pdf/generate-rekam-medis` | POST | tenaga_kesehatan, admin | `routes/pdf_routes.py:169-202` |
| `/api/pdf/generate-laporan-bulanan` | POST | admin | `routes/pdf_routes.py:205-238` |
| `/api/pdf/generate-efek-samping` | POST | tenaga_kesehatan, admin | `routes/pdf_routes.py:241-385` |
| `/api/pdf/generate-inventaris` | POST | tenaga_kesehatan, admin | `routes/pdf_routes.py:388-511` |
| `/api/admin/scrape` | POST | admin | `routes/admin_routes.py:21-38` |
| `/api/admin/users` | GET | admin | `routes/admin_routes.py:41-45` |
| `/api/admin/users` | POST | admin | `routes/admin_routes.py:48-85` |
| `/api/admin/users/<username>` | DELETE | admin | `routes/admin_routes.py:88-103` |
| `/api/admin/system-stats` | GET | admin | `routes/admin_routes.py:106-127` |

Bentuk *envelope*: success body adalah JSON apa adanya (atau `{"status":"ok"}`) lewat `helpers.ok`. Error body `{"error":"...","fields"?:[...]}` lewat `helpers.err`. Pelanggaran auth selalu 401; pelanggaran role selalu 403; validasi gagal 400 dengan pesan Bahasa Indonesia (contoh `patient_routes.py:177-178`).

**Next.js API proxy** (`src/app/api/[...slug]/route.ts:1-108`): pola *catch-all* yang mem-forward semua `/api/...` ke `${BACKEND}/api/...`, menyuntik header `Authorization: Bearer <token>` dari cookie `medwatch_token` (`route.ts:38-42`), dan menulis kembali cookie pada login sukses (`route.ts:68-93`) atau menghapus pada logout (`route.ts:95-103`).

**Next.js edge middleware** (`src/proxy.ts:41-83`): mengatur redirect ke `/login` bila tidak ada cookie, redirect role-aware ke landing (`/admin/dashboard` untuk admin, `/drug-search` untuk masyarakat, `/dashboard` default), dan *role gate* untuk path `/admin` (`src/proxy.ts:65-67`) serta whitelist path untuk masyarakat (`src/proxy.ts:69-80`). Catatan rename `middleware.ts` -> `proxy.ts` adalah keputusan Wave 1 untuk menghindari *deprecation warning* Next 16 (lihat T1-SAFETY follow-ups).

### 3.7 Sudut Pandang Struktural (*Structural Viewpoint*)

*Concern*: tata letak folder dan tanggung jawab folder.

Repositori backend (`/Users/ghaisan/Documents/MedWatchIntegration/medWatch/`):

```text
medWatch/
  anggota1/                # Scraping + openFDA fetcher (Ghaisan). READ-ONLY untuk api/
    anggota1.py
    openfda/
      fetch.py             # Akuisisi openFDA
    data/
      drug_safety_data.json
      drug_recalls.json
  anggota2/                # CRUD pasien SOAP (Bimo). READ-ONLY.
    PasienCRUD.py
    pasien_helper.py
  anggota3/                # Visualisasi matplotlib (Alia). READ-ONLY.
    NewestVisualization/   # Additive module (Wave 1)
    grafik_*.py
    TampilGrafik.py
  anggota4/                # Drug safety check (Iqbal). READ-ONLY.
    data_loader.py
    pencarian_obat.py
    safety_checker.py
    data/
      drug_database.json
      effect_database.json
  anggota5/                # PDF + auth desktop (Abhidal). READ-ONLY post-Phase 1.
    auth.py
    export_pdf.py
    main_anggota5.py
    tkesehatan_crud.py
  api/                     # Backend Flask, owned by Ghaisan
    app.py
    auth.py
    bootstrap.py
    config.py
    helpers.py
    middleware.py
    storage.py
    data/
      users.json
      patients.json
    routes/
      auth_routes.py
      patient_routes.py
      drug_routes.py
      safety_routes.py
      visualization_routes.py
      pdf_routes.py
      admin_routes.py
      health.py
    tests/
      smoke_test.py
    static/                # Optional landing page assets
    Dockerfile
    README.md
    requirements.txt
  integrasi/               # Desktop CLI orchestrator, owned by Ghaisan
    adapter.py
    app_terpadu.py
  docs/                    # Documentation set (Wave 2 output)
    PRD.md, SRS.md, SDD.md (this file), AS-BUILT.md
    DATA-DICTIONARY.md, API.md, INSTALL.md, SECURITY.md, USER-MANUAL.md
    adr/0001-*.md ...
    diagrams/src/*.{mmd,puml}
    diagrams/png/*.png
  ProductionGrade-ImplementationPlan/   # Forward-looking plan
  Dockerfile, Procfile
  main.py
  README.md
  CLAUDE.md
```

Repositori frontend (`/Users/ghaisan/Documents/FrontendMedWatch/`):

```text
FrontendMedWatch/
  src/
    app/
      api/[...slug]/route.ts   # Catch-all backend proxy
      login/page.tsx
      dashboard/page.tsx
      admin/dashboard/page.tsx
      admin/scraper/page.tsx
      admin/users/page.tsx
      patients/page.tsx, [id]/page.tsx, new/page.tsx
      drug-search/page.tsx
      drug-comparison/page.tsx
      safety-checker/page.tsx
      visualization/page.tsx
      heatmap/page.tsx
      export-pdf/page.tsx, export/page.tsx
      pasien/profile/page.tsx
      layout.tsx, page.tsx, globals.css
    components/
    lib/
      api.ts                   # fetch wrapper
      auth-store.ts            # Zustand store
      patient-format.ts        # SOAP helpers + parseResepToMeds
      patient-validation.ts    # Numeric range validator (mirror backend)
      heatmap-colors.ts        # 5-stop risk-matrix color scale
      pdf-generator.ts
      safety-checker.ts
      drug-format.ts, nav.ts, store.ts, utils.ts
    hooks/
    proxy.ts                   # Edge middleware (was middleware.ts)
    data/
  package.json, next.config.ts, tsconfig.json
  docs/                        # Frontend-specific docs (Wave 2 output)
```

Dasar pemilihan tata letak ini:

- **Folder anggota1..5 dipertahankan** karena merupakan submission desktop CustomTkinter milik tiap anggota; integrasi web tidak boleh menghapus jejak kepemilikan.
- **`api/` adalah lapisan tipis** yang hanya berisi orkestrasi web. Logic *domain* (safety check, PDF render anggota5, scraping anggota1) tetap di folder anggota.
- **Frontend `src/lib/`** memisahkan logika pure dari komponen UI; util seperti `heatmap-colors.ts` dapat diuji tanpa render.

### 3.8 Sudut Pandang Interaksi (*Interaction Viewpoint*; sequence flows)

*Concern*: urutan pesan antar komponen untuk flow utama.

Diagram sumber tiap sequence: `docs/diagrams/src/seq-*.mmd`.

#### 3.8.1 Login JWT

1. User memasukkan `username`, `password` di `src/app/login/page.tsx`. `useAuthStore.login` (`src/lib/auth-store.ts:25-44`) memanggil `POST /api/auth/login`.
2. Next.js proxy (`src/app/api/[...slug]/route.ts:16-67`) menerima request, meneruskan ke `${BACKEND}/api/auth/login` (tidak ada cookie yang dilampirkan saat itu karena path adalah login).
3. Flask di `api/routes/auth_routes.py:13-40` memuat user via `storage.load_users()` (`storage.py:101-109`), membandingkan password dengan `auth.verify_password` (`auth.py:15-19`), menerbitkan JWT via `auth.issue_token` (`auth.py:22-32`).
4. Response 200 berisi `{"token","user"}`. Proxy meng-set cookie `medwatch_token` httpOnly Secure SameSite=Lax max-age 12 jam (`route.ts:76-93`).
5. Browser kembali ke `landingForRole(role)` (`auth-store.ts:70-74` dan `src/proxy.ts:35-39`).

#### 3.8.2 CRUD Pasien SOAP

Create (`POST /api/patients`):
1. Halaman `src/app/patients/new/page.tsx` memanggil `api.post('/api/patients', body)` (`src/lib/api.ts:42`). Form telah divalidasi client-side dengan `validateObjective` (`src/lib/patient-validation.ts:74-93`).
2. Proxy meneruskan dengan cookie token.
3. `api/routes/patient_routes.py:162-187` mengecek `nama`, `S.keluhan`, `A.diagnosa`, `P.tindakan` ada, lalu jalankan `_validate_medical_ranges` (`patient_routes.py:56-99`). Bila lolos, generator ID berbasis Bimo dipakai (`_generate_id`, `patient_routes.py:102-112`), data disimpan via `storage.save_patients`. Response 201.

Read list (`GET /api/patients`):
1. Halaman `src/app/patients/page.tsx` memuat list.
2. Backend sort newest-first dengan `_parse_visit_date` (DD-MM-YYYY desc) dan tiebreak `_id_num` desc (`patient_routes.py:30-53,141-145`). Implementasi memperbaiki B07.

Read one / Update / Delete: lihat `patient_routes.py:149-217`. Update menggunakan `_deep_merge` (`patient_routes.py:125-132`) sehingga partial PATCH-style body dapat memodifikasi sub-tree S/O/A/P tanpa menghapus field lain.

#### 3.8.3 Cek Interaksi Obat dengan Active Meds (B05)

1. Halaman `src/app/safety-checker/page.tsx` memilih pasien P00X. UI memanggil `GET /api/patients/P00X` untuk dapat full SOAP (`patient_routes.py:149-159`).
2. Halaman menjalankan `parseResepToMeds(full.P.resep)` (TypeScript mirror dari backend) dan menampilkan *chip list* "Obat aktif pasien" (lihat T1-SAFETY).
3. User menambah obat manual atau membiarkan auto-populate, kemudian klik "Cek Interaksi". `POST /api/safety/check` dengan `{drugs:[...], pasien_id:"P00X"}`.
4. Backend `api/routes/safety_routes.py:16-72` memanggil `anggota4.safety_checker.cek_keamanan_obat(drugs)` (`safety_checker.py:166-203`).
5. Bila `pasien_id` ada, backend memuat full patient, mem-parse `P.resep` via `helpers.parse_resep_to_meds` (`api/helpers.py:47-96`) dan menambahkan `pasien_active_meds` ke response (`safety_routes.py:45-61`).
6. Aggregator label: `safety_routes.py:33-41` mengambil `max(skor_risiko)` lintas obat dan label tertinggi via `_LABEL_ORDER`. Mapping ke label Inggris (`low/medium/high`) di `safety_routes.py:12-13`.
7. UI menampilkan VERDIKT + panel penjelasan B08 (collapsible help panel) yang menyebut bobot 1/2/4 dan ambang 40/70 yang dirujuk dari `anggota4/safety_checker.py:14,36-40`.

#### 3.8.4 Scraping Pipeline openFDA Pivot

1. Operator (Ghaisan, role admin) mengeksekusi akuisisi *offline*:
   `OPENFDA_API_KEY=<value> .venv/bin/python -m anggota1.openfda.fetch` (`anggota1/openfda/fetch.py:1-31`).
2. Script membaca daftar obat default (`fetch.py:69-105`, daftar > 50 obat) atau file kustom via `--drugs FILE`.
3. Untuk tiap obat, GET `https://api.fda.gov/drug/event.json` dengan `api_key`, polite delay 250ms (`fetch.py:59-61`), retry exponential backoff max 5 (`fetch.py:62-63`).
4. Untuk recall: paginate `https://api.fda.gov/drug/enforcement.json` dengan page size 1000 (`fetch.py:60`).
5. Hasil ditulis ke `anggota1/data/drug_safety_data.json` dan `drug_recalls.json` (`fetch.py:29-30`).
6. Saat user web menekan tombol scraper di admin dashboard, `POST /api/admin/scrape` (`admin_routes.py:21-38`) hanya menjalankan *mock* (sleep 3 detik + baca jumlah obat saat ini) untuk memberi sinyal demo; akuisisi nyata tetap *offline*. Implementasi ini mencegah Cloud Run timeout dan biaya egress.

#### 3.8.5 PDF Generation

Rekam medis per pasien (`POST /api/pdf/generate-rekam-medis`):
1. UI memanggil `downloadBlob('/api/pdf/generate-rekam-medis', {pasien_id})` (`src/lib/api.ts:47-66`).
2. Backend `pdf_routes.py:169-202` memuat pasien, men-translate ke format nested anggota5 lewat `_to_anggota5_format` (`pdf_routes.py:135-166`), memanggil `anggota5.export_pdf.buat_laporan_pdf` ke file sementara, lalu mengirim file sebagai response `application/pdf`.

Efek samping aggregate (`POST /api/pdf/generate-efek-samping`, B04):
1. Backend `pdf_routes.py:241-385` memuat `anggota1/data/drug_safety_data.json` (read-only), menghitung frekuensi efek tertimbang oleh resep pasien (`pdf_routes.py:262-282`), dan menggambar PDF dengan fpdf2 langsung di proses (bukan delegasi anggota5) untuk menjaga *out-of-scope* anggota5.

#### 3.8.6 Heatmap Visualisasi (B11)

1. Halaman `src/app/heatmap/page.tsx` (lihat T1-HEATMAP) memanggil paralel `GET /api/visualizations/heatmap-efek` dan `GET /api/visualizations/top-efek-samping`.
2. Endpoint `visualization_routes.py:113-138` mengembalikan binary `0/1` matrix; endpoint `:83-110` mengembalikan list efek dengan `tingkat_keparahan`.
3. Klien bobotkan presence dengan severity (ringan=1, sedang=2, serius=4), urutkan baris/kolom *descending* by total, lalu warnai dengan `buildColorScale(min, max)` (`src/lib/heatmap-colors.ts:33-40`) menggunakan piecewise interpolator dari ramp 5-stop (`heatmap-colors.ts:18-24`).
4. Pemilihan warna teks kontras per sel via `getContrastingTextColor` (`heatmap-colors.ts:92-94`) berdasarkan WCAG relative luminance dengan threshold 0.55.

### 3.9 Sudut Pandang State Dinamis (*Dynamic State Viewpoint*)

*Concern*: status berubah di mana, dengan rentang hidup berapa lama.

State client-side (browser, in-memory):

- `useAuthStore` (`src/lib/auth-store.ts:20-68`): user, isLoading, hydrated. Hilang saat tab ditutup; di-rehydrate via `fetchMe()` saat *first mount*.
- State halaman lokal (React `useState`) per page; tidak ada Redux global tambahan.

State server-side (cookie httpOnly):

- Cookie `medwatch_token` (set di `route.ts:82-87`): nilai = JWT, expire 12 jam (`COOKIE_MAX_AGE` di `route.ts:14`), httpOnly, Secure di production, SameSite=Lax, path `/`. Dihapus di logout (`route.ts:95-103`).

State backend (in-memory dan persisten):

- `_LAST_SCRAPE` (`api/routes/admin_routes.py:15`): dict efemeral yang menyimpan hasil scrape mock terakhir per *process*. Hilang saat container Cloud Run restart.
- `_PROCESS_STARTED_AT` (`admin_routes.py:18`): timestamp UTC saat module di-import. Dipakai untuk *uptime KPI* di `/api/admin/system-stats` (`admin_routes.py:113-114`). Memperbaiki B10.
- `_loaded` cache modul anggota di `api/bootstrap.py:15`: simpan referensi modul agar import dinamis tidak diulang.
- Data persisten: `api/data/users.json`, `api/data/patients.json` (lokal) atau objek `users.json`, `patients.json` di bucket GCS `medwatch-polban-2026-state`. Dipilih runtime oleh `USE_CLOUD_STORAGE` (`storage.py:63-87`).

Visit Lifecycle: setiap entri pasien diasumsikan *single-visit* sesuai skema kanonik. Tidak ada array `visits[]`. Status transisi sederhana:

1. *Draft* (form di UI, belum POST). 
2. *Created* (POST `/api/patients` 201; ada `id`).
3. *Edited* (PUT `/api/patients/<pid>`; field termutakhir).
4. *Deleted* (DELETE; hanya admin).

State machine penuh terdokumentasi di `docs/diagrams/src/sm-visit-lifecycle.mmd`.

### 3.10 Sudut Pandang Algoritma (*Algorithmic Viewpoint*)

*Concern*: algoritma kunci yang melekat pada keputusan rancangan.

**Parser resep bidan** (`api/helpers.py:25-96`):

- Split free-text pada newline, semicolon, dan koma (`helpers.py:71`).
- Buang dosage hint dengan regex `_DOSAGE_HINT_RE` (`helpers.py:25-38`) menutup pola `\d+x\d+`, dosis dengan satuan (`mg, mcg, ml, g, tablet, ...`), frekuensi Indonesia (`sehari, per hari, kali, x`), dan tanda kurung.
- Buang Latin frequency token `_TRAILING_NOTE_RE` (`helpers.py:41-44`): `prn, qd, bid, tid, qid`, plus frasa Indonesia "jika perlu", "bila perlu".
- Collapse whitespace, strip leading/trailing punctuation `". ; : -"`.
- Dedupe case-insensitive sambil pertahankan casing pertama (`helpers.py:90-94`).

Cermin TS di `src/lib/patient-format.ts` `parseResepToMeds` (lihat T1-SAFETY) mengikuti aturan yang sama.

**Severity weighting** (`anggota4/safety_checker.py:14`): bobot `ringan=1, sedang=2, serius=4`. Skor risiko per obat dihitung di `safety_checker.py:18-31` dengan formula `total_bobot / (jumlah_efek * 4) * 100` dan dibulatkan 1 desimal. Label dari ambang 40/70 (`safety_checker.py:36-40`). Backend `api/routes/safety_routes.py:33-41` melakukan agregasi *max-of-labels* lintas obat untuk verdikt headline.

**Patient list sort** (`api/routes/patient_routes.py:30-53,141-145`): kunci primer `_parse_visit_date(tanggal_kunjungan)` yang mem-parse `DD-MM-YYYY` menjadi tuple `(year, month, day)` (entri tak valid -> `(0,0,0)` sehingga jatuh ke bawah saat *reverse=True*). Tiebreak `_id_num(id)` mengembalikan tail numerik dari `P001` -> `1`. Sort `reverse=True` -> *newest first, larger id first on tie*. Perbaikan B07.

**Heatmap luminance contrast** (`src/lib/heatmap-colors.ts:73-94`):

- `relativeLuminance(color)` menghitung WCAG relative luminance dari sRGB hex/rgb input via `parseRgb` (`heatmap-colors.ts:46-67`).
- Per komponen: `c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4)`.
- Bobot luminance `0.2126 R + 0.7152 G + 0.0722 B`.
- Threshold 0.55 (sedikit di atas midpoint matematika 0.5) untuk pilih warna teks `#1A1815` atau `#FFFFFF`. Threshold dipilih agar teks pada amber/pale-yellow tetap hitam.

**Color scale piecewise** (`src/lib/heatmap-colors.ts:18-40`): 5-stop ramp green->light green->pale yellow->orange->red. Domain `[min, max]` *clamped*; bila `min==max`, fallback ke stop 0. Interpolasi `piecewise(interpolateRgb, RISK_RAMP)`.

**Validasi medis** (`api/routes/patient_routes.py:56-99`):

- TD format regex `^\s*(\d{1,3})\s*/\s*(\d{1,3})\s*$` (`patient_routes.py:27`).
- Rentang sistolik [60, 250], diastolik [30, 160] (`patient_routes.py:25-26`).
- Field skalar dengan rentang `NUMERIC_RANGES` (`patient_routes.py:17-24`): bb_kg 1..300, tb_cm 30..300, lila_cm 8..60, nadi 30..220, suhu_c 30..44, respirasi 5..80.
- Pesan error berbahasa Indonesia, semua angka ditampilkan via format `:g` agar `1.0` ditulis `1`.

Cermin client-side `src/lib/patient-validation.ts:22-92` mempertahankan rentang identik untuk konsistensi.

**ID generator pasien** (`api/routes/patient_routes.py:102-112`): pakai `anggota2.pasien_helper.generate_id` bila modul ter-load; jika tidak, fallback inline: ambil tail numerik valid, tambah 1, pad ke 3 digit dengan prefix `P`.

**PDF schema translator** `_to_anggota5_format` (`api/routes/pdf_routes.py:135-166`): mengubah skema kanonik Bimo (flat SOAP) menjadi skema nested Abhidal (`identitas`, `anamnesis`, `pemeriksaan`, `diagnosis_tindakan`). Ini menjaga `anggota5/export_pdf.py` *read-only* sambil tetap memakainya untuk rendering.

### 3.11 Sudut Pandang Sumber Daya (*Resource Viewpoint*)

*Concern*: kuota dan batas sumber daya yang membatasi desain.

| Sumber daya | Batas | Mitigasi desain |
|---|---|---|
| Vercel Hobby plan | 100 GB-h bandwidth / bulan, 100 deploy / hari, fungsi serverless 10s timeout. | Halaman SSR ringan, proxy hanya forward; tidak ada *heavy work* di Vercel. |
| Cloud Run free trial | $300 USD kredit, 2 vCPU per request, 256 MB memori container. | gunicorn 1 worker; scraping nyata *offline*; `_LAST_SCRAPE` mock untuk dashboard. |
| GCS bucket | `medwatch-polban-2026-state`; 5 GB Always Free. | Hanya `users.json` dan `patients.json` (KB-an). Tidak menyimpan PDF generated; PDF dihasilkan tempfile dan dikirim. |
| Secret Manager | 6 versi aktif gratis per secret. | Satu secret `medwatch-jwt-secret` saja. |
| openFDA API | 240 request/menit, 1000/hari tanpa key; 240/menit, 120000/hari dengan key. | Polite delay 250ms (`anggota1/openfda/fetch.py:59`), retry exponential 5x (`fetch.py:62`), pakai env `OPENFDA_API_KEY` (`fetch.py:21`). |
| RAM Cloud Run | 256 MB default. | PDF besar dipotong (top 25 efek, top 25 obat per laporan). |
| Browser memory | Variabel; mobile 4 GB+. | Heatmap grid <= 6x17 saat ini; sort dilakukan sekali dengan `useMemo`. |
| openFDA daily quota | 120k/day dengan key. | Akuisisi *batch offline* sebulan sekali; backend tidak query waktu nyata. |

---

## 4. Rancangan Detail (*Detailed Design*)

Bagian ini memberikan *pseudocode* atau ekuivalennya untuk algoritma kritis. Semua rujukan ke kode sumber asli yang berlaku.

### 4.1 Login (`POST /api/auth/login`)

Acuan: `api/routes/auth_routes.py:13-40`.

```text
function login(request):
    data := JSON body or {}
    username := strip(data.username)
    password := data.password
    if username empty or password empty:
        return 401 "invalid credentials"
    users := storage.load_users()
    for u in users:
        if u.username == username:
            if auth.verify_password(password, u.password_hash):
                token := auth.issue_token(username, role, name)
                log "login ok"
                return 200 {token, user:{username, role, name}}
            log "login bad password"
            return 401 "invalid credentials"
    log "login user not found"
    return 401 "invalid credentials"
```

`auth.verify_password` (file `api/auth.py:15-19`) memanggil `bcrypt.checkpw` yang menggunakan *constant-time comparison*. Tidak ada early return berdasarkan keberadaan user vs password.

### 4.2 `_validate_medical_ranges` (Patient POST/PUT)

Acuan: `api/routes/patient_routes.py:56-99`.

```text
function _validate_medical_ranges(body) -> list[str]:
    errors := []
    O := body.O if dict else error "Field O harus berupa objek." -> return
    td := strip(O.tekanan_darah)
    if td not empty:
        m := match TD_PATTERN, td
        if no match:
            errors += "Tekanan darah harus dalam format sistolik/diastolik..."
        else:
            sys, dia := float(m[1]), float(m[2])
            if sys out of SYSTOLIC_RANGE: errors += "Tekanan darah sistolik harus antara ..."
            if dia out of DIASTOLIC_RANGE: errors += "Tekanan darah diastolik harus antara ..."
    for key, (lo, hi, label) in NUMERIC_RANGES:
        raw := O[key]; skip if None or empty
        try v := float(raw.replace(",", "."))
        except: errors += "{label} harus berupa angka."; continue
        if v out of [lo, hi]: errors += "{label} harus antara {lo} dan {hi}."
    return errors
```

Kosong / missing diperlakukan *not provided* dan diabaikan (bidan tidak selalu mengisi).

### 4.3 Safety Check (`POST /api/safety/check`)

Acuan: `api/routes/safety_routes.py:16-72`.

```text
function safety_check(request):
    drugs := body.drugs
    pasien_id := body.pasien_id (optional)
    require drugs is non-empty list -> else 400
    sc := bootstrap.get_module("anggota4", "safety_checker")
    if not sc: return 503 "safety checker unavailable"
    payload := sc.cek_keamanan_obat(drugs)  # see anggota4/safety_checker.py:166
    hasil_obat := payload.hasil_obat
    max_skor := max(h.skor_risiko for h in hasil_obat) or 0
    agg_label_id := max(h.label_risiko for h in hasil_obat) ranked by _LABEL_ORDER
    pasien_context := None; pasien_active_meds := []
    if pasien_id:
        target := find patient by id
        if target:
            pasien_context := projection of {id, nama, kategori, diagnosa, kondisi_umum}
            pasien_active_meds := helpers.parse_resep_to_meds(target.P.resep)
    return 200 {
        drugs: hasil_obat,
        interactions: payload.efek_tumpang_tindih,
        severity_score: round(max_skor),
        severity_level: _LABEL_MAP[agg_label_id],
        warnings: payload.peringatan_prioritas,
        obat_tidak_ditemukan: payload.obat_tidak_ditemukan,
        pasien_context, pasien_active_meds
    }
```

Detil agregasi label ada di `safety_routes.py:33-41`. Bandingkan dengan `anggota4/safety_checker.py:36-40` untuk asal angka 40 dan 70.

### 4.4 Heatmap Cell Coloring

Acuan: `src/lib/heatmap-colors.ts:32-40` dan `src/app/heatmap/page.tsx` (lihat T1-HEATMAP §4).

```text
function buildColorScale(min, max):
    if max <= min: return (_ -> RISK_RAMP[0])
    interpolator := piecewise(interpolateRgb, RISK_RAMP)
    scale := d3.scaleLinear().domain([min, max]).range([0,1]).clamp(true)
    return (v -> interpolator(scale(v)))

function cellRender(v):
    bg := colorScale(v)
    fg := relativeLuminance(bg) > 0.55 ? "#1A1815" : "#FFFFFF"
    td.style.background = bg; td.style.color = fg
    td.title = "{Drug} × {Effect}: {v}"; td.aria-label = same
```

### 4.5 Storage Auto-Fallback

Acuan: `api/storage.py:63-87`.

```text
function _load(key, fallback_default):
    try:
        if USE_CLOUD_STORAGE:
            data := _load_gcs(key)
            if data is None:
                log "GCS {key} missing, seeding from local fallback"
                local := _load_local(key)
                if local is not None:
                    _save_gcs(key, local)
                    return local
                return fallback_default
            return data
        else:
            data := _load_local(key)
            return data if data is not None else fallback_default
    except e:
        log "load {key} failed: {e}, returning fallback"
        return fallback_default
```

Logika *ensure password hashed on first read* (`storage.py:90-98,105-109`) berjalan setelah load: bila user object berisi `password_plain`, di-hash bcrypt cost 12 (`auth.py:11-12`) dan file ditulis ulang. Plaintext tidak persis setelah server boot pertama.

### 4.6 Edge Middleware Proxy (Frontend)

Acuan: `src/proxy.ts:41-83`.

```text
function proxy(req):
    pathname := req.nextUrl.pathname
    if isPublic(pathname): return next
    token := req.cookies.medwatch_token
    if not token:
        redirect to /login?from=pathname
    role := decodeRole(token)
    if not role: redirect to /login
    if pathname == "/": redirect to landingFor(role)
    if pathname startsWith "/admin" and role != "admin":
        redirect to landingFor(role)
    if role == "masyarakat" and pathname not in allowed:
        redirect to /drug-search
    return next
```

`decodeRole` (`src/proxy.ts:22-33`) hanya melakukan *client-side payload inspection*; verifikasi tanda tangan tetap di backend (Edge tidak boleh memegang kunci HMAC karena tidak ada akses ke Secret Manager dari Vercel Edge). Ini *defense in depth*, bukan *primary trust*.

### 4.7 PDF Schema Translator

Acuan: `api/routes/pdf_routes.py:135-166`.

Fungsi `_to_anggota5_format(p)` mengubah dict kanonik:

```text
{
  identitas: { "ID Pasien": p.id, "Nama Pasien": p.nama, "Umur": "{umur} Tahun", "Tanggal Kunjungan": p.tanggal_kunjungan, "Alamat": p.alamat },
  anamnesis: "Keluhan Utama : {S.keluhan}\nRiwayat Sakit : {S.riwayat}",
  pemeriksaan: "Tekanan Darah : {O.tekanan_darah} mmHg\nNadi : {O.nadi} x/menit\nSuhu Tubuh : {O.suhu_c} °C\nBerat Badan : {O.bb_kg} kg\nCatatan Lain : {O.catatan}",
  diagnosis_tindakan: "DIAGNOSA (A) :\n{A.diagnosa}\n\nTINDAKAN (P) :\n{P.tindakan}\n\nRESEP OBAT : {P.resep}\nJADWAL KONTROL : {P.jadwal_kontrol}"
}
```

Output ini diterima oleh `anggota5.export_pdf.buat_laporan_pdf` (read-only) tanpa modifikasi.

---

## 5. Kerangka Pengujian (*Test Framework*)

Strategi pengujian SDD ini mereferensikan rencana pengujian black-box lengkap di Wave 5. Untuk *backend smoke* yang sudah berjalan saat ini:

- File: `api/tests/smoke_test.py` (165 baris).
- Lingkup: `test_health`, `test_login_three_roles`, `test_login_invalid`, `test_patients_crud`, `test_drug_search`, `test_safety_check`, `test_visualizations`, `test_role_enforcement` (`smoke_test.py:19-141`).
- Cara jalan: `BASE_URL=http://localhost:8080 .venv/bin/python api/tests/smoke_test.py`.
- *Negative assertions*: `test_role_enforcement` memastikan tenaga_kesehatan menerima 403 di `/api/admin/users` (`smoke_test.py:131-133`), dan password tidak bocor (`smoke_test.py:139`).

Hasil eksekusi terakhir (per T1-SAFETY §"Backend smoke-test regression"):
```
OK /api/health
OK login bidan_siti as tenaga_kesehatan
OK login umum_budi as masyarakat
OK login admin_ghaisan as admin
OK auth negatives all 401
OK POST /api/patients -> P008
OK GET /api/patients/P008
OK /api/drugs/search?q=paracetamol
OK /api/safety/check -> severity=medium score=60
OK /api/visualizations/kunjungan-trend
OK /api/visualizations/keluhan-distribution
OK /api/visualizations/top-efek-samping
OK /api/visualizations/heatmap-efek
OK role-based access enforced and passwords not leaked
done all smoke tests passed
```

Test plan lengkap (TC-MOD-NNN) ditulis di Wave 5. Untuk *frontend* tidak ada *unit test* Wave 1; *e2e* Playwright ditunda sampai Next 16 Turbopack dev-server stabil (lihat T1-SAFETY §followups dan As-Built Known Issues).

---

## 6. Lampiran

### 6.1 Glosarium ringkas

| Singkatan | Arti |
|---|---|
| ADR | Architecture Decision Record |
| API | Application Programming Interface |
| C4 L1/L2/L3 | Level 1 (Context), Level 2 (Container), Level 3 (Component) pada model C4 |
| CORS | Cross-Origin Resource Sharing |
| CRUD | Create, Read, Update, Delete |
| ERD | Entity-Relationship Diagram |
| GCP | Google Cloud Platform |
| GCS | Google Cloud Storage |
| JWT | JSON Web Token |
| MADR | Markdown Architectural Decision Record |
| PRD | Product Requirements Document |
| RSC | React Server Component |
| SDD | Software Design Description |
| SOAP | Subjective, Objective, Assessment, Plan |
| SRS | Software Requirements Specification |
| SSR | Server-Side Rendering |
| WCAG | Web Content Accessibility Guidelines |

### 6.2 Referensi lintas dokumen

- `docs/PRD.md` - kebutuhan produk dan persona.
- `docs/SRS.md` - kebutuhan fungsional FR-001..N dan non-fungsional.
- `docs/adr/0001-vercel-cloud-run-split.md` ... `000N-*.md` - keputusan arsitektur.
- `docs/API.md` - daftar endpoint dan request/response per endpoint.
- `docs/DATA-DICTIONARY.md` - kamus data lengkap.
- `docs/INSTALL.md` - panduan instalasi dan deployment.
- `docs/SECURITY.md` - threat model dan posture.
- `docs/USER-MANUAL.md` - manual pengguna per role.
- `docs/AS-BUILT.md` - laporan As-Built per ISO/IEC/IEEE 15289:2019.
- `docs/diagrams/src/*.{mmd,puml}` dan `docs/diagrams/png/*.png` - diagram sumber + render.

### 6.3 Catatan as-built post Wave 1

Perubahan Wave 1 yang tercermin di SDD ini:

1. **B01 (admin scraper navigation)** - `src/app/admin/dashboard/page.tsx` mendapatkan link ke `/admin/scraper` (lihat T1-ADMIN).
2. **B02 ("Lihat semua" inert)** - tautan diperbaiki ke halaman patient list (lihat T1-ADMIN).
3. **B03 (numeric validation)** - `api/routes/patient_routes.py:17-99` dan `src/lib/patient-validation.ts:22-92`.
4. **B04 (PDF only SOAP)** - `api/routes/pdf_routes.py:241-385` (efek samping) dan `:388-511` (inventaris).
5. **B05 (safety active meds)** - `api/routes/safety_routes.py:45-61` dan `api/helpers.py:25-96`.
6. **B07 (sort newest first)** - `api/routes/patient_routes.py:30-53,141-145`.
7. **B08 (safety inline help)** - frontend `src/app/safety-checker/page.tsx` collapsible help panel (lihat T1-SAFETY §B08).
8. **B09 (manual login)** - lihat T1-LOGIN.
9. **B10 (admin KPI hardcoded)** - `api/routes/admin_routes.py:18,106-127` mengembalikan `process_started_at`, `uptime_seconds`, dan agregasi user real.
10. **B11 (heatmap not real)** - `src/lib/heatmap-colors.ts:1-128` dan `src/app/heatmap/page.tsx` (T1-HEATMAP).

Catatan: rename `middleware.ts` -> `proxy.ts` adalah respons terhadap *deprecation warning* Next 16 dan dibahas di T1-SAFETY follow-ups; file referensi terkini adalah `src/proxy.ts`.

### 6.4 Kepatuhan terhadap CLAUDE.md dan misi

- Tidak ada modifikasi *in-place* pada folder `anggota1..5` (aturan 2). Lapisan wrapper di `api/` (aturan 5 misi).
- Tidak ada nilai kredensial dalam dokumen ini. Nama resource (`medwatch-polban-2026`, `medwatch-polban-2026-state`, `medwatch-jwt-secret`, `medwatch-api`) disebut sesuai mission constraint 12.
- Bahasa Indonesia untuk prose, Inggris untuk identifier kode dan standar.
- Tidak ada em dash, tidak ada emoji.
- Skema kanonik yang dirujuk konsisten dengan CLAUDE.md aturan 3.
- Endpoint dan baris kode yang dikutip sudah diverifikasi terhadap file sumber per 18 Mei 2026.

---

Akhir SDD.
