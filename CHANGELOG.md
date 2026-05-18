# Changelog

All notable changes to this project will be documented here. Format per Keep a Changelog (https://keepachangelog.com). Versioning per Semantic Versioning (https://semver.org).

## [Unreleased]

### Added
- Wave 0 (2026-05-18): autonomous mission scaffold, 11 Opus-4.7 agents, secret-scan hook.
- Wave 1 (2026-05-18): real openFDA acquisition module anggota1/openfda/. New anggota3/NewestVisualization/.
  Fixes B01..B11 across both repos (admin nav, lihat-semua, patient validation, multi-type PDF, safety active-meds, login manual, heatmap continuous scale, real admin KPIs).
- Wave 2 (2026-05-18): industry-grade documentation set (PRD, SRS, SDD, 10 ADRs, API, DATA-DICTIONARY, INSTALL, USER-MANUAL, SECURITY, AS-BUILT, 15 diagrams, 27 docx).
- Wave 3 (2026-05-18): docstrings across api/ integrasi/ and additive modules; CHANGELOG CONTRIBUTING LICENSE editorconfig .gitignore .gitattributes env example.

### Changed
- drugs.com scraping pivoted to openFDA (ADR-0004).

### Fixed
- 11 known bugs B01..B11 (see Wave 1 commits and findings).

### Deferred
- B-WAVE1-BUILD-1: Next.js 16.2.1 + Node 25.6 build chunk-emit race (deferred to Wave 5).

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
