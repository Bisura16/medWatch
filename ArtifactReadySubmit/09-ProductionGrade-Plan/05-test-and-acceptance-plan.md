---
title: Test and Acceptance Plan MedWatch Production
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking plan (belum diimplementasi)
related_docs:
  - ProductionGrade-ImplementationPlan/00-overview.md
  - ProductionGrade-ImplementationPlan/01-production-PRD.md
  - ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md
  - ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md
  - ProductionGrade-ImplementationPlan/04-hardening-plan.md
  - ProductionGrade-ImplementationPlan/06-roadmap.md
  - docs/SRS.md
  - docs/USER-MANUAL.md
---

# 05 - Test and Acceptance Plan MedWatch Production

Dokumen ini menjabarkan tes regresi pra-rilis, tes UAT bersama bidan Faskes 1, dan kriteria sign-off "production-ready" untuk MedWatch versi 1.0. Dokumen ini menjadi referensi formal antara tim pengembang (Kelompok B5) dan stakeholder (dosen pembimbing, calon klien). Eksekusi tes dijadwalkan di Phase 4 di `06-roadmap.md` (September 2026).

---

## 1. Filosofi Pengujian Production

### 1.1 Beda dengan tes akademik

Tes akademik (Wave 1 + Wave 2 W2-D14 di mission constitution) memvalidasi bahwa modul `anggota1`..`anggota5` masing-masing berfungsi dan integrasi lewat `api/` mengembalikan response yang benar. Black-box test plan akademik mencakup TC-MOD-NNN dengan teknik Equivalence Partitioning, Boundary Value Analysis, dan State Transition.

Tes production menambah dua dimensi:

1. **Tes lingkungan asing.** Aplikasi harus bekerja di mesin di luar laptop developer.
2. **Tes pengguna asing.** Aplikasi harus dipakai oleh bidan yang belum pernah melihat source code.

### 1.2 Dua kategori utama

- **Regression test suite**: tes otomatis yang harus PASS sebelum membuat installer release. Bertujuan memastikan refactor tidak merusak fungsionalitas.
- **UAT (User Acceptance Test)**: tes manual oleh bidan, bertujuan memvalidasi bahwa software cocok untuk operasional sehari-hari.

---

## 2. Regression Suite

### 2.1 Skenario yang harus PASS

Diturunkan dari user stories di `01-production-PRD.md` Section 3 dan dari functional requirements di `docs/SRS.md`.

| ID | Skenario | Bukti yang dibutuhkan |
|---|---|---|
| REG-01 | Login admin berhasil dengan kredensial valid | HTTP 200 + cookie `medwatch_token` ter-set |
| REG-02 | Login dengan password salah mengembalikan generic error | HTTP 401 + body `"username atau password salah"` |
| REG-03 | Login dengan password salah 5x dalam 15 menit memicu rate limit (H1) | HTTP 429 setelah attempt ke-6 |
| REG-04 | CRUD pasien (Create/Read/Update/Delete) berfungsi penuh | Round-trip Save < 200 ms, Read < 100 ms |
| REG-05 | Patient list ter-sort newest first (B07 fix) | Item pertama memiliki `tanggal_kunjungan` paling baru |
| REG-06 | Validasi numeric pada field medical menolak input alfabetik (B03 fix) | HTTP 400 saat POST `umur="dua puluh"` |
| REG-07 | Patient masyarakat tidak bisa akses record orang lain (A01 RBAC) | HTTP 403 saat masyarakat GET `/api/patients/<other_owner_id>` |
| REG-08 | Safety check obat "paracetamol" mengembalikan skor + label | Response time < 500 ms, body memuat `skor_risiko` 0-100 dan `label_risiko` |
| REG-09 | Cek interaksi obat menampilkan obat aktif pasien (B05 fix) | Field `pasien_active_meds` ada di response saat `pasien_id` di-supply |
| REG-10 | Ekspor PDF rekam medis menghasilkan file valid (B04 fix) | File `.pdf` ter-buat, dapat dibuka di Adobe Reader |
| REG-11 | Visualisasi dashboard menampilkan KPI dari data real, bukan hardcoded (B10 fix) | Angka di KPI sama dengan COUNT query SQLite |
| REG-12 | Heatmap menggunakan continuous color scale, bukan binary (B11 fix) | PNG output memuat minimal 4 gradasi warna |
| REG-13 | Logout menghapus cookie | Set-Cookie `medwatch_token=; Max-Age=0` di response |
| REG-14 | Aplikasi tetap berjalan saat kabel jaringan dicabut | Semua REG-01..REG-13 PASS dalam mode offline |
| REG-15 | Cold start aplikasi < 3 detik | Stopwatch klik ikon -> dialog login muncul |
| REG-16 | Total install size < 300 MB | `du -sh dist/MedWatch/` < 300 MB |
| REG-17 | Tidak ada credential value di binary | `strings MedWatch.exe | grep -E '(JWT_SECRET=|password=|api_key=)[^<]' ` empty |
| REG-18 | Tidak ada HTTP request keluar di runtime non-admin | Test: socket.create_connection monkeypatch raises; aplikasi tetap responsif |
| REG-19 | Backup ke external drive berhasil | File `medwatch-backup-YYYY-MM-DD.db` ter-buat di target |
| REG-20 | Restore dari backup mengembalikan data | Setelah restore, pasien jumlahnya sama dengan sebelum backup |

