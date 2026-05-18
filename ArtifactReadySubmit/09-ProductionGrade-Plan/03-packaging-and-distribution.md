---
title: Packaging and Distribution Plan MedWatch
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking plan (belum diimplementasi)
related_docs:
  - ProductionGrade-ImplementationPlan/00-overview.md
  - ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md
  - ProductionGrade-ImplementationPlan/05-test-and-acceptance-plan.md
  - ProductionGrade-ImplementationPlan/06-roadmap.md
---

# 03 - Packaging and Distribution Plan MedWatch

Dokumen ini menjabarkan rencana packaging MedWatch dari source code menjadi installer yang dapat didistribusikan via media fisik (flashdisk) ke workstation klien Faskes 1. Toolchain utama: PyInstaller untuk bundling Python ke executable, Inno Setup untuk installer Windows, dmgbuild untuk macOS, AppImage untuk Linux. Pemilihan tool memperhatikan keterbatasan tim mahasiswa: gratis, dokumentasi memadai, komunitas aktif.

---

## 1. Tujuan dan Prinsip

### 1.1 Tujuan

1. Menghasilkan installer satu file yang dapat dijalankan oleh non-developer di workstation klien.
2. Total ukuran distribusi kurang dari 300 MB termasuk runtime Python, library, snapshot openFDA, dan asset.
3. Smoke-test pada mesin bersih (di luar laptop developer) selesai tanpa error dengan langkah yang dapat direproduksi.

### 1.2 Prinsip

- Build script reproducible. Build dari source di tag `v1.0.0` pada dua mesin developer berbeda harus menghasilkan hash SHA-256 yang konsisten (modulo timestamp metadata yang in-build).
- Distribution package berisi installer + readme + uninstaller + manifest. Tidak ada referensi ke laptop developer atau path absolut yang menyertai.
- Tidak ada hardcoded credential di binary. Verifikasi via `strings MedWatch.exe | grep -E '(api_key|JWT_SECRET|password)='` saat smoke test.

---

## 2. PyInstaller: Bundling Python ke Executable

### 2.1 One-folder vs One-file

PyInstaller menyediakan dua mode bundling. Tabel berikut membandingkan keduanya untuk konteks MedWatch.

| Aspek | One-folder | One-file |
|---|---|---|
| Cold start time | Lebih cepat (kurang dari 3 detik) karena tidak ada extract step | Lebih lambat (5-10 detik) karena extract ke temp tiap launch |
| Distribusi via flashdisk | Banyak file, tetap berfungsi setelah copy keseluruhan folder | Satu file, lebih sederhana di-copy |
| Antivirus false-positive risk | Lebih rendah | Lebih tinggi (heuristic deteksi packer) |
| Ukuran total | Sama (sekitar 200-250 MB) | Sama |
| Update incremental | Mungkin (overwrite file yang berubah) | Tidak mungkin (single binary) |
| Debug saat error | Lebih mudah (file Python jelas terlihat di subfolder) | Lebih sulit |

**Rekomendasi: One-folder mode untuk versi 1.0.** Alasan utama: cold start lebih cepat sesuai Success Metric di `01-production-PRD.md` Section 6.2 (kurang dari 3 detik). Antivirus false-positive lebih rendah, dan tim mahasiswa belum punya code-signing certificate (lihat Section 6).

Pertimbangkan migrasi ke one-file di versi 2.0 jika klien meminta single-file distribution.

### 2.2 PyInstaller Spec File

File spec disimpan di `ProductionGrade-ImplementationPlan/build/medwatch.spec` sebagai referensi. **Tidak dijalankan pada Wave 2; hanya disimpan sebagai dokumen.** Eksekusi PyInstaller terjadi di Phase 2 sesuai `06-roadmap.md`.

Isi spec:

```python
# -*- mode: python ; coding: utf-8 -*-
# MedWatch PyInstaller spec, one-folder mode.
# Build: pyinstaller medwatch.spec --clean --noconfirm
# Output: dist/MedWatch/

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('anggota1/data/drug_safety_data.json', 'data/anggota1'),
        ('anggota1/data/drug_recalls.json',     'data/anggota1'),
        ('anggota4/data/drug_database.json',    'data/anggota4'),
        ('anggota4/data/effect_database.json',  'data/anggota4'),
        ('api/data/users.json',                 'data/api'),   # seed users (dev/demo)
        ('docs/USER-MANUAL.md',                 'docs'),
    ],
    hiddenimports=[
        'flask', 'flask_cors', 'jwt', 'bcrypt',
        'fpdf', 'matplotlib', 'numpy', 'PIL',
        # Eksplisit listed karena CustomTkinter sub-imports lazy
        'customtkinter', 'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Build-time only, tidak boleh di runtime bundle
        'anggota1.openfda.fetch',
        # Test artefacts
        'pytest', 'unittest', '_pytest',
        # GCS client tidak dipakai di production offline
        'google.cloud.storage',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MedWatch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             # UPX kompresi sering trigger AV; disabled
    console=False,          # GUI app, no console window
    icon='assets/medwatch.ico',
    version='build/version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MedWatch',
)
```

