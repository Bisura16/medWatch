---
title: ProductionGrade Overview - Definisi Production-Grade MedWatch
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking plan (not yet implemented)
audience: Tim Kelompok B5, dosen pendamping, calon klien Faskes 1, kontributor pasca-akademik
related_docs:
  - docs/PRD.md
  - docs/SRS.md
  - docs/SECURITY.md
  - ProductionGrade-ImplementationPlan/01-production-PRD.md
  - ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md
  - ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md
  - ProductionGrade-ImplementationPlan/04-hardening-plan.md
  - ProductionGrade-ImplementationPlan/05-test-and-acceptance-plan.md
  - ProductionGrade-ImplementationPlan/06-roadmap.md
---

# 00 - Overview ProductionGrade MedWatch

Dokumen ini adalah pembuka folder `ProductionGrade-ImplementationPlan/`. Folder ini berisi rencana forward-looking untuk memindahkan MedWatch dari status MVP akademik (siap diserahkan kepada dosen pada 25 Mei 2026) menuju distribusi production-grade yang dapat diserahkan kepada klien Faskes 1 yang membayar pada akhir 2026. Folder ini sengaja bersifat plan, bukan implementation. Tidak ada satu baris kode produksi pun yang ditulis dalam Wave 2; setiap penulisan, packaging, dan hardening akan dieksekusi pada wave sesudah submission akademik.

---

## 1. Mengapa folder ini ada

### 1.1 Konteks akademik vs konteks production

MedWatch lahir sebagai proyek mata kuliah Proyek 1 Pengembangan Perangkat Lunak Desktop di D4 Teknik Informatika POLBAN. Sasaran akademiknya jelas: lima modul `anggota1/`..`anggota5/` yang terintegrasi melalui lapisan `api/`, demo web showcase di Vercel + Cloud Run, dokumentasi lengkap, dan defek B01-B11 yang sudah ditutup di Wave 1. Sasaran ini sudah tercapai per `docs/PRD.md` bagian "Ringkasan Eksekutif" (74 rekord obat dan 6000 rekord recall openFDA, modul `anggota3/NewestVisualization/`, perbaikan defek B01-B11).

Namun dosen pembimbing (Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana) memberi instruksi tambahan: skemakan langkah-langkah produksi yang dibutuhkan jika hasil kerja kelompok ingin diserahkan kepada klien Faskes 1 nyata sebagai produk berbayar (bukan demo akademik). Folder ini adalah jawaban formal terhadap instruksi tersebut.

### 1.2 Posisi terhadap mission constitution

Wave 2 dari `.mission/plan.md` menyebutkan ticket W2-PROD dengan ruang lingkup tujuh file di folder ini. Wave 2 sengaja berhenti pada level perencanaan agar tidak menggeser perhatian dari deliverable submission akademik (PRD, SRS, SDD, ADR, diagram, As-Built, User Manual). Implementasi produksi nyata adalah pekerjaan pasca-25-Mei-2026 yang dijabarkan timeline-nya di `06-roadmap.md`.

---

## 2. Definisi "Production-Grade" untuk MedWatch

MedWatch production-grade dirumuskan sebagai konjungsi dari empat sifat berikut. Sifat-sifat ini tidak mengorbankan bentuk MVP akademik; ia menambahkan disiplin produksi di atasnya.

### 2.1 Sifat 1: Installable

Produk dapat dipasang pada workstation Windows 10 atau Windows 11 milik Faskes 1 tanpa intervensi developer. Bidan menerima media (flashdisk atau installer) dari koordinator klinik, menjalankan installer dengan klik dua kali, dan menyelesaikan instalasi dalam waktu kurang dari 5 menit pada PC kelas kantor (Intel Core i3 generasi terbaru, RAM 8 GB, storage 256 GB SSD). Tidak ada langkah `pip install`, `npm install`, atau editing `.env` secara manual.

Bukti yang dibutuhkan untuk lulus sifat ini:

- Folder hasil PyInstaller satu kali jalan tanpa error pada workstation bersih (di luar laptop developer).
- Installer Inno Setup (Windows) atau dmgbuild (macOS) atau AppImage (Linux) yang memvalidasi prasyarat (Windows version, free disk space) sebelum mulai.
- Uninstaller bersih: setelah uninstall, tidak ada residu di `Program Files/`, `AppData/`, atau Windows Registry.

### 2.2 Sifat 2: Distributable

Produk dapat diserahkan melalui media fisik (flashdisk) atau saluran terbatas (USB drive, email zip dengan ukuran wajar). Tidak diperlukan koneksi internet untuk instalasi maupun runtime. Total ukuran distribusi target kurang dari 300 MB (termasuk runtime Python, snapshot openFDA, dan dependency CustomTkinter / fpdf2 / matplotlib).

Bukti yang dibutuhkan:

