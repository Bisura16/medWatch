---
title: Offline Implementation Plan MedWatch
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking plan (belum diimplementasi)
related_docs:
  - ProductionGrade-ImplementationPlan/00-overview.md
  - ProductionGrade-ImplementationPlan/01-production-PRD.md
  - ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md
  - docs/PRD.md
  - docs/SECURITY.md
---

# 02 - Offline Implementation Plan MedWatch

Dokumen ini menjabarkan rencana konkret untuk membuat MedWatch beroperasi penuh tanpa koneksi internet pada workstation Faskes 1. Strategi terdiri atas empat pilar: (1) bundle snapshot data openFDA saat build-time, (2) migrasi storage dari JSON file menjadi SQLite lokal, (3) menghapus seluruh HTTP request runtime dari desktop modular runtime, (4) menyediakan jalur ekspor/impor manual untuk pertukaran data antarmesin.

---

## 1. Tujuan dan Non-Tujuan

### 1.1 Tujuan

1. Menghilangkan dependency runtime terhadap koneksi internet untuk semua jalur fungsional kecuali tombol opsional "Refresh openFDA" pada menu admin.
2. Memastikan startup aplikasi dan operasi CRUD pasien tetap cepat (kurang dari 3 detik cold start, kurang dari 200 ms simpan pasien) setelah migrasi storage.
3. Tetap mempertahankan kompatibilitas schema dengan modul `anggota1`..`anggota5` agar tidak melanggar mission constraint 5 (modul anggota read-only).

### 1.2 Non-Tujuan

1. Tidak menulis ulang modul anggota1-5. Pengubahan persistensi dilakukan di layer baru `app/storage_sqlite.py` (atau setara) yang menjadi adapter; modul anggota tetap dipanggil dengan dict/list yang sama.
2. Tidak memaksa schema relasional kompleks. SQLite yang dipakai bersifat key-value document oriented (kolom `id` + `data_json TEXT`) untuk meminimalkan migration friction.
3. Tidak mendukung concurrent multi-user. Satu instance MedWatch pada satu workstation memegang lock file di SQLite. Multi-user concurrent ditolak per `01-production-PRD.md` Section 5.

---

## 2. Audit Status Saat Ini

### 2.1 Modul yang memiliki HTTP call di import time

`grep -rn "^import requests\|^from requests" anggota*` saat dokumen ditulis menghasilkan dua hit:

| File | Baris | Konsekuensi production |
|---|---|---|
| `anggota1/anggota1.py` | line 17 `import requests` | Saat `app.py` mengimpor `anggota1.py` untuk fitur scraping awal, runtime mengeluarkan koneksi DNS. Akan dipindah ke lazy import. |
| `anggota1/openfda/fetch.py` | line 45 `import requests` | File ini hanya dipakai saat build-time menjalankan snapshot openFDA. Tidak perlu di-include di bundle production runtime. |

Modul `anggota2`, `anggota3`, `anggota4`, `anggota5` tidak memiliki import HTTP pada level top file. `grep -rn "^import requests\|^from requests\|^import urllib\|^from urllib\|^import http\|^from http" anggota2/ anggota3/ anggota4/ anggota5/` menghasilkan kosong saat dokumen ditulis. Implikasi: hanya `anggota1` yang membutuhkan strategi lazy import. anggota2-5 sudah offline-ready by virtue of their dependency footprint.

### 2.2 Storage saat ini

`api/storage.py` mendukung dua mode: local file JSON (`_save_local` line 38, `_load_local` line 30) dan Google Cloud Storage (`_save_gcs` line 55, `_load_gcs` line 45). Production akan menambahkan mode ketiga: SQLite (`_save_sqlite`, `_load_sqlite`). Mode SQLite dipilih melalui env var `STORAGE_BACKEND=sqlite` (default untuk build production), `STORAGE_BACKEND=local` (default untuk dev), `STORAGE_BACKEND=gcs` (default untuk Cloud Run demo akademik).

### 2.3 Lapisan modul mahasiswa sebagai konsumen storage

- `anggota2/pasien_helper.py` line 6 `import json`, line 7 `import os` - desktop modul membaca/menulis `Pasien.json` lokalnya sendiri. Production tidak akan mengganti perilaku ini; modul desktop boleh tetap memakai JSON file lokal saat user hanya menjalankan `python -m anggota2.PasienCRUD`. Storage SQLite hanya berlaku untuk path API (Flask `api/`) yang menjadi backend bundle production.
- `anggota4/data_loader.py` line 8 `import json` - sama; menyalin file `drug_database.json` dan `effect_database.json` saat install.

---

## 3. Bundle Snapshot Data openFDA

### 3.1 Mengapa snapshot, bukan live API

openFDA gratis dan publik, tetapi punya tiga masalah saat dipakai runtime di Faskes 1:

