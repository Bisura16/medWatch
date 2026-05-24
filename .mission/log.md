# Mission Log

Wave-by-wave one-paragraph summary. Append in chronological order.

## Wave 0 - Bootstrap and recon (complete, 2026-05-24T21:13Z)

Created `.mission/` skeleton in backend repo. Captured tool versions and confirmed `OPENFDA_API_KEY` env presence without leaking value. Verified `CLAUDE_CODE_SUBAGENT_MODEL` and `CLAUDE_CODE_EFFORT_LEVEL` are unset. Inspected backend `api/app.py` Flask layout, frontend `package.json` (Next 16.2.1, React 19.2.4, Tailwind v4), and prior `anggota1/openfda/fetch.py` JSON scraper. Hit openFDA `/drug/ndc.json?search=finished:true+AND+product_type:%22HUMAN+PRESCRIPTION+DRUG%22&limit=1` and confirmed actual prescription-drug total of 55,666 records (mission estimate was 25-50k; will dedupe down). Renamed prior `doc-writer.md` to `doc-writer.prior-mission.md` to preserve. Created 8 new agent definitions for this mission. Confirmed two future blockers: macOS host has no `wine`, no `pyinstaller` installed, so Windows .exe production needs deferral plan (deferred to Wave 2 surface with concrete evidence). Dispatched scout via `general-purpose` (subagent_type), model `opus`, with full role contract from `.claude/agents/scout.md` inlined in the prompt.

Scout returned `phase_status: complete` with a 443-line findings file at `.mission/findings/wave-0-scout.md`. Confirmed all five openFDA endpoints reachable with the auth key: label 258,334; ndc 135,206; ndc-prescription 55,666; event 20,328,575; enforcement 17,661. Rate limit 240/min confirmed; `Link: rel="next"` cursor paging confirmed. Backend has 8 blueprints, ~24 routes; `PORT` env-driven default 8080 on host `0.0.0.0` (api/config.py:43); CORS_ORIGINS hardcoded (api/config.py:28-32). Frontend has 21 pages; 3 carry `export const dynamic = 'force-dynamic'` (login, safety-checker, drug-comparison) and `src/app/api/[...slug]/route.ts` plus `src/proxy.ts` block static export today; all enumerated for Wave 3 migration. Scout surfaced a new blocker: Python 3.14.5 on dev host is incompatible with PyInstaller 6.10 (3.13 max). Will install Python 3.13 via pyenv in Wave 2. The previously-known wine absence is reconfirmed for Wave 5.

Wave 0 complete. Advancing to Wave 1.

Wave 0 local commit: `2334b0c chore(installer-mission): wave 0 bootstrap and recon` (16 files, 1476 insertions).

## Wave 1 - Scaffold both variants (complete, 2026-05-24T21:25Z)

Dispatched scaffold-builder via `general-purpose` (opus). Created the two top-level Electron variant folders inside the backend repo with literal user-specified names: `installer-based app/` (folder name contains a space) and `portable-app/` (hyphen). Each contains `electron-builder.yml`, `package.json`, `main/index.js`, `preload/index.js`, `resources/.gitkeep`, `resources/renderer/.gitkeep`, `README.md`. Picked `electron@36.9.5` (latest stable in the v36 line) and `electron-builder@26.11.1`. Both folders resolve a 391-package graph cleanly under `npm install --dry-run`. NSIS variant configured with `oneClick: false`, `allowToChangeInstallationDirectory: true`, desktop + Start Menu shortcuts. Portable variant configured with `artifactName: MedWatch-${version}-portable.exe`. `main/index.js` is the Wave-5-ready skeleton (placeholder createWindow + the standard quit handler). README documents output paths, build steps, SmartScreen warning, offline mode, DB location, maintainer.

Wave 1 complete. Advancing to Wave 2.

Wave 1 local commit: `a08fff0 feat(installer): wave 1 scaffold installer-based and portable variants` (18 files, 498 insertions).

## Wave 2 - PyInstaller backend bundle (complete, 2026-05-24T21:42Z)

Dispatched backend-bundler via `general-purpose` (opus). Wrote `api/desktop_entry.py` as a sibling entry to keep `api/app.py` untouched: the new module is the PyInstaller target, reads `MEDWATCH_DESKTOP=1` env to activate, binds `127.0.0.1:0` via `wsgiref.simple_server.make_server`, prints `MEDWATCH_BACKEND_PORT=<n>` to stdout for the Electron handshake, reads `MEDWATCH_DB_PATH` env for the SQLite path. Wrote `medwatch_desktop.spec` (PyInstaller --onefile, excludes `google.cloud.storage`, `gunicorn`, `matplotlib.tests`, `numpy.testing`, `tkinter`). 

Big surprise: Python 3.13.13 was already on the dev host via Homebrew at `/opt/homebrew/bin/python3.13`. Backend-bundler created `.venv-desktop/` on that interpreter (no system install), installed `pyinstaller==6.20.0`, and produced a 24 MB macOS arm64 binary at `dist/medwatch-backend`. Smoke test passed: launched with `MEDWATCH_DESKTOP=1 MEDWATCH_DB_PATH=/tmp/test-medwatch.db`, captured `MEDWATCH_BACKEND_PORT=60022` from stdout, `GET /api/health` returned 200, `GET /api/info` returned 200. The Python 3.14 blocker is RESOLVED. The Windows `.exe` blocker for Wave 5 remains; backend-bundler delivered `.mission/findings/wave-2-runbook-windows-build.md` covering three remediation paths (GitHub Actions recommended).

Updated `.gitignore`: added `.venv-desktop/` under the venv section and `!medwatch_desktop.spec` exception to the `*.spec` ignore rule so the spec gets tracked.

Wave 2 complete. Advancing to Wave 3.