Catatan: `assets/medwatch.ico` dan `build/version_info.txt` akan dibuat di Phase 2 saat implementation. Saat ini hanya placeholder agar spec dapat ditinjau secara struktural.

### 2.3 Verifikasi Build

Setelah build, jalankan smoke check di workstation builder:

1. `dist/MedWatch/MedWatch.exe` launch dalam waktu kurang dari 3 detik.
2. Total ukuran `dist/MedWatch/` kurang dari 280 MB (target distribusi 300 MB termasuk installer overhead).
3. `dist/MedWatch/data/anggota1/drug_safety_data.json` ada dan berukuran kurang lebih sama dengan source repo.
4. Pencarian string sensitif: `strings dist/MedWatch/MedWatch.exe | grep -E '(JWT_SECRET|password|api_key)='` harus kosong. Per mission constraint 12.

### 2.4 Exclusion List

File-file berikut sengaja TIDAK di-include di bundle production runtime:

| File | Alasan eksklusi |
|---|---|
| `anggota1/openfda/fetch.py` | Build-time only; tidak dipakai user akhir. Aktivitas refresh openFDA dilakukan oleh developer saat menyiapkan rilis. |
| `anggota1/scraper.log` | Log historis scraping; tidak relevan di production. |
| `api/tests/` | Test suite; tidak dipakai production. |
| `docs/diagrams/src/` | Source diagrams; tidak dipakai runtime. |
| `*.pyc`, `__pycache__/` | Compiled artefacts; PyInstaller membuat sendiri. |
| `.git/`, `.mission/`, `./` | Metadata repo dan mission; bukan asset production. |

---

## 3. Per-OS Installer

Tim utama bekerja pada macOS (Ghaisan menggunakan MacBook). Target distribusi utama: Windows 10/11. Karena cross-compile Windows installer dari macOS membutuhkan ekstra setup (Wine, atau pakai mesin Windows virtual), strategi praktis:

1. Bangun PyInstaller bundle pada masing-masing host OS native.
2. Bangun installer Windows pada VM Windows 11 (di mesin pribadi) atau pada GitHub Actions Windows runner.
3. macOS dan Linux installer dibangun lokal saat dibutuhkan, lebih jarang.

### 3.1 Windows: Inno Setup

