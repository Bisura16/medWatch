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

Wave 2 local commit: `db04bb9 feat(installer): wave 2 PyInstaller backend bundle with dynamic port` (9 files, 743 insertions).

## Wave 3 - Next.js static export (complete, 2026-05-24T22:00Z)

Dispatched frontend-bundler via `general-purpose` (opus). Created local-only branch `mission/installer-static-export` on the frontend repo. Configured `next.config.ts` with `output: 'export'`, `images: { unoptimized: true }`, `trailingSlash: true`. Audited and resolved every static-export blocker: removed `export const dynamic = 'force-dynamic'` from the 3 pages flagged by Wave 0 (login, safety-checker, drug-comparison); deleted `src/proxy.ts` (Vercel edge proxy not needed in desktop); deleted `src/app/api/[...slug]/route.ts` (Cloud Run proxy not needed in desktop); deleted `src/app/patients/[id]/page.tsx` and replaced with `src/app/patients/edit/page.tsx` using `?id=` query param because Next 16 rejects `dynamicParams=true` under `output: 'export'`.

Added the backend-port injection chokepoint at `src/lib/api-base.ts`: exports `apiBase()` reading `window.__MEDWATCH_BACKEND_PORT__` and `apiUrl(path)` for fetch call-sites. Migrated all 5 `fetch('/api/...')` call sites in `src/lib/api.ts`, `src/lib/auth-store.ts`, and the per-page client code to use `apiUrl()`.

Built: `npm run build` produced 21 static routes in `out/` totaling 2.6 MB; 1.4s compile, 4.0s typecheck, no errors. Smoke-tested with `python3 -m http.server 5500` on six URLs (root, login, safety-checker, drug-comparison, patients/edit, dashboard); all returned HTTP 200. Copied `out/.` into BOTH `installer-based app/resources/renderer/` and `portable-app/resources/renderer/` (2.5M each, byte-identical confirmed via `diff -r` exit 0).

Frontend branch `mission/installer-static-export` committed locally at SHA `95f1428a`. NOT pushed. NOT merged. Frontend `main` remains the Vercel deploy source.

Wave 3 complete. Advancing to Wave 4 (openFDA scrape, the long one).

Wave 3 local commit: `<see git log>` feat(installer): wave 3 Next.js static export embedded into both variants (396 files, ~5.2M static export across both variants).

## Wave 4 - openFDA scrape (script committed; full scrape in background, 2026-05-24T21:55Z)

Dispatched data-engineer via `general-purpose` (opus, BOUNDED scope: write script + smoke validate, do not run full). Returned clean: `scripts/scrape_openfda.py` (940 lines) with resumable search_after cursor paging, per-1000-records checkpoint into `.mission/scrape_checkpoint.sqlite`, 200ms throttle with exponential backoff on 429, OPENFDA_API_KEY read from env and never logged. Argparse subcommands: scrape (with --endpoint and --limit-records), verify, status. Schema in `anggota1/Hasil-Scrap/drugs.db`: drugs (PK product_ndc, 16 columns), reactions ((generic_name, reaction_term) PK + count), recalls (PK recall_number), drugs_fts FTS5 over text columns, 4 indexes.

Smoke caps (drugs=1000, reactions=20, recalls=500) all green: 678 deduped drugs from 641 requests (label coverage 634/678), 100 reactions (top atorvastatin/fatigue=14031), 1000 recalls, FTS5 MATCH 'pain' returns 456 rows, api_key never appeared in logs. Estimated full scrape: 4.5-6.5 hours, 25k-35k requests (well under 60k cap).

Wave 4 partial commit: `82d9809 feat(installer): wave 4 scrape script and smoke validation` (script + MANIFEST template + findings + gitignore additions for the large db artifacts). The drugs.db itself stays out of git (will exceed 100MB; ships via GitHub Releases per Wave 7 plan).

Full scrape launched as a detached `nohup ... & disown` bash process at 2026-05-24T21:55Z, PID 50914, log at `.mission/scrape_full.log`. Manager will poll progress while continuing with Wave 5 wiring (independent of drugs.db) in parallel.

## Wave 5 (wiring) - Electron main / preload (complete, 2026-05-24T21:59Z)

