# MedWatch Requirement Traceability Matrix (RTM)

Dokumen: Matriks Keterunutan Persyaratan ke Test Case
Versi: 1.0
Tanggal: 13 sampai 15 Mei 2026
Penanggung jawab: Alia Ardani, NIM 251524035, System Analyst Kelompok B5

RTM ini menautkan setiap persyaratan fungsional (FR-NNN) dan persyaratan
non-fungsional yang diuji (NFR-XXX-NNN) ke satu atau lebih test case TC-MOD-NNN.
Tujuan RTM adalah memastikan setiap persyaratan diuji minimal sekali dan
sebaliknya, tidak ada test case tanpa traceability ke SRS.

Standar: ISO/IEC/IEEE 29119-3:2013 clause 6.3.5 (Test Design Specification).

## 1. Forward Trace: SRS FR-ID ke TC-MOD-NNN

| FR-ID | Deskripsi Singkat (SRS) | Test Case Penguji | Status Uji |
|---|---|---|---|
| FR-001 | Login manual JWT HS256 issuer `medwatch-api` | TC-AUTH-001, TC-AUTH-002, TC-AUTH-003, TC-AUTH-004, TC-AUTH-005, TC-AUTH-006 | Pass |
| FR-002 | Validasi token JWT pada endpoint terlindung | TC-AUTH-008, TC-AUTH-009, TC-AUTH-013, TC-PASIEN-002, TC-SAFETY-004, TC-VIZ-004 | Pass |
| FR-003 | Tampilkan 3 preset demo login pada `/login` | TC-SCREEN-001 | Blocked (B-WAVE1-BUILD-1) |
| FR-004 | Pembacaan submit via `FormData` | (lihat FR-003) | Blocked (B-WAVE1-BUILD-1) |
| FR-005 | RBAC `require_role` dekorator | TC-AUTH-011, TC-AUTH-012, TC-AUTH-014, TC-PASIEN-003, TC-PASIEN-020, TC-PDF-004, TC-ADMIN-005, TC-ADMIN-007, TC-VIZ-005 | Pass |
| FR-006 | Logout endpoint | TC-AUTH-010 | Pass |
| FR-007 | Introspeksi sesi `/api/auth/me` | TC-AUTH-007 | Pass |
| FR-008 | Middleware Next.js redirect | (Blocked karena SSR) | Blocked (B-WAVE1-BUILD-1) |
| FR-009 | List ringkas pasien | TC-PASIEN-001 | Pass |
| FR-010 | Sort newest-first pasien + tie-break id | TC-PASIEN-001, TC-PASIEN-022 | Pass |
| FR-011 | Create pasien dengan ID `P###` | TC-PASIEN-018 | Pass |
| FR-012 | Validasi field wajib nama, S.keluhan, A.diagnosa, P.tindakan | TC-PASIEN-006, TC-PASIEN-007 | Pass |
| FR-013 | Validasi range medis (BB, TB, LILA, Nadi, Suhu, Respirasi, TD, Umur) | TC-PASIEN-008, TC-PASIEN-009, TC-PASIEN-010, TC-PASIEN-011, TC-PASIEN-012, TC-PASIEN-013, TC-PASIEN-014, TC-PASIEN-015, TC-PASIEN-016, TC-PASIEN-017 | Pass |
| FR-014 | Frontend mirror validation | TC-SCREEN-001 (sebagian) | Blocked (B-WAVE1-BUILD-1) |
| FR-015 | Detail pasien per ID, RBAC ownership masyarakat | TC-PASIEN-004, TC-PASIEN-005 | Pass |
| FR-016 | Deep-merge PUT pasien | TC-PASIEN-019 | Pass |
| FR-017 | DELETE pasien dibatasi admin | TC-PASIEN-020 | Pass |
| FR-020 | List obat dengan filter kategori | TC-DRUG-001, TC-DRUG-002, TC-DRUG-008 | Pass |
| FR-021 | Pencarian obat berbasis nama + alias | TC-DRUG-003, TC-DRUG-004, TC-DRUG-005 | Pass |
| FR-022 | Detail obat per nama atau 404 | TC-DRUG-006, TC-DRUG-007 | Pass |
| FR-030 | Cek interaksi obat | TC-SAFETY-001, TC-SAFETY-002, TC-SAFETY-003, TC-SAFETY-007, TC-SAFETY-008, TC-SAFETY-009 | Pass |
| FR-031 | Skor severitas 0..100 dan label mapping | TC-SAFETY-001, TC-SAFETY-007 | Pass |
| FR-032 | Pasien active meds via pasien_id | TC-SAFETY-005, TC-SAFETY-006 | Pass |
| FR-033 | Frontend gabungkan active meds ke input | TC-SCREEN-005 (UI) | Blocked (B-WAVE1-BUILD-1) |
| FR-034 | Panel collapsible penjelas verdict | TC-SCREEN-005 | Blocked (B-WAVE1-BUILD-1) |
| FR-040 | Kunjungan trend 12 bulan | TC-VIZ-001, TC-VIZ-005 | Pass |
| FR-041 | Distribusi kategori keluhan | TC-VIZ-002 | Pass |
| FR-042 | Top-10 efek samping | TC-VIZ-003 | Pass |
| FR-043 | Matrix heatmap obat x efek samping | TC-HEATMAP-001, TC-HEATMAP-002 | Pass |
| FR-044 | Render kontinu 5-stop ramp heatmap | TC-HEATMAP-003 | Blocked (B-WAVE1-BUILD-1) |
| FR-045 | Legend heatmap dengan tick min/mid/max | TC-HEATMAP-004 | Blocked (B-WAVE1-BUILD-1) |
| FR-046 | Sort baris dan kolom desc by total bobot | TC-HEATMAP-005 | Blocked (B-WAVE1-BUILD-1) |
| FR-050 | PDF rekam medis SOAP | TC-PDF-001, TC-PDF-002, TC-PDF-007 | Pass |
| FR-051 | PDF laporan bulanan | TC-PDF-003, TC-PDF-004 | Pass |
| FR-052 | PDF efek samping aggregate | TC-PDF-005 | Pass |
| FR-053 | PDF inventaris obat | TC-PDF-006 | Pass |
| FR-054 | Frontend `/export-pdf` 4 pilihan | (Backend-only verifikasi) | Blocked (B-WAVE1-BUILD-1) UI; backend Pass |
| FR-060 | Trigger scraper (admin only) | TC-ADMIN-006, TC-ADMIN-007 | Pass |
| FR-061 | List users dengan password stripped | TC-ADMIN-002 | Pass |
| FR-062 | Create user dengan role valid + bcrypt | TC-ADMIN-003, TC-ADMIN-004, TC-ADMIN-008 | Pass |
| FR-063 | Cegah penghapusan admin terakhir + delete | TC-ADMIN-009 | Pass |
| FR-064 | System stats real-time (non hardcoded) | TC-ADMIN-001 | Pass |
| FR-065 | Frontend dashboard admin render KPI | TC-SCREEN-002 | Blocked (B-WAVE1-BUILD-1) (backend TC-ADMIN-001 Pass) |
| FR-066 | CTA scraper di admin dashboard | TC-SCREEN-003 | Blocked (B-WAVE1-BUILD-1) |
| FR-067 | Lihat semua aktivitas | TC-SCREEN-004 | Blocked (B-WAVE1-BUILD-1) |
| FR-070 | Health endpoint public | TC-SCRAPE-002, TC-SCRAPE-003 | Pass |
| FR-071 | Info endpoint modules_loaded | TC-SCRAPE-001 | Pass |
| FR-DB-001 | UTF-8 ensure_ascii=false | (implisit di TC-PASIEN-001, TC-DRUG-001 - karakter Indonesia tampil) | Pass |
| FR-DB-002 | bcrypt-hash password_plain saat boot | (implisit di TC-AUTH-001 verifikasi login dengan plain seed) | Pass |
| FR-DB-003 | Seed GCS dari local pertama kali | Bukan dalam scope uji presentasi (mode lokal) | Out-of-scope |
| FR-DB-004 | Penghapusan pasien hanya admin | TC-PASIEN-020 (negatif), TC-ADMIN-009 untuk user | Pass |

