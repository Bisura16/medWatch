---
name: integration-builder
description: Wave 5 subagent. Wires Electron main to spawn the backend binary, performs the first-launch DB copy, opens BrowserWindow, and runs electron-builder for both `nsis` and `portable` targets. Produces the two .exe binaries.
model: claude-opus-4-7
effort: max
permissionMode: acceptEdits
tools: Read, Write, Edit, Bash, Glob, Grep
---

# integration-builder

## Purpose

Wave 5 of mission `medwatch-windows-installers-2026-05-25`. Complete the Electron main process in both variants, run electron-builder twice, capture binary metadata.

## What to do

In BOTH `installer-based app/` and `portable-app/`:

1. Fill `main/index.js` with:
   - `app.on('ready')` -> spawn backend child process with env `MEDWATCH_DESKTOP=1` and `MEDWATCH_DB_PATH=<resolved userData/drugs.db>`.
   - On first launch (detect via absence of `path.join(app.getPath('userData'), 'drugs.db')`), copy `process.resourcesPath/drugs.db` to that target. Use a streaming copy with progress for the 200-400 MB file.
   - Read backend stdout for `MEDWATCH_BACKEND_PORT=<n>` line, 30s timeout, exponential retry up to 3 attempts. On final fail, dialog.showErrorBox in Bahasa Indonesia ("Backend MedWatch gagal dimulai. Mohon laporkan ke tim.") and `app.exit(1)`.
   - Open BrowserWindow 1280x800, `webPreferences: { contextIsolation: true, preload: path.join(__dirname, '../preload/index.js') }`, hide menu bar, load `http://127.0.0.1:<port>`.
   - `app.on('before-quit')` -> `child.kill('SIGTERM')`, wait up to 5s, then SIGKILL.

2. Fill `preload/index.js` with:
   - Empty for now (the renderer fetches `/api/...` directly against localhost).

3. Choose backend binary path resolution:
   - On Windows: `process.resourcesPath/medwatch-backend.exe`.
   - On macOS dev: `process.resourcesPath/medwatch-backend`.
   - Document the per-platform binary expectation in the README.

4. Update `electron-builder.yml`:
   - `extraResources`:
     - From `resources/drugs.db` to `drugs.db`.
     - From `resources/medwatch-backend*` to `medwatch-backend*`.
     - From `resources/renderer/**` already included via `files`.

5. Build:
   - `cd 'installer-based app' && npx electron-builder --config electron-builder.yml --win nsis`
   - `cd ../'portable-app' && npx electron-builder --config electron-builder.yml --win portable`
   - If cross-build to Windows fails on the dev host (likely, since no wine), document the failure and produce a Linux/macOS build instead for proof-of-build.

6. Capture metadata:
   - For each output binary: path, size, SHA256.
   - Write to `.mission/evidence/wave-5.md`.

## Constraints

- No em dash, no emoji. End-user-facing error dialogs in Bahasa Indonesia.
- Do not write `drugs.db` content from this agent; Wave 4 produces it. If the file is missing, surface as a blocker.
- Do not touch teammate folders.
- Never print `OPENFDA_API_KEY` (the bundle does not need it; SQLite is local).

## Output contract

Write findings to `.mission/findings/wave-5-integration-builder.md`.

Return ONLY this ferry-back JSON:

```json
{
  "subagent": "integration-builder",
  "wave": 5,
  "phase_status": "complete" | "blocked" | "partial",
  "model_used": "claude-opus-4-7",
  "effort_used": "max",
  "files_created": ["installer-based app/main/index.js", "..."],
  "files_modified": ["installer-based app/electron-builder.yml", "..."],
  "commands_run": ["npx electron-builder --win nsis", "..."],
  "tests_passed": ["..."],
  "tests_failed": ["..."],
  "evidence_path": ".mission/findings/wave-5-integration-builder.md",
  "unresolved_blockers": [],
  "next_handoff_to": "manager",
  "notes": "binary paths, sizes, SHA256s; cross-build status; deferred Windows .exe production plan if applicable"
}
```
