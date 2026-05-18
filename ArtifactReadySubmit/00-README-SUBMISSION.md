---
title: MedWatch Submission Package - Indeks Penyerahan
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048) bersama Kelompok B5
date: 2026-05-18
---

# MedWatch Submission Package

Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung, Kelas 1B-D4, Semester 2 TA 2025/2026.
Mata kuliah: Proyek 1 Pengembangan Perangkat Lunak Desktop.
Dosen pembimbing: Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana.
Submission Deadline: 25 Mei 2026.

## Ringkasan

Paket ini adalah salinan lengkap (bukan symlink) seluruh artefak dokumentasi MedWatch versi rilis Wave 5, disusun dalam sepuluh subfolder bernomor agar mudah dibuka dan dinilai. Setiap dokumen utama disediakan dalam format Markdown serta versi Word (.docx) untuk kebutuhan cetak. Diagram disediakan dalam dua bentuk: sumber Mermaid (.mmd) yang dapat di-render ulang dan PNG hasil render dengan resolusi tinggi.

## Tim

| Nama | NIM | Peran | Modul | Tanggung Jawab Dokumen Utama |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader | anggota1 (scraping) | Koordinasi PRD, integrasi backend, README backend, semua ADR keputusan teknis lintas modul |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Test Plan, Test Cases AUTH dan PASIEN (eksekusi terbesar), Defect Log |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi) | SRS, RTM, Test Cases VIZ dan HEATMAP |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | Test Cases SAFETY dan DRUG, dokumentasi algoritma severity weighting |
| Abhidal Muhammad Gazza | 251524032 | UI/UX | anggota5 (PDF dan auth) | User Manual, Quick Start, Test Cases PDF dan SCREEN, UX login |

## Daftar Artefak per Folder

### 01-Proposal-PRD

Dokumen perencanaan dan spesifikasi mengikuti standar IEEE 830-1998 untuk SRS dan IEEE 1016-2009 untuk SDD. PRD ditulis sebagai dokumen kontrak fitur level proyek mengikuti praktik MADR (Markdown Architectural Decision Records) untuk traceability.

- `PRD.md` dan `PRD.docx` - Product Requirements Document (kebutuhan produk, problem statement, success metrics). Disusun oleh Ghaisan, ditelaah seluruh anggota.
- `SRS.md` dan `SRS.docx` - Software Requirements Specification mengikuti IEEE 830-1998 (functional requirement FR-001 sampai FR-072, non-functional NFR, use case). Owner: Alia Ardani (251524035).
- `SDD.md` dan `SDD.docx` - Software Design Description mengikuti IEEE 1016-2009 (arsitektur, modul, antarmuka, data design). Owner: Ghaisan Khoirul Badruzaman (251524048).

### 02-Diagrams

Diagram disusun mengikuti C4 model (Simon Brown) untuk arsitektur, UML 2.5 untuk use case dan sequence dan class dan state, serta notasi Chen dan Crow's Foot untuk Entity-Relationship. Sumber Mermaid dan PNG hasil render terlampir bersama berkas legend di setiap diagram utama.

