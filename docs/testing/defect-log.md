# MedWatch Defect Log

Dokumen: Catatan Cacat Pengujian
Versi: 1.0
Tanggal: 12 sampai 18 Mei 2026
Penanggung jawab: Bimo Surya Anggara, NIM 251524040, QA Kelompok B5

Defect log ini memuat cacat historis (Wave 1 B01..B11) yang dideteksi oleh
QA dan UI/UX kelompok, hasil bug-hunt Wave 4 (H01-1..H17-2), serta cacat baru
yang ditemukan saat sesi pengujian Wave 5 (W5-RT-NNN).

Skala keparahan:
- Critical: memblokir submission atau membahayakan data.
- Major: mempengaruhi narasi demo atau alur penting.
- Minor: kosmetik atau perbaikan masa depan.

Status:
- Open: belum diperbaiki.
- Fixed in <wave>: telah diperbaiki dengan referensi wave.
- Documented: didokumentasikan sebagai keputusan desain sengaja.
- Inconclusive: tidak dapat dipastikan tanpa investigasi lebih lanjut.

Sumber referensi:
- `.mission/bugs.md` (Bug Register awal).
- `.mission/findings/bugs/W4-HUNT.md` (bug-hunt Wave 4).
- `.mission/waves/wave-01-results.md` (resolusi Wave 1).
- `.mission/findings/bugs/W5-FIX-CRITICAL.md` (resolusi Wave 5).

## 1. Cacat Historis Wave 1 (B01 sampai B11)

Cacat berikut ditemukan saat sesi UI testing dengan dosen pada minggu Wave 0.
Semua telah diperbaiki di Wave 1.

| ID | Keparahan | Modul | Deskripsi | File:Line referensi | Status | TC Reproduksi |
|---|---|---|---|---|---|---|
| B01 | Major | ADMIN | Admin dashboard tidak memiliki CTA ke halaman scraper. | `src/app/admin/dashboard/page.tsx:170-226` | Fixed in Wave 1 | TC-SCREEN-003 (Blocked B-WAVE1-BUILD-1) |
| B02 | Major | DASHBOARD | Tombol "Lihat semua" pada panel aktivitas tidak memiliki target. | `src/app/dashboard/page.tsx:442`; route `src/app/dashboard/aktivitas/page.tsx` | Fixed in Wave 1 | TC-SCREEN-004 (Blocked B-WAVE1-BUILD-1) |
| B03 | Major | PASIEN | Form pasien menerima huruf pada field numerik medis (BB, TB, LILA, dll). | `api/routes/patient_routes.py:17-99`; `src/lib/patient-validation.ts` | Fixed in Wave 1 | TC-PASIEN-008 sampai TC-PASIEN-014 |
| B04 | Major | PDF | Export PDF hanya mendukung rekam medis (3 jenis lain hilang). | `api/routes/pdf_routes.py:169-511`; `src/app/export-pdf/page.tsx` | Fixed in Wave 1 | TC-PDF-001 sampai TC-PDF-007 |
| B05 | Major | SAFETY | Cek interaksi obat tidak menampilkan obat aktif pasien. | `api/routes/safety_routes.py:44-61`; `src/app/safety-checker/page.tsx` | Fixed in Wave 1 | TC-SAFETY-005 |
| B06 | Minor | ADMIN | Link scraper di admin dan KPI pengguna aktif "self-fixed". | `src/app/admin/dashboard/page.tsx` | Fixed in Wave 1 | TC-SCREEN-003, TC-ADMIN-001 |
| B07 | Major | PASIEN | List pasien terurut newest-first salah, item terbaru di bawah. | `api/routes/patient_routes.py:135-146` | Fixed in Wave 1 | TC-PASIEN-001, TC-PASIEN-022 |
| B08 | Major | SAFETY | Safety checker tidak menjelaskan inline cara membaca verdikt. | `src/app/safety-checker/page.tsx` | Fixed in Wave 1 | TC-SCREEN-005 (Blocked B-WAVE1-BUILD-1) |
| B09 | Major | AUTH | Login manual yang diketik gagal; demo creds tidak terlihat. | `src/app/login/page.tsx:18-43, 80-109` | Fixed in Wave 1 | TC-SCREEN-001 (Blocked B-WAVE1-BUILD-1) |
| B10 | Major | ADMIN | Admin dashboard menampilkan KPI hardcoded (1.247, 38, 89, 2). | `src/app/admin/dashboard/page.tsx:43-81` | Fixed in Wave 1 | TC-ADMIN-001 (backend), TC-SCREEN-002 (UI Blocked) |
| B11 | Major | HEATMAP | Heatmap tidak benar-benar heatmap (warna tidak kontinu). | `src/app/heatmap/page.tsx`; `src/lib/heatmap-colors.ts` | Fixed in Wave 1 | TC-HEATMAP-001 (backend), TC-HEATMAP-003 (UI Blocked) |

