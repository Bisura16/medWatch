# Cara Pasang MedWatch Desktop (Installer)

Dokumen ini ditujukan untuk dosen pendamping, anggota tim, atau pengguna umum yang ingin memasang aplikasi MedWatch Desktop di komputer Windows. Ikuti langkah secara berurutan.

## Persyaratan

- Sistem operasi Windows 10 atau Windows 11 (versi 64-bit).
- RAM minimum 4 GB.
- Ruang kosong di hard disk sekitar 500 MB. Installer berukuran 139 MB dan basis data obat akan menambah sekitar 250 MB setelah pemasangan.
- Tidak perlu koneksi internet untuk menjalankan aplikasi setelah pemasangan selesai.

## Berkas yang Anda butuhkan

Berkas installer bernama `MedWatch Setup 0.1.0.exe`. Ukurannya 139 MB. Berkas ini dihasilkan dari `installer-based app/dist/`.

## Langkah pasang

1. Klik dua kali berkas `MedWatch Setup 0.1.0.exe`.
2. Jika muncul peringatan Windows SmartScreen dengan tulisan "Windows protected your PC", klik tautan kecil "More info" di bagian kiri jendela peringatan, lalu klik tombol "Run anyway" yang muncul setelahnya. Peringatan ini wajar karena installer belum ditandatangani secara digital (kode signing tidak termasuk dalam cakupan proyek akademik ini).
3. Wizard pasang MedWatch akan terbuka. Klik tombol "Next" untuk lanjut.
4. Pilih folder pasang. Folder default adalah `C:\Program Files\MedWatch` dan boleh Anda pakai apa adanya. Jika ingin folder lain, klik "Browse" dan pilih lokasi yang Anda inginkan. Setelah selesai memilih, klik "Next".
5. Tunggu proses extract selesai. Karena installer membawa basis data obat sebesar 246 MB, tahap ini bisa memakan waktu sekitar 30 detik. Sabar saja dan jangan tutup jendela.
6. Setelah proses selesai, klik tombol "Finish" untuk menutup wizard.

Sampai di sini, MedWatch sudah terpasang dan shortcut akan otomatis dibuat di Desktop dan di Start Menu Windows.

## Menjalankan MedWatch

Klik dua kali shortcut "MedWatch" yang ada di Desktop. Anda juga bisa membuka Start Menu, ketik "MedWatch", lalu klik hasil pencariannya. Jendela aplikasi akan muncul dalam waktu sekitar 5 sampai 10 detik untuk pertama kali (karena backend perlu extract sekali di awal). Setelah itu, jalannya akan jauh lebih cepat.

## Catatan penting

Versi installer ini dilengkapi berkas `medwatch-backend.exe` berstatus placeholder. Artinya, mesin backend yang sebenarnya belum bisa dijalankan langsung dari berkas yang sekarang Anda pasang. Sebelum aplikasi bisa dipakai untuk operasi sehari-hari, berkas `medwatch-backend.exe` asli harus diproduksi terlebih dulu melalui GitHub Actions Windows runner, kemudian disisipkan ulang ke dalam installer. Prosedur teknis lengkap dijelaskan di berkas `KNOWN_LIMITATION_BACKEND_EXE.md` di root repository (dokumen dalam bahasa Inggris).

Selama backend masih placeholder, ketika MedWatch dijalankan akan muncul dialog kesalahan berbahasa Indonesia berbunyi "Backend MedWatch gagal dimulai. Mohon laporkan ke tim." Itu perilaku yang diharapkan dan menjadi tanda bahwa langkah penggantian backend belum dilakukan.

## Uninstall

Untuk menghapus MedWatch dari komputer Anda:

1. Buka Settings Windows (Win + I).
2. Pilih "Apps" lalu "Installed apps" (atau "Apps and features" untuk Windows 10).
3. Cari "MedWatch" pada daftar, klik titik tiga di sebelah kanan, lalu pilih "Uninstall".
4. Konfirmasi dengan klik "Uninstall" sekali lagi.

Cara alternatif: buka Start Menu, cari folder "MedWatch", lalu klik shortcut "Uninstall MedWatch" yang ada di dalamnya.

Catatan: basis data dan berkas konfigurasi pengguna di `%APPDATA%\MedWatch\` tidak ikut terhapus secara otomatis. Jika Anda ingin membersihkan semuanya, hapus folder tersebut secara manual setelah uninstall selesai.

## Kontak

Untuk pertanyaan atau laporan masalah, hubungi:

Ghaisan Khoirul Badruzaman
ghaisan.khoirul.b@gmail.com
Project Leader, Kelompok B5, POLBAN D4 Teknik Informatika 1B-D4
