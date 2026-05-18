---
title: Production PRD MedWatch (Pasca-MVP Akademik)
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking PRD (belum diimplementasi)
related_docs:
  - docs/PRD.md (PRD akademik AS-BUILT)
  - ProductionGrade-ImplementationPlan/00-overview.md
  - ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md
  - ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md
  - ProductionGrade-ImplementationPlan/06-roadmap.md
---

# 01 - Production PRD MedWatch

PRD ini melanjutkan `docs/PRD.md` (PRD akademik AS-BUILT). Dokumen ini menjawab pertanyaan: "Apa yang harus ada di produk MedWatch agar bisa diserahkan kepada bidan Faskes 1 sebagai produk berbayar?" PRD akademik fokus pada submission tugas mata kuliah; PRD production fokus pada pengguna nyata di lapangan tanpa pendamping developer.

---

## 1. Ringkasan Eksekutif

MedWatch versi production adalah aplikasi desktop installable, offline-capable yang berjalan pada satu workstation Windows 10 atau Windows 11 di Faskes 1. Pengguna tunggal (bidan koordinator atau bidan pelaksana) menjalankan aplikasi langsung dari flashdisk atau installer lokal tanpa membutuhkan koneksi internet, akun cloud, atau integrasi dengan sistem lain. Distribusi dilakukan via media fisik oleh tim atau koordinator klinik yang bekerja sama dengan tim. Data pasien, snapshot openFDA, dan data master obat semuanya tersimpan lokal di mesin pengguna.

---

## 2. Latar Belakang dan Justifikasi

### 2.1 Mengapa offline-first dan bukan SaaS

Faskes 1 di Indonesia memiliki kondisi konektivitas yang tidak konsisten. Puskesmas pinggiran kota kabupaten sering menggunakan modem USB 4G dengan kuota harian yang dibatasi. Polindes yang berada di desa kerap tidak punya koneksi sama sekali. Bidan tidak boleh kehilangan akses ke rekam medis pasien hanya karena internet padam saat ada pasien yang masuk dengan keluhan urgent. Selain itu, klien Faskes 1 lazimnya tidak memiliki budget OPEX untuk biaya bulanan SaaS. Model lisensi sekali bayar dengan media fisik lebih cocok untuk struktur biaya mereka.

### 2.2 Apa yang sudah didapat dari MVP akademik

Per `docs/PRD.md` Section 1, MVP akademik sudah menyediakan:

- Modul CRUD pasien dengan format SOAP yang divalidasi (`api/routes/patient_routes.py:56` `_validate_medical_ranges`).
- Modul cek interaksi obat berdasarkan database lokal di `anggota4/data/drug_database.json` (8 obat) dan `anggota4/data/effect_database.json` (60 efek).
- Modul akuisisi data openFDA dengan 74 rekord adverse-event dan 6000 rekord recall (`anggota1/data/drug_safety_data.json`, `anggota1/data/drug_recalls.json`).
- Modul visualisasi (`anggota3/` + `anggota3/NewestVisualization/`).
- Modul ekspor PDF rekam medis (`anggota5/export_pdf.py`).
- Lapisan autentikasi tiga-role (admin, tenaga_kesehatan, masyarakat) di `api/auth.py` + `api/middleware.py`.

Production tinggal mengubah cara pengiriman, persistensi, dan packaging-nya; bukan menulis ulang fitur.

---

## 3. User Stories Production

Format: As a / I want / So that.

### 3.1 Story PROD-US-01 Instalasi tanpa pendamping

As a bidan koordinator Faskes 1 yang menerima flashdisk MedWatch dari dosen pendamping atau koordinator klinik,
I want untuk menyelesaikan instalasi dengan klik dua kali file `MedWatchSetup.exe` dan mengikuti wizard berbahasa Indonesia,
So that saya bisa mulai mencatat pasien dalam waktu kurang dari 5 menit tanpa menelepon siapapun.

Acceptance: wizard memvalidasi Windows version dan free disk minimum 500 MB, kemudian copy folder aplikasi dan membuat shortcut Desktop + Start Menu. Tidak ada pertanyaan teknis (port, environment variable, file config). Setelah instalasi, ikon MedWatch muncul di Desktop.

### 3.2 Story PROD-US-02 Login pertama kali

