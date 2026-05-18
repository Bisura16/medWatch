---
title: Roadmap MedWatch dari MVP Akademik ke Production v1.0
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
  - ProductionGrade-ImplementationPlan/05-test-and-acceptance-plan.md
---

# 06 - Roadmap MedWatch dari MVP Akademik ke Production v1.0

Roadmap ini memetakan fase-fase implementasi dari titik nol pasca-submission akademik 25 Mei 2026 sampai rilis production v1.0 yang ditargetkan untuk Oktober 2026. Setiap fase memiliki goal terdefinisi, deliverable, dan exit criteria. Sequencing dijaga agar tidak ada fase yang block fase berikutnya secara fundamental.

---

## 1. Ringkasan Timeline

| Phase | Bulan | Fokus | Status |
|---|---|---|---|
| Phase 0 | Sampai 25 Mei 2026 | MVP akademik (5 wave mission) | SELESAI saat dokumen ini ditulis |
| Phase 1 | 26 Mei - 31 Mei 2026 | Cleanup pasca-submission + close B-WAVE1-BUILD-1 | Belum mulai |
| Phase 2 | Juni - Juli 2026 | Offline packaging + alpha tester | Belum mulai |
| Phase 3 | Agustus 2026 | Production hardening | Belum mulai |
| Phase 4 | September 2026 | UAT bidan Faskes 1 | Belum mulai |
| Phase 5 | Oktober 2026 | Rilis v1.0 ke klien pertama | Belum mulai |

Total: 5 bulan kalender dari 26 Mei 2026 ke akhir Oktober 2026. Tim 1-5 orang (Ghaisan core full-time; anggota lain sesuai availability pasca-mata-kuliah).

---

## 2. Phase 0: MVP Akademik (Selesai per 25 Mei 2026)

Phase 0 adalah ruang lingkup mission yang sedang berjalan (Wave 0-5 di `.mission/plan.md`). Tujuan: software MedWatch siap dikumpulkan ke dosen pada 25 Mei 2026 sebagai realisasi tugas Proyek 1 Pengembangan Perangkat Lunak Desktop.

### 2.1 Deliverable Phase 0

- Modul `anggota1`..`anggota5` siap.
- 11 defect register B01-B11 ditutup di Wave 1.
- Modul tambahan `anggota3/NewestVisualization/` selesai.
- Data nyata openFDA: 74 rekord adverse-event + 6000 rekord recall (per `wc -l` 18 Mei 2026).
- Dokumentasi lengkap di Wave 2: PRD, SRS, SDD, ADR, API doc, data dictionary, install/deploy, security, user manual, As-Built, diagrams.
- Folder ini (`ProductionGrade-ImplementationPlan/`) selesai sebagai bagian Wave 2.
- ArtifactReadySubmit/ folder konsolidasi siap untuk dosen di Wave 5.

### 2.2 Status saat dokumen ditulis (18 Mei 2026)

- Wave 0: SELESAI (bootstrap mission).
- Wave 1: SELESAI (B01-B11 fix + viz module + openFDA real data).
- Wave 2: SEDANG BERJALAN (dokumentasi termasuk dokumen ini).
- Wave 3-5: belum mulai. Estimasi selesai 24 Mei 2026 (mid-night sebelum submission).

### 2.3 Exit Criteria Phase 0

- All mission waves PASS audit.
- ArtifactReadySubmit/ folder konsolidasi tersedia dengan minimum 10 subfolder per acceptance Wave 5.
- Final commit di-tag `v0.1.0-academic-submission`.
- Mission state.json status = "complete".

---

## 3. Phase 1: Cleanup Pasca-Submission (26 Mei - 31 Mei 2026)

### 3.1 Goal

Tutup loose ends teknis yang ter-defer di Phase 0 karena fokus submission. Pastikan repository dalam state production-ready untuk Phase 2.

### 3.2 Deliverable

1. **Close B-WAVE1-BUILD-1** (open blocker dari Wave 1 per `.mission/state.json:70`):
   - Install Node 22 LTS via fnm/nvm pada laptop Ghaisan.
   - Re-run `npm install && npm run build && npm run start` di FrontendMedWatch.
   - Re-verify Playwright clickthrough untuk login flow (yang ter-defer ke Wave 5 per state.json:77).
   - Confirm SSR routes tetap bekerja.
