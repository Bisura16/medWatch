# Open Blockers

Format: `- [SEVERITY] [WAVE] description (discovered: <date>, status: <open|mitigated|resolved>)`

Severity scale: BLOCKER (mission stops) > HIGH (one wave stops) > MEDIUM (degrades quality, work continues) > LOW (note for record).

## Active

- [MEDIUM] [Wave 5] Windows cross-compile blocked by Docker daemon state, NOT by absence of tooling. Docker CLI 29.4.3 is installed; daemon was off when checked at 2026-05-25 00:05Z. User picked option (A) at the Docker ferry: pause and start Docker Desktop, then resume. Once daemon comes up, primary path is `electronuserland/builder:wine` image for both electron-builder targets (NSIS + portable) and for the PyInstaller backend `.exe` build (Wine + Python). Runbook at `.mission/findings/wave-2-runbook-windows-build.md` has the three commands. (discovered: 2026-05-25, status: waiting-on-user-Docker-Desktop-start)

## Resolved

- [RESOLVED 2026-05-25] [Wave 5 scope correction] Earlier framing treated the macOS arm64 backend binary as the primary deliverable with the Windows `.exe` "deferred to Phase H runbook". That inverted the mission spec which states Windows installer is the PRIMARY target and Mac is OUT OF SCOPE. Corrected: the Mac binary built in Wave 2 (`dist/medwatch-backend`) is a spec-proof artifact only and is NOT shipped. The Wave 2 runbook is rewritten with Mac out of scope and Windows as the target, with Docker `electronuserland/builder:wine` as the primary cross-compile path.

## Resolved

- [RESOLVED 2026-05-25] [Wave 2] Python 3.14.5 vs PyInstaller 6.10 incompatibility. Resolution: Python 3.13.13 was already installed on the dev host via Homebrew at `/opt/homebrew/bin/python3.13`. Backend-bundler created a clean `.venv-desktop/` venv on that interpreter, installed `pyinstaller==6.20.0`, and built a 24 MB macOS arm64 binary that smoke-tests green on `/api/health` and `/api/info`. Port handshake (`MEDWATCH_BACKEND_PORT=<n>` to stdout) confirmed working. No system install was performed.