### 2.2 Skenario hardening (dari `04-hardening-plan.md`)

| ID | Hardening Item | Skenario |
|---|---|---|
| REG-H1 | H1 rate limit | Sudah di REG-03 |
| REG-H2 | H2 structured logs | Audit log JSON ada di `<appdata>/logs/audit.log` setelah 10 user actions |
| REG-H3 | H3 CSRF token | POST tanpa header `X-CSRF-Token` di-block 403 |
| REG-H4 | H4 JWT rotation | Setelah rotasi, token lama tetap valid dalam 24h, lalu invalid |
| REG-H5 | H5 CI dependency scan | GitHub Actions workflow run di PR baru |
| REG-H6 | H6 atomic JSON write atau SQLite | Test kill -9 saat save: data tetap konsisten |
| REG-H7 | H7 Cloud Run IAM (N/A jika cloud demo decommissioned) | Skip atau verify IAM binding |
| REG-H8 | H8 archived dep cleanup | `npm audit --omit=dev --audit-level=high` returns 0 |

### 2.3 Eksekusi regression

- Setiap PR yang menyentuh `api/` atau `anggota*` mem-trigger CI yang menjalankan REG-01..REG-20 + REG-H1..REG-H8 yang relevan.
- Suite menggunakan pytest dengan fixture untuk SQLite in-memory + Flask test client.
- Estimasi runtime suite: kurang dari 5 menit total.

### 2.4 Tooling

- pytest (sudah ada di `api/tests/`).
- requests untuk HTTP integration test pada local Flask.
- subprocess untuk smoke test bundle PyInstaller (test "REG-15 cold start").
- pdfminer.six atau PyPDF2 untuk validasi PDF output (REG-10).

### 2.5 Smoke test bundle pre-distribusi

Sebelum membuat installer release, jalankan smoke test pada bundle hasil PyInstaller dari `03-packaging-and-distribution.md` Section 5. Checklist tersebut menjadi gate sebelum installer di-copy ke flashdisk distribusi.

---

## 3. UAT dengan Bidan Faskes 1

### 3.1 Recruit Bidan UAT

Tim mencari 1 bidan dari Faskes 1 yang bersedia melakukan UAT. Kriteria:

- Bidan praktek minimal 2 tahun di Faskes 1 (puskesmas, polindes, klinik bersalin).
- Familiar dengan PC desktop (Windows). Tidak perlu familiar dengan istilah teknis (port, environment variable, dsb).
- Bersedia meluangkan minimal 4 jam dalam 1 hari kerja untuk sesi UAT.
- Lokasi: Bandung atau Jawa Barat. Diutamakan yang dapat dikunjungi langsung oleh tim.

Kontak via koordinator dosen pendamping (Aprianti Nanda Sari) atau via jaringan alumni POLBAN yang sudah bekerja di Faskes 1. Recruitment dijadwalkan paling lambat 2 minggu sebelum Phase 4 di `06-roadmap.md`.

Konsensual: bidan menerima pendaftaran tertulis, di-brief bahwa software masih versi alpha, dan menyatakan setuju memberikan feedback. Tim memberikan kompensasi waktu (sesuai praktik etis penelitian; nominal disepakati di Phase 4).

### 3.2 UAT Task List (10 task)

Bidan diminta menyelesaikan 10 task berikut tanpa bantuan developer, hanya berbekal User Manual yang sudah dicetak.