1. Memerlukan internet (tidak tersedia di banyak Faskes 1).
2. Memerlukan API key (lihat constraint 11 di mission constitution). Klien tidak bisa diharapkan mendaftar API key sendiri.
3. Latency 2-5 detik per request akan merusak UX yang menjanjikan kurang dari 500 ms untuk safety check.

Snapshot diambil oleh developer (Ghaisan) sebelum build installer, lalu di-bundle. Snapshot di-refresh setiap minor release (lihat `06-roadmap.md`).

### 3.2 Format snapshot

File snapshot disimpan di repo source di path `anggota1/data/` (tidak berubah dari MVP akademik). Saat build production, build script akan mengarahkan PyInstaller untuk meng-copy folder ini ke `data/anggota1/` di dalam bundel `dist/`. Lihat detail PyInstaller spec di `03-packaging-and-distribution.md` Section 2.

Skema file snapshot tetap memakai schema yang dibangun di Wave 1:

- `anggota1/data/drug_safety_data.json` - 74 rekord (per `wc -l` 18 Mei 2026), masing-masing `{drug_name, category, side_effects[], severity_level, warnings, source_url}` sesuai output `fetch_adverse_events_for_drug` di `anggota1/openfda/fetch.py:342`.
- `anggota1/data/drug_recalls.json` - 6000 rekord, masing-masing `{product_name, reason, recall_date, severity_class, company}` sesuai output `fetch_drug_recalls` di `anggota1/openfda/fetch.py:422`.

### 3.3 Build-time snapshot pipeline

Pada hari developer mempersiapkan release baru:

1. Set env var: `export OPENFDA_API_KEY="<dummy_placeholder>"` (nilai nyata diset oleh developer secara lokal, tidak pernah masuk repo per mission constraint 12).
2. Jalankan: `.venv/bin/python -m anggota1.openfda.fetch --max-drugs 80 --max-recall-pages 6`.
3. Verify output: `wc -l anggota1/data/drug_safety_data.json` minimal 50 obat; `wc -l anggota1/data/drug_recalls.json` minimal 4000 rekord.
4. Commit snapshot dengan message `chore(data): refresh openFDA snapshot YYYY-MM-DD`.
5. Tag build: `git tag v1.0.0-snapshot-YYYY-MM-DD`.
6. Lanjutkan ke build PyInstaller per `03-packaging-and-distribution.md`.

### 3.4 First-run snapshot loader

Saat user pertama kali menjalankan aplikasi production:

1. Aplikasi memeriksa `%APPDATA%\MedWatch\data\drug_safety_data.json` (Windows) atau `~/Library/Application Support/MedWatch/data/` (macOS) atau `~/.local/share/MedWatch/data/` (Linux).
2. Jika folder kosong, aplikasi menyalin snapshot dari bundle `<install_dir>/data/anggota1/*` ke folder app data.
3. Loader mencatat tanggal snapshot di file `<appdata>/data/snapshot-info.json` agar user tahu kapan data terakhir di-refresh.
4. Jika folder sudah ada (upgrade), aplikasi mempertahankan snapshot existing kecuali user secara eksplisit klik menu "Update Snapshot" di Help -> Tentang Aplikasi (memerlukan internet).

---

## 4. Migrasi Storage ke SQLite

### 4.1 Mengapa SQLite

JSON file yang dipakai oleh `api/storage.py:38` (write open mode `w`) memiliki residual risk R6 di `docs/SECURITY.md` Section 7: penulisan tidak atomic, race kondisi crash bisa meninggalkan file korup. Mitigasi yang dipilih untuk production: migrasi ke SQLite yang memberikan write transaction dan crash recovery built-in. SQLite juga membuka jalan untuk indexing efficient saat jumlah pasien tumbuh melebihi 1000 record (di mana scan linear JSON menjadi lambat).

Alternatif yang dipertimbangkan dan ditolak:

- PostgreSQL embedded: terlalu berat untuk single-Faskes deployment.
- Pattern atomic-rename pada JSON file (`write-to-temp + os.replace`): lebih sederhana tapi tidak menyelesaikan masalah scaling. Dapat dipakai sebagai bridging strategy untuk versi 1.0 jika scope SQLite terlalu besar; akan diputuskan di awal Phase 2 (lihat `06-roadmap.md`). Pattern atomic-rename sudah dicatat sebagai mitigasi R6 di `docs/SECURITY.md` Section 7.

### 4.2 Skema SQLite (draft)

Skema mengikuti document-oriented sederhana agar minim friction migrasi dari JSON:

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    owner_username TEXT,
    tanggal_kunjungan TEXT,
    data_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_patients_tanggal ON patients (tanggal_kunjungan DESC);
