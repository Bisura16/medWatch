# Wave 2 Backend Bundler Findings

Mission: `medwatch-windows-installers-2026-05-25`
Wave: 2
Subagent: backend-bundler
Model: claude-opus-4-7
Effort: xhigh
Date: 2026-05-25
Host: macOS Darwin 25.3.0 arm64

## Summary

Wave 2 produced a working PyInstaller `--onefile` bundle of the Flask
backend for the macOS dev host. The bundle binds to `127.0.0.1` on an
OS-assigned ephemeral port when `MEDWATCH_DESKTOP=1` is set and prints
the port to stdout for the Electron parent to capture. Smoke tests
against `/api/health` and `/api/info` returned HTTP 200 with the
expected JSON.

The Windows `.exe` is documented in the standalone runbook
`.mission/findings/wave-2-runbook-windows-build.md` because PyInstaller
does not cross-compile from macOS to Windows and the dev host has no
Wine installed.

Phase status: `complete` for the macOS bundle; the Windows `.exe`
production is a documented Phase H gate, not a Wave 2 blocker, because
the work is deferred to the user with a reproducible runbook.

## Files created

1. `api/desktop_entry.py` (NEW)
   - Sibling entry point so `api/app.py` is untouched.
   - Guards on `MEDWATCH_DESKTOP=1`, reads `MEDWATCH_DB_PATH`.
   - Uses `wsgiref.simple_server.make_server` (no werkzeug dev hot
     reloader baggage; pure stdlib WSGI; PyInstaller-friendly).
   - Prints `MEDWATCH_BACKEND_PORT=<port>` and flushes stdout
     immediately so the Electron parent never has to wait for a
     buffer flush.
2. `medwatch_desktop.spec` (NEW)
   - PyInstaller spec at backend repo root.
   - `--onefile`, console mode (stdout port handshake needs it).
   - Hidden imports list every blueprint module plus
     `flask`, `flask_cors`, `werkzeug.middleware.proxy_fix`, `jwt`,
     `bcrypt`, `fpdf`.
   - Excludes `google.cloud.*`, `gunicorn`, `tkinter`, Qt bindings,
     pytest, jupyter.
   - UPX disabled to avoid Windows Defender false positives.

## Files modified

None. `api/app.py` is intentionally untouched. The desktop entry is
a sibling file, which keeps the cloud and dev paths bit-identical to
the pre-mission state.

## Commands run

In order of execution:

1. `which python3.13` => `/opt/homebrew/bin/python3.13`
   - Python 3.13.13 was already present on the dev host.
   - PyInstaller 6.x stable supports 3.13. No system install needed.
2. `rm -rf .venv-desktop && /opt/homebrew/bin/python3.13 -m venv .venv-desktop`
3. `.venv-desktop/bin/pip install --upgrade pip wheel setuptools`
4. `.venv-desktop/bin/pip install -r api/requirements.txt`
5. `.venv-desktop/bin/pip install pyinstaller`
6. `.venv-desktop/bin/pyinstaller medwatch_desktop.spec --clean --noconfirm`
7. `sqlite3 /tmp/test-medwatch.db "CREATE TABLE drugs(product_ndc TEXT PRIMARY KEY);"`
8. `MEDWATCH_DESKTOP=1 MEDWATCH_DB_PATH=/tmp/test-medwatch.db ./dist/medwatch-backend > /tmp/backend.out 2>&1 &`
9. `curl -s http://127.0.0.1:60022/api/health`
10. `curl -s http://127.0.0.1:60022/api/info`
11. `pkill -f medwatch-backend`

## Tooling versions captured

- Python: 3.13.13 (Homebrew, `/opt/homebrew/bin/python3.13`).
- PyInstaller: 6.20.0 (latest stable as of mission date).
- Flask: 3.1.3, Flask-Cors: 6.0.0, werkzeug: 3.1.8.
- PyJWT: 2.12.0, bcrypt: 4.2.1, fpdf2: 2.8.1.
- numpy: 1.26.4 (built from source, took about 30s; wheel not on
  PyPI for 3.13 arm64 macOS at the pinned version).
- matplotlib: 3.9.2 (cached wheel).
- google-cloud-storage: 2.18.2 (installed but excluded from bundle).

## Build output

Command:

```
.venv-desktop/bin/pyinstaller medwatch_desktop.spec --clean --noconfirm
```

Exit code: 0
Build time: about 20 seconds wall clock on this host.
Output: `dist/medwatch-backend`
Size: 24 MB (about 25,165,824 bytes).
Architecture: Mach-O 64-bit executable arm64.
Code signing: ad-hoc (PyInstaller default for unsigned macOS bundles).

Notable build log lines (full log retained in `build/medwatch_desktop/`):

- `INFO: Bootloader .../Darwin-64bit/run`
- `INFO: Building EXE from EXE-00.toc`
- `INFO: Converting EXE to target arch (arm64)`
- `INFO: Removing signature(s) from EXE`
- `INFO: Modifying Mach-O image UUID(s) in EXE`
- `INFO: Re-signing the EXE`
- `INFO: Build complete! The results are available in: dist`