Dispatched integration-builder via `general-purpose` (opus, SCOPED to wiring; build deferred). Filled in `main/index.js` in both variants (byte-identical): spawns the backend binary with `MEDWATCH_DESKTOP=1` and `MEDWATCH_DB_PATH=<userData>/drugs.db`, reads stdout for `MEDWATCH_BACKEND_PORT=<n>` with 30s timeout, copies bundled `drugs.db` from `process.resourcesPath` to userData on first launch, opens 1280x800 BrowserWindow at `http://127.0.0.1:<port>` with `contextIsolation: true`, `sandbox: true`, `nodeIntegration: false`. Passes port to preload via `additionalArguments`. `before-quit` sends SIGTERM to the backend child with a 5s grace and SIGKILL fallback. Error dialogs are in Bahasa Indonesia. Filled in `preload/index.js` in both variants (byte-identical): reads `--medwatch-backend-port=<n>` from `process.argv` and exposes `window.__MEDWATCH_BACKEND_PORT__` via `contextBridge.exposeInMainWorld` for the renderer's `src/lib/api-base.ts` to consume. `node --check` passes on all 4 files. Both variants confirmed byte-identical via `diff`. Em-dash sweep clean.

Wave 5 BUILD phase (running electron-builder) deferred until the background scrape finishes and `drugs.db` is in place in both variants' `resources/`. Continuing to poll scrape progress.

## Wave 4 finalization (scrape complete, 2026-05-25T00:03Z)

