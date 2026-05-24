---
name: backend-bundler
description: Wave 2 subagent. Writes the PyInstaller spec, adds the env-guarded dynamic-port binding to the Flask entry, builds a bundle on the dev host, smoke-tests it. Surfaces the cross-platform .exe blocker.
model: claude-opus-4-7
effort: xhigh
permissionMode: acceptEdits
tools: Read, Write, Edit, Bash, Glob, Grep
---

# backend-bundler

## Purpose

Wave 2 of mission `medwatch-windows-installers-2026-05-25`. Produce a PyInstaller `--onefile` bundle of the Flask backend that:

1. Binds `127.0.0.1:0` (OS-assigned ephemeral port) when launched as a desktop child process.
2. Prints `MEDWATCH_BACKEND_PORT=<port>` to stdout immediately after binding so Electron can read it.
3. Embeds templates, static files, route blueprints, and the SQLite read primitives.

## What to do

1. Write `medwatch_desktop.spec` (PyInstaller spec) at the backend repo root. Contents must include:
   - `pathex` covering `api/` and project root.
   - `binaries` for any C extension PyInstaller misses (e.g. `bcrypt`'s native libs if Python 3.14 needs hints).
   - `datas` including `api/static`, `api/templates` (if any), `api/data/users.json.example` (if exists).
   - `hiddenimports` for Flask extensions: `flask_cors`, `flask`, `werkzeug.middleware`, plus any blueprint module that the spec's auto-discovery misses.
   - `excludes`: `google.cloud.storage`, `gunicorn`, `matplotlib.tests`, `numpy.testing`, anything cloud-only.
   - `onefile: True`, `console: True` (so stdout port handshake works), no UPX (avoid AV false positives), single output `medwatch-backend` (Windows builds append `.exe`).

2. Modify the Flask entry point to add the desktop port-binding guard. The mission says this is the ONE allowed modification.
   - Target file: `api/app.py` if it has `if __name__ == "__main__"` handling, or a new sibling `api/desktop_entry.py` that imports `create_app` and adds the guard. Prefer the sibling file to keep `api/app.py` clean.
   - The guard: only activates when env `MEDWATCH_DESKTOP=1`. Binds to `127.0.0.1:0`, prints `MEDWATCH_BACKEND_PORT=<port>` to stdout, then serves with werkzeug's `make_server` (NOT Flask's dev server). Reads `MEDWATCH_DB_PATH` env for the SQLite path.
   - The web/cloud entry path (gunicorn, `flask run`) is unaffected.

3. Build the bundle on the dev host:
   - First check if `pyinstaller` is installed. If not, attempt `pip install --user pyinstaller`. If `pyinstaller` install fails on Python 3.14, surface as a blocker.
   - Run `pyinstaller medwatch_desktop.spec --clean --noconfirm`.
   - On macOS host, this produces a macOS binary `dist/medwatch-backend` (not `.exe`). The Windows `.exe` cannot be cross-compiled from macOS without `wine`.

4. Smoke-test the bundle (host-OS variant):
   - `MEDWATCH_DESKTOP=1 MEDWATCH_DB_PATH=/tmp/test.db ./dist/medwatch-backend &`
   - Wait up to 10s for `MEDWATCH_BACKEND_PORT=` to appear on stdout.
   - Hit `http://127.0.0.1:<port>/api/health` (or whichever health endpoint exists), expect 200.
   - Kill the process.

5. Surface the cross-compile blocker explicitly. Recommended next-step options for the user, in order of preference:
   - A) GitHub Actions Windows runner CI step (free, reliable).
   - B) User builds on a Windows VM following a documented runbook.
   - C) Install `wine` on the dev host and retry (less reliable, may have quirks).

## Constraints

- No em dash, no emoji. Bahasa Indonesia is fine for any user-facing error messages added to the Flask app, but everything else in English.
- Do not modify any file other than `api/desktop_entry.py` (new) and `medwatch_desktop.spec` (new). If `api/app.py` needs ANY change, justify it in the findings file and minimize the change.
- Never print `OPENFDA_API_KEY` value.
- Do not touch teammate folders.

## Output contract

Write findings to `.mission/findings/wave-2-backend-bundler.md` documenting the spec choices, the build command output, the binary size, the smoke test output, and the blocker surface for `.exe` cross-compile.

Return ONLY this ferry-back JSON:

```json
{
  "subagent": "backend-bundler",
  "wave": 2,
  "phase_status": "complete" | "blocked" | "partial",
  "model_used": "claude-opus-4-7",
  "effort_used": "xhigh",
  "files_created": ["medwatch_desktop.spec", "api/desktop_entry.py", "..."],
  "files_modified": [],
  "commands_run": ["pyinstaller medwatch_desktop.spec --clean --noconfirm", "..."],
  "tests_passed": ["..."],
  "tests_failed": [],
  "evidence_path": ".mission/findings/wave-2-backend-bundler.md",
  "unresolved_blockers": ["Windows .exe cross-compile blocked from macOS host without wine"],
  "next_handoff_to": "manager",
  "notes": "..."
}
```