| ID | Task | Acceptance |
|---|---|---|
| UAT-T01 | Install MedWatch dari flashdisk yang sudah dijalankan oleh asisten lab | Aplikasi tampil di Desktop dalam < 5 menit |
| UAT-T02 | Login dengan akun yang sudah disiapkan asisten (username + password ditulis di kertas) | Berhasil masuk ke dashboard |
| UAT-T03 | Tambahkan pasien baru: Ny. Dewi, 25 tahun, alamat Kp. Selang Cau, keluhan mual + telat mens, diagnosa G1P0A0 hamil 5 minggu | Pasien terlihat di daftar |
| UAT-T04 | Lihat detail pasien Ny. Dewi yang baru ditambahkan | Layar detail muncul, isi sama dengan input |
| UAT-T05 | Edit pasien Ny. Dewi: tambahkan kunjungan kedua minggu depan dengan tindakan kontrol kehamilan | Perubahan tersimpan |
| UAT-T06 | Cek keamanan obat paracetamol | Skor risiko + label rendah/sedang/tinggi muncul |
| UAT-T07 | Cek interaksi 2 obat: paracetamol dan ibuprofen | Daftar efek samping overlapping muncul |
| UAT-T08 | Ekspor rekam medis Ny. Dewi ke PDF, simpan di Desktop | File `.pdf` tersimpan dan dapat dibuka |
| UAT-T09 | Lihat menu visualisasi dashboard, sebutkan grafik mana yang menampilkan tren kunjungan | Bidan dapat menunjuk grafik yang benar |
| UAT-T10 | Backup database ke flashdisk yang baru | File backup `.db` tersimpan di flashdisk |

### 3.3 Metrik UAT

- **Completion rate**: berapa task dari 10 yang selesai dengan benar tanpa bantuan. Target: minimal 8.
- **Time per task**: rata-rata waktu per task. Target: tidak ada task yang melebihi 10 menit.
- **Error count**: jumlah kesalahan klik atau input yang dikoreksi sendiri oleh user. Target: rata-rata < 2 per task.
- **Survey kepuasan**: 5 pertanyaan skala 1-5 di akhir sesi:
  1. Apakah aplikasi mudah digunakan?
  2. Apakah tampilan jelas dan tidak membingungkan?
  3. Apakah respon aplikasi cepat?
  4. Apakah bahasa yang dipakai mudah dipahami?
  5. Apakah Anda mau menggunakan aplikasi ini di praktek harian?
  
  Target: rata-rata minimal 4.0.

### 3.4 Catatan UAT

Tim mendokumentasikan setiap sesi dalam format:

```
UAT Session Report - YYYY-MM-DD
Bidan: <inisial nama untuk privasi>
Faskes: <nama Faskes>
Waktu: <total menit>

Task UAT-T01: <PASS|PARTIAL|FAIL> - <catatan singkat>
Task UAT-T02: ...
...

Observasi qualitatif:
- <hal yang membingungkan bidan>
- <istilah yang tidak familiar>
- <fitur yang dicari tapi tidak ada>

Survei kepuasan: <skor>
Tindak lanjut: <prioritas perbaikan>
```

Dokumen disimpan di `docs/uat/YYYY-MM-DD-uat-<initial>.md` (tanpa nama lengkap untuk privasi).

---

## 4. Kriteria Sign-Off Production-Ready

Software MedWatch siap dirilis sebagai versi 1.0 production jika dan hanya jika SEMUA kriteria berikut terpenuhi.

### 4.1 Kriteria Functional

- [ ] Regression suite REG-01..REG-20 PASS 20/20.
- [ ] Hardening suite REG-H1..REG-H8 PASS (kecuali REG-H7 jika cloud demo decommissioned).
- [ ] Manual smoke test pada 3 mesin Windows berbeda PASS 3/3 (lihat `03-packaging-and-distribution.md` Section 5).

### 4.2 Kriteria Non-Functional

- [ ] Cold start < 3 detik pada minimum spec machine.
- [ ] Round-trip simpan pasien < 200 ms.
- [ ] Safety check obat < 500 ms.
- [ ] PDF export < 2 detik.
- [ ] Total install size < 300 MB.
- [ ] Tidak ada credential value di binary (verifikasi grep).
- [ ] Tidak ada HTTP request runtime pada path non-admin.

### 4.3 Kriteria Security

- [ ] OWASP Top 10:2021 posture: 10/10 PASS (target `04-hardening-plan.md` Section 12).
- [ ] Residual risk R1-R8 di `docs/SECURITY.md` Section 7 mitigated atau N/A.
- [ ] CI dependency scan workflow aktif dan menjalankan pip-audit + npm audit weekly.
- [ ] Tidak ada credential value di repo (verifikasi secret-scan hook).

### 4.4 Kriteria UAT

- [ ] Minimal 1 bidan UAT selesai.
- [ ] Completion rate minimal 80% (8 dari 10 task).
- [ ] Survey kepuasan rata-rata minimal 4.0.
- [ ] Zero bug Critical dicatat saat UAT.
- [ ] Maksimal 2 bug Minor dicatat saat UAT.

### 4.5 Kriteria Reproducibility

- [ ] Build PyInstaller dari source `v1.0.0` di 2 mesin developer berbeda menghasilkan hash SHA-256 yang konsisten.
- [ ] Installer Inno Setup di 2 build berbeda menghasilkan ukuran sama (toleransi 1 KB).

### 4.6 Kriteria Dokumentasi