- Folder distribusi `MedWatch/` berisi `MedWatch.exe`, `data/`, `README.txt`, `uninstall.bat` (Windows). Ukuran total dapat ditampilkan via `Get-ChildItem | Measure-Object -Property Length -Sum`.
- File hash SHA-256 untuk setiap binary disediakan agar klien dapat memvalidasi integritas.
- Manifest distribusi (lihat `03-packaging-and-distribution.md` Section 4) mencantumkan setiap file beserta peran dan lisensinya.

### 2.3 Sifat 3: Offline-capable

Workstation Faskes 1 sering kali tidak memiliki koneksi internet yang stabil; banyak puskesmas di pinggiran masih memakai modem USB sporadis atau bahkan tidak tersambung sama sekali. MedWatch production harus berfungsi penuh secara offline. Akuisisi data openFDA dilakukan saat developer membangun installer (build-time), bukan saat user menjalankan aplikasi (runtime). Snapshot openFDA di-bundle ke dalam installer.

Bukti yang dibutuhkan:

- Test instalasi pada workstation bersih dengan kabel jaringan dicabut: aplikasi tetap launch, semua menu (CRUD pasien, safety check, visualisasi, ekspor PDF) bekerja, hanya menu admin "Refresh openFDA" yang menampilkan pesan "Membutuhkan koneksi internet" (graceful).
- Tidak ada `requests.get`, `urllib`, atau `socket` call yang dijalankan pada path runtime non-admin. Audit grep menjadi bagian acceptance.

### 2.4 Sifat 4: Zero developer assistance

Begitu klien menerima media instalasi, mereka tidak perlu menghubungi developer untuk hal-hal rutin: instalasi, login pertama kali, backup database, recovery dari crash, upgrade ke versi minor. Dokumentasi User Manual (`docs/USER-MANUAL.md`, Wave 2 W2-D09) cukup untuk operasi sehari-hari.

Bukti yang dibutuhkan:

- UAT (User Acceptance Test) di `05-test-and-acceptance-plan.md` Section 3 selesai oleh bidan Faskes 1 yang belum pernah membuka source code, hanya dengan modal User Manual dan media installer.
- Pesan error berbahasa Indonesia tanpa stack trace teknis.
- File `crash.log` yang dapat dikirim balik ke developer via email biasa untuk investigasi tanpa membuka shell.

---

## 3. Hubungan Production-Grade dengan B01-B11

Defek register B01-B11 (`/.mission/bugs.md`) sudah ditutup pada Wave 1 dan menjadi prasyarat MVP akademik, bukan tujuan tambahan. Production-grade tidak meniadakan tutup-defek; ia menambahkan layer di atas software yang sudah lulus B01-B11. Tabel berikut menegaskan hubungan tersebut.

| Defek | Status Wave 1 | Status Production-Grade |
|---|---|---|
| B01 admin scraper navigation | Closed di Wave 1 | Diperluas: scraper menjadi build-time, bukan runtime klien |
| B02 "Lihat semua" inert | Closed di Wave 1 | Tetap berfungsi pada bundel CustomTkinter offline |
| B03 patient form numeric validation | Closed di Wave 1 | Diperketat: validation pada Pydantic/marshmallow schema (lihat `04-hardening-plan.md` Section 3) |
| B04 PDF export selain SOAP | Closed di Wave 1 | Production menambah PDF rekap kunjungan bulanan |
| B05 cek interaksi obat tanpa active meds | Closed di Wave 1 | Tidak berubah; sudah aman |
| B06 admin scraper link + pengguna aktif | Closed di Wave 1 | Tidak berubah; angka berasal dari storage lokal |
| B07 patient list sort newest | Closed di Wave 1 | Tidak berubah; SQLite akan mempertahankan kolom indeks DESC |
| B08 safety checker inline explanation | Closed di Wave 1 | Tidak berubah |
| B09 manual login tidak bisa | Closed di Wave 1 | Production tetap menampilkan demo credentials hanya pada mode dev, tidak pada build production |
| B10 admin dashboard KPI hardcoded | Closed di Wave 1 | KPI dihitung dari SQLite local |
| B11 heatmap bukan heatmap | Closed di Wave 1 | Tidak berubah |

---

## 4. Non-Goals Production-Grade

Folder ini secara eksplisit TIDAK mencakup item berikut. Item-item di bawah adalah skenario yang sering muncul saat membahas "bagaimana cara membuat MedWatch lebih besar"; tim sengaja membatasi cakupan agar tidak overscope:

