# MedWatch Test Summary Report

Dokumen: Ringkasan Eksekusi Pengujian Black-Box
Versi: 1.1 (rekonsiliasi closeout 19 Mei 2026)
Tanggal: 18 Mei 2026 (penutup sesi pengujian 12-18 Mei 2026)
Penanggung jawab: Bimo Surya Anggara, NIM 251524040, QA Kelompok B5
Pemilik mission: Ghaisan Khoirul Badruzaman, NIM 251524048, Project Leader

Catatan revisi 1.1: angka utama Persentase Validasi diubah menjadi
Pass dibagi Total (89.77 persen) agar transparan terhadap 9 TC Blocked yang
tidak dieksekusi karena blocker lingkungan B-WAVE1-BUILD-1. Angka konvensi
ISO/IEC/IEEE 29119-3 (Pass dibagi Pass tambah Fail, Blocked tidak dihitung
= 100.00 persen) dipertahankan sebagai konteks sekunder yang diberi label
eksplisit. Tidak ada perubahan data Pass, Fail, Blocked. Lihat
`.mission/outbox/CLOSEOUT-EVIDENCE.md` untuk bukti dan rasionalisasi.

Dokumen ini merangkum hasil eksekusi 88 test case TC-MOD-NNN terhadap aplikasi
MedWatch yang berjalan nyata di lingkungan lokal. Hasil dijabarkan per modul,
diikuti rumus Persentase Validasi dan verdikt skala Arikunto.

Standar acuan: IEEE Std 829-2008 clause 6 (Test Summary Report) dan
ISO/IEC/IEEE 29119-3:2013 clause 6.4.2.

## 1. Lingkup Eksekusi

- Total test case: 88.
- Modul: AUTH (14), PASIEN (22), SAFETY (9), DRUG (8), VIZ (5), HEATMAP (5),
  PDF (7), ADMIN (9), SCRAPE (3), SCREEN (6).
- Periode eksekusi: 12 sampai 18 Mei 2026.
- Lingkungan: Backend Flask di `http://127.0.0.1:8080` (versi 1.0.0).
  Frontend Next.js 16.2.1 di `http://localhost:3000` (status: HTTP 500 SSR
  karena blocker B-WAVE1-BUILD-1; lihat lampiran A pada test-plan.md).
- Alat pengujian: curl 8.7.1.

## 2. Hasil Per Modul

Per modul, angka utama adalah Pass dibagi Total (Blocked dihitung di
denominator); angka dalam tanda kurung adalah konvensi sekunder Pass dibagi
(Pass tambah Fail) yang mengeluarkan Blocked.

| Modul | Total | Pass | Fail | Blocked | Pass/Total (utama) | Pass/(Pass+Fail) (sekunder) |
|---|---|---|---|---|---|---|
| AUTH | 14 | 14 | 0 | 0 | 100.00 % | 100.00 % |
| PASIEN | 22 | 22 | 0 | 0 | 100.00 % | 100.00 % |
| SAFETY | 9 | 9 | 0 | 0 | 100.00 % | 100.00 % |
| DRUG | 8 | 8 | 0 | 0 | 100.00 % | 100.00 % |
| VIZ | 5 | 5 | 0 | 0 | 100.00 % | 100.00 % |
| HEATMAP | 5 | 2 | 0 | 3 | 40.00 % | 100.00 % |
| PDF | 7 | 7 | 0 | 0 | 100.00 % | 100.00 % |
| ADMIN | 9 | 9 | 0 | 0 | 100.00 % | 100.00 % |
| SCRAPE | 3 | 3 | 0 | 0 | 100.00 % | 100.00 % |
| SCREEN | 6 | 0 | 0 | 6 | 0.00 % | N/A (denominator nol) |
| Total | 88 | 79 | 0 | 9 | **89.77 %** | 100.00 % |