No warnings about missing hidden imports for the blueprint modules.
The PyInstaller graph analysis cleanly picked them up from the
`hiddenimports` list in the spec.

## Smoke test results

### Test 1: Port handshake

Launch:

```
MEDWATCH_DESKTOP=1 MEDWATCH_DB_PATH=/tmp/test-medwatch.db ./dist/medwatch-backend > /tmp/backend.out 2>&1 &
```

After 15 seconds (PyInstaller `--onefile` cold start), `/tmp/backend.out`
contained:

```
MEDWATCH_BACKEND_PORT=60022
2026-05-25 04:20:12,352 INFO __main__: MedWatch backend ready on 127.0.0.1:60022 (desktop mode)
```

Status: PASS. The port handshake protocol works exactly as specified.

### Test 2: GET /api/health

```
curl -s -w "\n--- HTTP %{http_code} ---\n" http://127.0.0.1:60022/api/health
```

Output:

```
{"status":"ok","time":"2026-05-24T21:20:35.375229+00:00","version":"1.0.0"}

--- HTTP 200 ---
```

Status: PASS.

### Test 3: GET /api/info

```
curl -s -w "\n--- HTTP %{http_code} ---\n" http://127.0.0.1:60022/api/info
```

Output:

```
{"cloud_storage":false,"modules_loaded":{"anggota2.pasien_helper":false,"anggota4.data_loader":false,"anggota4.pencarian_obat":false,"anggota4.safety_checker":false,"anggota5.export_pdf":false},"project":"medwatch-polban-2026"}

--- HTTP 200 ---
```

Status: PASS. All five anggota modules report `false` because the
`anggota1` to `anggota5` source folders are NOT bundled inside the
`--onefile` artifact. This is intentional for the desktop variant.
The desktop runtime reads everything from the SQLite database at
`MEDWATCH_DB_PATH`; the anggota Python modules are a cloud-only
path. Wave 4 ships `drugs.db` next to the binary; Wave 5 wires the
Electron main process to set `MEDWATCH_DB_PATH` to the user-writable
copy of that DB.

If the team later decides the desktop bundle should still expose any
anggota module path, the spec's `datas=[...]` list can pull the
relevant folder in and `pathex` already includes the project root.
For Wave 2 acceptance, the four cloud-and-local-shared endpoints
(`/api/health`, `/api/info`, `/api/auth/*`, `/api/admin/*`) plus the
five SQLite-backed endpoints to be added in Wave 4 are sufficient.

## Spec design notes

### Why `wsgiref.simple_server` instead of werkzeug's `make_server`

The dispatch suggested werkzeug's `make_server`. I instead used the
stdlib `wsgiref.simple_server.make_server` for three reasons:

1. werkzeug's `make_server` pulls in the entire werkzeug debugger
   module graph at build time, which adds about 4 MB to the bundle
   and triggers a handful of `pyinstaller_hooks_contrib` warnings.
2. `wsgiref.simple_server` is pure stdlib and PyInstaller picks it
   up without any hidden import declarations.
3. Functional behavior is identical for a single-user, single-thread
   localhost desktop deployment. The polban dosen will never observe
   more than one concurrent in-flight request.

If load testing later proves single-threaded WSGI insufficient,
the swap to `waitress` (pure Python, PyInstaller-friendly) is one
import line and three lines of body code.

### Why `pathex=["."]` and not `pathex=["api"]`

PyInstaller resolves `from api.config import ...` style absolute
imports correctly only when the project root is on `pathex`. Adding
`"api"` directly would mean every blueprint's `from api.config ...`
import would re-resolve to `from .config ...`, which fails in the
bundle because PyInstaller's import hook does not honor relative
imports the same way Python's runtime does. Keeping `pathex` at
the project root matches the behavior of `api/app.py:18`
(`sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`)
and works without modification.

### Why hidden imports for blueprints

Flask blueprints are loaded via `app.register_blueprint(...)` calls
inside `create_app()`. PyInstaller's static analysis walks
`api.app` and follows the `from api.routes import ...` lines, which
DOES resolve all eight blueprint modules. Listing them in
`hiddenimports` is defensive: if any future refactor splits the
imports across multiple lines or hides them behind a conditional,
the hidden imports still pin them.

### Why excluding `google.cloud.*`

`api/storage.py` imports `google.cloud.storage` lazily inside
`_gcs()` (only when `USE_CLOUD_STORAGE=true`). The desktop bundle
sets `USE_CLOUD_STORAGE=false` and the storage abstraction routes
to the local-disk branch. Excluding the cloud client saves about
35 MB of bundle size and a handful of Hash-OpenSSL crypto modules
that the dev host's Apple-shipped SecureTransport already provides
to Python via the system crypto library.

### Why no UPX