| Non-goal | Alasan ditolak | Kapan dapat dipertimbangkan kembali |
|---|---|---|
| Cloud hosting permanen (Cloud Run untuk klien) | Klien Faskes 1 tidak punya budget operasional; offline-first lebih cocok | Setelah dapat 5 klien yang bersedia bayar OPEX bulanan |
| Multi-Faskes synchronization | Setiap Faskes berdiri sendiri; sinkronisasi membutuhkan PIC IT yang tidak ada di Faskes 1 | Jika ada perjanjian klaster pemerintah dengan minimal 3 Faskes |
| Mobile app (Android/iOS) | Bidan menggunakan PC desktop; ponsel tidak cocok untuk SOAP entry panjang | Setelah versi 1.0 desktop stabil dan ada permintaan tertulis dari pengguna |
| Custom domain berbayar | Versi production berjalan lokal; tidak ada URL publik yang dibutuhkan | Jika cloud hosting di-revisit |
| Sertifikasi medical-grade (CE Mark, ISO 13485) | MedWatch adalah alat bantu pencatatan, bukan alat diagnosis/treatment device | Tidak relevan; produk tidak akan masuk klasifikasi medical device |
| Multi-bahasa selain Bahasa Indonesia | Pasar target adalah Faskes 1 di Indonesia | Setelah ada permintaan ekspor regional (Malaysia, Brunei) |
| Auto-update via internet | Bertentangan dengan offline-first; update dilakukan manual via flashdisk baru | Tidak akan dipertimbangkan untuk versi 1.x |
| Integrasi BPJS Health Application | Membutuhkan kerja sama institusional; di luar lingkup tim mahasiswa | Setelah ada MoU resmi dengan BPJS |

---

## 5. Kriteria Acceptance "Production-Ready"

Definisi formal kriteria ada di `05-test-and-acceptance-plan.md` Section 4. Ringkasan di sini agar pembaca tahu finish line tanpa harus loncat dokumen:

1. Installer berhasil pada minimal 3 mesin Windows berbeda (Windows 10 home, Windows 11 home, Windows 11 pro).
2. Aplikasi launch dalam waktu kurang dari 3 detik (cold start) pada mesin spesifikasi minimum.
3. CRUD pasien (Create, Read, Update, Delete) berfungsi penuh tanpa koneksi internet.
4. Safety check obat mengembalikan verdict (skor risiko + label) dalam waktu kurang dari 500 ms untuk skenario tipikal (1 obat, 5 efek samping di database).
5. PDF export pasien (rekam medis SOAP) dihasilkan dengan font yang konsisten dan layout yang rapi tanpa karakter rusak.
6. UAT oleh satu bidan Faskes 1 (TBD, akan dipilih di Phase 4 Roadmap) selesai dengan minimal 8 dari 10 task user terselesaikan tanpa bantuan developer.
7. Zero bug Critical dan maksimal 2 bug Minor yang tercatat saat UAT.
8. Build reproducible: pembangunan installer dari source di dua mesin developer berbeda menghasilkan hash SHA-256 yang konsisten (modulo timestamp).

---

## 6. Cara Membaca Folder Ini

Urutan pembacaan yang disarankan tergantung peran pembaca.

### 6.1 Dosen pembimbing

Baca: 00 (file ini), 01, 06. Tujuan: konfirmasi tim memiliki rencana yang masuk akal pasca-akademik.

### 6.2 Calon klien Faskes 1

Baca: 01, 03, 05. Tujuan: pahami apa yang akan didapat klien (PRD), bagaimana ia menerima produknya (packaging), dan bagaimana ia tahu produk diterima (acceptance).

### 6.3 Developer pasca-akademik (tim B5 atau pengganti)

Baca: 00 sampai 06 secara berurutan. Tujuan: pahami rencana penuh dan mulai eksekusi pada fase yang tepat di roadmap (06).

### 6.4 Security reviewer

Baca: 04 (hardening) dan rujuk silang ke `docs/SECURITY.md` Section 7 (Residual Risk Register R1-R8) yang menjadi sumber backlog hardening.

---

## 7. Glosarium

| Istilah | Definisi singkat |
|---|---|
| Faskes 1 | Fasilitas Kesehatan Tingkat 1 (puskesmas, polindes, klinik bersalin kecil) sesuai BPJS Kesehatan |
| openFDA | API publik U.S. FDA untuk data adverse event dan recall obat, sumber data utama MedWatch |
| MVP akademik | Software yang dikumpulkan ke dosen pada 25 Mei 2026, ekuivalen dengan tag `v0.1.0` |
| Production-grade | Software siap diserahkan ke klien Faskes 1 yang membayar, target Q4 2026 (lihat `06-roadmap.md`) |
| PyInstaller | Tool packaging Python ke executable mandiri (one-folder atau one-file) |
| Inno Setup | Tool authoring installer Windows berbasis script |
| dmgbuild | Tool packaging .dmg untuk macOS |
| AppImage | Format eksekutabel portable Linux yang tidak butuh instalasi root |
| SQLite | Database file embedded yang menjadi target migrasi storage produksi |
| OWASP | Open Web Application Security Project, sumber Top 10 risk framework |

---

## 8. Tanggal dan Pemilik

- Tanggal dokumen: 18 Mei 2026.
- Pemilik: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Status: forward-looking plan, belum diimplementasi. Implementasi dijabarkan timeline-nya di `06-roadmap.md`.
- Approval untuk eksekusi: setelah submission akademik 25 Mei 2026 dilewati dengan PASS dari dosen.