## 2. Cacat Wave 4 Bug Hunt (H01-1 sampai H17-2)

Bug-hunter Wave 4 melakukan 17-kategori sweep read-only. Total 22 temuan
dengan klasifikasi sebagai berikut.

### 2.1 Critical (1 temuan)

| ID | Keparahan | Modul | Deskripsi | File:Line | Status |
|---|---|---|---|---|---|
| H07-1 | Critical | SAFETY | Masyarakat dapat memanen PII (nama, diagnosa, kategori, obat aktif) pasien sembarang via POST `/api/safety/check` dengan `pasien_id`. | `api/routes/safety_routes.py:24-92` | Fixed in Wave 5; diverifikasi pada TC-SAFETY-006 (pasien_context:null, pasien_active_meds:[]) |

### 2.2 Major (6 temuan)

| ID | Keparahan | Modul | Deskripsi | File:Line | Status |
|---|---|---|---|---|---|
| H01-1 | Major | PASIEN | Field `umur` menerima sembarang teks termasuk negatif dan out-of-range. | `api/routes/patient_routes.py:26-33` | Fixed in Wave 5; diverifikasi TC-PASIEN-015, TC-PASIEN-016, TC-PASIEN-017 |
| H06-1 | Major | DASHBOARD | Bidan/admin `/dashboard` KPI hardcoded (regresi B10 sebagian). | `src/app/dashboard/page.tsx:302-307` | Fixed in Wave 5 (frontend) |
| H06-2 | Major | ADMIN | Admin dashboard `auditLog` panel hardcoded dengan IP palsu. | `src/app/admin/dashboard/page.tsx:102-108` | Fixed in Wave 5 (frontend) |
| H06-3 | Major | DASHBOARD | `/dashboard/aktivitas` feed seluruhnya hardcoded. | `src/app/dashboard/aktivitas/page.tsx:29-57` | Fixed in Wave 5 (frontend) |
| H07-2 | Major | PASIEN | Bidan dapat membaca rekam SOAP yang dibuat bidan lain (tidak ada multi-faskes scope). | `api/routes/patient_routes.py:175-195` | Documented (single-faskes assumption); didokumentasikan di SECURITY.md Wave 5 |
| H10-1 | Major | PASIEN | Race condition POST `/api/patients`: duplikat ID dan hilang silently. | `api/routes/patient_routes.py:228-235`; `api/storage.py:51-56` | Fixed in Wave 5 (threading.Lock) |

### 2.3 Minor (15 temuan)

| ID | Keparahan | Modul | Deskripsi | File:Line | Status |
|---|---|---|---|---|---|
| H01-2 | Minor | PASIEN | Field free-text tidak memiliki cap panjang maksimum. | `api/routes/patient_routes.py:198-235` | Open (low-priority for submission) |
| H01-3 | Minor | PASIEN | `nama` pasien menerima payload HTML atau script mentah (XSS reflected only di PDF). | `api/routes/patient_routes.py:198-235` | Open (no XSS surface in current UI) |
| H02-1 | Minor | SAFETY | Frontend safety-checker membuang detail backend `fields` saat 400. | `src/app/safety-checker/page.tsx:335` | Open |
| H03-1 | Minor | AUTH | Cookie `secure` flag tergantung NODE_ENV. | `src/app/api/[...slug]/route.ts:108,122` | Documented (production deploys with NODE_ENV=production) |
| H03-2 | Minor | AUTH | `fetchMe` failure path menyatukan network error dengan logged-out. | `src/lib/auth-store.ts:69-79` | Open |
| H04-1 | Minor | DASHBOARD | Fallback peran `masyarakat` masih merender blok admin (kolaps karena route guard). | `src/app/dashboard/page.tsx:288-307` | Open |
| H05-1 | Minor | ADMIN | `/api/admin/users` tidak memiliki sort stabil. | `api/routes/admin_routes.py:56-67` | Open |
| H06-4 | Minor | PASIEN PROFILE | `/pasien/profile` masih hardcoded identitas dan obat-saya. | `src/app/pasien/profile/page.tsx:118-164` | Open |
| H06-5 | Minor | SCRAPER | `/admin/scraper` job list hardcoded, menyebut situs yang tidak di-scrape. | `src/app/admin/scraper/page.tsx:31-50` | Open |
| H06-6 | Minor | UI | "12.4k obat" atau "1.4M interaksi" copy fabrikasi. | `src/app/login/page.tsx:262`, `src/app/dashboard/page.tsx:432`, `src/app/safety-checker/page.tsx:356,720` | Open |
| H07-3 | Minor | AUTH | Tidak ada rate limit atau lockout pada `/api/auth/login`. | `api/routes/auth_routes.py:19-55` | Documented (residual risk) |
| H09-1 | Minor | VIZ | `kunjungan-trend` dummy fallback dapat menyesatkan saat patient kosong. | `api/routes/visualization_routes.py:38-41,65-66` | Documented (T1-VERIFY accepts dummy for demo continuity) |
| H12-2 | Minor | A11Y | Logout icon button menggunakan `title` bukan `aria-label`. | `src/components/shell/NavBar.tsx:104-130` | Open |
| H13-1 | Minor | UI | "Edit SOAP" English string di patient list CTA. | `src/app/patients/page.tsx:458` | Open |
| H13-2 | Minor | UI | Admin scraper mengekspos "running"/"success"/"failed" English token di UI. | `src/app/admin/scraper/page.tsx:20-24,30-50` | Open |
| H14-1 | Minor | PERF | Safety-checker refetch `/api/drugs` setiap mount. | `src/app/safety-checker/page.tsx:171-187` | Open |
| H16-1 | Minor | AUTH | Backend `/api/auth/login` tidak set Set-Cookie (hanya proksi yang lakukan). | `api/routes/auth_routes.py:19-55` | Documented (proxy pattern by design) |
| H16-3 | Minor | AUTH | Tidak ada minimum length atau complexity policy pada password. | `api/routes/admin_routes.py:99-100` | Open |
| H17-1 | Minor | LOG | Login failure log menyertakan username yang dicoba (username enumeration aid). | `api/routes/auth_routes.py:51,54` | Open |
| H17-2 | Minor | LOG | INFO log tidak terstruktur JSON (concern future-prod). | `api/routes/patient_routes.py:234,285`, `api/routes/admin_routes.py:41,118,145` | Open |

