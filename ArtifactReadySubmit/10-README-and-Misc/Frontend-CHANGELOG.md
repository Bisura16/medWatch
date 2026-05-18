# Changelog

All notable changes to this project will be documented here. Format per Keep a Changelog (https://keepachangelog.com). Versioning per Semantic Versioning (https://semver.org).

## [Unreleased]

### Added
- Wave 0 (2026-05-18): autonomous mission scaffold, 11 Opus-4.7 agents, secret-scan hook under `.claude/scripts/`.
- Wave 1 (2026-05-18): fixes B01 admin scraper CTA wired on the admin home; B02 "Lihat semua" links navigate to their target list pages; B03 patient form numeric medical fields reject letters via client-side validation on blur and submit; B07 patients list displays newest-first; B08 safety-checker inline VERDIKT explanation panel; B09 manual typed login plus visible demo credentials; B11 heatmap rebuilt as a true continuous-scale grid with sorted axes and gradient legend.
- Wave 1 (2026-05-18): pre-Next 16 `src/middleware.ts` renamed to `src/proxy.ts` to match Next.js 16 proxy convention. Proxy attaches the JWT cookie as `Authorization: Bearer ...` and forwards every `/api/*` request to `BACKEND_API_URL` (server-only env var).
- Wave 2 (2026-05-18): README rewritten to industry-standard structure (17 sections) with embedded backend diagrams (C4 L1, C4 L2, ERD Crow's Foot, deployment) and cross-links to backend `docs/`.
- Wave 3 (2026-05-18): TSDoc on `src/app/**/page.tsx`, `src/app/**/route.ts`, `src/lib/*.ts`, `src/components/**/*.tsx`, `src/hooks/*.ts`, and `src/proxy.ts`. CHANGELOG, CONTRIBUTING, LICENSE, `.editorconfig`, refined `.gitignore`, `.gitattributes`, `.env.example`.

### Changed
- Wave 1 (2026-05-18): admin dashboard KPI numbers now read from backend instead of hardcoded placeholders.
- Wave 1 (2026-05-18): export-PDF page covers all four offered report types (rekam medis, kunjungan bulanan, efek samping ter-ranked, inventaris obat), not just SOAP.

### Fixed
- 11 known bugs B01..B11 (see Wave 1 commits and the mission findings under `.mission/findings/bugs/`).
- Wave 5 (2026-05-18): H01-1 Major umur client-side validation: `src/app/patients/new/page.tsx` and `src/app/patients/[id]/page.tsx` mirror the backend range check `0 <= umur <= 150` with Bahasa Indonesia inline error message matching the server response. Aligned with backend fix in `api/routes/patient_routes.py` (W5-FIX-CRITICAL).
- Wave 5 (2026-05-18): H06-2 + H06-3 + H06-1 Major hardcoded dashboard data: `src/app/admin/dashboard/page.tsx` fabricated `auditLog` array (5 fake rows with `103.8.xx.xx`, `bidan_rina`, etc.) removed or replaced with a link to the existing `/dashboard/aktivitas` route; literal admin KPI numbers (1247, 38, 89, 2) at `src/app/dashboard/page.tsx:302-307` removed and either sourced from `/api/admin/system-stats` or hidden with explicit rationale. Pre-fix evidence in `.mission/findings/bugs/W4-HUNT.md` Section 6.

### Deferred
- B-WAVE1-BUILD-1: Next.js 16.2.1 plus Node 25.6 build chunk-emit race condition. The webpack build sometimes fails the first time then succeeds on a clean retry. Tracked for Wave 5 follow-up.

## [0.1.0] - 2026-05-18

Initial release for Proyek 1 Pengembangan Perangkat Lunak Desktop submission (Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung, semester 2 TA 2025/2026).

### Added
- Next.js 16 App Router web showcase wrapping the desktop modules anggota1-5 via the Flask REST API.
- Authentication with three roles (tenaga_kesehatan, masyarakat, admin) using httpOnly cookie JWT and middleware role gating on `/admin/*` and `/pasien/*`.
- CRUD pasien SOAP at `/patients`, `/patients/new`, `/patients/[id]` with bidan-style form, clinical-range validation, and printable detail view.
- Drug search plus comparison at `/drug-search` and `/drug-compare`, multi-input chip safety checker at `/safety-checker`, visualization at `/visualization`, heatmap at `/heatmap`, four-type export PDF at `/export-pdf`.
- Admin tooling at `/admin/scraper`, `/admin/users`, `/admin/dashboard`. Masyarakat profile at `/pasien/profile`.
- Proxy (`src/proxy.ts`) routing every `/api/*` request to `BACKEND_API_URL` with JWT injection; cookie set on `/api/auth/login` and cleared on `/api/auth/logout`.
- Tailwind v4 plus shadcn/ui plus Framer Motion plus Recharts plus Zustand plus next-themes plus d3-scale plus jspdf.
- Industry-grade README with embedded PNG diagrams.
- Repository tidy artifacts: CHANGELOG, CONTRIBUTING, LICENSE, `.editorconfig`, `.gitignore` refinements, `.gitattributes`, `.env.example`.

### Security
- Per-commit secret-scan hook at `.claude/scripts/secret-scan.sh` gating the staged diff against API keys, JWT_SECRET, service-account JSON, private keys, embedded URL credentials, and the Vercel OIDC token pattern.
- Backend URL kept server-side only as `BACKEND_API_URL` (never `NEXT_PUBLIC_`); the browser only ever sees Vercel-origin `/api/*` paths.
- JWT lives in an httpOnly Secure SameSite=Lax cookie set by the Next.js proxy after a successful backend login response.