As a bidan yang baru pertama kali membuka MedWatch,
I want melihat dialog login yang menerima username dan password yang sudah dibuat oleh koordinator klinik sebelumnya,
So that hanya saya dan rekan yang berhak yang bisa membuka data pasien.

Acceptance: dialog login berbahasa Indonesia. Password salah menampilkan pesan generik "username atau password salah" (sesuai mitigasi A07 di `docs/SECURITY.md` Section 4 baris 165). Pesan tidak membedakan antara "username tidak ada" vs "password salah". Tidak ada demo credentials yang ditampilkan di production build (berbeda dengan demo akademik yang sengaja menampilkan).

### 3.3 Story PROD-US-03 Pencatatan SOAP offline

As a bidan saat menerima pasien Ny. Dewi yang datang dengan keluhan mual dan terlambat menstruasi,
I want mengisi form SOAP (S keluhan, O TD/BB/TB/LILA, A diagnosa G1P0A0, P tindakan istirahat + asam folat) dan menyimpannya tanpa khawatir internet padam,
So that catatan langsung tersimpan ke database lokal yang ada di mesin saya.

Acceptance: form mencakup field sesuai canonical schema di CLAUDE.md (id, tanggal_kunjungan DD-MM-YYYY, nama, umur, alamat, S keluhan/riwayat, O tekanan_darah/nadi/suhu_c/respirasi/bb_kg/tb_cm/lila_cm/catatan, A diagnosa, P tindakan/resep/jadwal_kontrol). Required: nama, S.keluhan, A.diagnosa, P.tindakan. O.nadi/suhu_c/respirasi commonly blank. Penyimpanan ke SQLite lokal (lihat `02-offline-implementation-plan.md` Section 4). Round-trip Save -> Read kurang dari 200 ms.

### 3.4 Story PROD-US-04 Safety check obat offline

As a bidan yang akan meresepkan paracetamol kepada Ny. Dewi yang sedang hamil 5 minggu,
I want mengetik nama "paracetamol" lalu menekan tombol Cek Keamanan untuk melihat skor risiko dan efek samping,
So that saya bisa cepat memutuskan apakah obat aman untuk pasien.

Acceptance: hasil ditampilkan dalam waktu kurang dari 500 ms. Output mencakup skor risiko 0-100 (skala dari `anggota4/safety_checker.py:14` BOBOT_KEPARAHAN), label "rendah/sedang/tinggi", daftar efek samping dengan tingkat keparahan, dan peringatan kehamilan. Data berasal dari database lokal hasil bundle openFDA snapshot (`02-offline-implementation-plan.md` Section 3) + `anggota4/data/`. Tidak ada HTTP request keluar.

### 3.5 Story PROD-US-05 Ekspor PDF rekam medis

As a bidan yang menerima permintaan rekap dari dosen pembimbing program Bidan Magang,
I want klik tombol "Ekspor PDF" pada record pasien Ny. Dewi dan menyimpan PDF ke folder yang saya tentukan,
So that saya bisa print atau email file tersebut.

Acceptance: PDF dihasilkan via fpdf2 (`anggota5/export_pdf.py` line 2) dengan font yang bisa render karakter Bahasa Indonesia (akan memerlukan tambahan font file Unicode-aware, lihat residual risk A03 di `docs/SECURITY.md` Section 4 baris 126). Output PDF mencakup header Faskes 1 (nama klinik yang dapat dikonfigurasi), data pasien, kunjungan terakhir, dan footer dengan tanggal cetak. Ukuran PDF kurang dari 100 KB.

### 3.6 Story PROD-US-06 Backup ke external drive

As a bidan koordinator yang ingin backup mingguan ke flashdisk cadangan,
I want klik menu "Backup" dan memilih folder tujuan di external drive,
So that data pasien aman jika hard drive workstation rusak.

Acceptance: tombol Backup mengekspor seluruh database SQLite ke folder pilihan dengan filename `medwatch-backup-YYYY-MM-DD.db`. Restore via menu "Restore" + pemilihan file backup. Tidak ada kompresi (file SQLite bisa langsung dibuka oleh DB Browser for SQLite jika diperlukan investigasi).

### 3.7 Story PROD-US-07 Update aplikasi via flashdisk baru

As a klien yang menerima media baru dari tim MedWatch untuk versi 1.1,
I want jalankan installer baru yang otomatis mendeteksi instalasi sebelumnya dan upgrade tanpa kehilangan data pasien,
So that saya tidak perlu re-entry data setelah update.

