# Diagrams MedWatch

Folder ini menyimpan sumber Mermaid (`src/`) dan hasil render PNG (`png/`) untuk seluruh diagram arsitektur MedWatch. Diagram wajib menyertakan legenda notasi: legenda tertanam di dalam sumber Mermaid sebagai blok `note`, atau (untuk diagram C4 yang tidak mendukung note) sebagai sidecar `*.legend.md` di folder `src/`.

Render diagram dilakukan dengan mermaid-cli (`mmdc`) versi 11.14.0. Perintah render standar:

```bash
mmdc -i docs/diagrams/src/<file>.mmd -o docs/diagrams/png/<file>.png -w 2400 -H 1600 -s 2 -b white --quiet
```

## Indeks diagram

| Nomor | Sumber | PNG | Caption singkat |
|---|---|---|---|
| 1 | `src/c4-l1-context.mmd` | `png/c4-l1-context.png` | C4 Level 1 - System Context: tiga aktor (tenaga_kesehatan, masyarakat, admin), MedWatch, dan dua sistem eksternal (openFDA, Secret Manager). |
| 2 | `src/c4-l2-container.mmd` | `png/c4-l2-container.png` | C4 Level 2 - Container: Browser, Frontend Next.js, Backend Flask, GCS bucket, seed data, plus external openFDA dan Secret Manager. |
| 3 | `src/c4-l3-component-backend.mmd` | `png/c4-l3-component-backend.png` | C4 Level 3 - Component backend `api/`: app factory, middleware, blueprint per fitur, storage, bootstrap, dan boundary modul anggota1..5 read-only. |
| 4 | `src/deployment.mmd` | `png/deployment.png` | Diagram Deployment: Browser klien, Vercel Edge, Cloud Run asia-southeast1, GCS bucket, Secret Manager, openFDA US-East. |
| 5 | `src/use-case.mmd` | `png/use-case.png` | Diagram Use Case: tiga aktor dengan 12 use case (Login, CRUD Pasien SOAP, Cek Interaksi Obat, Lihat Drug Info, Export PDF, Trigger Scrape, Manage Users, Lihat Stats, Lihat Visualisasi, dll) plus include/extend. |
| 6 | `src/seq-login.mmd` | `png/seq-login.png` | Sequence Login: Browser ke Vercel proxy ke `auth_routes`, bcrypt verify, issue JWT, Set-Cookie httpOnly, redirect per role. |
| 7 | `src/seq-pasien-crud.mmd` | `png/seq-pasien-crud.png` | Sequence CRUD Pasien SOAP: GET (sort desc B07), POST (validasi range B03), PUT, DELETE (admin only). |
| 8 | `src/seq-safety-check.mmd` | `png/seq-safety-check.png` | Sequence Cek Interaksi Obat: pasien selection, `parse_resep_to_meds`, response berisi `pasien_active_meds` dan `severity_score` (B05 + B08). |
| 9 | `src/seq-scraping.mmd` | `png/seq-scraping.png` | Sequence Scraping Pipeline: admin memicu `/api/admin/scrape`, `anggota1.openfda.fetch` menulis JSON, jalur cached mengembalikan jumlah obat. |
| 10 | `src/seq-pdf.mmd` | `png/seq-pdf.png` | Sequence PDF Generation (B04): cabang rekam-medis vs laporan-bulanan/efek-samping/inventaris, fpdf2, binary response. |
| 11 | `src/class-backend.mmd` | `png/class-backend.png` | Class Diagram backend: FlaskApp, lima Blueprint, AuthService, StorageService, Middleware, plus entity User, Patient (composition SOAP_S/O/A/P), Drug, SideEffect, AdverseEvent, Recall, AuthToken. |
| 12 | `src/activity-pasien-intake.mmd` | `png/activity-pasien-intake.png` | Activity Diagram Pasien Intake: input nama required, optional fields, SOAP, validasi range B03, save, redirect ke list desc. |
| 13 | `src/sm-visit-lifecycle.mmd` | `png/sm-visit-lifecycle.png` | State Machine Visit Lifecycle: Draft -> Saved -> Updated -> Archived, dengan nested state Draft (Empty/Filling/Validating). |
| 14 | `src/erd-crowsfoot.mmd` | `png/erd-crowsfoot.png` | ERD Crow's Foot Logical: USER, PATIENT, VISIT_SOAP, DRUG, SIDE_EFFECT, RECALL, ADVERSE_EVENT, dengan PK/FK dan kardinalitas. |
| 15 | `src/erd-chen.mmd` | `png/erd-chen.png` | ERD Chen Conceptual: entity (solid), weak entity (dashed), relationship (diamond/hexagon), attribute (oval), key attribute (filled), multivalued (dashed oval). |

## Legend sidecar

Beberapa diagram C4 menggunakan parser khusus yang tidak mendukung `note`. Untuk diagram tersebut, legenda dirender sebagai file Markdown sidecar:

- `src/c4-l1-context.legend.md`
- `src/c4-l2-container.legend.md`
- `src/c4-l3-component-backend.legend.md`

Diagram lainnya menyertakan legenda langsung di blok `Note over` (sequence, state) atau dalam node terpisah ber-class `legend` (flowchart, activity, use case, deployment).

## Catatan render

- Resolusi: width 2400px, height 1600px, scale 2x (retina-ready, satu PNG).
- Background: putih (`-b white`) untuk konsistensi pencetakan dan dokumentasi PDF/.docx.
- Tidak ada credential atau nilai rahasia yang tampil pada label diagram. Nama resource (project `medwatch-polban-2026`, bucket `medwatch-polban-2026-state`, secret `medwatch-jwt-secret`) diperbolehkan sesuai aturan project.

## Regenerasi semua PNG

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
for f in docs/diagrams/src/*.mmd; do
  base=$(basename "$f" .mmd)
  mmdc -i "$f" -o "docs/diagrams/png/$base.png" -w 2400 -H 1600 -s 2 -b white --quiet
done
```

Tiket terkait: **W2-D05** Diagrams (Iterasi 2 Batch 2).
