# Contributing to MedWatch (Frontend)

This document describes the team workflow for contributing to the MedWatch frontend repository. MedWatch is the Proyek 1 Pengembangan Perangkat Lunak Desktop submission by Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung, semester 2 TA 2025/2026.

The frontend is a Next.js 16 App Router web showcase that wraps the backend desktop modules (anggota1-5) through a Flask REST API. The backend repository is at https://github.com/Bisura16/medWatch.

## Team and module ownership

Each member owns exactly one anggota module on the backend side. The web frontend itself is owned and maintained by Ghaisan as Project Leader. The backend `anggotaN/` folders are READ-ONLY across both repositories.

| Owner | NIM | Role | Backend module | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader, Team Coordinator | anggota1 (scraping plus openFDA acquisition) | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi matplotlib plus NewestVisualization) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | anggota5 (PDF export plus auth) | Heimdall |

The Next.js codebase under `src/` is co-owned and maintained by Ghaisan on behalf of the team. Do not modify backend `anggotaN/` files from this repository. Integration adjustments that would require changing a backend teammate file must be implemented as a proxy or adapter in `src/lib/`, `src/proxy.ts`, or a Next.js API route under `src/app/api/`.

## Conventional Commits (required)

Every commit message uses the Conventional Commits specification (https://www.conventionalcommits.org). Allowed types:

- `feat:` a new feature.
- `fix:` a bug fix.
- `docs:` documentation only.
- `chore:` tooling, configuration, repository hygiene.
- `refactor:` code change that neither fixes a bug nor adds a feature.
- `test:` adding or correcting tests.
- `perf:` performance improvement.

Optional scope in parentheses describes the area of the change, for example `fix(patients): client-side numeric validation on medical fields`. The body explains what changed and why, never how. No `Co-authored-by: Claude` trailer. No emoji. No em dashes.

## Branch model

- `main` is the default integration branch. Only Project Leader merges to `main`.
- Topical work branches follow the pattern `ghaisan-<topic>` (for example `ghaisan-APIIntegration`, `ghaisan-pitch-video`).
- Long-running feature work rebases onto `main` before opening a pull request to avoid bulky merge commits.

## Code review

Every pull request requires at least one peer review before merge. The Project Leader self-merges via `gh pr merge --squash` after recording the reviewer in the PR body. Reviewers check:

- Acceptance criteria from the originating ticket are satisfied.
- `npx tsc --noEmit` passes (TypeScript strict typecheck).
- `npx next build --webpack` succeeds (note: project uses the webpack builder; the Turbopack builder is not supported here due to B-WAVE1-BUILD-1 on Node 25).
- No backend teammate file under `anggotaN/` is modified from this repo.
- No credential VALUES are present anywhere in the diff (resource NAMES are allowed in docs).
- Conventional commit subject is correct.

## Tooling and conventions

- Next.js 16 (App Router) with React 19 and TypeScript 5 strict mode.
- Tailwind CSS v4 utility-first styling. Class order: layout, spacing, typography, color, state.
- shadcn/ui plus Base UI plus Framer Motion plus Recharts plus Zustand plus next-themes.
- ESLint with the `eslint-config-next` baseline (see `eslint.config.mjs`).
- File naming: `kebab-case.tsx` for routes, `PascalCase.tsx` for shared components.
- Server Components by default; `"use client"` only when state, effects, or browser APIs are required.
- No `any` without a justification comment. Explicit return types on exported functions.
- User-facing strings (UI labels, error messages, copy) in Bahasa Indonesia with formal register. Code identifiers and standards citations in English.
- Date formatting in displayed content uses `dd-MM-yyyy`. ISO 8601 in JSON wire format.
- No `console.log` in committed code outside dev-only blocks.
- No commented-out code blocks. Delete or document why preserved.

## npm scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Next.js dev server with hot reload on http://localhost:3000. |
| `npm run build` | Production build. Project uses the webpack builder; pass `--webpack` when running `next build` directly to avoid the B-WAVE1-BUILD-1 Turbopack issue on Node 25. |
| `npm run start` | Run the production build. |
| `npm run lint` | ESLint pass over the codebase. |

## Local development

1. Clone the repository.
2. Install dependencies: `npm install`.
3. Copy `.env.example` to `.env.local` and set `BACKEND_API_URL`. For local-only frontend dev against the running backend on port 8080 the value is `http://127.0.0.1:8080`.
4. Run the backend separately (see the backend repository's `CONTRIBUTING.md`).
5. Run the frontend: `npm run dev`.
6. Type check: `npx tsc --noEmit`.
7. Production build sanity check: `BACKEND_API_URL=http://127.0.0.1:8080 npx next build --webpack`.

## Security

- Never commit credential VALUES. The `.env.example` template uses a clearly-local placeholder (`http://127.0.0.1:8080`).
- `.env.local` is gitignored. The Vercel CLI may write a development OIDC token there; that token must never be committed.
- The pre-commit secret-scan hook (`.claude/scripts/secret-scan.sh`) blocks commits whose staged diff matches forbidden patterns (API keys, GitHub tokens, AWS keys, Slack tokens, private keys, JWT_SECRET with a real value, service-account JSON, embedded URL credentials).
- The backend URL is server-side only: `BACKEND_API_URL`. Do not introduce a `NEXT_PUBLIC_` variant; the proxy in `src/proxy.ts` is the only place the backend URL is read.

## Question or doubt

Open an issue with the prefix `question:` or contact the Project Leader. Do not block on ambiguity: log the question, proceed with the conservative interpretation, and surface it during the next sync.