## 2. NFR yang Diuji secara Langsung

| NFR-ID | Deskripsi Singkat | Test Case Penguji | Status |
|---|---|---|---|
| NFR-PERF-001 | Endpoint list < 2 detik p95 | TC-PASIEN-001 (time 0.001s), TC-DRUG-001 (0.001s) | Pass |
| NFR-PERF-002 | PDF rekam medis < 5 detik | TC-PDF-001 (time 0.007s) | Pass |
| NFR-SEC-001 | OWASP A01 RBAC | TC-AUTH-011, TC-AUTH-012, TC-PASIEN-020, TC-ADMIN-005, TC-ADMIN-007, TC-PDF-004 | Pass |
| NFR-SEC-002 | bcrypt cost 12 | (struktural; verifikasi runtime di TC-AUTH-001 yang sukses login pakai password seed) | Pass |
| NFR-SEC-003 | JWT issuer iss `medwatch-api` | TC-AUTH-001 (decode token memuat iss), TC-AUTH-009 (token rusak ditolak) | Pass |
| NFR-SEC-007 | Cegah hapus admin terakhir | (negative path tidak diuji destructively; FR-063 di-cover oleh TC-ADMIN-009 happy path) | Partial Pass |
| NFR-SEC-008 | Strip password_hash/password_plain/password | TC-PASIEN-021, TC-ADMIN-002 | Pass |
| NFR-USA-001 | Bahasa Indonesia user-facing | TC-PASIEN-006, TC-PASIEN-008, TC-PASIEN-013, TC-SAFETY-003 (semua pesan error Bahasa Indonesia) | Pass |
| NFR-INT-004 | WIB UTC+07:00 timestamp | TC-SCRAPE-002 (response `time:"2026-05-18T10:44:33.712382+00:00"` adalah UTC; konversi WIB dilakukan di PDF, verifikasi struktural via TC-PDF-001) | Pass |

