# Changelog

All notable changes to this project will be documented here. Format per Keep a Changelog (https://keepachangelog.com). Versioning per Semantic Versioning (https://semver.org).

## [Unreleased]

### Added
- Wave 0 (2026-05-18): autonomous mission scaffold, 11 Opus-4.7 agents, secret-scan hook.
- Wave 1 (2026-05-18): real openFDA acquisition module anggota1/openfda/. New anggota3/NewestVisualization/.
  Fixes B01..B11 across both repos (admin nav, lihat-semua, patient validation, multi-type PDF, safety active-meds, login manual, heatmap continuous scale, real admin KPIs).
- Wave 2 (2026-05-18): industry-grade documentation set (PRD, SRS, SDD, 10 ADRs, API, DATA-DICTIONARY, INSTALL, USER-MANUAL, SECURITY, AS-BUILT, 15 diagrams, 27 docx).
- Wave 3 (2026-05-18): docstrings across api/ integrasi/ and additive modules; CHANGELOG CONTRIBUTING LICENSE editorconfig .gitignore .gitattributes env example.
- Wave 5 (2026-05-18): black-box test documentation suite under `docs/testing/`: `test-plan.md`, `test-cases.md` with TC-MOD-NNN identifiers covering AUTH, PASIEN, SAFETY, DRUG, VIZ, PDF, ADMIN, SCRAPE, HEATMAP, SCREEN modules, `rtm.md` requirement traceability matrix, `defect-log.md` including W4-HUNT historical entries, `test-summary.md` with persentase validasi plus Arikunto scale verdict. Five matching `.docx` deliverables under `docs/deliverable/`.
- Wave 5 (2026-05-18): `ArtifactReadySubmit/` hand-over folder organized into 10 numbered subfolders (01-Proposal-PRD, 02-Diagrams, 03-Architecture-Decisions, 04-API-DataModel, 05-Testing, 06-User-Manual, 07-As-Built, 08-Security, 09-ProductionGrade-Plan, 10-README-and-Misc) plus `00-README-SUBMISSION.md` index identifying every artifact by team member NIM (Kelompok B5 D4 Teknik Informatika POLBAN Kelas 1B-D4 Semester 2 TA 2025/2026, submission deadline 25 Mei 2026). Generated after W5-ARTIFACT-SUBMIT lands.

### Changed
- drugs.com scraping pivoted to openFDA (ADR-0004).
- Wave 5 (2026-05-18): `docs/AS-BUILT.md` Section 15 extended with W4-HUNT Inconclusive items (Browser/responsive sweep deferred, focus rings deferred, bundle size sweep deferred, dark-mode contrast sweep deferred) all gated on B-WAVE1-BUILD-1 blocker. Section 16 extended with 6 additional deviations covering Wave 5 fixes plus single-faskes assumption (H07-2).
- Wave 5 (2026-05-18): `docs/SECURITY.md` Residual Risk Register updated: R9 (H07-1) moved from "open Critical" to "RESOLVED in Wave 5 with file:line citation". New Section 7.5 documents single-faskes ownership assumption for H07-2 explicitly. STRIDE table 5.2 A2 Patient PII expanded with E (Elevation of Privilege) note for hypothetical multi-Faskes deployment.

### Fixed
- 11 known bugs B01..B11 (see Wave 1 commits and findings).
- Wave 5 (2026-05-18): H07-1 Critical RBAC PII leak in `api/routes/safety_routes.py`: masyarakat role now receives `pasien_context: null` and `pasien_active_meds: []` regardless of pasien_id supplied; bidan and admin retain access. New assertion in `api/tests/smoke_test.py` confirms behavior. Pre-fix evidence in `.mission/findings/bugs/W4-HUNT.md` Section 7 H07-1 and auditor reproduction in `.mission/findings/audits/wave-04-audit.md` lines 91-117.
- Wave 5 (2026-05-18): H10-1 Major race in `api/routes/patient_routes.py` create/update/delete handler: added `threading.Lock` around load-then-save sequences to prevent duplicate-ID generation and silent write loss under concurrent POST /api/patients.
- Wave 5 (2026-05-18): H01-1 Major umur validation in `api/routes/patient_routes.py`: backend range check 0..150 added to `_validate_medical_ranges` (or equivalent guard) with Bahasa Indonesia inline error message.
- Wave 5 (2026-05-18): H06-2 + H06-3 + H06-1 Major hardcoded UI data: admin dashboard fabricated `auditLog` array removed or replaced with link to existing `/dashboard/aktivitas` route; `/dashboard` admin KPIs sourced from `/api/admin/system-stats` rather than literal 1247/38/89/2 values. Documented in `docs/AS-BUILT.md` Section 16.

### Deferred
- B-WAVE1-BUILD-1: Next.js 16.2.1 + Node 25.6 build chunk-emit race (deferred to Wave 5).
- Wave 5 (2026-05-18): four W4-HUNT Inconclusive items remain gated on B-WAVE1-BUILD-1 swap to Node 22 LTS: Browser/responsive sweep (Category 11), focus rings audit (H12-1), bundle size sweep (Category 14), dark-mode contrast sweep. Documented in `docs/AS-BUILT.md` Section 15.2 as Wave-5-followup.

## [0.1.0] - 2026-05-18

Initial release for Proyek 1 Pengembangan Perangkat Lunak Desktop submission (Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung, semester 2 TA 2025/2026).

### Added
- Modular desktop application anggota1..anggota5 covering scraping (Ghaisan), CRUD pasien SOAP (Bimo), visualisasi matplotlib (Alia), drug safety check (Iqbal), PDF export plus auth (Abhidal).
- Backend integration layer `api/` exposing Flask endpoints for admin, auth, drug, patient, pdf, safety, visualization, with role-based access for tenaga_kesehatan, masyarakat, admin.
- openFDA data acquisition module `anggota1/openfda/` producing 1850 adverse-event reaction occurrences across 74 drug records and 6000 recall records.
- Additive visualization module `anggota3/NewestVisualization/` with five static PNG charts using the MedWatch palette.
- Full documentation set under `docs/` (PRD, SRS, SDD, 10 ADRs, API reference, data dictionary, install guide, user manual, security threat model, as-built record) plus 15 architecture diagrams and 27 docx deliverables.
- Production-grade implementation plan under `ProductionGrade-ImplementationPlan/` (overview, PRD, offline plan, packaging, hardening, test plan, roadmap).
- Repository tidy artifacts: CHANGELOG, CONTRIBUTING, LICENSE, .editorconfig, .gitignore refinements, .gitattributes, .env.example.

### Security
- Per-commit secret-scan hook gating staged-diff leaks against API keys, JWT_SECRET, service-account JSON, private keys, embedded URL credentials.
- bcrypt cost factor 12 for password hashing; httpOnly Secure SameSite=Lax cookies for JWT.
- CORS allowlist limited to the Vercel deployment URL and localhost dev ports.
