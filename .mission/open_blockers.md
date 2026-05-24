# Open Blockers

Format: `- [SEVERITY] [WAVE] description (discovered: <date>, status: <open|mitigated|resolved>)`

Severity scale: BLOCKER (mission stops) > HIGH (one wave stops) > MEDIUM (degrades quality, work continues) > LOW (note for record).

## Active

- [HIGH] [Wave 5] Windows `medwatch-backend.exe` and Electron `MedWatch-Setup.exe` / `MedWatch-portable.exe` cannot be produced from the macOS dev host: no `wine` is installed, and PyInstaller cannot cross-compile to Windows from macOS regardless. Recommended remediation paths (in order of preference): (a) GitHub Actions Windows runner with the runbook at `.mission/findings/wave-2-runbook-windows-build.md`, (b) user runs the build on a Windows VM following the same runbook, (c) install `wine` on the dev host (least reliable). The macOS arm64 backend binary built in Wave 2 (24 MB, smoke-tests green) is the proof-of-build that the spec is correct. Wave 5 integration will produce a macOS-only Electron build as additional proof. (discovered: 2026-05-24, status: deferred-to-Phase-H)

## Resolved

- [RESOLVED 2026-05-25] [Wave 2] Python 3.14.5 vs PyInstaller 6.10 incompatibility. Resolution: Python 3.13.13 was already installed on the dev host via Homebrew at `/opt/homebrew/bin/python3.13`. Backend-bundler created a clean `.venv-desktop/` venv on that interpreter, installed `pyinstaller==6.20.0`, and built a 24 MB macOS arm64 binary that smoke-tests green on `/api/health` and `/api/info`. Port handshake (`MEDWATCH_BACKEND_PORT=<n>` to stdout) confirmed working. No system install was performed.