Acceptance: installer melakukan migrasi schema SQLite (Alembic-style version table) jika diperlukan. Data pasien existing tetap utuh setelah upgrade. User Manual mencatat versi yang sedang dipakai di menu Help -> About.

### 3.8 Story PROD-US-08 Support model

As a klien yang menemukan bug atau punya pertanyaan teknis,
I want klik menu Help -> Hubungi Tim yang membuka template email berbahasa Indonesia ke alamat support resmi,
So that saya bisa minta bantuan tanpa harus mencari kontak via WhatsApp.

Acceptance: menu Help membuka mailto link dengan subject "MedWatch Support [versi X.Y.Z]" dan body yang prepopulated dengan diagnostik dasar (OS version, app version, last error from crash.log). Tidak ada data pasien yang ikut terkirim.

---

## 4. Fitur Tambahan di Atas MVP Akademik

### 4.1 Installer

Installer adalah fitur baru. MVP akademik dijalankan via `python main.py` oleh developer. Production menyediakan `.exe` installer yang dapat dijalankan oleh non-developer. Detail teknis ada di `03-packaging-and-distribution.md`.

### 4.2 Auto-update strategy

Karena offline-first, auto-update tidak melakukan HTTP polling. Strategi: ketika klien menerima flashdisk baru untuk versi minor, installer baru mendeteksi versi lama via Windows Registry key `HKLM\SOFTWARE\MedWatch\Version` (akan dibuat saat instalasi pertama). Jika versi baru lebih tinggi, prompt user untuk in-place upgrade. Tidak ada call ke server eksternal.

### 4.3 Lisensi dan aktivasi

MVP akademik tidak punya lisensi (gratis untuk demo). Production mendukung dua skema:

- Skema 1 (paling sederhana, MVP production): tidak ada aktivasi. Cukup pembayaran sekali di muka untuk media + setup. Tim percaya pada perjanjian B2B dengan klien institusional.
- Skema 2 (jika dibutuhkan kemudian): file lisensi `license.dat` yang berisi nama klien, tanggal kadaluwarsa, dan signature ECDSA. Aplikasi memeriksa file ini saat startup. Jika tidak valid atau kadaluwarsa, aplikasi tetap berjalan dalam read-only mode (data tetap bisa dilihat dan diekspor, tetapi CRUD baru di-block). Implementasi schema 2 ditunda sampai ada permintaan klien.

### 4.4 Support model

Tim menyediakan saluran kontak resmi yang dipilih dari salah satu opsi berikut (keputusan final saat Phase 5 di `06-roadmap.md`):

- Email tim (alamat akan dibuat khusus, bukan email personal).
- WhatsApp Business dengan auto-reply jam kerja.
- Form Google Forms minimal dengan kolom OS, versi, deskripsi.

Tim berkomitmen merespons dalam waktu 3 hari kerja untuk bug Critical/Major; 7 hari kerja untuk pertanyaan umum. SLA ini didokumentasikan di User Manual.

### 4.5 Optional backup to external drive

Lihat Story PROD-US-06. Fitur ini sederhana karena database berbentuk file SQLite tunggal. Cukup `shutil.copy2` dari `%APPDATA%\MedWatch\medwatch.db` ke path pilihan user.

---

## 5. Out-of-Scope (Production v1.0)

Item-item ini ditolak agar fokus versi 1.0 tetap pada offline-first single-Faskes. Lihat juga `00-overview.md` Section 4.

| Item | Alasan eksklusi |
|---|---|
| Cloud sync antar-mesin | Bertentangan dengan offline-first; ditunda sampai ada permintaan klaster |
| Auto-update via internet | Bertentangan dengan offline-first |
| Multi-user concurrent pada satu DB | SQLite mendukung tetapi UX-nya buruk untuk 1 mesin tunggal; cukup 1 user aktif pada satu waktu |
| Mobile app | Bidan menggunakan PC desktop |
| Integrasi BPJS / SIMRS | Membutuhkan MoU institusional |
| Multibahasa selain Bahasa Indonesia | Pasar target Indonesia |
| Custom branding per klien | Versi 1.0 menggunakan brand MedWatch standar; custom branding bisa di-quote sebagai service tambahan |
| Audit log durable di luar mesin | Stdout logging cukup; log file lokal dapat diekspor manual |