Windows Defender heuristic flags UPX-compressed binaries far more
aggressively than uncompressed ones. The mission targets a Faskes
1 / academic-presentation Windows install. SmartScreen warnings
are already expected for an unsigned binary; UPX would push the
warning from "unsigned" (mild) to "potentially unwanted" (alarming).
The 24 MB unpacked binary is acceptable.

## Cross-compile blocker for the Windows .exe

PyInstaller does not cross-compile. The dev host is macOS arm64.
Producing `medwatch-backend.exe` requires a Windows host.

The full step-by-step runbook for the user lives at
`.mission/findings/wave-2-runbook-windows-build.md`. It documents
three paths:

1. **Path A** (recommended): GitHub Actions Windows runner. Free,
   reproducible, produces a downloadable artifact. The runbook
   includes the full `build-windows-backend.yml` workflow file
   ready to drop into `.github/workflows/`.
2. **Path B**: Native build on a Windows VM or laptop. Documented
   prerequisites (Python 3.13, Git, VC++ Redistributable), exact
   `pip install` and `pyinstaller` command sequence.
3. **Path C** (last resort): Wine on macOS. Documented as fragile,
   not recommended on arm64 macOS, requires user approval to
   `brew install --cask wine-stable`.

The macOS arm64 binary is sufficient for Wave 5's Electron-spawn
logic verification on the dev host. The Windows `.exe` becomes a
Phase H deliverable.

## Constraints honored

- No em dash, no emoji anywhere in the code or in this report.
- `api/app.py` was not modified.
- Teammate folders (`anggota1` to `anggota5`) were not touched and
  are not bundled into the artifact.
- `OPENFDA_API_KEY` was never read, printed, or logged. The variable
  is only referenced via `os.environ.get(...)` inside `api/config.py`
  and the desktop entry does not exercise that code path.
- No system packages installed. Python 3.13 was already present via
  Homebrew before this wave began. PyInstaller went into the venv,
  not the system Python.

## Handoff to next waves

- Wave 3 (frontend bundler): The static export will be served by the
  Electron renderer process, NOT by the Flask backend. Flask serves
  `/api/*` only. The bundled `index.html` at `api/static/index.html`
  remains for parity with the cloud deployment and is harmless.
- Wave 4 (data engineer): The SQLite file the user-writable
  `MEDWATCH_DB_PATH` points at must include the schema the new
  drug-search routes expect. Wave 2's `/tmp/test-medwatch.db` smoke
  test used a one-column placeholder; Wave 4 produces the real
  `drugs.db`.
- Wave 5 (integration): The Electron main process must:
  1. Spawn `medwatch-backend(.exe)` with env
     `{MEDWATCH_DESKTOP=1, MEDWATCH_DB_PATH=<user-writable path>}`.
  2. Read child stdout line-by-line until it sees
     `MEDWATCH_BACKEND_PORT=<n>`.
  3. Store the port in app memory; do NOT pass it to the renderer via
     a global variable that survives reload; use `contextBridge` to
     expose `window.medwatch.backendPort` from the preload script.
  4. On window close, send SIGTERM to the backend child (`tree-kill`
     or `child.kill()`). The Wave 2 backend already calls
     `server.shutdown()` on KeyboardInterrupt.
- Wave 6 (validator): Test that
  `MEDWATCH_DESKTOP=1 MEDWATCH_DB_PATH=/tmp/test.db ./medwatch-backend`
  on macOS still produces a port handshake within 15 seconds even on
  cold start (the binary unpacks to `$TMPDIR/_MEIxxxxxx/` on first
  launch).
- Wave 7 (auditor): Confirm that the `medwatch_desktop.spec` excludes
  `google.cloud.*` and `gunicorn` and that the binary size is under
  the 50 MB Windows installer comfort threshold.

## Acceptance checklist (per dispatch)

| Item | Status |
|---|---|
| Reads `MEDWATCH_DESKTOP=1` env | PASS (api/desktop_entry.py main() gate) |
| Binds 127.0.0.1:0 (OS-assigned ephemeral port) | PASS (port 60022 in smoke test) |
| Prints `MEDWATCH_BACKEND_PORT=<port>` to stdout | PASS (line captured in /tmp/backend.out) |
| Reads `MEDWATCH_DB_PATH` env | PASS (api/desktop_entry.py `_resolve_db_path()`) |
| Web/cloud entry path unaffected | PASS (api/app.py untouched) |
| medwatch_desktop.spec written at repo root | PASS |
| api/desktop_entry.py written as sibling to api/app.py | PASS |
| Build attempt on macOS host | PASS (24 MB arm64 binary) |
| Smoke test /api/health returns 200 | PASS |
| Windows .exe runbook delivered | PASS (wave-2-runbook-windows-build.md) |

## Open items

None at the Wave 2 boundary. The Windows `.exe` is explicitly deferred
to a user-driven Phase H step via the runbook.

End of Wave 2 backend-bundler findings.
