# Cara Pakai MedWatch Portable

Dokumen ini ditujukan untuk dosen pendamping, anggota tim, atau pengguna umum yang ingin menjalankan aplikasi MedWatch versi portable di komputer Windows tanpa proses pemasangan. Ikuti langkah secara berurutan.

## Persyaratan

- Sistem operasi Windows 10 atau Windows 11 (versi 64-bit).
- RAM minimum 4 GB.
- Ruang kosong di hard disk sekitar 500 MB. Berkas portable berukuran 112 MB dan basis data obat akan menambah sekitar 250 MB ketika aplikasi pertama kali dijalankan (basis data disalin ke folder pengguna).
- Tidak perlu koneksi internet untuk menjalankan aplikasi.

## Berkas yang Anda butuhkan

Berkas portable bernama `MedWatch-0.1.0-portable.exe`. Ukurannya 112 MB. Berkas ini dihasilkan dari `portable-app/dist/`.

## Cara pakai

1. Salin berkas `MedWatch-0.1.0-portable.exe` ke folder mana saja di komputer Windows Anda. Bisa di Desktop, Documents, USB flash disk, atau folder lain sesuai selera. Tidak ada batasan lokasi.
2. Klik dua kali berkas tersebut untuk menjalankannya.
3. Jika muncul peringatan Windows SmartScreen dengan tulisan "Windows protected your PC", klik tautan kecil "More info" di bagian kiri jendela peringatan, lalu klik tombol "Run anyway" yang muncul setelahnya. Peringatan ini wajar karena berkas portable belum ditandatangani secara digital (kode signing tidak termasuk dalam cakupan proyek akademik ini).
4. Aplikasi akan otomatis extract isinya ke folder sementara di `%LOCALAPPDATA%\Temp` lalu jendela MedWatch akan terbuka. Proses extract pertama kali memakan waktu sekitar 5 sampai 10 detik. Pada peluncuran berikutnya, jika berkas portable belum berubah, MedWatch akan langsung jalan dari cache sehingga waktu mulai jauh lebih cepat.
5. Data pasien dan basis data obat tersimpan di folder `%APPDATA%\MedWatch\drugs.db`. Folder ini akan tetap ada walaupun Anda menutup aplikasi atau menghapus berkas portable, jadi catatan pasien tidak akan hilang antar-jalankan.

## Hapus portable

Untuk membersihkan MedWatch Portable dari komputer Anda:

1. Tutup aplikasi MedWatch jika sedang terbuka.
2. Hapus berkas `MedWatch-0.1.0-portable.exe` dari folder tempat Anda menyimpannya.
3. Jika Anda ingin membersihkan semuanya termasuk data pasien dan basis data, hapus juga folder `%APPDATA%\MedWatch`. Caranya: buka File Explorer, ketik `%APPDATA%` di kotak alamat lalu tekan Enter, cari folder bernama `MedWatch`, klik kanan, lalu pilih "Delete".
4. Folder cache extract di `%LOCALAPPDATA%\Temp` akan dibersihkan otomatis oleh Windows pada siklus disk cleanup berikutnya. Anda boleh juga menghapusnya secara manual jika ingin segera.

## Catatan penting

Versi portable ini dilengkapi berkas `medwatch-backend.exe` berstatus placeholder. Artinya, mesin backend yang sebenarnya belum bisa dijalankan langsung dari berkas yang sekarang Anda jalankan. Sebelum aplikasi bisa dipakai untuk operasi sehari-hari, berkas `medwatch-backend.exe` asli harus diproduksi terlebih dulu melalui GitHub Actions Windows runner, kemudian disisipkan ulang ke dalam berkas portable. Prosedur teknis lengkap dijelaskan di berkas `KNOWN_LIMITATION_BACKEND_EXE.md` di root repository (dokumen dalam bahasa Inggris).

Selama backend masih placeholder, ketika MedWatch dijalankan akan muncul dialog kesalahan berbahasa Indonesia berbunyi "Backend MedWatch gagal dimulai. Mohon laporkan ke tim." Itu perilaku yang diharapkan dan menjadi tanda bahwa langkah penggantian backend belum dilakukan.

## Kontak

Untuk pertanyaan atau laporan masalah, hubungi:

Ghaisan Khoirul Badruzaman
ghaisan.khoirul.b@gmail.com
Project Leader, Kelompok B5, POLBAN D4 Teknik Informatika 1B-D4
