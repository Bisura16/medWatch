---
title: Quick Start Demo MedWatch
version: 1.0
owner: Abhidal Muhammad Gazza (251524032) bersama Kelompok B5
date: 2026-05-18
---

# Panduan Cepat Demo MedWatch (Quick Start)

Lembar satu halaman ini memandu dosen pembimbing dan peserta demo untuk memulai sistem MedWatch dalam waktu kurang dari dua menit. Untuk detail penuh per fitur, silakan rujuk `USER-MANUAL.md` di subfolder yang sama.

## Sasaran Pembaca

Dokumen ini ditujukan untuk dosen pembimbing (Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana) serta peserta demo kelas 1B-D4 yang ingin menguji sistem MedWatch tanpa perlu instalasi lokal. Semua skenario dijalankan langsung dari peramban Chrome atau Firefox terbaru.

## Akses Aplikasi Live

| Komponen | URL Publik | Catatan |
|---|---|---|
| Frontend Next.js (Vercel) | https://medwatch-frontend.vercel.app | Buka URL ini dari peramban modern. Halaman login MedWatch akan tampil. |
| Backend Flask (Cloud Run) | https://medwatch-api-517694123086.asia-southeast1.run.app | Dipakai otomatis oleh frontend; tidak perlu dibuka langsung. Tersedia endpoint `/api/health` untuk verifikasi cepat. |

Frontend selalu memproksi panggilan ke backend lewat Vercel API route, sehingga peramban tidak pernah memanggil Cloud Run secara langsung. Pola ini didokumentasikan di `03-Architecture-Decisions/0001-vercel-cloud-run-security-pattern.md`.

## Akun Demo

Di bawah formulir login pada halaman utama frontend, terdapat tiga kartu preset yang menampilkan kredensial demo dengan jelas. Klik salah satu kartu untuk mengisi formulir otomatis dan masuk dengan sekali klik tombol Masuk.

| Peran | Username | Password | Modul yang Dapat Diakses |
|---|---|---|---|
| Tenaga Kesehatan (Bidan) | bidan_siti | siti2026 | Manajemen pasien SOAP, cek interaksi obat dengan konteks pasien, ekspor PDF, lihat visualisasi data obat. |
| Masyarakat Umum | umum_budi | budi2026 | Cek interaksi obat tanpa konteks pasien, lihat informasi efek samping obat, dasbor publik. |
| Administrator Sistem | admin_ghaisan | admin2026 | Dasbor admin (KPI sistem), pemicu scraping ulang openFDA, kelola pengguna, tinjau log audit. |

Kredensial ini sengaja ditampilkan untuk demo akademik (FR-003 di `01-Proposal-PRD/SRS.md`). Untuk skenario produksi, kartu demo dihapus dan akun seed diganti, sebagaimana dijelaskan di `08-Security/SECURITY.md` dan ADR-0002.

## Skenario Demo per Peran

Bidan (bidan_siti). Setelah masuk, halaman utama menampilkan ringkasan pasien aktif dan tombol pintas Tambah Pasien. Buka menu Pasien untuk melihat daftar SOAP (terurut terbaru di atas), klik salah satu untuk mengedit, lalu klik Cek Obat untuk memvalidasi interaksi obat aktif pasien tersebut. Tombol Unduh PDF mengekspor catatan SOAP ke berkas PDF rapi.

Masyarakat (umum_budi). Menu Cek Obat dapat dipakai tanpa konteks pasien. Masukkan satu atau lebih nama obat, sistem menampilkan ringkasan keamanan dengan severity rendah, sedang, atau tinggi serta penjelasan singkat per item. Peran masyarakat tidak melihat data pasien manapun (verifikasi keamanan H07-1 di `08-Security/W4-SEC-summary.md`).

Administrator (admin_ghaisan). Dasbor admin menampilkan KPI sistem riil dari endpoint backend, daftar pengguna aktif, dan tombol Scraper untuk memicu pengambilan data openFDA ulang. Semua angka KPI ditarik dari `/api/admin/stats` (bukan placeholder), sebagaimana diverifikasi pada Wave 5.

## Verifikasi Cepat

Untuk memastikan backend hidup sebelum demo, buka URL `https://medwatch-api-517694123086.asia-southeast1.run.app/api/health` pada peramban. Jawaban yang diharapkan berbentuk JSON `{"status":"ok"}` dengan kode HTTP 200.

## Lanjutan

Detail per fitur, alur pengujian, daftar pesan error, dan tangkapan layar tersedia di `06-User-Manual/USER-MANUAL.md` dan `06-User-Manual/USER-MANUAL.docx`. Daftar lengkap requirement yang ditelusuri ke test case ada di `05-Testing/rtm.md`.
