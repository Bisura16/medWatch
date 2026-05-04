# MedWatch Project Memory

This file is auto-loaded by Claude Code at session start. It contains permanent project context, immutable rules, and source-of-truth pointers. Read this carefully before any task.

---

## Project Identity

**Name:** MedWatch: Sistem Monitoring Keamanan Obat & Manajemen Klinik Faskes 1
**Mata kuliah:** Proyek 1 Pengembangan Perangkat Lunak Desktop
**Institution:** Politeknik Negeri Bandung (POLBAN), D4 Teknik Informatika, Kelas 1B-D4
**Term:** Semester 2: Tahun Akademik 2025/2026
**Team designation:** Kelompok B5

### Dosen pendamping
- Aprianti Nanda Sari (Project Manager)
- Ade Chandra Nugraha
- Ardhian Ekawijana

### Team roster
| Nama | NIM | Role | Modul Python | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader / Team Coordinator | anggota1 (scraping drugs.com + FDA) | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi matplotlib) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | anggota5 (PDF export fpdf) | Heimdall |

You are working on behalf of **Ghaisan Khoirul Badruzaman** (the Project Leader). Address him as "Ghaisan" or "lu" in casual register if responding in Indonesian.

---

## Repository Registry

| Repo | URL | Owner | Purpose | Integration branch |
|---|---|---|---|---|
| Backend (THE main project) | `https://github.com/Bisura16/medWatch` | Bimo (Bisura16) | Modular Python anggota1-5 modules. Integration layer `api/` is added by Ghaisan in his branch. | `ghaisan-APIIntegration` |
| Frontend (Vercel showcase) | `https://github.com/Finerium/FrontendMedwatch` | Ghaisan (Finerium) | Next.js 15 + TypeScript + Tailwind v4 glassmorphism, deployed to Vercel | `ghaisan-APIIntegration` |

### Reference-only repositories (DO NOT modify)
- `https://github.com/ball-droid/MedwatchProto`: Iqbal's CustomTkinter monolithic prototype, not merged
- `https://github.com/Bisura16/Proyek_Kelompok5_W3`: Week 3 weekly assignment (news scraper), unrelated
- `https://github.com/Finerium/Proyek_Kelompok5`: original team landing page

### Live URLs
- Frontend: `https://medwatch-frontend.vercel.app` (Vercel, owned by Ghaisan)
- Backend: deployed to Cloud Run at `https://medwatch-api-XXXXX-as.a.run.app` after Phase 4 of integration mission

---

## Immutable Rules

These rules are non-negotiable. Failure to follow any of them is a critical defect that requires rollback.

### 1. Git authorship

- **Git author for all commits:** `Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>`
- Before committing, verify `git config user.name` returns `Ghaisan Khoirul Badruzaman` and `git config user.email` returns `ghaisan.khoirul.b@gmail.com`. Set them if missing or wrong.
- **NEVER include any of the following in commit messages, file headers, or anywhere else:**
  - `Co-authored-by: Claude` or any Claude attribution
  - `"Generated with Claude Code" robot emoji marker` emblem
  - "Generated with Claude", "via Claude", "with assistance from Claude"
  - Any emoji robot or AI marker
- Commit messages use **conventional commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `perf:`) in clear English. Indonesian is acceptable too but English is preferred for consistency with industry convention.
- Commit messages explain **what changed and why**, never **how**.
- Squash trivial commits before push (no `wip`, `asdf`, `temp` left behind).

### 2. Modul anggota1-5 are READ-ONLY (with one explicit, one-time exception)

- Files inside `anggota1/`, `anggota2/`, `anggota3/`, `anggota4/`, `anggota5/` belong to Ghaisan's teammates. **Never modify them**, with one explicit exception described below.
- If integration with a teammate's module requires a fix (e.g. broken import path, missing dependency), do NOT fix in their file. Instead, write a wrapper or shim in `api/` that handles the issue gracefully.
- Reading and importing teammates' modules is fine. Writing is forbidden.
- Existing JSON data files (`anggota4/data/drug_database.json`, `anggota4/data/effect_database.json`, `anggota5/data/Pasien.json`) are also read-only. The new `api/` layer maintains its own copies in `api/data/`.

**One-time exception (Phase 1 only): Abhidal-authorized anggota5 auth revision.** Abhidal Muhammad Gazza has formally requested via Ghaisan to implement two revisions to his anggota5 module: removing the open-signup feature, and implementing role-based CRUD access (admin can manage tenaga kesehatan accounts and trigger scraper; tenaga kesehatan can only access patient CRUD). The Phase 1 sub-phase in the master prompt implements this revision by modifying exactly four files in `anggota5/`:

- `anggota5/data/users.json` (replace with new schema)
- `anggota5/auth.py` (replace with role-aware version)
- `anggota5/tkesehatan_crud.py` (NEW file)
- `anggota5/main_anggota5.py` (replace with role-based menu)

No other anggota5 file (e.g. `export_pdf.py`, `ambil_data.py`) may be touched.

**Workflow:** team `Bisura16/medWatch` follows a per-anggota branch + PR pattern. The Abhidal revision is committed to the existing `Abhidal_anggota5` branch (not directly to main), pushed, then opened as a PR `Abhidal_anggota5 -> main` and self-merged via `gh pr merge --squash` by Ghaisan with Abhidal's authorization. The PR body documents the spec and authorship.

After the squash-merge to main is confirmed, anggota5 returns to read-only status. This exception does NOT extend to anggota1, anggota2, anggota3, or anggota4 under any circumstances.

### 3. Schema source of truth

When data formats conflict between modules, the canonical schema is:

| Entity | Source of truth | Notable conventions |
|---|---|---|
| Pasien | `anggota2/pasien_helper.py` (Bimo's format) | ID auto-generated as `P001`, `P002`, ... (uppercase P + 3 digits). NOT `PSN-001` (Abhidal's draft is non-canonical). |
| Drug | `anggota4/data/drug_database.json` (Iqbal's format) | Fields: `nama_obat, alias[], kategori, bahan_aktif[], indikasi[], dosis_umum, kehamilan, peringatan[], kontraindikasi[], interaksi[], efek_samping[]` |
| Side effect | `anggota4/data/effect_database.json` (Iqbal's format) | Fields: `nama_efek, kategori, tingkat_keparahan (ringan/sedang/serius), rekomendasi`. Severity scoring: ringan=1, sedang=2, serius=4. |
| Visit/SOAP | `anggota2/Pasien.json` (Bimo's format) | Format: `id, tanggal_kunjungan (DD-MM-YYYY), nama, umur, alamat, kategori, S{keluhan, riwayat}, O{tekanan_darah, nadi, suhu_c, respirasi, bb_kg, tb_cm, lila_cm, catatan}, A{diagnosa}, P{tindakan, resep, jadwal_kontrol}` |
| User auth | `api/data/users.json` (NEW, replaces `anggota5/data/users.json`) | Schema: `{username, password_hash (bcrypt), role, name, phone}`. Roles: `tenaga_kesehatan`, `masyarakat`, `admin`. |

#### Bidan workflow reality (Pasien input/display)

The structured SOAP schema above is for **storage and validation**. The UX must respect that bidan in Faskes 1 do not always fill every field. Reference example provided by Ghaisan:

```
Tgl 28 Februari 2026
Nama : Ny. Dewi
Umur : 25 THN
Alamat : Kp. Selang Cau
S : mengeluh mual, muntah, pusing, telat mens 1 bln mens terakhir tgl 25 Januari 2026
O : td. 110/70, BB 50 kg, tb 150, lingkar lengan 23 cm, tespek positif
A : G1P0A0 hamil 5 mg
P : Istirahat cukup
    Makan sedikit tapi sering
    Asam folat 1x1 sehari
```

Mapping rules:
- Required fields: `nama`, `S.keluhan`, `A.diagnosa`, `P.tindakan`. All others optional.
- `O.nadi`, `O.suhu_c`, `O.respirasi` commonly blank: bidan does not always measure these.
- `O.catatan` is the catch-all for non-structured observations like "tespek positif", "DJJ 140 x/menit", etc.
- `P.tindakan` is multi-line: newlines preserved in storage and rendered as bullet list.
- Display reconstruction uses bidan abbreviations (`td.`, `BB`, `tb`, `lila`) not the raw JSON keys (`tekanan_darah`, etc.). See `composeO()` helper spec in master prompt Phase 6.

### 4. Role nomenclature

Always use **`tenaga_kesehatan`** (not "dokter") and **`masyarakat`** (not "pasien" in technical contexts) for backend role values. UI labels can show "Dokter" or "Pasien" if more user-friendly, but API role string values are canonical. This aligns with PRD target user definitions and team convention from WhatsApp discussions.

The third role is **`admin`**, used for the team member who manages the scraper trigger and user accounts. Admin is an extension beyond PRD original scope (PRD section 5.2 originally listed auth as out-of-scope), so its presence should be framed as a presentation supplement, not a core PRD feature.

### 5. PRD scope tension awareness

The original `MedWatch_PRD.pdf` explicitly lists as **out of scope**:
- "Fitur login atau multi-user dengan autentikasi"
- "Deployment ke platform web atau mobile"

The integration mission adds both of these as **supplementary demo features**, not as replacements for the desktop CustomTkinter modules anggota1-5. The narrative for the lecturer is: "demo fitur, bukan demo aplikasi": the desktop modular CustomTkinter remains the primary submission, the Cloud Run + Vercel stack is a presentation polish layer that connects modul anggota1-5 to a web frontend showcase.

Do not propose modifying the PRD. Do not suggest expanding the auth feature beyond what the integration mission specifies.

### 6. README files are append-only

`Bisura16/medWatch/README.md` and `Finerium/FrontendMedwatch/README.md` contain content authored by teammates (Bimo) or Ghaisan himself. **Never delete or rewrite existing README content.** Only **append** new sections at the end, separated by a horizontal rule (`---`). This applies even if existing content is sparse, outdated, or imperfect: it is teammate property.

NEW README files (e.g. `medWatch/api/README.md`) can be authored freely.

### 7. Cyber security responsibility

Every code path that handles authenticated requests, PII (patient data), or secrets is subject to a security review pass at the end of the integration mission. The standard is OWASP Top 10 plus GCP-specific checks. Apply defense-in-depth: middleware on backend AND middleware on frontend AND CORS allowlist. Never log passwords. Never return password hashes. Never commit secrets to git.

The audit produces `medWatch/docs/SECURITY_AUDIT.md`. Critical findings block push.

### 8. All resources must be free

- GCP free trial credit ($300, attached to Ghaisan's billing account at `ghaisan.khoirul.b@gmail.com`) is the budget. No paid services beyond what fits in free trial.
- No paid third-party services (no Auth0, no SendGrid, no paid Cloudflare, no Sentry paid tier).
- No custom domains. Default `.run.app` and `.vercel.app` URLs are sufficient.
- Vercel free tier hosting only. Stay within Hobby plan limits.

### 9. Zero user interaction during execution

- Ghaisan launches Claude Code with `claude --dangerously-skip-permissions` and expects autonomous completion.
- Do **not** ask clarifying questions during execution. Every decision is locked in this CLAUDE.md and the master prompt.
- If a hard error blocks progress, log the error to `~/Documents/MedWatchIntegration/EXECUTION_LOG.md`, attempt the next phase, and surface the error in the final report.

---

## Tooling Stack

### Backend (`api/` layer in Bisura16/medWatch)
- Python 3.11 (Cloud Run runtime)
- Flask 3.0+ for HTTP server
- Flask-CORS for cross-origin (although requests proxy through Vercel, keep CORS for direct testing)
- PyJWT for JWT issuance/verification
- bcrypt for password hashing
- google-cloud-storage for persistent state backup
- requests + beautifulsoup4 (already used by anggota1, do not re-import)
- matplotlib (already used by anggota3, return charts as base64 PNG when needed for PDF)
- fpdf2 (already used by anggota5)
- gunicorn for production WSGI

### Backend deployment
- GCP project: `medwatch-polban-2026` (created during Phase 4)
- Region: `asia-southeast1`
- Service: `medwatch-api` (Cloud Run)
- Container: built via Cloud Build from `api/Dockerfile`
- Storage: `medwatch-polban-2026-state` bucket for `users.json` and `patients.json` persistence
- Secrets: JWT signing key in Secret Manager as `medwatch-jwt-secret`

### Frontend (Finerium/FrontendMedwatch)
- Next.js 15 (App Router)
- TypeScript strict mode
- Tailwind CSS v4
- shadcn/ui components
- Framer Motion for animations
- Recharts for data viz
- Zustand for client state (auth, etc.)
- next-themes for dark/light
- Vercel deployment (already configured)

### Frontend <-> Backend correlation pattern

**Vercel API routes proxy** (security pattern B). The browser only ever sees Vercel domain. The backend Cloud Run URL is stored in Vercel environment variable `BACKEND_API_URL` (server-side only, **not** prefixed with `NEXT_PUBLIC_`). Next.js API routes at `app/api/[...slug]/route.ts` forward requests to the backend with proper auth headers, attach the JWT from httpOnly cookie, return the response. Browser-side code calls `/api/...` paths only.

This means:
- JWT lives in httpOnly cookies (XSS-resistant)
- Backend URL is never exposed to client
- Backend can be swapped via Vercel env var update without frontend code change
- Same-origin requests, no CORS preflight overhead per call

---

## Working Directory Convention

When the master prompt is launched, Claude Code creates a parent integration workspace:

```
~/Documents/MedWatchIntegration/
├── medWatch/                 # cloned from Bisura16/medWatch (backend)
├── FrontendMedwatch/         # cloned from Finerium/FrontendMedwatch (frontend)
├── EXECUTION_LOG.md          # error/decision log
├── PROGRESS.md               # phase-by-phase status
└── DESIGN.md                 # extracted from master prompt for reference
```

This `CLAUDE.md` file is placed at the **root of each repository** (`medWatch/CLAUDE.md` and `FrontendMedwatch/CLAUDE.md`) so that future Claude Code sessions in either repo automatically load it. Both copies are identical.

If Ghaisan already has the frontend cloned at `~/Documents/FrontendMedWatch/` (note slightly different casing), Claude Code uses that location instead of re-cloning. The integration parent dir is created freshly for the backend.

---

## Methodology Note

Claude Code is configured with the **Superpowers plugin (obra/superpowers)** which auto-triggers structured skills (brainstorming, writing-plans, using-git-worktrees, subagent-driven-development, test-driven-development, requesting-code-review, finishing-a-development-branch).

Behavior expected from these skills:
- **brainstorming SKIPPED:** This integration mission represents an already-approved, fully-specified design. The master prompt is the brainstorm output. Skip the brainstorming skill and proceed directly to writing-plans.
- **writing-plans:** Generate task breakdown per phase from the master prompt. Each task should be 2-5 minutes of work, with exact file paths and verification steps.
- **using-git-worktrees:** Create separate worktrees per repo for parallel work where independent.
- **subagent-driven-development:** Dispatch a fresh subagent per logical task with two-stage review.
- **test-driven-development:** Apply lightly. For Flask endpoints, write smoke tests (curl-style verification scripts). Full unit-test TDD is overkill for this presentation-focused integration. Tests should verify "endpoint returns 200, response shape matches schema, auth blocks unauthorized."
- **requesting-code-review:** Apply at end of each phase before commit. Self-review against acceptance criteria.
- **finishing-a-development-branch:** Apply at end of mission. Push branches, do not auto-merge. Surface as draft PR to Ghaisan via final report.

---

## Coding Conventions

### Python (`api/` layer)
- PEP 8, 4-space indentation
- Type hints on all public functions
- Docstrings in English, brief (one-liner for trivial, multi-line with `Args:`/`Returns:` for non-trivial)
- File comments at top: short module docstring stating purpose, no author tag, no date
- Imports: standard lib, third-party, local: separated by blank line
- f-strings for formatting, no `%` or `.format()`
- Logging: use `logging` module configured at app startup, never `print()` in production paths

### TypeScript (frontend)
- Strict mode, no `any` without justification comment
- Explicit return types on exported functions
- React Server Components by default, `"use client"` only when needed (state, effects, browser APIs)
- File naming: `kebab-case.tsx` for routes, `PascalCase.tsx` for components
- Imports sorted: React, third-party, `@/` aliases, relative
- No barrel files (`index.ts` re-exports) unless they exist already
- Tailwind classes ordered: layout -> spacing -> typography -> color -> state

### Both
- No console.log / print in committed code (unless inside dev-only blocks)
- No commented-out code blocks. Delete or document why preserved.
- No TODO comments without an issue/ticket reference. Replace `TODO` with `NOTE:` or remove.
- Variable names in English. UI strings in Indonesian where user-facing.

---

## Security Boundaries

- JWT secret never committed to git. Stored in GCP Secret Manager, accessed via env var.
- bcrypt cost factor: 12 (default). Faster cost is rejected.
- httpOnly + Secure + SameSite=Lax cookies for JWT.
- Cloud Run service account: minimal permissions (Storage Object Admin on the state bucket only, Secret Manager Secret Accessor on jwt secret only).
- No service account key files committed to git. Use Workload Identity or default Cloud Run service account.
- CORS allowlist: only the Vercel deployment URL plus localhost dev ports.
- No `eval()`, no `exec()`, no shell injection vectors. Pasien data sanitized before SOAP rendering.

---

## When to Stop and Ask

There are exactly two situations where you must stop autonomous execution and surface to Ghaisan instead of pushing through:

1. A required GCP API quota or billing issue would lock the entire deployment phase. (E.g. free trial expired, billing account suspended.)
2. The Bisura16/medWatch repo has been updated by a teammate in a way that conflicts with the `ghaisan-APIIntegration` branch base, and rebasing would touch teammate files (which is forbidden by Rule 2).

Anything else: log it, work around it, surface in the final report. Do not block on user input.

---

## End

This file is reference material. The mission to execute lives in the master prompt that the user pastes at session start.