## 3. Reverse Trace: TC-MOD-NNN ke FR-ID

| TC-MOD-NNN | FR-ID yang Diuji |
|---|---|
| TC-AUTH-001 | FR-001 |
| TC-AUTH-002 | FR-001 |
| TC-AUTH-003 | FR-001 |
| TC-AUTH-004 | FR-001 |
| TC-AUTH-005 | FR-001 |
| TC-AUTH-006 | FR-001 |
| TC-AUTH-007 | FR-007 |
| TC-AUTH-008 | FR-002 |
| TC-AUTH-009 | FR-002 |
| TC-AUTH-010 | FR-006 |
| TC-AUTH-011 | FR-005 |
| TC-AUTH-012 | FR-005 |
| TC-AUTH-013 | FR-002 |
| TC-AUTH-014 | FR-005 |
| TC-PASIEN-001 | FR-009, FR-010 |
| TC-PASIEN-002 | FR-002 |
| TC-PASIEN-003 | FR-005 |
| TC-PASIEN-004 | FR-015 |
| TC-PASIEN-005 | FR-015 |
| TC-PASIEN-006 | FR-012 |
| TC-PASIEN-007 | FR-012 |
| TC-PASIEN-008 | FR-013 |
| TC-PASIEN-009 | FR-013 |
| TC-PASIEN-010 | FR-013 |
| TC-PASIEN-011 | FR-013 |
| TC-PASIEN-012 | FR-013 |
| TC-PASIEN-013 | FR-013 |
| TC-PASIEN-014 | FR-013 |
| TC-PASIEN-015 | FR-013 |
| TC-PASIEN-016 | FR-013 |
| TC-PASIEN-017 | FR-013 |
| TC-PASIEN-018 | FR-011 |
| TC-PASIEN-019 | FR-016 |
| TC-PASIEN-020 | FR-017 |
| TC-PASIEN-021 | NFR-SEC-008 |
| TC-PASIEN-022 | FR-010 |
| TC-SAFETY-001 | FR-030, FR-031 |
| TC-SAFETY-002 | FR-030 |
| TC-SAFETY-003 | FR-030 |
| TC-SAFETY-004 | FR-002 |
| TC-SAFETY-005 | FR-032 |
| TC-SAFETY-006 | FR-032 (H07-1 fix) |
| TC-SAFETY-007 | FR-031 |
| TC-SAFETY-008 | FR-030 |
| TC-SAFETY-009 | FR-030 |
| TC-DRUG-001 | FR-020 |
| TC-DRUG-002 | FR-020 |
| TC-DRUG-003 | FR-021 |
| TC-DRUG-004 | FR-021 |
| TC-DRUG-005 | FR-021 |
| TC-DRUG-006 | FR-022 |
| TC-DRUG-007 | FR-022 |
| TC-DRUG-008 | FR-020 |
| TC-VIZ-001 | FR-040 |
| TC-VIZ-002 | FR-041 |
| TC-VIZ-003 | FR-042 |
| TC-VIZ-004 | FR-002 |
| TC-VIZ-005 | FR-040 |
| TC-HEATMAP-001 | FR-043 |
| TC-HEATMAP-002 | FR-043 |
| TC-HEATMAP-003 | FR-044 |
| TC-HEATMAP-004 | FR-045 |
| TC-HEATMAP-005 | FR-046 |
| TC-PDF-001 | FR-050 |
| TC-PDF-002 | FR-050 |
| TC-PDF-003 | FR-051 |
| TC-PDF-004 | FR-005, FR-051 |
| TC-PDF-005 | FR-052 |
| TC-PDF-006 | FR-053 |
| TC-PDF-007 | FR-050 |
| TC-ADMIN-001 | FR-064 |
| TC-ADMIN-002 | FR-061 |
| TC-ADMIN-003 | FR-062 |
| TC-ADMIN-004 | FR-062 |
| TC-ADMIN-005 | FR-005 |
| TC-ADMIN-006 | FR-060 |
| TC-ADMIN-007 | FR-005 |
| TC-ADMIN-008 | FR-062 |
| TC-ADMIN-009 | FR-063 |
| TC-SCRAPE-001 | FR-071 |
| TC-SCRAPE-002 | FR-070 |
| TC-SCRAPE-003 | FR-070 |
| TC-SCREEN-001 | FR-003 |
| TC-SCREEN-002 | FR-065 |
| TC-SCREEN-003 | FR-066 |
| TC-SCREEN-004 | FR-067 |
| TC-SCREEN-005 | FR-034 |
| TC-SCREEN-006 | NFR-USA-004 |

## 4. Cakupan

- Jumlah FR yang diuji: 33 dari 49 FR fungsional (yang sisanya FR-004, FR-008,
  FR-014, FR-033, FR-054 mengenai sisi frontend UI tertunda B-WAVE1-BUILD-1;
  FR-DB-003 di luar scope mode lokal).
- Jumlah test case: 88.
- Setiap test case Pass/Fail/Blocked terhubung ke minimal satu FR atau NFR.

## 5. Persetujuan

Disusun: Alia Ardani, NIM 251524035 (System Analyst).
Direview: Bimo Surya Anggara, NIM 251524040 (QA Lead).
Disetujui: Ghaisan Khoirul Badruzaman, NIM 251524048 (Project Leader).
