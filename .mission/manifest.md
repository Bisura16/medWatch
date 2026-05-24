# Mission Manifest: medwatch-windows-installers-2026-05-25

## Goal

Produce two Windows desktop installer variants for MedWatch, both fully offline, both bundling the openFDA prescription drug dataset as a local SQLite database.

- `installer-based app/` - NSIS installer wizard. Output: `MedWatch-Setup.exe`.
- `portable-app/` - Single-file portable executable. Output: `MedWatch.exe`.

## Architecture (locked)

- Renderer: Next.js static export embedded as Electron renderer files. No SSR at runtime.
- Backend: Flask packaged with PyInstaller `--onefile` as `medwatch-backend.exe`. Spawned by Electron main, binds `127.0.0.1:0`, prints port to stdout for handshake.
- Database: SQLite `drugs.db` bundled as `extraResources`. Copied to `%APPDATA%\MedWatch\drugs.db` on first launch.
- Shell: Electron with `electron-builder` targeting both `nsis` and `portable`.
- Code signing: out of scope. README documents SmartScreen "More info -> Run anyway".
- Mac build: out of scope; electron-builder config accepts future `--mac` target without architectural change.

## Author

- Git author for all commits: Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>
- Co-authored-by trailer: OMITTED to satisfy the project's permanent CLAUDE.md prohibition (the mission prompt says "permitted, not required"; CLAUDE.md says "never include `Co-authored-by: Claude`").

## Constraints recap

- Model: claude-opus-4-7 for every agent. Manager effort: max. Subagent effort: max (validator, data-engineer, integration-builder) or xhigh (scout, scaffold-builder, backend-bundler, frontend-bundler, doc-writer).
- No em dash anywhere. No emoji anywhere.
- `anggota2/`, `anggota3/`, `anggota4/`, `anggota5/` are read-only teammate code. `anggota1/` is Ghaisan's, freely writable in this mission including the new `anggota1/Hasil-Scrap/` directory.
- Backend Flask code is read freely, modified only for desktop port binding (one guarded change in `api/app.py` or its entry point).
- No `git push origin main` and no merge to `main` before Phase H gate. Branch push is autonomous in Phase H.
- `dudungdotnet@gmail.com` is absolute-forbidden across the mission.
- Credentials read from env only; never written, printed, logged, or committed.
- Every reported number traces to a real command in `.mission/evidence/`.

## Wave summary

- Wave 0: Bootstrap, recon, dispatch scout.
- Wave 1: Scaffold two variant folders with electron-builder configs.
- Wave 2: PyInstaller backend bundle, dynamic-port guard.
- Wave 3: Next.js static export, embed renderer into both variants.
- Wave 4: openFDA scrape into `anggota1/Hasil-Scrap/drugs.db`, copy to both variant resources.
- Wave 5: Wire Electron main, run electron-builder for nsis and portable.
- Wave 6: Validator audit + end-user docs.
- Wave 7: Handover report + branch creation + branch push + Phase H gate.

## Phase H gate

After Wave 7, manager creates `mission/windows-installers-20260525` branch from `main`, pushes it to remote, captures the compare URL, then stops and presents a MERGE BRIEF to the user. Manager only merges into `main` after the user replies with the literal word `merge`.