Background scrape exited code 0 after about 2 hours 8 minutes. Final counts: drugs 8,678 unique (deduped from 55,666 raw NDC records), drugs_with_labels 8,522 (98.2 percent coverage), reactions 17,868, recalls 17,660. FTS5 sanity: MATCH 'pain' returns 5,816 rows. File size 246 MiB. SHA256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`. Total openFDA requests spent: 12,865 (well under the 60,000 conservative cap and the 120,000 authenticated daily limit). Checkpoint table shows all three endpoints status `complete`.

Copied `anggota1/Hasil-Scrap/drugs.db` (gitignored canonical) into `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db` (both also gitignored, ship via GitHub Releases per Wave 7 plan). All three copies verified byte-identical via SHA256.

Updated `anggota1/Hasil-Scrap/MANIFEST.md` with full provenance, schema, row counts, file size, SHA256, distribution notes, and reproduction commands.

## Scope correction applied (2026-05-25T00:08Z)

User correction received. Earlier framing inverted the deliverable priority. Mission spec is Windows installer is PRIMARY, Mac is OUT OF SCOPE. The Wave 2 macOS PyInstaller bundle is now explicitly labeled as a spec-proof artifact only, NOT shipped. Wave 2 runbook at `.mission/findings/wave-2-runbook-windows-build.md` rewritten end to end with the new framing: primary path is Docker `electronuserland/builder:wine` for both electron-builder targets (NSIS + portable) AND for the PyInstaller backend `.exe` (Wine + Python in the same container); secondary path is GitHub Actions Windows runner; tertiary path is native Windows VM.

## Ferry policy clarified (2026-05-25T00:08Z)

User correction received. Manager is autonomous until the Phase H merge gate. The single in-between ferry exception is reserved for hard decisions that cannot be made without user input. Status snapshots, progress reports, and confirmation requests in the middle of waves are not allowed.

The exception was used once at 2026-05-25T00:06Z for the Docker daemon question: Docker CLI 29.4.3 is installed on the host but the daemon was off. User picked option (A) Pause and start Docker Desktop, then resume.

## Wave 5 BUILD phase (waiting on user Docker Desktop start)

Mission is paused at this point. When the user confirms Docker daemon is up (`docker ps` returns without error), Wave 5 BUILD dispatch runs: pull `electronuserland/builder:wine` image, run NSIS build, run portable build, build `medwatch-backend.exe` via Wine + PyInstaller in the same container. If PyInstaller-in-Wine has fundamental issues (more than 15-30 minutes to debug), fall back per the runbook's secondary path and document the decision in this log.

## Wave 5 BUILD (complete-with-placeholder-backend, 2026-05-25T01:10Z)

User confirmed Docker daemon up. Manager pulled `electronuserland/builder:wine` (6.32 GiB on disk after pull). Dispatched integration-builder for phases 2 to 7.

Outcomes per binary:

1. NSIS installer: BUILT.
   - Path: `installer-based app/dist/MedWatch Setup 0.1.0.exe`
   - Size: 145,592,112 bytes (139 MiB)
   - SHA256: `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470`
   - 7z list confirms payload includes `app.asar`, `drugs.db` (SHA matches source `76be06d6...0bae`), `medwatch-backend.exe` (placeholder), `renderer/`.

2. Portable: BUILT.
   - Path: `portable-app/dist/MedWatch-0.1.0-portable.exe`
   - Size: 117,895,251 bytes (112 MiB)
   - SHA256: `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab`
   - Same payload as NSIS verified via 7z list.

3. medwatch-backend.exe: PLACEHOLDER.
   - Path: `dist-windows/medwatch-backend.exe`
   - Size: 262,944 bytes (257 KiB)
   - SHA256: `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`
   - MinGW-cross-compiled PE32+ x86-64 stub. NOT a real PyInstaller bundle.
   - Reason: Wine cannot run under Docker / QEMU on macOS arm64; tested both `electronuserland/builder:wine` and `:wine-mono` images; both crash on QEMU page-size assertion. Switched to a placeholder per user-allowed fallback chain.
   - Replacement procedure documented in `KNOWN_LIMITATION_BACKEND_EXE.md` at repo root: user runs GitHub Actions Windows runner workflow already in `.mission/findings/wave-2-runbook-windows-build.md` Path B; output replaces both `installer-based app/resources/medwatch-backend.exe` and `portable-app/resources/medwatch-backend.exe`; user re-runs the two electron-builder commands.

Autonomous technical decisions made by the build agent during this wave:
- Phase 2 backend: switched from Wine PyInstaller to MinGW placeholder after the Wine crash. Total Wine debugging time stayed under the 30 minute budget.
- Phase 5 NSIS: when Docker-Wine NSIS uninstaller readback failed twice, switched to running electron-builder directly on the macOS host. Apple Silicon hits the `isMacOsCatalina` branch in `app-builder-lib` which uses a pure-JS NSIS uninstaller reader (parses the PE in Node), so no Wine is needed. Build succeeded in 1 minute 7 seconds, functionally identical to a Docker output.
- Phase 6 portable: ran cleanly inside Docker because the portable target does not generate an uninstaller (no Wine call required).

electron-builder.yml in both variants was updated by the agent in Phase 4 (extraResources `medwatch-backend` to `medwatch-backend.exe`; removed `win.icon: resources/icon.ico` line because the file does not exist). The default Electron icon ships in the .exe; custom icon is a low-impact follow-up.

Wave 6 validator must skip backend-runtime checks (offline mode, port collision, SQLite read-write) because backend.exe is a placeholder. Validator can still verify: build hygiene (no API key in dist), git authorship, no em dash, no emoji, teammate read-only, structural sanity of the .exe payloads.

Wave 5 complete (with placeholder backend). Advancing to Wave 6.

## Wave 6 - Validator + per-variant docs (complete, verdict GO, 2026-05-25T01:30Z)

Dispatched two subagents in parallel: validator (read-only audit) and doc-writer (READMEs + INSTALL + RUN).

Validator verdict: GO. The five deterministic checks all pass: build hygiene (zero credential patterns in either installer .exe payload, including extracted app.asar contents and drugs.db dump and strings scan), git authorship (only `Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>` in `git log 2334b0c..HEAD`), em-dash and emoji sweep across mission files plus variant trees plus commit messages (zero hits in each), teammate read-only (`git diff 2334b0c..HEAD -- anggota{2,3,4,5}*` empty), and binary structural sanity (both installer .exe are PE32 NSIS SFX, contain app.asar with renderer at resources/app.asar/resources/renderer/, contain drugs.db at the SHA matching the Wave 4 capture, contain medwatch-backend.exe placeholder at the SHA matching the Wave 5 fallback). The three runtime checks (network isolation, SQLite read-write persistence, port collision) are correctly classified as unconfirmable with a Windows-VM user-side runbook in `.mission/findings/wave-6-validation.md`; this is the expected state given the placeholder backend.exe.

Doc-writer outputs:
- `installer-based app/README.md` rewritten (English, technical) with actual Wave 5 metadata, isMacOsCatalina build path explanation, KNOWN_LIMITATION pointer.
- `portable-app/README.md` rewritten (same structure adapted for portable).
- `installer-based app/INSTALL.md` (Bahasa Indonesia formal, end-user-facing): wizard install steps including SmartScreen "More info / Run anyway" bypass.
- `portable-app/RUN.md` (Bahasa Indonesia formal, end-user-facing): portable double-click usage, %APPDATA%\MedWatch\drugs.db persistence note.

All four docs em-dash-free and emoji-free per re-verified sweep.

Wave 6 complete. Advancing to Wave 7 (HANDOVER-REPORT).

## Wave 7 - HANDOVER-REPORT (complete, 2026-05-25T01:40Z)

Dispatched doc-writer (Wave 7) for the comprehensive HANDOVER-REPORT.md. Returned 293-line / 23,690-byte English document at `.mission/HANDOVER-REPORT.md` covering all 10 required sections: mission identity and dates, honest binary inventory, SQLite stats, Wave 6 validator verbatim, open blockers verbatim, commit log, pre-push plan, exact Phase H.M commands, Phase H ferry contract, and the dosen-facing summary. One UNVERIFIED note about a benign page-alignment delta in drugs.db size when extracted-from-installer vs source (SHA256 matches across all 3 copies, treated benign).

Wave 7 complete. Phase H autonomous portion next: branch create, branch push, MERGE BRIEF, stop and wait for user `merge` keyword.