CREATE INDEX idx_patients_owner ON patients (owner_username);
```

Field `data_json TEXT` menyimpan JSON payload aslinya (sesuai canonical schema di `CLAUDE.md` baris 95-105). Field top-level seperti `id`, `tanggal_kunjungan`, `owner_username` di-promote menjadi kolom terpisah untuk indexing.

### 4.3 Migration tool

Skrip `tools/migrate_json_to_sqlite.py` (akan dibuat di Phase 2):

1. Buka file `api/data/users.json` (jika ada).
2. Untuk setiap user dict, INSERT ke tabel `users` dengan `data_json = json.dumps(user)`.
3. Buka file `api/data/patients.json` (jika ada).
4. Untuk setiap patient dict, INSERT ke tabel `patients`.
5. Set `schema_version.version = 1, applied_at = NOW()`.
6. Verify: SELECT COUNT(*) FROM users dan patients sesuai dengan jumlah entry JSON awal.

### 4.4 Layer adapter

File `api/storage_sqlite.py` (akan ditambahkan saat implementation) menyediakan API identik dengan `api/storage.py`:

- `load_users() -> list[dict]` -> SELECT data_json FROM users; json.loads().
- `save_users(users)` -> bulk UPSERT per username.
- `load_patients() -> list[dict]` -> SELECT data_json FROM patients ORDER BY tanggal_kunjungan DESC.
- `save_patients(patients)` -> bulk UPSERT per id.

Layer ini di-route oleh `api/config.py` berdasarkan env `STORAGE_BACKEND`. Build production set `STORAGE_BACKEND=sqlite`; dev tetap pakai `STORAGE_BACKEND=local` agar tidak mengubah workflow tim mahasiswa.

---

## 5. Lazy Import HTTP Dependency

### 5.1 anggota1/anggota1.py

File `anggota1/anggota1.py` line 17 melakukan `import requests` di module top-level. Saat `api/bootstrap.py` mengimpor `anggota1` untuk akses helper kategorisasi, runtime melakukan setup HTTP transport meskipun aplikasi production tidak pernah melakukan scraping di runtime.

Strategi mitigasi (tanpa modifikasi file anggota per constraint 5):

- Production build menggunakan wrapper di `api/bootstrap.py` yang memuat `anggota1` melalui lazy import (`importlib.import_module("anggota1", package=None)` saat user benar-benar klik menu admin Refresh openFDA).
- Untuk akses fungsi helper `tebak_kategori` yang sering dipakai, definisi yang sama sudah ada di `anggota1/openfda/fetch.py:136`. Production dapat memilih fungsi mana yang dipanggil. Karena `anggota1/openfda/fetch.py` juga mengimpor `requests` di line 45, strategi terbaik adalah:
  - Extract `KATEGORI_MAP` constant ke file baru `api/categori_constants.py` (file baru, additive, tidak melanggar constraint 5). Constant ini di-import oleh `api/` saat dibutuhkan.
  - Lazy import `anggota1.openfda.fetch` hanya saat tombol Admin "Refresh openFDA" di-klik.

### 5.2 anggota1/openfda/fetch.py

File ini hanya dipakai untuk build-time snapshot. Production runtime tidak meng-include file ini di PyInstaller bundle (lihat exclusion list di `03-packaging-and-distribution.md` Section 2.4).

### 5.3 Verifikasi audit grep

Acceptance test untuk fitur "fully offline": pada bundle PyInstaller production, jalankan:

```bash
python -c "import sys; sys.path.insert(0, '<install_dir>'); import api.app; import socket; socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('network forbidden'))"
```

Aplikasi harus dapat melayani semua endpoint non-admin tanpa memanggil `socket.create_connection`. Tes ini menjadi test case di `05-test-and-acceptance-plan.md` Section 2.

---

## 6. Sync Strategy (Optional)

### 6.1 Mengapa hanya manual

Konteks Faskes 1 tidak membutuhkan sinkronisasi otomatis. Setiap Faskes berdiri sendiri. Jika di masa depan ada permintaan klaster (multi-Faskes di bawah satu dinas kesehatan kabupaten), bisa dipertimbangkan di versi 2.0.

### 6.2 Ekspor/impor manual

Memanfaatkan pipeline PDF/JSON yang sudah ada:

- Ekspor pasien (PDF): `anggota5/export_pdf.py` line 2 menggunakan `from fpdf import FPDF`. Production menambah menu "Ekspor JSON" yang menulis `patients-export-YYYY-MM-DD.json` (skema sama dengan `api/data/patients.json`).
- Impor pasien: menu "Impor JSON" memvalidasi file kemudian INSERT ke SQLite. Konflik ID di-resolve dengan rename otomatis (P001 yang sudah ada di-rename ke P001-import-1 saat impor).

### 6.3 Backup ke external drive

Lihat `01-production-PRD.md` Story PROD-US-06. Implementasi: `shutil.copy2(<appdata>/medwatch.db, <user_target>/medwatch-backup-YYYY-MM-DD.db)`.

---

## 7. Path Folder dan Environment Variables

Saat production build:

- Install directory: `C:\Program Files\MedWatch\` (Windows), `/Applications/MedWatch.app/` (macOS), `/opt/MedWatch/` (Linux).
- App data directory: `%APPDATA%\MedWatch\` (Windows), `~/Library/Application Support/MedWatch/` (macOS), `~/.local/share/MedWatch/` (Linux).
- Database file: `<appdata>/medwatch.db`.
- Snapshot data: `<appdata>/data/anggota1/*.json` (di-copy dari `<install_dir>/data/anggota1/` saat first run).
- Crash log: `<appdata>/logs/crash.log`.
- Config: `<appdata>/config.ini` (opsional, untuk kustomisasi nama klinik di header PDF).

Env var yang diset oleh installer (Windows) atau wrapper shell script (macOS/Linux):

- `MEDWATCH_DATA_DIR` -> `%APPDATA%\MedWatch\` (sesuai OS).
- `STORAGE_BACKEND` -> `sqlite`.
- `FLASK_DEBUG` -> `false`.
- `MEDWATCH_OFFLINE_MODE` -> `true` (digunakan oleh wrapper untuk menyembunyikan menu admin yang mengandalkan internet jika di-set).

Env var tidak diset oleh installer:

- `JWT_SECRET` -> di-generate saat first run dari `secrets.token_hex(32)` dan disimpan di `<appdata>/.jwt-key` dengan permission 600. Tidak ada nilai yang masuk repo (per mission constraint 12).
- `OPENFDA_API_KEY` -> tidak diset secara default. Hanya diisi via menu admin "Pengaturan Lanjutan" saat user ingin refresh snapshot.

---

## 8. Risiko dan Mitigasi

| ID | Risiko | Likelihood | Dampak | Mitigasi |
|---|---|---|---|---|
| OFF-R1 | Migrasi JSON ke SQLite memunculkan data corruption pada existing test data | Rendah | Major | Migration tool memvalidasi count + sample 10 record sebelum dan sesudah. Test pada copy DB, bukan original. |
| OFF-R2 | SQLite file lock conflict saat user buka 2 instance bersamaan | Sedang | Minor | Aplikasi memeriksa lock file di startup. Jika sudah ada, tampilkan pesan "MedWatch sudah berjalan". |
| OFF-R3 | Snapshot openFDA basi (lebih dari 6 bulan) | Sedang | Major | Aplikasi menampilkan banner kuning di dashboard admin jika `snapshot-info.json` menunjukkan umur lebih dari 180 hari. |
| OFF-R4 | Lazy import `anggota1` gagal karena `requests` tidak tersedia di bundle | Rendah | Major | `requests` tetap di-include di bundle (kebutuhan size minor); fitur menu admin Refresh tetap berfungsi saat ada internet. |
| OFF-R5 | First-run copy data gagal karena permission folder AppData | Rendah | Major | Installer membuat folder dengan permission user current; fallback ke `<install_dir>/data/` jika AppData inaccessible. |
| OFF-R6 | User mengganti `<appdata>/config.ini` dengan path tidak valid | Sedang | Minor | Validasi config saat startup dengan fallback ke default jika invalid. |

---

## 9. Kriteria Penerimaan Section "Offline-Capable"

Lihat juga `05-test-and-acceptance-plan.md` Section 2. Ringkasan:

1. Aplikasi berjalan penuh dengan kabel jaringan dicabut: launch, login, CRUD pasien, safety check obat, visualisasi, ekspor PDF semuanya bekerja.
2. Audit grep pada bundle PyInstaller: tidak ada panggilan HTTP yang tereksekusi pada path non-admin.
3. Snapshot openFDA di-bundle dan diakses dari local file system saja.
4. SQLite menjadi backend storage default untuk build production; data persist setelah restart aplikasi.
5. Ekspor/impor JSON antarmesin bekerja dengan integritas data terjaga.

---

## 10. Tanggung Jawab dan Estimasi Waktu

| Item | PIC saran | Estimasi |
|---|---|---|
| Migration tool JSON -> SQLite | Ghaisan | 1 hari |
| Adapter `api/storage_sqlite.py` | Ghaisan | 1 hari |
| Update `api/config.py` untuk route STORAGE_BACKEND | Ghaisan | 0.5 hari |
| First-run snapshot loader (Python) | Ghaisan | 0.5 hari |
| Lazy import wrapper di `api/bootstrap.py` | Ghaisan | 0.5 hari |
| Test offline mode end-to-end | Bimo (QA) | 1 hari |
| Total | | 4.5 hari kerja |

Estimasi di atas asumsi developer full-time. Pekerjaan dijadwalkan di Phase 2 di `06-roadmap.md` (Juni-Juli 2026).