[Inno Setup](https://jrsoftware.org/isdl.php) adalah authoring tool installer Windows gratis dengan script DSL sederhana. Pilihan utama karena:

- Free dan open-source.
- Dokumentasi lengkap dan komunitas aktif.
- Mendukung pembuatan shortcut Desktop + Start Menu, registry entry, uninstaller otomatis.
- Output: single `.exe` installer.

Script Inno Setup outline (file `build/medwatch.iss`, akan dibuat di Phase 2):

```ini
[Setup]
AppName=MedWatch
AppVersion=1.0.0
DefaultDirName={pf}\MedWatch
DefaultGroupName=MedWatch
PrivilegesRequired=admin
OutputDir=installer_output
OutputBaseFilename=MedWatchSetup-1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
MinVersion=10.0.17763   ; Windows 10 1809+

[Files]
Source: "dist\MedWatch\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\MedWatch"; Filename: "{app}\MedWatch.exe"
Name: "{commondesktop}\MedWatch"; Filename: "{app}\MedWatch.exe"

[Registry]
Root: HKLM; Subkey: "SOFTWARE\MedWatch"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\MedWatch"
```

Alternatif yang dipertimbangkan: NSIS. Ditolak karena syntax script lebih verbose dan tooling Windows-only lebih luas di Inno Setup.

### 3.2 macOS: dmgbuild atau PKG

Untuk distribusi macOS, dua opsi:

- **dmgbuild**: pip-installable, membuat `.dmg` dengan drag-to-Applications layout. Cocok untuk Mac yang tidak diaktivasi Gatekeeper strict. Tidak notarized.
- **PKG (notarized via notarytool)**: lebih formal, butuh Apple Developer Account ($99/tahun). Out of budget tim mahasiswa per mission constraint 6 (free tier).

Rekomendasi: dmgbuild untuk versi 1.0. User akan diminta klik kanan -> Buka pada saat pertama kali untuk menerima warning Gatekeeper. Notarization dipertimbangkan jika ada klien macOS yang membayar.

### 3.3 Linux: AppImage

[AppImage](https://appimage.org/) adalah format eksekutabel portable. Cocok karena:

- Tidak membutuhkan package manager (apt, dnf, pacman) berbeda.
- Tidak butuh sudo untuk dijalankan.
- Single file portable.

Build: `appimagetool` mengkonversi folder PyInstaller dist menjadi `MedWatch-1.0.0-x86_64.AppImage`. Klien Linux jarang di Faskes 1, sehingga prioritas Linux lebih rendah dari Windows.

---

## 4. Flashdisk-Ready Folder Layout

Struktur folder pada flashdisk yang dikirim ke klien:

```
MedWatch-Flashdisk-1.0.0/
├── MedWatchSetup-1.0.0.exe        # Inno Setup installer Windows
├── MedWatch-1.0.0.dmg              # macOS (opsional, jika klien macOS)
├── MedWatch-1.0.0-x86_64.AppImage  # Linux (opsional)
├── README.txt                      # Panduan singkat Bahasa Indonesia
├── docs/
│   ├── USER-MANUAL.pdf             # Hasil pandoc convert dari docs/USER-MANUAL.md
│   └── INSTALL-QUICK-START.txt
├── samples/
│   └── sample-pasien.json          # Contoh data pasien untuk demo
└── support/
    └── KONTAK-TIM.txt              # Saluran support per 01-production-PRD Section 4.4
```

Total ukuran flashdisk target: kurang dari 350 MB (installer + dokumen + samples). Flashdisk 1 GB sudah cukup.

### 4.1 README.txt root flashdisk

Isi (draft):

```
================================
MedWatch 1.0.0 - Panduan Singkat
================================

MedWatch adalah aplikasi pemantauan keamanan obat dan
manajemen klinik untuk Faskes 1. Aplikasi ini berjalan
offline tanpa membutuhkan koneksi internet.

INSTALASI WINDOWS
1. Klik dua kali file "MedWatchSetup-1.0.0.exe".
2. Ikuti wizard. Setujui lokasi instalasi default.
3. Setelah selesai, klik ikon "MedWatch" di Desktop.
4. Login dengan username dan password yang diberikan
   oleh koordinator klinik.

DOKUMENTASI LENGKAP
Buka folder "docs/" lalu file "USER-MANUAL.pdf".

BUTUH BANTUAN
Lihat folder "support/" file "KONTAK-TIM.txt".

(c) 2026 Kelompok B5, D4 Teknik Informatika POLBAN.
```

### 4.2 Layout post-install di workstation klien (Windows)

```
C:\Program Files\MedWatch\
├── MedWatch.exe
├── _internal\           # PyInstaller internal (Python runtime, libraries)
├── data\
│   ├── anggota1\
│   │   ├── drug_safety_data.json
│   │   └── drug_recalls.json
│   └── anggota4\
│       ├── drug_database.json
│       └── effect_database.json
├── docs\
│   └── USER-MANUAL.md
└── unins000.exe         # Inno Setup uninstaller

%APPDATA%\MedWatch\
├── medwatch.db          # SQLite database (created on first run)
├── data\
│   └── anggota1\        # Copied from install dir on first run
├── logs\
│   └── crash.log
├── config.ini
└── .jwt-key             # Auto-generated, permission 600
```

---

## 5. Smoke-Test Checklist (Clean Machine)

Smoke test dilakukan pada mesin bersih (bukan laptop developer) sebelum mengirim flashdisk ke klien. Lihat juga `05-test-and-acceptance-plan.md` Section 2.5 untuk acceptance lengkap.

### 5.1 Pra-Test

- [ ] Mesin: Windows 10 atau Windows 11, 64-bit, 8 GB RAM, 256 GB SSD, account user non-admin.
- [ ] Pastikan mesin belum pernah menginstall MedWatch (cek `Program Files`, `AppData`, Registry `HKLM\SOFTWARE\MedWatch`).
- [ ] Cabut kabel jaringan / matikan WiFi untuk verifikasi offline.

### 5.2 Test Instalasi

- [ ] Klik dua kali `MedWatchSetup-1.0.0.exe`. Wizard muncul dalam waktu kurang dari 5 detik.
- [ ] Selesaikan wizard dengan default. Total waktu kurang dari 5 menit.
- [ ] Shortcut Desktop muncul. Shortcut Start Menu muncul.
- [ ] `C:\Program Files\MedWatch\MedWatch.exe` exists. Ukuran kurang dari 280 MB total folder.

### 5.3 Test Cold Start

- [ ] Klik ikon Desktop. Aplikasi launch dalam waktu kurang dari 3 detik.
- [ ] Dialog login muncul, berbahasa Indonesia, tanpa demo credentials yang terlihat.
- [ ] Login dengan kredensial demo (didokumentasikan terpisah, tidak di file ini per mission constraint 12). Berhasil dalam waktu kurang dari 1 detik.

### 5.4 Test Fungsional Offline

- [ ] Dengan kabel masih tercabut, lakukan create pasien baru. Round-trip kurang dari 200 ms.
- [ ] Edit pasien. Update tersimpan.
- [ ] Delete pasien. Konfirmasi muncul, lalu pasien hilang dari list.
- [ ] Safety check obat "paracetamol". Hasil dalam waktu kurang dari 500 ms, label risiko dan efek samping tampil.
- [ ] Ekspor PDF rekam medis. File `.pdf` ter-generate, dapat dibuka via Adobe Reader, layout rapi.
- [ ] Klik menu admin "Refresh openFDA". Pesan "Membutuhkan koneksi internet" muncul (graceful).

### 5.5 Test Uninstall

- [ ] Settings -> Apps -> MedWatch -> Uninstall.
- [ ] Setelah uninstall, `C:\Program Files\MedWatch\` hilang. `%APPDATA%\MedWatch\` hilang. Registry `HKLM\SOFTWARE\MedWatch` hilang.
- [ ] Shortcut Desktop dan Start Menu hilang.

### 5.6 Reproduksi Build

- [ ] Build PyInstaller dijalankan ulang pada mesin developer kedua. `dist/MedWatch/MedWatch.exe` hash SHA-256 sama dengan build pertama (toleransi: timestamp build di metadata).
- [ ] Installer Inno Setup output ukuran sama (toleransi: 1 KB karena variabel kompresi).

---

## 6. Code Signing (Out-of-Scope v1.0)

Code signing dengan certificate dari Certificate Authority resmi (DigiCert, Sectigo, GlobalSign) menyebabkan installer dipercaya oleh Windows SmartScreen tanpa peringatan. Biaya certificate: USD 200-500 per tahun.

**Keputusan v1.0: out of scope.** Alasan:

1. Mission constraint 6 (free tier). Biaya certificate keluar dari budget akademik.
2. Klien Faskes 1 kemungkinan besar tidak peduli SmartScreen warning jika mereka menerima flashdisk dari saluran tepercaya (dosen pendamping, koordinator klinik) dengan instruksi klik "More info -> Run anyway".
3. Self-signed certificate gratis tetapi memberikan warning yang lebih buruk daripada unsigned, sehingga tidak dipilih.

Mitigasi sementara:

- README.txt flashdisk mencantumkan SHA-256 hash setiap installer. User dapat membandingkan dengan hash yang tertera di User Manual (yang juga di-distribute via flashdisk yang sama, sehingga ini bukan verifikasi independen; lebih sebagai best-effort integrity check).
- Inno Setup script include `[Setup] AppPublisher=Kelompok B5 POLBAN`. Saat user klik "More info" pada SmartScreen, identifikasi tim muncul.

Code signing dipertimbangkan kembali jika tim mendapatkan funding dari klien institusional atau dosen pendamping menyetujui pembelian.

---

## 7. Versioning dan Release Strategy

### 7.1 SemVer

MedWatch mengikuti Semantic Versioning 2.0.0. Format: `MAJOR.MINOR.PATCH`.

- MAJOR: perubahan breaking schema database (memerlukan migration). Contoh: dari SQLite kembali ke PostgreSQL.
- MINOR: penambahan fitur backward-compatible. Contoh: tambahan menu Backup.
- PATCH: bug fix tanpa perubahan fitur. Contoh: fix layout PDF.

Versi pertama production: `1.0.0`. Tag git: `v1.0.0`.

### 7.2 Release artifact naming

- `MedWatchSetup-1.0.0.exe` (Windows installer)
- `MedWatch-1.0.0.dmg` (macOS, opsional)
- `MedWatch-1.0.0-x86_64.AppImage` (Linux, opsional)
- `MedWatch-1.0.0-src.zip` (source tarball, opsional untuk arsip)

Snapshot openFDA tertanam di binary; tanggal snapshot dapat dilihat via menu Help -> Tentang Aplikasi.

### 7.3 Changelog

File `CHANGELOG.md` ditulis dengan format Keep-a-Changelog. Diisi pada setiap rilis. Tidak relevan untuk Wave 2 (belum ada production release); placeholder akan disiapkan di repo saat Phase 5 di `06-roadmap.md`.

---

## 8. Distribusi: Saluran dan SOP

### 8.1 Saluran utama: flashdisk dari koordinator klinik

Skema yang dipilih untuk versi 1.0:

1. Tim menyiapkan master image folder `MedWatch-Flashdisk-1.0.0/` di hard drive developer.
2. Tim menyalin master image ke flashdisk USB 1 GB atau 2 GB. Flashdisk dijual ke klien sebagai bagian dari paket.
3. Koordinator klinik membawa flashdisk ke Faskes 1, melakukan instalasi mengikuti README.txt.

### 8.2 Saluran sekunder: email zip

Untuk klien yang menerima ukuran zip kurang dari 100 MB lewat email (post-PyInstaller compression mungkin sampai 80 MB jika UPX di-enable; lihat trade-off di Section 2.3), zip + checksum dapat dikirim sebagai backup. Tidak menjadi saluran utama karena attachment besar sering diblock oleh email provider.

### 8.3 SOP Penyerahan

Tim menyiapkan SOP dokumen terpisah (dijadwalkan di Phase 5 di `06-roadmap.md`) yang mencakup:

- Briefing kepada koordinator klinik (15 menit).
- Sesi tanya jawab dasar.
- Penyerahan flashdisk + cetak User Manual.
- Pembuatan akun login awal (admin sementara + 1 atau 2 akun tenaga_kesehatan).
- Backup pertama (kosong, tetap dilakukan agar user familiar dengan menu Backup).

---

## 9. Risiko dan Mitigasi

| ID | Risiko | Likelihood | Dampak | Mitigasi |
|---|---|---|---|---|
| PKG-R1 | Antivirus Windows Defender false-positive di PyInstaller-built exe | Tinggi | Major | UPX disabled, code signing dipertimbangkan di v2.0, instruksi whitelist di User Manual |
| PKG-R2 | Ukuran bundle membengkak karena dependency tidak perlu (matplotlib backends, NumPy testing) | Sedang | Minor | Exclude list di spec PyInstaller (Section 2.4) dan PyInstaller exclude flag |
| PKG-R3 | Workstation klien punya antivirus enterprise (Symantec, McAfee) yang mem-block installer | Sedang | Major | Koordinator klinik diminta whitelist folder install sebelum instalasi |
| PKG-R4 | Cross-compile Windows installer dari macOS gagal | Sedang | Major | Build Windows installer di VM Windows lokal atau GitHub Actions Windows runner |
| PKG-R5 | Inno Setup script error pada Windows version langka (mis. Windows 11 ARM) | Rendah | Major | Minimal target Windows 10 1809 x64; ARM dan tablet edition tidak didukung |
| PKG-R6 | Flashdisk corrupted setelah duplikasi banyak | Sedang | Minor | Verifikasi SHA-256 setelah copy ke flashdisk; sediakan dua flashdisk per klien (primary + backup) |
| PKG-R7 | Path absolut developer macOS bocor di bundle | Rendah | Minor | Audit `strings` pada exe untuk pattern `/Users/<developer>/...` |

---

## 10. Tanggung Jawab dan Estimasi Waktu

| Item | PIC saran | Estimasi |
|---|---|---|
| Tulis PyInstaller spec final | Ghaisan | 1 hari |
| Build dan smoke test bundle (Windows VM) | Ghaisan | 1 hari |
| Tulis Inno Setup script + test | Ghaisan | 1 hari |
| Tulis script dmgbuild (opsional macOS) | Ghaisan | 0.5 hari |
| Build AppImage Linux (opsional) | Ghaisan | 0.5 hari |
| Smoke test pada 3 mesin Windows berbeda | Bimo (QA) | 2 hari |
| Tulis README.txt flashdisk + KONTAK-TIM.txt | Abhidal (UI/UX) | 0.5 hari |
| Total | | 6.5 hari kerja |

Pekerjaan dijadwalkan di Phase 2 di `06-roadmap.md` (Juni-Juli 2026).

---

## 11. Tanggal dan Pemilik

- Tanggal dokumen: 18 Mei 2026.
- Pemilik: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Status: forward-looking plan, belum diimplementasi. Eksekusi dijadwalkan di Phase 2 (Juni-Juli 2026) per `06-roadmap.md`.