- 15 berkas `.mmd` sumber Mermaid dan 15 berkas `.png` hasil render (C4 L1, C4 L2, C4 L3 component, use case, class, ERD Chen, ERD Crow's Foot, sequence login, sequence pasien CRUD, sequence safety check, sequence PDF, sequence scraping, activity pasien intake, state machine visit lifecycle, deployment).
- 18 berkas PNG diagram tambahan format awal (01..18) dari `_generate.py` mencakup C4 context, use case, class, sequence, state, ER, deployment, network topology, dan structure chart per anggota.
- 4 berkas legend `.legend.md` (c4-l1-context, c4-l2-container, c4-l3-component-backend) berisi penjelasan notasi.
- `README.md` indeks subfolder diagram.

### 03-Architecture-Decisions

Architecture Decision Records (ADR) mengikuti format MADR (Markdown Any Decision Records, Nygard style). Setiap ADR berisi konteks, opsi, keputusan, konsekuensi, dan tanggal.

- `0001-vercel-cloud-run-security-pattern.md` Pemilihan pola proxy Vercel di depan Cloud Run untuk httpOnly cookie.
- `0002-jwt-bcrypt-httponly.md` Pilihan JWT bcrypt dan httpOnly cookie untuk auth.
- `0003-pasien-soap-schema-canonicalization.md` Kanonikalisasi skema pasien SOAP.
- `0004-drugs-com-akamai-to-openfda-pivot.md` Keputusan pivot dari drugs.com (Akamai blocked) ke openFDA.
- `0005-anggota3-newest-visualization-additive.md` Tambahan modul visualisasi additive untuk anggota3.
- `0006-heatmap-continuous-color-scale.md` Skala warna kontinu untuk heatmap.
- `0007-patient-list-sort-newest-first.md` Urutan daftar pasien terbaru di atas (fix B07).
- `0008-pdf-endpoints-in-process-fpdf2.md` Pemilihan fpdf2 in-process untuk PDF.
- `0009-numeric-medical-field-validation.md` Validasi numerik field medis (umur, tekanan darah).
- `0010-formdata-login-submit.md` Submit login dengan FormData (fix B09).
- 10 berkas `.docx` setara plus `ADR-Index.docx` dan `README.md` indeks.

### 04-API-DataModel

Spesifikasi API dan kamus data mengikuti OpenAPI/REST style. Data dictionary mendaftar setiap entitas, field, tipe, batasan, dan sumber.

- `API.md` dan `API.docx` - Daftar endpoint REST, request, response, error model. Owner: Ghaisan.
- `DATA-DICTIONARY.md` dan `DATA-DICTIONARY.docx` - Kamus data untuk seluruh entitas (Pasien, User, ReactionTerm, Recall, dst).

### 05-Testing

Dokumentasi pengujian black-box mengikuti IEEE 829 untuk struktur, ISO/IEC/IEEE 29119-3 untuk template test plan dan test cases, serta teknik Equivalence Partitioning (EP), Boundary Value Analysis (BVA), Decision Table, State Transition, Use Case Testing, dan Error Guessing.

- `test-plan.md` dan `test-plan.docx` - Master test plan (scope, strategy, environment, schedule 12-18 Mei 2026, exit criteria). Owner: Bimo Surya Anggara (251524040).
- `test-cases.md` dan `test-cases.docx` - 80 case TC-MOD-NNN lintas modul AUTH, PASIEN, SAFETY, DRUG, VIZ, PDF, ADMIN, SCRAPE, HEATMAP, SCREEN. Tester didistribusikan per anggota sesuai modul.
- `rtm.md` dan `rtm.docx` - Requirements Traceability Matrix (FR ke TC). Owner: Alia Ardani (251524035).
- `defect-log.md` dan `defect-log.docx` - Log defek dengan ID W4-HUNT historis dan W5-RT-NNN baru. Owner: Bimo.
- `test-summary.md` dan `test-summary.docx` - Ringkasan eksekusi dengan persentase validasi formula `(Sum pass / Sum total) * 100%` dan skala Arikunto (86-100 sangat baik, 71-85 baik, 56-70 cukup, 41-55 kurang, kurang dari 41 sangat kurang).
- Subfolder `evidence/` berisi 80 transcript curl per test case sebagai bukti eksekusi nyata.

### 06-User-Manual

Buku panduan pengguna mengikuti ISO/IEC/IEEE 26514:2018 untuk struktur user documentation.

- `USER-MANUAL.md` dan `USER-MANUAL.docx` - Panduan lengkap per peran (bidan, masyarakat, admin) dengan tangkapan layar dan skenario lengkap. Owner: Abhidal Muhammad Gazza (251524032).
- `QUICK-START.md` - Lembar satu halaman untuk dosen dan peserta demo, ditulis bersama Wave 5 (URL live, akun demo, skenario per peran).

### 07-As-Built

Dokumen As-Built mengikuti praktik 19-section dengan Deviations table eksplisit (ISO/IEC/IEEE 15289:2019 informational items). Mencerminkan kondisi sistem pasca Wave 5 fixes (H07-1 dan kawan-kawan).

- `AS-BUILT.md` dan `AS-BUILT.docx` - Snapshot arsitektur, modul, dependensi, deviasi terhadap spek, dan known issues residual.

### 08-Security

Dokumentasi keamanan mengikuti OWASP ASVS sebagai checklist, threat model STRIDE, dan praktik per-control documentation.

- `SECURITY.md` dan `SECURITY.docx` - Threat model STRIDE, residual risk register R1..R8 (H07-1 sudah closed di Wave 5), control listing per OWASP A01..A10.
- `W4-SEC-summary.md` - Ringkasan satu halaman pemindaian keamanan Wave 4 dengan jumlah temuan per severity dan order remediasi. Tidak memuat nilai kredensial apapun. Owner: Ghaisan.

### 09-ProductionGrade-Plan

Rencana implementasi produksi tujuh dokumen yang merancang penurunan dari demo akademik ke aplikasi desktop offline siap produksi.

- `00-overview.md` Ringkasan rencana.
- `01-production-PRD.md` PRD produksi (target pasar nyata, success metric).
- `02-offline-implementation-plan.md` Rencana implementasi offline (SQLite, Electron, file storage lokal).
- `03-packaging-and-distribution.md` Strategi packaging (PyInstaller, MSI, signed installer) dengan berkas `medwatch.spec` PyInstaller terlampir.
- `04-hardening-plan.md` Rencana hardening keamanan dan reliability.
- `05-test-and-acceptance-plan.md` Rencana uji penerimaan untuk produksi.
- `06-roadmap.md` Roadmap rilis enam bulan ke depan.
- 7 berkas `.docx` setara, satu per dokumen.

### 10-README-and-Misc

Berkas pendukung repo, README, lisensi, dan dokumen tambahan yang tidak masuk kategori utama.

- `Backend-README.md` - README utama repo backend (deskripsi proyek, akses URL live, dependensi, cara menjalankan, sumber data, kontribusi).
- `Frontend-README.md` - README utama repo frontend Next.js (showcase web, arsitektur proxy, dependensi).
- `Backend-CHANGELOG.md` dan `Frontend-CHANGELOG.md` - Catatan rilis per wave (Wave 0 sampai Wave 5).
- `Backend-LICENSE` dan `Frontend-LICENSE` - Lisensi MIT untuk kedua repo.
- `Backend-CONTRIBUTING.md` dan `Frontend-CONTRIBUTING.md` - Panduan kontribusi.
- `Backend-INSTALL.md` dan `Backend-INSTALL.docx` - Panduan instalasi penuh (dev, Docker, deploy Cloud Run).
- `Backend-INTEGRATION_GUIDE.md` - Panduan integrasi backend.
- `Backend-SCOPE_NOTE.md` - Catatan ruang lingkup misi pengembangan.
- `Backend-SECURITY_AUDIT.md` - Catatan audit keamanan internal.
- `Deliverable-Manifest-README.md` - Manifest folder deliverable internal.

## Tonggak Pengembangan

- Wave 0 Bootstrap mission scaffold (folder `.mission/`, manifest, log).
- Wave 1 Perbaikan defek B01 sampai B11, akuisisi data openFDA nyata (1850 reaction terms, 6000 recalls), modul additive `anggota3/NewestVisualization/` dengan 5 PNG visualisasi.
- Wave 2 Dokumentasi industri-grade 14 deliverable (PRD, SRS, SDD, API, DATA-DICTIONARY, INSTALL, USER-MANUAL, AS-BUILT, SECURITY, ADR 10 dokumen, ProductionGrade-ImplementationPlan).
- Wave 3 Code commenting (docstring Python plus TSDoc) dan tidy repo (CHANGELOG, CONTRIBUTING, LICENSE, .editorconfig).
- Wave 4 Pemindaian keamanan plus bug-hunt 17 kategori (W4-SEC, W4-HUNT).
- Wave 5 Remediasi defek Critical dan Major plus eksekusi suite uji nyata plus assembly `ArtifactReadySubmit/` plus FINAL-REPORT.

## Catatan Penyerahan

- Semua dokumen Markdown utama disertai versi .docx untuk kebutuhan cetak.
- Diagram disediakan sebagai sumber Mermaid plus PNG hasil render. Berkas legend `.legend.md` melampirkan penjelasan notasi setiap diagram utama.
- Persentase validasi pengujian lihat `05-Testing/test-summary.md`.
- Defek terbuka residual didokumentasikan di `07-As-Built/AS-BUILT.md` Section 15 (Known Issues).
- Hak cipta: Kelompok B5 D4 Teknik Informatika POLBAN (MIT License, lihat `10-README-and-Misc/Backend-LICENSE` dan `10-README-and-Misc/Frontend-LICENSE`).
- Akses cepat untuk dosen lihat `06-User-Manual/QUICK-START.md`.
- Posisi keamanan saat ini lihat `08-Security/W4-SEC-summary.md`.