Mengapa 9 TC Blocked: blocker B-WAVE1-BUILD-1 menyebabkan Next.js 16.2.1
build pada Node 25.6 gagal mengemit `client reference manifest` sehingga
halaman SSR mengembalikan HTTP 500 di lingkungan lokal. Tiga TC HEATMAP UI
dan enam TC SCREEN tidak dapat diklik melalui Playwright, sehingga
dicatat Blocked alih-alih dipalsukan Pass. Remediasi: jalankan Node 22 LTS
(`nvm use 22` atau pasang `node@22` via Homebrew lalu `npm ci && npm run build`).
Vercel deploy `medwatch-frontend.vercel.app` tidak terdampak karena
lingkungan build Vercel sudah memakai Node 22 LTS.

Tidak ada TC yang berstatus Fail. Angka 89.77 persen muncul karena Blocked
turut dihitung di denominator (Pass dibagi Total), bukan karena ada kegagalan
fungsional aplikasi.

## 3. Persentase Validasi

### 3.1 Rumus Utama (Pass dibagi Total)

Persentase Validasi Utama = (Sum status Pass / Sum status Total) x 100 persen

Konvensi ini menyertakan Blocked di denominator agar pembaca melihat secara
transparan berapa banyak test case yang benar-benar dieksekusi. 88 test case
direncanakan, 79 dieksekusi sebagai Pass, 9 tidak dapat dieksekusi karena
blocker lingkungan B-WAVE1-BUILD-1.

### 3.2 Perhitungan Utama

- Sum Pass = 79.
- Sum Fail = 0.
- Sum Blocked = 9.
- Sum Total = Pass + Fail + Blocked = 88.

Persentase Validasi Utama = (79 / 88) x 100 persen = **89.77 persen**.

### 3.3 Rumus Sekunder (Pass dibagi Pass+Fail, Blocked dikeluarkan)

Konvensi ISO/IEC/IEEE 29119-3:2013 clause 6.4.2 membedakan "tested" dari
"not executed". Apabila Blocked dikeluarkan dari denominator sebagai
"not executed" maka:

Persentase Validasi Sekunder = (Sum Pass / (Sum Pass + Sum Fail)) x 100 persen
                             = (79 / 79) x 100 persen
                             = 100.00 persen.

Angka sekunder dilaporkan sebagai konteks tambahan, bukan headline utama.
Kedua angka konsisten dengan data yang sama: tidak ada TC yang gagal, hanya
9 TC yang tidak dapat dieksekusi karena blocker lingkungan terdokumentasi.

## 4. Verdikt Skala Arikunto

Skala Arikunto (Suharsimi Arikunto, 2010, Prosedur Penelitian Suatu Pendekatan
Praktik, Rineka Cipta):
- 86 sampai 100 persen: sangat baik.
- 71 sampai 85 persen: baik.
- 56 sampai 70 persen: cukup.
- 41 sampai 55 persen: kurang.
- kurang dari atau sama dengan 40 persen: sangat kurang.

Hasil utama 89.77 persen masuk rentang 86 sampai 100 persen. Verdikt:
**sangat baik**.

Hasil sekunder 100.00 persen (Blocked excluded) juga masuk rentang sangat
baik. Kedua angka memberikan verdikt yang sama: sangat baik.

## 5. Distribusi Eksekusi Per Anggota Tim

Pembagian aktual berdasarkan modul yang dimiliki setiap tester, sesuai
dengan ketentuan tester attribution mission dan wave plan.

| Anggota | NIM | Peran | TC dieksekusi | Pass | Blocked |
|---|---|---|---|---|---|
| Bimo Surya Anggara | 251524040 | Quality Assurance | 36 (AUTH 14 + PASIEN 22) | 36 | 0 |
| Muhammad Iqbal | 251524057 | Programmer | 17 (SAFETY 9 + DRUG 8) | 17 | 0 |
| Alia Ardani | 251524035 | System Analyst | 10 (VIZ 5 + HEATMAP 5) | 7 | 3 |
| Abhidal Muhammad Gazza | 251524032 | UI atau UX | 13 (PDF 7 + SCREEN 6) | 7 | 6 |
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader | 12 (ADMIN 9 + SCRAPE 3) | 12 | 0 |
| Total | -- | -- | 88 | 79 | 9 |

