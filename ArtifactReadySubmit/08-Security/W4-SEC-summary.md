---
title: Ringkasan Pemindaian Keamanan W4-SEC
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048) untuk Kelompok B5
date: 2026-05-18
---

# Ringkasan Pemindaian Keamanan Wave 4 (W4-SEC)

Dokumen satu halaman ini meringkas hasil audit keamanan menyeluruh atas dua repo MedWatch yang dilakukan pada 18 Mei 2026 sebagai Wave 4 misi pengembangan. Tujuan ringkasan ini adalah memberi gambaran posisi keamanan kepada dosen pembimbing tanpa membuka detail kredensial. Laporan lengkap tetap tersedia di repo internal `.mission/findings/security/W4-SEC.md`.

## Lingkup

Audit dilakukan terhadap dua repositori (backend `medWatch` dan frontend `FrontendMedWatch`) pada working tree dan seluruh riwayat git (semua branch lokal serta remote). Alat utama yang dipakai adalah `gitleaks` (versi 8.x dari Homebrew) dengan dukungan grep manual untuk dua belas pola minimum sesuai konstrain misi serta `git log --all -p -S<token>` (history pickaxe) untuk verifikasi histori. Pemindaian berlangsung pada commit backend `c70bb7d` (81 commits, sekitar 4,10 MB) dan commit frontend `b8387675` (34 commits, sekitar 2,95 MB).

## Hasil Ringkas

| Kategori | Jumlah |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 3 |
| Info | 7 |
| Total temuan | 12 |
| Kredensial nilai nyata yang ter-leak | 0 |

`gitleaks detect` mengonfirmasi `no leaks found` untuk pola signature scanner standar pada kedua repo. Status terhadap konstrain misi nomor 12 ("zero credential VALUES exposed anywhere"): **PARTIAL - 1 known LOW dev-loopback secret, accepted by user (Ghaisan Khoirul Badruzaman, 251524048, Project Leader Kelompok B5), documented**. Penerimaan risiko ini dilakukan oleh user secara eksplisit pada closeout 2026-05-19, bukan self-waive agen. Detail di docs/SECURITY.md Section 7.6 (Known Accepted Findings) WT-04.

## Temuan Medium dan Remediasi

Dua temuan Medium yang seluruhnya berkategori demo-by-design.

1. Berkas `<redacted: pattern bcrypt-hash>` pada seed users backend memuat hash satu-arah (bukan plaintext) untuk lima akun demo. Untuk skenario demo akademik, hal ini dapat diterima sesuai FR-003 pada SRS. Order remediasi untuk produksi: ganti seed dengan akun nyata milik klinik via endpoint admin, lalu publish ulang ke Cloud Storage.
2. Kemunculan `<redacted: pattern demo-password-string>` di beberapa berkas dokumentasi dan kartu login frontend yang sengaja ditampilkan untuk demo. Order remediasi untuk produksi: hapus blok kartu demo di halaman login, ganti contoh password di README dan dokumen contoh dengan placeholder, dan ganti seed demo dengan akun pengguna riil.

## Temuan Low dan Info

Tiga temuan Low semuanya berbentuk string literal `<redacted: pattern JWT_SECRET=literal>` di berkas dokumentasi yang nilai-nya secara eksplisit menyebut "dev-only" atau "dev-mission-secret-local" (terkonsolidasi sebagai WT-04 di laporan internal). Nilai hanya menandatangani JWT terhadap backend Flask `127.0.0.1:8080` loopback localhost; produksi memakai GCP Secret Manager `medwatch-jwt-secret` lewat Cloud Run `--set-secrets`, sehingga token signed dev tidak valid di produksi. Pengambil keputusan menerima risiko LOW ini: Ghaisan Khoirul Badruzaman (251524048) sebagai Project Leader Kelompok B5, didokumentasikan pada closeout 2026-05-19. Mission acceptance criterion melarang agen menutup temuan secret secara mandiri; penerimaan harus oleh user, dan itulah yang dilakukan di sini. Order remediasi opsional: ganti contoh di dokumentasi dengan placeholder agar pola scanner di repo lain tidak match. Detail lengkap di docs/SECURITY.md Section 7.6.

Tujuh temuan Info terdiri dari nomor identifier publik openFDA (UPC barcode dan NDC), nomor telepon fixture dengan pola sekuensial demo, nama pasien synthetic dengan suffix test, token OIDC Vercel di berkas `.env.local` yang tidak pernah tracked, serta meta-reference pola scanner di berkas konfigurasi agent. Tidak ada aksi yang diperlukan untuk kategori ini.

## Verifikasi Hardening

Beberapa hal yang sudah diverifikasi PASS pada audit.

- Berkas `.gitignore` di kedua repo mencakup `.env*`, `*.pem`, `*.key`, `service-account*.json`, dan `gcp-key*.json`.
- Berkas `.gcloudignore` di backend mencakup `.env`, `.env.local`, dan `.env.example` sehingga env tidak ikut ke build context Cloud Run.
- Skrip pre-commit `secret-scan.sh` di kedua repo memuat dua belas pola minimum dan berfungsi pada mode hook PreToolUse maupun mode standalone.
- Cookie JWT di frontend di-set dengan flag httpOnly, secure, dan sameSite=lax.
- Berkas `Dockerfile`, `Procfile`, dan `next.config.ts` tidak memuat kredensial; semua nilai sensitif diset runtime via Secret Manager atau Vercel project settings.

## Order Remediasi Prioritas

1. Saat hand-over ke klinik produksi: ganti seed demo dengan akun riil (Medium #1 dan Medium #2).
2. Polish opsional: ganti literal `JWT_SECRET=<dev value>` di dokumentasi dengan placeholder (tiga temuan Low).
3. Tidak ada aksi yang diperlukan untuk tujuh temuan Info.

## Pernyataan Akhir

Tidak ada kredensial produksi yang bocor di working tree atau history git. Mission constraint nomor 12 ("zero credential VALUES exposed anywhere") berstatus **PARTIAL: 1 known LOW dev-loopback secret accepted by user Ghaisan Khoirul Badruzaman (251524048) sebagai Project Leader, documented sebagai WT-04 di docs/SECURITY.md Section 7.6**. Untuk produksi klinik, dua langkah remediasi Medium di atas harus dieksekusi sebelum live; rotasi WT-04 dev-loopback secret opsional sebelum live, tidak memblokir submission akademik. Detail lengkap audit, perintah yang dijalankan, dan daftar berkas yang diperiksa tersedia di `.mission/findings/security/W4-SEC.md` pada repo backend.