2. **Repo tidy lanjutan**:
   - Remove `__pycache__/` files yang masih tertinggal di working tree (lihat git status).
   - Audit `.gitignore` untuk pastikan tidak ada bocoran pasca Wave 5.
3. **Decision: Cloud Run demo decommissioning**:
   - Apakah cloud demo dipertahankan untuk akses dosen post-submission? Diskusi tim minggu pertama Juni.
   - Jika decommissioned: `gcloud run services delete medwatch-api --region asia-southeast1` + delete bucket `medwatch-polban-2026-state` (atau retain dengan IAM lockdown, lihat `04-hardening-plan.md` Section 9).
   - Jika dipertahankan: hardening H7 dieksekusi sebelum production v1.0.

### 3.3 Exit Criteria

- B-WAVE1-BUILD-1 closed (login Playwright PASS).
- Cloud demo decision tertulis di `.mission/log.md`.
- Repo bersih: `git status` kosong selain branch metadata.
- Tag `v0.2.0-post-submission` di-set.

### 3.4 Time Budget

5 hari kerja (26-30 Mei 2026, 1 hari buffer Sabtu).

---

## 4. Phase 2: Offline Packaging + Alpha Tester (Juni - Juli 2026)

### 4.1 Goal

Implementasi rencana `02-offline-implementation-plan.md` dan `03-packaging-and-distribution.md`. Aplikasi dapat di-install dari installer offline di workstation Windows bersih.

### 4.2 Deliverable

1. **Storage migration**:
   - File `tools/migrate_json_to_sqlite.py` dan adapter `api/storage_sqlite.py` (lihat `02-offline-implementation-plan.md` Section 4).
   - Migration tested pada copy DB, tidak overwrite original.
2. **Snapshot loader**:
   - First-run logic copy `<install_dir>/data/anggota1/*` ke `<appdata>/data/anggota1/*`.
   - `<appdata>/data/snapshot-info.json` dengan field `date`, `record_count`.
3. **Lazy import refactor**:
   - File `api/categori_constants.py` (additive) berisi `KATEGORI_MAP` salinan.
   - Wrapper di `api/bootstrap.py` lazy-load `anggota1`.
4. **PyInstaller build**:
   - `ProductionGrade-ImplementationPlan/build/medwatch.spec` di-execute.
   - Output `dist/MedWatch/` dengan size kurang dari 280 MB.
   - Smoke test pada Windows 11 VM PASS.
5. **Inno Setup installer**:
   - File `build/medwatch.iss` di-author.
   - Output `installer_output/MedWatchSetup-1.0.0-alpha.exe`.
   - Test instalasi pada 3 mesin Windows berbeda PASS.
6. **Alpha tester**:
   - Cari 1 alpha tester (bidan atau tenaga IT klinik) untuk feedback awal sebelum UAT formal di Phase 4.
   - Bidan tidak melakukan UAT lengkap; cukup install + 30 menit penggunaan + feedback bebas.
   - Feedback didokumentasikan di `docs/feedback/alpha-YYYY-MM-DD.md`.

### 4.3 Exit Criteria

- Bundle PyInstaller satu-folder bekerja offline pada 3 mesin Windows.
- Installer Inno Setup bekerja end-to-end.
- Alpha tester telah memberi feedback awal.
- Tag `v0.5.0-alpha` di-set.

### 4.4 Time Budget

8 minggu (Juni-Juli 2026). Detail per `02-offline-implementation-plan.md` Section 10 (4.5 hari) + `03-packaging-and-distribution.md` Section 10 (6.5 hari) = 11 hari kerja teknis + buffer alpha tester recruitment + iteration.

---

## 5. Phase 3: Production Hardening (Agustus 2026)

### 5.1 Goal

Implementasi rencana `04-hardening-plan.md` H1-H8 + tambahan pydantic schema, Indonesian error messages, pre-generated viz cache. Postur OWASP Top 10 menjadi 10/10 PASS.

### 5.2 Deliverable

1. **H1 flask-limiter** untuk `/api/auth/login`.
2. **H2 structured JSON logs** ke `<appdata>/logs/audit.log` + audit table SQLite.
3. **H3 CSRF token** (jika web demo dipertahankan dari Phase 1 decision).
4. **H4 JWT dual-key rotation procedure**.
5. **H5 GitHub Actions security scan** workflow.
6. **H6 SQLite atau atomic-rename**: sudah selesai di Phase 2 secara design; verifikasi acceptance.
7. **H7 Cloud Run IAM lockdown** (jika cloud demo dipertahankan).
8. **H8 cleanup archived deps** di frontend.
9. **Pydantic schema migration** untuk validasi input.
10. **Indonesian error messages** dictionary di `api/i18n/messages_id.py`.
11. **Pre-generated viz cache** untuk dashboard first-run speed.

