# MedWatch Master Test Plan

Dokumen: MedWatch Black-Box Test Plan
Versi: 1.0
Tanggal: 12 Mei 2026 sampai 18 Mei 2026
Penanggung jawab: Bimo Surya Anggara, NIM 251524040, Quality Assurance Kelompok B5
Mata Kuliah: Proyek 1 Pengembangan Perangkat Lunak Desktop
Institusi: Politeknik Negeri Bandung, D4 Teknik Informatika, Kelas 1B-D4
Semester: 2 Tahun Akademik 2025/2026

## 1. Identifikasi Rencana Uji

Rencana uji ini disusun mengikuti struktur IEEE Std 829-2008 untuk Software Test
Documentation dan ISO/IEC/IEEE 29119-3:2013 Test Documentation. Rencana ini
mengatur seluruh aktivitas pengujian black-box pada sistem MedWatch yaitu
backend Flask (API) dan frontend Next.js (web showcase). Rencana ini melengkapi
SRS (`docs/SRS.md`) dan Bug Register (lihat `.mission/bugs.md`).

## 2. Lingkup Pengujian

### 2.1 Sistem yang Diuji
Backend MedWatch versi 1.0.0 yang dideploy di `http://127.0.0.1:8080`,
beserta layer integrasi `api/` (modul Python di bawah `anggota1` hingga
`anggota5` diuji secara tidak langsung melalui endpoint backend).

Frontend Next.js 16.2.1 di `http://localhost:3000` diuji untuk halaman SSR
melalui pemeriksaan ketersediaan. Pengujian klik UI Playwright dijadwalkan
tetapi dihalangi oleh blocker B-WAVE1-BUILD-1 (lihat lampiran).

### 2.2 Fitur dalam Lingkup
Pengujian mencakup sepuluh modul fungsional dengan kode test case
`TC-MOD-NNN`:
- AUTH: login, logout, introspeksi sesi, RBAC dekorator.
- PASIEN: CRUD pasien dengan skema SOAP, validasi range medis, sort.
- SAFETY: cek interaksi obat, agregasi verdict, konteks pasien.
- DRUG: pencarian obat, filter kategori, detail obat.
- VIZ: endpoint visualisasi (kunjungan-trend, keluhan-distribution, top-efek-samping).
- HEATMAP: endpoint heatmap obat x efek samping (matrix 6x17).
- PDF: empat tipe laporan PDF (rekam medis, bulanan, efek samping, inventaris).
- ADMIN: statistik sistem, manajemen user, pemicu scraper.
- SCRAPE: endpoint pendukung scraping (info, health).
- SCREEN: pengujian usability halaman UI SSR. Dihalangi B-WAVE1-BUILD-1.

### 2.3 Fitur di Luar Lingkup
- Pengujian load tingkat tinggi (>30 req/s) dilakukan terpisah pada fase deploy.
- Pengujian penetration testing tingkat lanjut. Mengacu pada `docs/SECURITY.md`.
- Pengujian klik UI bidan/admin halaman SSR dihalangi karena lingkungan build
  Node 25 + Next 16 belum stabil (blocker B-WAVE1-BUILD-1). Status Blocked
  digunakan untuk modul SCREEN.

## 3. Pendekatan dan Strategi Pengujian

### 3.1 Tipe Pengujian
Black-box functional testing. Tester memperlakukan sistem sebagai kotak hitam
dan melakukan validasi melalui kontrak antar muka (HTTP). Tidak ada
inspeksi internal terhadap implementasi.

### 3.2 Teknik Perancangan Test Case
Setiap test case ditandai dengan satu teknik perancangan utama:
- EP (Equivalence Partitioning): partisi nilai valid dan tidak valid.
- BVA (Boundary Value Analysis): nilai pada batas atas, batas bawah, di atas
  batas, di bawah batas.
- Decision Table: tabel keputusan untuk kombinasi role x endpoint.
- State Transition: transisi sesi login dari unauthenticated ke authenticated.
- Use Case: skenario alur pengguna ujung ke ujung.
- Error Guessing: input yang sengaja salah untuk menguji ketahanan error
  handler.

### 3.3 Standar Acuan
- IEEE Std 829-2008 Standard for Software and System Test Documentation.
- ISO/IEC/IEEE 29119-3:2013 Test Documentation.
- ISO/IEC/IEEE 29119-4:2015 Test Techniques (untuk teknik EP, BVA, dll).
- ISTQB Foundation Level Syllabus 2018 untuk istilah dasar.
- OWASP Top 10 (2021) untuk skenario uji keamanan.

### 3.4 Persentase Validasi dan Arikunto
Persentase Validasi dihitung dengan rumus berikut.

Persentase Validasi = (Jumlah status Pass / (Jumlah status Pass + Jumlah status Fail)) x 100 persen

