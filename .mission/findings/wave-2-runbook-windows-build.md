# Wave 2 Runbook: Producing the Windows medwatch-backend.exe

Audience: Ghaisan, when he has access to a Windows machine or a Windows
build runner (GitHub Actions, Windows VM, or borrowed Windows laptop).

Mission: `medwatch-windows-installers-2026-05-25`.

This runbook is the Windows-side companion to Wave 2. The macOS side
of Wave 2 already produced a working `dist/medwatch-backend` arm64
binary that smoke-tests green. The Windows `.exe` cannot be cross
compiled from macOS without Wine and is therefore deferred to the user.

There are three viable paths. Pick one, follow it end to end, do not
mix steps from different paths.

---

## Path A: GitHub Actions Windows runner (recommended)

Use the free Windows runner provided by GitHub Actions to produce
`medwatch-backend.exe` as a downloadable artifact. This is the most
reproducible option and produces a clean binary without touching a
local Windows machine.

### A.1 Add the workflow file

Path: `.github/workflows/build-windows-backend.yml`

Content:

```yaml
name: Build Windows backend
on:
  workflow_dispatch:
  push:
    paths:
      - "medwatch_desktop.spec"
      - "api/**"
      - "api/requirements.txt"
      - ".github/workflows/build-windows-backend.yml"

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: python -m pip install --upgrade pip wheel setuptools
      - run: pip install -r api/requirements.txt
      - run: pip install pyinstaller==6.20.0
      - run: pyinstaller medwatch_desktop.spec --clean --noconfirm
      - uses: actions/upload-artifact@v4
        with:
          name: medwatch-backend-windows
          path: dist/medwatch-backend.exe
```

### A.2 Trigger and download

1. Commit the workflow file.
2. Push the branch.
3. From the GitHub repo `Actions` tab, run `Build Windows backend`
   from the `workflow_dispatch` button.
4. Wait approximately 4 to 6 minutes for the runner.
5. Download the artifact `medwatch-backend-windows.zip`, extract
   `medwatch-backend.exe`.
6. Place the `.exe` at:
   - `installer-based app/resources/medwatch-backend.exe`
   - `portable-app/resources/medwatch-backend.exe`

Both Electron variant folders need a copy because each one packages
its own resources.

### A.3 Verify on a Windows host

If you have any Windows machine (laptop or VM), copy the `.exe` over
and run:

```cmd
set MEDWATCH_DESKTOP=1
set MEDWATCH_DB_PATH=C:\Users\%USERNAME%\AppData\Local\Temp\test.db
medwatch-backend.exe
```

Expect `MEDWATCH_BACKEND_PORT=<number>` within 10 seconds of launch.

---

## Path B: Build on a Windows VM or laptop

Use this if you already have a Windows 10 or Windows 11 machine
available. Avoids the GitHub Actions roundtrip but requires local
tooling.

### B.1 Prerequisites on the Windows machine

Install in this order:

1. Python 3.13 from `https://www.python.org/downloads/` (the
   Microsoft Store build is acceptable; the `python.org` installer
   gives more control over PATH).
   - During install, check "Add Python to PATH".
   - Verify: `py -3.13 --version` returns `Python 3.13.x`.
2. Git from `https://git-scm.com/download/win`.
3. Visual C++ Redistributable (usually already present; required by
   some wheels at runtime).

Do NOT install Python 3.14. PyInstaller 6.20 stable does not support
3.14. Stick to 3.13.

### B.2 Clone and bundle

```cmd
git clone https://github.com/Bisura16/medWatch.git
cd medWatch
git checkout ghaisan-APIIntegration
py -3.13 -m venv .venv-desktop
.venv-desktop\Scripts\activate
python -m pip install --upgrade pip wheel setuptools
pip install -r api\requirements.txt
pip install pyinstaller==6.20.0
pyinstaller medwatch_desktop.spec --clean --noconfirm
```

The output is `dist\medwatch-backend.exe`. Copy it to both Electron
variant folders' `resources\` directories.

### B.3 Verify locally

```cmd
set MEDWATCH_DESKTOP=1
set MEDWATCH_DB_PATH=%TEMP%\test.db
dist\medwatch-backend.exe
```

Expect `MEDWATCH_BACKEND_PORT=<port>` within 10 seconds. Hit
`http://127.0.0.1:<port>/api/health` from a separate Command Prompt
with `curl` or a browser.

---

## Path C: Wine on the macOS dev host (not recommended)

PyInstaller can in theory be run under Wine on macOS or Linux to
produce a Windows `.exe`, but the workflow is fragile and Wine on
arm64 macOS is particularly unreliable. Use only as a last resort.

### C.1 Install Wine (requires user approval, NOT done by Claude)

```bash
brew install --cask --no-quarantine wine-stable
```

(The user must approve and run this; Claude is forbidden from
installing system packages.)

### C.2 Set up Python under Wine

This is where Wine on arm64 macOS commonly breaks. Expect to spend
two to four hours debugging Wine prefix issues, missing DLLs, and
Python installer hangs. If you reach this point, prefer Path A.

---

## After the `.exe` exists

Whichever path was used, the deliverable is a single file:

- `medwatch-backend.exe` (about 25 to 30 MB)

Drop a copy into each Electron variant folder:

- `installer-based app/resources/medwatch-backend.exe`
- `portable-app/resources/medwatch-backend.exe`

Wave 5 picks up from there to wire the Electron main process to
spawn the `.exe`, parse the port handshake, and proxy HTTP requests
from the static-export renderer to the bundled backend.

---

## Known gotchas

1. PyInstaller `--onefile` extracts to `%TEMP%` on first launch.
   First launch is slow (5 to 10 seconds) while the bootloader
   unpacks. Subsequent launches reuse the cached extraction. Do not
   interpret the cold-start delay as a hang.
2. Windows Defender or SmartScreen may flag the unsigned `.exe`.
   The README in each variant folder already documents this for
   the end user. Code-signing the binary requires a paid cert and is
   out of scope for this mission.
3. The `.exe` must NOT be UPX-compressed. The current `medwatch_desktop.spec`
   already disables UPX. UPX-compressed binaries trip Windows Defender
   heuristics far more aggressively than uncompressed ones.
4. If `pip install` fails on Windows for `bcrypt`, install
   `Microsoft C++ Build Tools` from the Visual Studio Installer
   then retry. bcrypt 4.x usually ships prebuilt wheels for cp313
   so this should not be necessary, but is the standard workaround.
5. The bundled binary expects `MEDWATCH_DB_PATH` to point at a valid
   SQLite file. The Electron main process (Wave 5) handles first-run
   DB copy from the read-only bundled `drugs.db` to the user-writable
   `%APPDATA%\medwatch\drugs.db` location.

End of runbook.
