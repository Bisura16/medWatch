---
title: MedWatch - Paket Hand-over Dokumen (.docx)
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048)
date: 2026-05-18
---

# MedWatch - Paket Hand-over Dokumen (.docx)

Folder ini berisi versi Microsoft Word (.docx) dari dokumen dosen-facing MedWatch. Sumber otoritatif tetap berkas Markdown di `docs/` (atau `ProductionGrade-ImplementationPlan/` di akar repo backend); .docx di sini adalah salinan hasil konversi yang dipakai untuk hand-over dan pengarsipan formal.

Konversi dilakukan dengan `pandoc 3.9.0.2` (binari `/opt/homebrew/bin/pandoc`) memakai flag berikut.

```
pandoc <sumber>.md \
  -o /Users/ghaisan/Documents/MedWatchIntegration/medWatch/docs/deliverable/<nama>.docx \
  --resource-path=.:./diagrams/png \
  --standalone \
  --toc \
  --metadata title="<judul>"
```

Catatan teknis:

- Setiap berkas .docx dibuat ulang dari Markdown terbaru pada 18 Mei 2026 (Wave 2 - tiket W2-DOCX).
- Bahasa Indonesia dipertahankan dalam UTF-8.
- Daftar isi (`--toc`) otomatis disisipkan di awal setiap dokumen panjang.
- USER-MANUAL menyertakan placeholder gambar; ketika tangkapan layar tersedia, jalankan ulang konversi.
- Versi .docx untuk dokumen pengujian (test plan, test cases, RTM, defect log, test summary) diproduksi pada Wave 5; tidak termasuk dalam tiket ini.

## Manifest dokumen

| Nama berkas .docx | Sumber Markdown | Baris sumber | Ukuran .docx |
|---|---|---|---|
| PRD.docx | docs/PRD.md | 385 | 27 KB |
| SRS.docx | docs/SRS.md | 838 | 43 KB |
| SDD.docx | docs/SDD.md | 894 | 42 KB |
| AS-BUILT.docx | docs/AS-BUILT.md | 1014 | 52 KB |
| USER-MANUAL.docx | docs/USER-MANUAL.md | 528 | 27 KB |
| SECURITY.docx | docs/SECURITY.md | 464 | 32 KB |
| API.docx | docs/API.md | 1566 | 35 KB |
| DATA-DICTIONARY.docx | docs/DATA-DICTIONARY.md | 522 | 26 KB |
| INSTALL.docx | docs/INSTALL.md | 632 | 23 KB |
| ADR-Index.docx | docs/adr/README.md | 65 | 14 KB |
| ADR-0001-vercel-cloud-run-security-pattern.docx | docs/adr/0001-vercel-cloud-run-security-pattern.md | 81 | 13 KB |
| ADR-0002-jwt-bcrypt-httponly.docx | docs/adr/0002-jwt-bcrypt-httponly.md | 80 | 13 KB |
| ADR-0003-pasien-soap-schema-canonicalization.docx | docs/adr/0003-pasien-soap-schema-canonicalization.md | 77 | 13 KB |
| ADR-0004-drugs-com-akamai-to-openfda-pivot.docx | docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md | 130 | 14 KB |
| ADR-0005-anggota3-newest-visualization-additive.docx | docs/adr/0005-anggota3-newest-visualization-additive.md | 88 | 13 KB |
| ADR-0006-heatmap-continuous-color-scale.docx | docs/adr/0006-heatmap-continuous-color-scale.md | 87 | 13 KB |
| ADR-0007-patient-list-sort-newest-first.docx | docs/adr/0007-patient-list-sort-newest-first.md | 80 | 13 KB |
| ADR-0008-pdf-endpoints-in-process-fpdf2.docx | docs/adr/0008-pdf-endpoints-in-process-fpdf2.md | 81 | 13 KB |
| ADR-0009-numeric-medical-field-validation.docx | docs/adr/0009-numeric-medical-field-validation.md | 92 | 13 KB |
| ADR-0010-formdata-login-submit.docx | docs/adr/0010-formdata-login-submit.md | 87 | 13 KB |
| ProductionGrade-00-overview.docx | ProductionGrade-ImplementationPlan/00-overview.md | 181 | 18 KB |
| ProductionGrade-01-production-PRD.docx | ProductionGrade-ImplementationPlan/01-production-PRD.md | 234 | 19 KB |
| ProductionGrade-02-offline-implementation-plan.docx | ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md | 280 | 21 KB |
| ProductionGrade-03-packaging-and-distribution.docx | ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md | 460 | 23 KB |
| ProductionGrade-04-hardening-plan.docx | ProductionGrade-ImplementationPlan/04-hardening-plan.md | 476 | 24 KB |
| ProductionGrade-05-test-and-acceptance-plan.docx | ProductionGrade-ImplementationPlan/05-test-and-acceptance-plan.md | 337 | 20 KB |
| ProductionGrade-06-roadmap.docx | ProductionGrade-ImplementationPlan/06-roadmap.md | 324 | 19 KB |

Total: 27 berkas .docx.

## Verifikasi pembukaan

Berkas .docx ini diuji melalui konversi pandoc tanpa eror; pandoc 3.x menghasilkan format OOXML yang kompatibel dengan Microsoft Word 2016+, Word Online, dan LibreOffice 7+.

## Reproduksi

Untuk regenerasi seluruh paket setelah Markdown sumber diperbarui:

```
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
mkdir -p docs/deliverable
# Lakukan untuk setiap berkas seperti contoh perintah di atas.
```

Dokumen induk: lihat `docs/AS-BUILT.md` untuk gambaran sistem hasil-akhir Wave 1.