### 5.3 Exit Criteria

- Regression suite REG-H1..REG-H8 PASS.
- OWASP Top 10 mapping di `04-hardening-plan.md` Section 12 menjadi 10/10 PASS.
- Tag `v0.8.0-hardened` di-set.

### 5.4 Time Budget

4 minggu (Agustus 2026). Detail per `04-hardening-plan.md` Section 13 (9 hari kerja teknis) + buffer testing.

---

## 6. Phase 4: UAT Bidan Faskes 1 (September 2026)

### 6.1 Goal

Validasi langsung dengan bidan dari Faskes 1 yang nyata bahwa MedWatch dapat dipakai operasional sehari-hari tanpa pendamping developer. Hasil UAT menjadi gate sebelum release v1.0.

### 6.2 Deliverable

1. **Recruit bidan UAT** sesuai kriteria di `05-test-and-acceptance-plan.md` Section 3.1.
2. **Persiapan UAT**:
   - Hard copy User Manual PDF.
   - Flashdisk distribusi MedWatch v0.9.0-rc.
   - Synthetic patient data demo untuk warming up (5 pasien sample).
   - Form survey kepuasan.
3. **Sesi UAT**:
   - 1 sesi 4 jam, disediakan ruangan tenang.
   - Tim observer (Bimo + Alia + Ghaisan) di belakang, tidak intervensi kecuali ditanya.
   - Bidan menyelesaikan 10 task per `05-test-and-acceptance-plan.md` Section 3.2.
   - Stopwatch per task; observasi qualitative dicatat oleh observer.
4. **Analisis UAT**:
   - Completion rate target minimal 8/10.
   - Survey kepuasan target rata-rata minimal 4.0.
   - Defect list dengan severity Critical/Major/Minor.
5. **Iterasi pasca-UAT**:
   - Fix semua Critical bug (jika ada).
   - Fix Major bug atau dokumentasikan workaround.
   - Tolerate maksimal 2 Minor bug.

### 6.3 Exit Criteria

- UAT sesi selesai dan terdokumentasi di `docs/uat/`.
- Zero Critical bug remaining.
- Maksimal 2 Minor bug remaining (didokumentasi di Known Issues).
- Survey kepuasan rata-rata minimal 4.0.
- Tag `v0.9.0-rc-uat-passed` di-set.

### 6.4 Time Budget

4 minggu (September 2026). 1 minggu recruit + 1 minggu UAT session prep + 1 hari sesi + 2 minggu iterasi fix.

---

## 7. Phase 5: Rilis v1.0 ke Klien Pertama (Oktober 2026)

### 7.1 Goal

Release production v1.0 dan distribusi flashdisk ke klien pertama yang sudah bersedia menjadi early adopter. Klien pertama dapat berasal dari koneksi UAT atau jaringan alumni POLBAN.

### 7.2 Deliverable

1. **Build v1.0.0 final**:
   - Tag `v1.0.0` di repo.
   - Build PyInstaller + Inno Setup pada 2 mesin developer untuk verifikasi reproducibility.
   - SHA-256 hash setiap artifact.
2. **Distribution package**:
   - Flashdisk master image siap.
   - User Manual PDF, README.txt, KONTAK-TIM.txt finalisasi.
   - Minimal 3 flashdisk fisik disiapkan (1 untuk klien, 2 untuk arsip + backup).
3. **Sign-off**:
   - Sign-off form `docs/release/v1.0.0-signoff.md` ditandatangani 5 anggota tim.
   - Persetujuan dosen pendamping (informal, tidak block release teknis).
4. **Penyerahan**:
   - SOP penyerahan (lihat `03-packaging-and-distribution.md` Section 8.3) dieksekusi.
   - Klien menerima paket dengan briefing 15 menit + tanya jawab.
   - Pembuatan akun login awal.
   - Backup pertama (kosong).
5. **Support channel aktif**:
   - Email tim atau WhatsApp Business sudah live.
   - Tim siap merespon dalam SLA 3 hari kerja untuk Critical/Major.
6. **Versi public** (opsional):
   - Repo GitHub MedWatch ditandai release dengan changelog publik.
   - Jika tim memutuskan open source, lisensi MIT atau Apache 2.0 di-pilih (dibahas saat sign-off).