Status Blocked dikeluarkan dari denominator dan dilaporkan terpisah pada
laporan ringkasan. Hasil persentase dipetakan ke skala Arikunto (Suharsimi
Arikunto, 2010, Prosedur Penelitian Suatu Pendekatan Praktik) sebagai
verdikt akhir:
- 86 sampai 100 persen sangat baik.
- 71 sampai 85 persen baik.
- 56 sampai 70 persen cukup.
- 41 sampai 55 persen kurang.
- kurang dari atau sama dengan 40 persen sangat kurang.

## 4. Lingkungan Pengujian

### 4.1 Perangkat Keras
Workstation Apple MacBook Pro M2, RAM 16 GB, penyimpanan SSD 512 GB.

### 4.2 Perangkat Lunak
- macOS Darwin 25.3.0.
- Python 3.11 dengan Flask 3.0 berjalan di `http://127.0.0.1:8080` (proses
  backend dijalankan via `python -m flask --app api.app run --port 8080`).
- Node.js v25 dengan Next.js 16.2.1 di `http://localhost:3000` (status:
  Internal Server Error pada SSR karena blocker B-WAVE1-BUILD-1).
- curl 8.7.1 sebagai alat utama pengujian HTTP.
- pandoc 3.9.0.2 untuk konversi Markdown ke docx.
- python3 untuk parsing JSON respons.

### 4.3 Data Uji
- File `api/data/users.json` berisi enam user seed: dua tenaga_kesehatan
  (`bidan_siti`, `bidan_putri`), dua masyarakat (`umum_budi`, `umum_dewi`),
  dua admin (`admin_ghaisan`, `admin_sistem`). Password seed dihash bcrypt
  cost 12 saat boot pertama.
- File `api/data/patients.json` berisi 24 rekam pasien (P001 sampai P024,
  bertambah selama eksekusi uji).
- File `anggota4/data/drug_database.json` berisi enam obat kanonik:
  Paracetamol, Ibuprofen, Amoxicillin, Captopril, Cetirizine, Metformin.

### 4.4 Kredensial Demo
Tester menggunakan kredensial demo yang terdokumentasi pada README backend
(`api/README.md`).
- `bidan_siti` dengan password `siti2026` peran `tenaga_kesehatan`.
- `umum_budi` dengan password `budi2026` peran `masyarakat`.
- `admin_ghaisan` dengan password `admin2026` peran `admin`.

### 4.5 Persiapan Eksekusi
Sebelum sesi pengujian harian, tester menjalankan urutan berikut.
1. Verifikasi backend hidup via `GET /api/health`. Respon harus HTTP 200 dan
   bidang `status:"ok"`.
2. Login admin lalu menyimpan token JWT ke `/tmp/medwatch-test/token-admin.txt`.
3. Login bidan dan masyarakat dengan cara serupa.
4. Mengeksekusi script curl per modul, menyimpan transcript ke
   `docs/testing/evidence/<TC-ID>.txt`.

## 5. Pembagian Tanggung Jawab dan Jadwal

Eksekusi tersebar di rentang 12 sampai 18 Mei 2026 sesuai dengan peran setiap
anggota Kelompok B5.

| Anggota | NIM | Peran | Modul Eksekusi | Tanggal |
|---|---|---|---|---|
| Bimo Surya Anggara | 251524040 | Quality Assurance, pemilik master test plan | AUTH, PASIEN | 12 sampai 14 Mei 2026 |
| Alia Ardani | 251524035 | System Analyst, pemilik RTM | VIZ, HEATMAP | 13 sampai 15 Mei 2026 |
| Muhammad Iqbal | 251524057 | Programmer | SAFETY, DRUG | 14 sampai 16 Mei 2026 |
| Abhidal Muhammad Gazza | 251524032 | UI atau UX | PDF, SCREEN | 15 sampai 17 Mei 2026 |
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader | SCRAPE, ADMIN | 16 sampai 18 Mei 2026 |

## 6. Kriteria Masuk dan Kriteria Keluar

### 6.1 Kriteria Masuk (Entry Criteria)
- Backend MedWatch berhasil di-boot dan menjawab `GET /api/health` dengan HTTP 200.
- File data seed `users.json` dan `patients.json` ada dan valid JSON.
- Tester memiliki kredensial demo yang sah.
- Test case dan script eksekusi telah ditinjau silang.

### 6.2 Kriteria Keluar (Exit Criteria)
- Seluruh test case dieksekusi terhadap aplikasi yang berjalan nyata.
- Persentase Validasi dihitung dan dipetakan ke skala Arikunto.
- Defect log diisi untuk setiap status Fail dan Blocked.
- Bukti eksekusi tersimpan di `docs/testing/evidence/` per test case.
- Auditor mereproduksi sampel tiga sampai lima test case secara independen dan
  cocok.

## 7. Risiko dan Mitigasi