- [ ] `docs/USER-MANUAL.md` selesai dan mencakup semua fitur production v1.0.
- [ ] User Manual PDF di-include di flashdisk distribusi.
- [ ] `docs/INSTALL.md` ter-update untuk reflect installer flow (bukan hanya developer dev flow).
- [ ] `CHANGELOG.md` memuat entry v1.0.0.

### 4.7 Kriteria Distribusi

- [ ] Minimal 1 flashdisk distribusi (PRIMARY) ditest pada 3 mesin Windows berbeda.
- [ ] Backup flashdisk ke-2 disiapkan.
- [ ] SHA-256 hash setiap installer didokumentasikan di User Manual.
- [ ] SOP penyerahan ke koordinator klinik ditulis dan ditandatangani PIC.

---

## 5. Defect Severity Definition

### 5.1 Critical

Defect yang menyebabkan loss of data, security breach, atau aplikasi tidak bisa launch.

Contoh:

- Crash saat startup pada mesin Windows 10 64-bit.
- Login dengan password salah memberikan akses (auth bypass).
- Save pasien meng-overwrite pasien lain.

Aksi: BLOCK release. Tim wajib fix sebelum rilis.

### 5.2 Major

Defect yang mempengaruhi fitur utama tetapi ada workaround.

Contoh:

- Ekspor PDF gagal pada nama pasien yang mengandung karakter spesial.
- Safety check obat lambat (>2 detik) saat ada >50 obat di database.

Aksi: dikerjakan sebelum release, kecuali workaround sudah didokumentasikan di User Manual.

### 5.3 Minor

Defect yang mempengaruhi UX tetapi tidak meng-block tugas.

Contoh:

- Label tombol tidak konsisten (misal "Simpan" vs "Save").
- Margin layout PDF sedikit miring.

Aksi: maksimal 2 di-tolerate untuk versi 1.0. Sisanya ditunda ke versi 1.1.

### 5.4 Cosmetic

Issue visual murni tanpa dampak fungsional.

Contoh:

- Warna tombol sedikit beda dengan mockup.
- Typo di label menu (huruf besar/kecil).

Aksi: tidak block release. Fix di versi 1.1 atau lebih.

---

## 6. Rollback Plan

Jika setelah rilis (versi 1.0 di flashdisk klien) ditemukan Critical bug, tim:

1. Stop distribusi flashdisk baru sampai patch tersedia.
2. Komunikasikan ke klien yang sudah menerima v1.0 untuk hold instalasi atau lanjut dengan limitation (dijelaskan).
3. Develop hotfix di branch `release/1.0.x`, build versi 1.0.1.
4. Distribusi v1.0.1 via flashdisk baru atau email zip ke klien yang sudah ter-install v1.0.
5. Migrasi data v1.0 -> v1.0.1: pada implementasi schema-compatible v1.0.x, data SQLite tidak berubah; cukup replace folder install.

Rollback ke versi sebelum 1.0.0 tidak applicable (1.0.0 adalah versi production pertama).

---

## 7. Test Environment

### 7.1 Build environment

- macOS Sonoma 14.x atau newer (laptop Ghaisan).
- Python 3.13 venv per `api/requirements.txt`.
- PyInstaller 6.x.
- Untuk Windows installer: Windows 11 VM via Parallels/UTM, Inno Setup 6.x.

### 7.2 Test mesin

- Mesin Windows bersih disiapkan via VM atau borrow workstation kampus. Minimum 3 mesin berbeda untuk smoke test:
  - Windows 10 22H2 home, 8 GB RAM
  - Windows 11 23H2 home, 16 GB RAM
  - Windows 11 pro, 32 GB RAM (kelas enterprise dengan Defender lebih agresif)

### 7.3 Data testing

- Synthetic patient data: 100 pasien generate via script `tools/seed_patients.py`. Data tidak boleh nama asli orang nyata (privacy).
- openFDA snapshot hasil build-time terbaru.
- Drug master `anggota4/data/drug_database.json` apa adanya (sudah cukup untuk test).

---

## 8. Sign-Off

Sign-off untuk release v1.0:

- Project Leader (Ghaisan Khoirul Badruzaman, NIM 251524048): functional + non-functional + reproducibility.
- QA (Bimo Surya Anggara, NIM 251524040): regression suite + UAT.
- System Analyst (Alia Ardani, NIM 251524035): traceability terhadap SRS + UAT survey analysis.
- Programmer (Muhammad Iqbal, NIM 251524057): security hardening verification.
- UI/UX (Abhidal Muhammad Gazza, NIM 251524032): user-facing copy + UAT support.

Sign-off form ditulis di `docs/release/v1.0.0-signoff.md` saat Phase 5.

---

## 9. Tanggal dan Pemilik

- Tanggal dokumen: 18 Mei 2026.
- Pemilik: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Status: forward-looking plan. Eksekusi dijadwalkan di Phase 4 (September 2026) per `06-roadmap.md`.
