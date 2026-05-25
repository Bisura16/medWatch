# Open Blockers

Format: `- [SEVERITY] [WAVE] description (discovered: <date>, status: <open|mitigated|resolved>)`

Severity scale: BLOCKER (mission stops) > HIGH (one wave stops) > MEDIUM (degrades quality, work continues) > LOW (note for record).

## Active

(none)

## Resolved

- [RESOLVED 2026-05-25] [Wave 5 scope correction] Earlier framing treated the macOS arm64 backend binary as the primary deliverable with the Windows `.exe` "deferred to Phase H runbook". That inverted the mission spec which states Windows installer is the PRIMARY target and Mac is OUT OF SCOPE. Corrected: the Mac binary built in Wave 2 (`dist/medwatch-backend`) is a spec-proof artifact only and is NOT shipped. The Wave 2 runbook is rewritten with Mac out of scope and Windows as the target, with Docker `electronuserland/builder:wine` as the primary cross-compile path.

- [RESOLVED 2026-05-25T01:55Z] [Wave 5 + Wave 6] medwatch-backend.exe placeholder. User rejected the 257 KiB MinGW placeholder as not a valid deliverable. Resolution: GitHub Actions workflow `.github/workflows/build-backend-windows.yml` (committed at `b0c6388`, adjusted at `ff7678d` for Python 3.13 vs PyInstaller 6.20 hook-isolation regression) was triggered. Run id `26378942187` on `windows-latest` produced the real 38.1 MiB PyInstaller bundle (sha256 `bf68689a...912366`). Manager downloaded the artifact, replaced the placeholder in all three locations, re-ran electron-builder for both variants. NSIS rebuilt to 174.6 MiB (sha256 `ad4520da...0315`); portable rebuilt to 148.1 MiB (sha256 `320c294e...58fc`). Validator re-run (`.mission/findings/wave-6-validation-rerun.md`) confirms all 7 checks PASS including the three previously-unconfirmable runtime checks (network-isolation via sandbox-exec, SQLite read-write via Wave 2 macOS backend smoke, port-collision via ephemeral binding under contention). Zero unconfirmable remaining.

## Resolved

- [RESOLVED 2026-05-25] [Wave 2] Python 3.14.5 vs PyInstaller 6.10 incompatibility. Resolution: Python 3.13.13 was already installed on the dev host via Homebrew at `/opt/homebrew/bin/python3.13`. Backend-bundler created a clean `.venv-desktop/` venv on that interpreter, installed `pyinstaller==6.20.0`, and built a 24 MB macOS arm64 binary that smoke-tests green on `/api/health` and `/api/info`. Port handshake (`MEDWATCH_BACKEND_PORT=<n>` to stdout) confirmed working. No system install was performed.