### 7.3 Exit Criteria

- Klien pertama menerima paket dan sudah berhasil install.
- Klien melakukan minimal 1 hari operasional tanpa eskalasi Critical bug.
- Tim siap merespon pertanyaan/feedback klien.
- Tag `v1.0.0` di repo dan dokumentasi release di-publish.
- Roadmap pasca-v1.0 (versi 1.1, 1.2, ...) draft tersedia.

### 7.4 Time Budget

4 minggu (Oktober 2026). 1 minggu finalisasi build + 1 minggu persiapan flashdisk + 1 minggu penyerahan + 1 minggu support standby.

---

## 8. Risiko Roadmap dan Mitigasi

| ID | Risiko | Likelihood | Dampak | Mitigasi |
|---|---|---|---|---|
| RM-R1 | Tim B5 tidak available pasca-25 Mei karena fokus akademik lain | Tinggi | Major | Roadmap di-eksekusi oleh subset yang available; Ghaisan core full-time |
| RM-R2 | Tidak menemukan bidan UAT pada waktunya | Sedang | Major | Recruitment dimulai paling lambat 2 minggu sebelum Phase 4; backup melalui koordinator dosen |
| RM-R3 | Code-signing certificate tidak terjangkau di Phase 5 | Sedang | Minor | Sudah didokumentasikan sebagai out-of-scope di `03-packaging-and-distribution.md` Section 6 |
| RM-R4 | Klien pertama tidak ada di akhir Oktober | Sedang | Major | v1.0 tetap di-release ke arsip tim sebagai milestone; klien dicari di Q4 2026 atau Q1 2027 |
| RM-R5 | Bug Critical ditemukan setelah klien instalasi | Sedang | Critical | Rollback plan di `05-test-and-acceptance-plan.md` Section 6 dieksekusi; hotfix v1.0.1 |
| RM-R6 | openFDA mengubah skema response | Rendah | Major | Snapshot saat build, tidak runtime; ada waktu untuk adaptasi sebelum next release |
| RM-R7 | Hardware workstation klien tidak memenuhi minimum spec | Sedang | Minor | Spec minimum didokumentasikan di User Manual; klien dipastikan saat pre-sales |
| RM-R8 | Pencurian flashdisk distribusi | Rendah | Minor | Flashdisk berisi data dummy; SHA-256 verifikasi mencegah tampering |

---

## 9. Komunikasi dan Reporting

### 9.1 Selama Phase 1-5

- Update mingguan ke `.mission/log.md` setiap Sabtu.
- Decision logs di `docs/decisions/YYYY-MM-DD-<topic>.md` untuk keputusan signifikan (mis. Cloud Run decommissioning, alpha tester selection).
- Bug register di `docs/bugs-post-v0.1.0.md` melanjutkan tradisi `.mission/bugs.md`.

### 9.2 Saat Phase 5 release

- Release notes di `CHANGELOG.md`.
- Catatan transfer ke klien di `docs/customer/<initial>.md`.
- Public announcement (jika repo open-source) via README + Twitter/X tim (opsional).

---

## 10. Versi Setelah 1.0

Roadmap pasca-v1.0 di-draft saat sign-off. Inisial gambaran:

| Versi | Target | Fokus |
|---|---|---|
| 1.0.x patch | Sesuai kebutuhan klien | Bug fix Minor |
| 1.1 | Q1 2027 | Fitur tambahan dari feedback klien (mis. Excel export, custom branding) |
| 1.2 | Q2 2027 | Performance tuning untuk klien dengan 5000+ pasien |
| 2.0 | Q4 2027+ | Re-evaluate multi-Faskes sync, mobile companion app jika ada permintaan |

Item-item ini bersifat tentatif dan akan di-finalize berdasarkan kebutuhan klien nyata.

---

## 11. Sign-Off Roadmap

Roadmap ini di-approve oleh:

- Project Leader: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Optional review oleh dosen pendamping (Aprianti Nanda Sari) saat presentasi Wave 2.

Roadmap di-revisit pada akhir setiap fase untuk konfirmasi tetap relevan dengan kondisi tim dan ketersediaan klien.

---

## 12. Tanggal dan Pemilik

- Tanggal dokumen: 18 Mei 2026.
- Pemilik: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Status: forward-looking plan. Eksekusi mulai 26 Mei 2026 (Phase 1).
