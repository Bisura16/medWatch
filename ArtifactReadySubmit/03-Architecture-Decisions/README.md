# Architecture Decision Records (ADR)

Folder ini berisi ADR (Architecture Decision Records) yang mendokumentasikan
keputusan-keputusan arsitektur penting yang membentuk sistem MedWatch
sebagaimana yang dikirim (AS-BUILT, bukan SHOULD-BE) per 18 Mei 2026.

## Template

Setiap ADR menggunakan format **MADR 3.0** (Markdown Any Decision
Records), spesifikasi publik di https://adr.github.io/madr/ (Olaf
Zimmermann et al., 2023). Bagian baku per file:

1. Judul (`# ADR-XXXX: Short Title`)
2. Status, Date, Deciders
3. Context and Problem Statement
4. Decision Drivers (bullet list)
5. Considered Options (bullet list)
6. Decision Outcome (chosen option + justification)
7. Consequences (Good / Bad)
8. Confirmation (cara verifikasi keputusan bekerja, sertai
   `file:line` untuk klaim kode)
9. More Information (link, file paths, ADR terkait)

Standar referensi untuk decision records di industri: MADR (utama),
Nygard "Documenting Architecture Decisions" (2011) untuk historis,
dan IETF RFC 7322 untuk gaya tulisan.

## Daftar ADR

| ID | Judul singkat | Status |
|---|---|---|
| [ADR-0001](0001-vercel-cloud-run-security-pattern.md) | Vercel Next.js + Cloud Run Flask dengan security pattern B (server-side proxy) | accepted |
| [ADR-0002](0002-jwt-bcrypt-httponly.md) | JWT HS256 + bcrypt cost 12 + httpOnly cookie untuk autentikasi | accepted |
| [ADR-0003](0003-pasien-soap-schema-canonicalization.md) | Skema Pasien SOAP dikanonisasi ke format anggota2 (Bimo) | accepted |
| [ADR-0004](0004-drugs-com-akamai-to-openfda-pivot.md) | Pivot dari drugs.com (Akamai HTTP 403) ke openFDA REST API | accepted |
| [ADR-0005](0005-anggota3-newest-visualization-additive.md) | anggota3/NewestVisualization/ sebagai modul aditif untuk Alia | accepted |
| [ADR-0006](0006-heatmap-continuous-color-scale.md) | Heatmap memakai skala warna kontinu d3 dengan risk matrix 5 stop | accepted |
| [ADR-0007](0007-patient-list-sort-newest-first.md) | Daftar pasien diurutkan newest-first dengan parser DD-MM-YYYY dan tiebreak id descending | accepted |
| [ADR-0008](0008-pdf-endpoints-in-process-fpdf2.md) | Endpoint PDF efek-samping dan inventaris di-implementasi in-process dengan fpdf2 di api/ | accepted |
| [ADR-0009](0009-numeric-medical-field-validation.md) | Validasi field medical numerik di client dan server dengan composite parser untuk tekanan_darah | accepted |
| [ADR-0010](0010-formdata-login-submit.md) | Submit login membaca username dan password dari FormData untuk mencegah autofill race | accepted |

## Konvensi penomoran dan status

- Nomor monotonik 4 digit, tidak pernah didaur ulang.
- Status valid: `proposed`, `accepted`, `deprecated`, `superseded by ADR-YYYY`.
- ADR yang sudah landed (kode sudah merge ke main) ditandai `accepted`.
- ADR yang digantikan oleh ADR lain tetap di-checkin, statusnya berubah
  menjadi `superseded by ADR-YYYY` dan memuat ringkasan alasan
  supersession.

## Cross-reference

ADR-0001 dan ADR-0002 saling melengkapi (security pattern + JWT
cookie). ADR-0003 menjadi landasan ADR-0007 (parser dan tiebreak)
dan ADR-0009 (validasi field). ADR-0004 menjadi landasan ADR-0005
(modul visualisasi yang mengkonsumsi data hasil pivot). ADR-0006
mereferensikan palet keparahan yang dipakai oleh ADR-0005.

## Tracking link

- Standar dokumentasi keseluruhan dikutip di
  `~/Documents/FrontendMedWatch/.mission/waves/wave-02-plan.md`
  section "Standards to cite (by number)".
- Wave plan terkait: W2-D04 (ADRs) dalam wave-02-plan.md.
