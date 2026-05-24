# Open Blockers

Format: `- [SEVERITY] [WAVE] description (discovered: <date>, status: <open|mitigated|resolved>)`

Severity scale: BLOCKER (mission stops) > HIGH (one wave stops) > MEDIUM (degrades quality, work continues) > LOW (note for record).

## Active

- [HIGH] [Wave 2] PyInstaller cross-compile to Windows is not possible from macOS without `wine` and without `pyinstaller` installed. Dev host can produce a macOS/Linux backend bundle for proof-of-build, but the actual `medwatch-backend.exe` Windows binary requires either (a) `wine` installed on this host, (b) GitHub Actions Windows runner CI step, or (c) user runs the build on a Windows VM. Will surface concrete evidence and ask user direction when Wave 2 dispatch hits this. (discovered: 2026-05-24, status: open)

- [HIGH] [Wave 2] Python 3.14.5 on dev host is newer than PyInstaller 6.10 supports (3.13 max). Wave 2 dispatch must either install Python 3.13 via pyenv (`pyenv install 3.13 && pyenv local 3.13`) or use Homebrew's `python@3.13` to run the PyInstaller step. Scout confirmed `pyinstaller` is not on PATH at all on the dev host, so a clean 3.13 venv with `pip install pyinstaller` is the proposed approach. (discovered: 2026-05-24, status: open)