---

## 6. Success Metrics

Metrik berikut dipantau pasca-rilis 1.0 (target Oktober 2026 per `06-roadmap.md` Phase 5).

### 6.1 Metrik instalasi

- Time-to-install pada workstation bersih: kurang dari 5 menit.
- Success rate instalasi pada 3 mesin Windows berbeda: 100% (3 dari 3).
- Total ukuran distribusi: kurang dari 300 MB.

### 6.2 Metrik runtime

- Cold start (klik ikon sampai layar login muncul): kurang dari 3 detik pada mesin spec minimum (Intel Core i3 gen 10, RAM 8 GB, SSD 256 GB).
- Hot start (relogin tanpa restart aplikasi): kurang dari 1 detik.
- Round-trip simpan pasien (klik Simpan sampai konfirmasi sukses muncul): kurang dari 200 ms.
- Safety check obat: kurang dari 500 ms untuk skenario tipikal.
- Ekspor PDF satu pasien: kurang dari 2 detik.

### 6.3 Metrik fungsional

- CRUD pasien: berfungsi penuh offline. Test dengan kabel jaringan dicabut.
- Safety check obat: berfungsi penuh offline. Test dengan kabel jaringan dicabut.
- Visualisasi: berfungsi penuh offline (data dari local SQLite).
- Ekspor PDF: berfungsi penuh offline.
- Menu "Refresh openFDA": gracefully menampilkan pesan "Membutuhkan koneksi internet" jika kabel dicabut.

### 6.4 Metrik UAT

- Bidan UAT dapat menyelesaikan minimal 8 dari 10 task user (lihat `05-test-and-acceptance-plan.md` Section 3.2) tanpa bantuan developer.
- Survei kepuasan UAT (skala 1-5) menghasilkan rata-rata minimal 4.0.

---

## 7. Asumsi dan Dependency Eksternal

### 7.1 Asumsi

1. Workstation klien minimal Windows 10 64-bit dengan RAM 8 GB. Windows 7/8 tidak didukung.
2. Klien menerima media fisik (flashdisk USB 2.0 atau lebih cepat). Tidak ada distribusi via download internet pada launch.
3. Snapshot openFDA yang di-bundle valid untuk minimal 6 bulan ke depan dari tanggal build (data adverse-event tidak berubah cepat).
4. Klien tidak mengaktifkan antivirus berlebih yang mem-block PyInstaller-built `.exe`. Jika terjadi, dokumentasi User Manual menyediakan langkah whitelist.

### 7.2 Dependency eksternal

- openFDA: digunakan saat build-time (developer membuat snapshot). Lihat `02-offline-implementation-plan.md` Section 3.
- BPOM monograph: digunakan sebagai referensi konten User Manual (bukan sebagai fitur runtime).
- Tidak ada dependency eksternal runtime; mendukung offline-first.

---

## 8. Open Questions

Pertanyaan-pertanyaan berikut akan dijawab pada saat pelaksanaan roadmap. Saat ini dicatat sebagai TBD agar tidak menjadi blocker dokumen Wave 2.

1. Apakah klien membutuhkan kemampuan ekspor data pasien ke Excel (XLSX)? Akan ditanyakan di UAT.
2. Apakah ada batas atas jumlah pasien per file SQLite yang masuk akal (10k, 100k)? Production-grade target awal: 10k pasien per Faskes (5 tahun operasi dengan 5 pasien/hari).
3. Skema lisensi mana yang akan dipakai (Section 4.3 Skema 1 atau Skema 2)? Akan diputuskan saat ada klien pertama yang membayar.
4. Workstation Faskes 1 menggunakan akun Windows lokal atau domain? Akan dikonfirmasi saat survey calon klien.

---

## 9. Approvals

- Direktur produk: Ghaisan Khoirul Badruzaman (sebagai Project Leader Kelompok B5, akan menjadi de-facto PM produk).
- QA: Bimo Surya Anggara (sebagai QA Kelompok B5).
- Security reviewer: berdasarkan `docs/SECURITY.md` Section 7 residual risk register.
- Dokumen ini di-revisit setelah submission akademik 25 Mei 2026 untuk konfirmasi tim tetap berniat melanjutkan ke production-grade.