### 2.4 Inconclusive (1 temuan)

| ID | Keparahan | Modul | Deskripsi | Catatan |
|---|---|---|---|---|
| H12-1 | Inconclusive | A11Y | Visible focus ring pada `.btn`, `.input`, `.chip`, `.nav-pill` perlu verifikasi Playwright keyboard tab-through. | Verifikasi Playwright tertunda karena B-WAVE1-BUILD-1. |

## 3. Cacat Baru Selama Pengujian Wave 5 (W5-RT-NNN)

Tidak ditemukan cacat baru selama eksekusi 88 test case Wave 5. Semua TC
yang dieksekusi via curl Pass dengan hasil aktual sesuai harapan. TC Blocked
adalah konsekuensi B-WAVE1-BUILD-1 (lingkungan build), bukan cacat aplikasi.

Catatan observasi non-defect:
- W5-OBS-001 (informational): Endpoint `/api/safety/check` mengembalikan `severity_score:60` untuk dua obat dan untuk tiga obat. Ini sesuai spesifikasi FR-031 karena skor adalah `round(max(skor_per_obat))`. Pengamatan informasional, bukan cacat.
- W5-OBS-002 (informational): `pasien_active_meds:["Asam folat","Amoxicillin"]` di TC-SAFETY-005 sesuai parsing `parse_resep_to_meds` pada `P.resep:"Asam folat 1x1 sehari\nAmoxicillin 3x500mg"`. Operasi parsing benar.

## 4. Ringkasan Status

| Klasifikasi | Total | Fixed | Documented | Open |
|---|---|---|---|---|
| B01-B11 (Wave 1) | 11 | 11 | 0 | 0 |
| H Critical | 1 | 1 | 0 | 0 |
| H Major | 6 | 4 | 1 (H07-2 single-faskes) | 0 untuk Major yang harus-fix (H06-1, H06-2, H06-3 Fixed) |
| H Minor | 18 | 0 | 5 (H03-1, H07-3, H09-1, H16-1, alasan di tabel 2.3) | 13 |
| Inconclusive | 1 | 0 | 0 | 1 (H12-1 verifikasi tertunda) |
| W5-RT-NNN baru | 0 | n/a | n/a | n/a |

Tidak ada defect Critical atau Major yang masih Open ketika dokumen ini
ditulis. Semua Open adalah Minor yang dapat ditangani pada iterasi berikutnya
tanpa memblokir submission 25 Mei 2026.

## 5. Persetujuan

Disusun: Bimo Surya Anggara, NIM 251524040 (QA).
Validasi historis: Ghaisan Khoirul Badruzaman, NIM 251524048 (Project Leader).
Validasi keamanan: berdasarkan Wave 4 bug-hunt sweep yang independen.