| Kode Risiko | Deskripsi | Mitigasi |
|---|---|---|
| R-T-001 | Frontend SSR tidak dapat di-build (Next.js 16.2.1 + Node 25.6) menghalangi pengujian halaman UI. | Modul SCREEN ditandai Blocked dengan referensi B-WAVE1-BUILD-1. Pengujian alur API dijalankan setara via curl. |
| R-T-002 | Token JWT bocor melalui evidence file. | Token disimpan pada `/tmp/medwatch-test/` di luar repo. Evidence menyimpan respons aplikasi, bukan kredensial. |
| R-T-003 | Data persistensi berubah selama uji (POST membuat pasien baru). | Eksekusi dirancang idempotent. Tester memverifikasi ID pasien sebelum dan sesudah. |
| R-T-004 | Lingkungan macOS curl versi berbeda. | Versi curl direkam pada bagian 4.2. |
| R-T-005 | Reset state file selama uji menghapus pasien yang dibuat tester. | File `patients.json` ditambah saja selama uji; tidak ada reset paksa. |

## 8. Konfigurasi Test Case

### 8.1 Format Identifikasi
Setiap test case bernomor `TC-MOD-NNN`:
- `MOD` adalah kode modul: AUTH, PASIEN, SAFETY, DRUG, VIZ, HEATMAP, PDF,
  ADMIN, SCRAPE, SCREEN.
- `NNN` adalah indeks tiga digit terurut dalam modul.

### 8.2 Atribut per Test Case
Setiap test case memuat atribut berikut sesuai ISO/IEC/IEEE 29119-3 clause
6.3.7 (Test Cases).
- ID, Modul, Fitur.
- Tipe atau Teknik (EP, BVA, Decision Table, State Transition, Use Case,
  Error Guessing).
- Prasyarat.
- Langkah (urutan bernomor).
- Data Input.
- Hasil yang Diharapkan.
- Hasil Aktual (diisi dari eksekusi nyata).
- Status (Pass, Fail, Blocked).
- Tester (nama dan NIM).
- Tanggal eksekusi.
- Bukti atau Referensi (path file evidence dan referensi kode file:line).

## 9. Pelacakan Cacat (Defect Tracking)

Cacat dicatat di `docs/testing/defect-log.md`. Setiap cacat ditandai dengan
keparahan: Critical (memblokir submission), Major (mempengaruhi narasi demo),
Minor (kosmetik atau perbaikan masa depan). Cacat historis dari Wave 4 bug
hunt (`H01-1` sampai `H17-2`) dimasukkan sebagai input historis untuk
keterlacakan.

## 10. Penyerahan dan Bukti

Setiap test case Pass atau Fail wajib memiliki file bukti pada
`docs/testing/evidence/<TC-ID>.txt`. Test case Blocked menyertakan alasan
spesifik pada kolom Bukti.

Ringkasan persentase validasi dan verdikt Arikunto dilampirkan di
`docs/testing/test-summary.md`. Dokumen turunan format docx tersedia di
`docs/deliverable/test-plan.docx`, `test-cases.docx`, `rtm.docx`,
`defect-log.docx`, dan `test-summary.docx`.

## 11. Persetujuan

Penyusun: Bimo Surya Anggara, NIM 251524040.
Reviewer System Analyst: Alia Ardani, NIM 251524035.
Project Leader: Ghaisan Khoirul Badruzaman, NIM 251524048.
Dosen Pengampu: Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana.

## 12. Referensi

1. IEEE Std 829-2008, Standard for Software and System Test Documentation.
2. ISO/IEC/IEEE 29119-3:2013, Software and systems engineering, Software testing, Part 3: Test documentation.
3. ISO/IEC/IEEE 29119-4:2015, Software and systems engineering, Software testing, Part 4: Test techniques.
4. ISTQB Foundation Level Syllabus, version 2018.
5. OWASP Top 10 2021.
6. Suharsimi Arikunto, Prosedur Penelitian Suatu Pendekatan Praktik, edisi revisi 2010, Rineka Cipta.
7. MedWatch SRS, `docs/SRS.md`.
8. MedWatch As-Built, `docs/AS-BUILT.md`.
9. MedWatch Security, `docs/SECURITY.md`.
10. Wave 4 Bug Hunt Findings, `.mission/findings/bugs/W4-HUNT.md`.

## Lampiran A. Catatan Blocker B-WAVE1-BUILD-1

Blocker ini dikenal sejak Wave 1. Penjelasan singkat. Versi Next.js 16.2.1
tidak dapat menyelesaikan SSR build pada Node 25.6 di lingkungan macOS Darwin
25.3.0 karena ketidakcocokan webpack chunk loader pada module resolution baru.
Hasil pengamatan: `curl http://localhost:3000/` mengembalikan
`Internal Server Error` HTTP 500, baik untuk halaman UI (`/login`,
`/dashboard`, `/admin/dashboard`, `/safety-checker`, `/heatmap`,
`/export-pdf`) maupun untuk route API proxy (`/api/health`, `/api/patients`).

Konsekuensi terhadap pengujian: modul SCREEN dan beberapa test case di modul
AUTH, PASIEN, ADMIN, SAFETY yang memerlukan klik UI dicatat Blocked. Alur
HTTP API setara tetap diuji secara langsung melalui curl ke backend
`http://127.0.0.1:8080`. Penyebab teknis dan jalur perbaikan permanen
didokumentasikan pada `docs/AS-BUILT.md` bagian 16 Deviations.