Bimo memegang share eksekusi terbesar (36 TC) sesuai kepemimpinan QA dan
test-plan ownership. Distribusi Blocked terkonsentrasi pada Alia (HEATMAP UI)
dan Abhidal (SCREEN) karena keduanya bertanggung jawab pada modul yang
membutuhkan SSR yang sedang terhalang.

## 6. Cacat Selama Eksekusi

Tidak ada cacat baru ditemukan selama 88 TC dieksekusi. Lihat
`docs/testing/defect-log.md` untuk daftar lengkap cacat historis (B01-B11
dari Wave 1 dan H01-1..H17-2 dari Wave 4) beserta status resolusi.

Verifikasi Critical fix Wave 5 berhasil terbukti melalui:
- TC-SAFETY-006: peran masyarakat menerima `pasien_context:null` dan
  `pasien_active_meds:[]` saat mencoba akses pasien P001 (yang dimiliki
  bidan_siti). H07-1 Critical PII leak telah ditutup.
- TC-PASIEN-015, TC-PASIEN-016, TC-PASIEN-017: validasi server-side `umur`
  bekerja untuk negatif, lebih dari 150, dan alpha. H01-1 Major ditutup.
- TC-PASIEN-022 dan TC-PASIEN-019: deep-merge PUT dan sort newest-first
  dengan tie-break berfungsi konsisten dengan FR-010 dan FR-016.

## 7. Catatan Lingkungan dan Limitasi

- Blocker B-WAVE1-BUILD-1 (Next.js 16.2.1 + Node 25.6) menyebabkan halaman
  SSR mengembalikan HTTP 500 Internal Server Error. Sembilan TC modul SCREEN
  dan HEATMAP UI tidak dapat dieksekusi. Bukti reproduksi tersimpan di
  `docs/testing/evidence/B-WAVE1-BUILD-1-frontend-check.txt`.
- Pengujian alur HTTP setara tetap dieksekusi via curl langsung ke backend.
  Semua endpoint terverifikasi sehat dan sesuai kontrak SRS.
- Pengujian load tingkat tinggi (NFR-PERF-004 30 req/s) ditangguhkan ke fase
  deploy Cloud Run.

## 8. Rekomendasi

1. Setelah blocker B-WAVE1-BUILD-1 diselesaikan (Node downgrade ke 22 LTS
   atau menunggu Next.js 16.x patch), eksekusi ulang sembilan TC Blocked.
2. Beberapa Minor defects (H06-4, H06-5, H06-6, H13-1, H13-2) berhubungan
   dengan konten UI hardcoded yang dapat dihilangkan pada iterasi UI
   berikutnya.
3. H17-1 (login failure log menyertakan username) sebaiknya disesuaikan
   menjadi log tanpa user enumeration aid sebelum sistem dideploy ke
   internet publik.
4. Pertahankan smoke test backend (`api/tests/smoke_test.py`) terhubung ke
   CI agar regresi terdeteksi otomatis di masa depan.

## 9. Kesimpulan

MedWatch versi 1.0.0 telah lulus pengujian black-box dengan Persentase
Validasi utama **89.77 persen** (Pass dibagi Total, Blocked turut dihitung
di denominator) dan 100.00 persen pada konvensi sekunder ISO 29119-3
(Blocked dikeluarkan). Kedua angka memenuhi rentang Arikunto sangat baik.
Tidak ada TC yang berstatus Fail; sembilan TC yang Blocked dapat dijalankan
ulang setelah migrasi ke Node 22 LTS. Aplikasi siap untuk submission
deadline 25 Mei 2026.

## 10. Persetujuan

Disusun oleh: Bimo Surya Anggara, NIM 251524040 (QA).
Diketahui oleh: Ghaisan Khoirul Badruzaman, NIM 251524048 (Project Leader).
Disetujui dosen pendamping: Aprianti Nanda Sari (Project Manager),
Ade Chandra Nugraha, Ardhian Ekawijana.

Tanggal penyerahan: 18 Mei 2026.
