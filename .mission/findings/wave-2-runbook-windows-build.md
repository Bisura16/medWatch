# Runbook: Producing the Windows .exe deliverables

Audience: Ghaisan, for producing the three Windows binaries that the mission ships:

1. `installer-based app/dist/MedWatch Setup <version>.exe` (NSIS installer wizard).
2. `portable-app/dist/MedWatch <version>.exe` (single-file portable).
3. `medwatch-backend.exe` (PyInstaller bundle of the Flask backend, embedded into both installers via electron-builder `extraResources`).

Mission: `medwatch-windows-installers-2026-05-25`.

## Scope clarification (locked)

- Windows is the PRIMARY target of this mission. Both installer variants are Windows-only deliverables.
- macOS is OUT OF SCOPE for this mission. The macOS PyInstaller bundle produced in Wave 2 (`dist/medwatch-backend`, 24 MB, arm64) was a proof-of-build for the spec only and is NOT shipped. The Electron variants do NOT package a macOS binary.
- A future mission may revisit Mac (electron-builder accepts `--mac` targets without architectural change), but anything Mac-shaped in this repository today is for spec validation, not distribution.

## Primary path: Docker electronuserland/builder:wine on the macOS dev host

This is the supported path while the project is on a Mac. The container ships Wine plus the build prerequisites, and electron-builder uses Wine to package Windows NSIS and portable artifacts. The PyInstaller backend `.exe` is also built inside the same container (Wine + Python).

### Prerequisites

- Docker Desktop installed and the daemon running (`docker ps` returns without an error).
- Internet access to pull the image on first run (image is roughly 3 GB).
- Repo cloned at a path with no spaces in any parent directory (Docker volume mounting tolerates spaces inside the repo path but parent-dir spaces are quirky on some hosts; this repo is at `/Users/ghaisan/Documents/MedWatchIntegration/medWatch` which is OK).

### Image

`electronuserland/builder:wine` (multi-arch; the amd64 layer runs under Rosetta on Apple Silicon; the build is slower than a native amd64 host but works).

Reference: https://www.electron.build/multi-platform-build (see the Docker section).

### Build script (run from each variant folder)

```bash
cd '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/installer-based app'
docker run --rm \
  -v "$PWD":/project \
  -v ~/.cache/electron:/root/.cache/electron \
  -v ~/.cache/electron-builder:/root/.cache/electron-builder \
  electronuserland/builder:wine \
  bash -c "cd /project && npm install && npx electron-builder --win nsis"
```

```bash
cd '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/portable-app'
docker run --rm \
  -v "$PWD":/project \
  -v ~/.cache/electron:/root/.cache/electron \
  -v ~/.cache/electron-builder:/root/.cache/electron-builder \
  electronuserland/builder:wine \
  bash -c "cd /project && npm install && npx electron-builder --win portable"
```

Outputs land in `dist/` under each variant folder. Names follow the `productName` / `artifactName` settings in `electron-builder.yml`.

### PyInstaller backend in the same container

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
docker run --rm \
  -v "$PWD":/project \
  -v ~/.cache/pip:/root/.cache/pip \
  electronuserland/builder:wine \
  bash -c "cd /project && \
           wine python -m pip install -r api/requirements.txt && \
           wine python -m pip install pyinstaller==6.20.0 && \
           wine pyinstaller medwatch_desktop.spec --clean --noconfirm --distpath dist-windows"
```

The output is `dist-windows/medwatch-backend.exe`. Copy it into the two variant `resources/` directories before running the electron-builder steps above:

```bash
cp dist-windows/medwatch-backend.exe 'installer-based app/resources/medwatch-backend.exe'
cp dist-windows/medwatch-backend.exe 'portable-app/resources/medwatch-backend.exe'
```

If PyInstaller-in-Wine has issues that take longer than 15 to 30 minutes to debug (Wine prefix corruption, missing DLLs, Python installer hangs on the first launch), fall back to the secondary path for the backend only and keep the Docker path for the Electron build (electron-builder itself is robust under Wine).

## Secondary path: GitHub Actions Windows runner

Use when Docker is not available on the dev host, when the Docker run consistently fails, or for reproducible CI builds.

### Workflow file

Path: `.github/workflows/build-windows.yml`

```yaml
name: Build Windows deliverables
on:
  workflow_dispatch:
  push:
    paths:
      - "medwatch_desktop.spec"
      - "api/**"
      - "installer-based app/**"
      - "portable-app/**"
      - ".github/workflows/build-windows.yml"

jobs:
  backend:
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

  installer-nsis:
    needs: backend
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - uses: actions/download-artifact@v4
        with:
          name: medwatch-backend-windows
          path: installer-based app/resources/
      - working-directory: installer-based app
        run: npm install
      - working-directory: installer-based app
        run: npx electron-builder --win nsis
      - uses: actions/upload-artifact@v4
        with:
          name: MedWatch-Setup-Windows
          path: "installer-based app/dist/MedWatch Setup *.exe"

  portable:
    needs: backend
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - uses: actions/download-artifact@v4
        with:
          name: medwatch-backend-windows
          path: portable-app/resources/
      - working-directory: portable-app
        run: npm install
      - working-directory: portable-app
        run: npx electron-builder --win portable
      - uses: actions/upload-artifact@v4
        with:
          name: MedWatch-Portable-Windows
          path: portable-app/dist/MedWatch-*-portable.exe
```

Trigger via the `Actions` tab `workflow_dispatch`. Roughly 8 to 12 minutes total wall clock across the three jobs.

The `drugs.db` is excluded from git (too large), so the runner must either fetch it from a GitHub Release attached to a tag or download it from an artifact uploaded by a separate dispatch. Add a step that fetches `drugs.db` from the release page (URL goes here once the release exists), or upload `drugs.db` as a workflow artifact in a pre-step.

## Tertiary path: native Windows VM or laptop

Use only when both Docker and GitHub Actions are unavailable.

### Prerequisites on the Windows machine

1. Python 3.13 (NOT 3.14; PyInstaller 6.20 stable does not support 3.14).
2. Git for Windows.
3. Node.js 22 LTS.
4. Visual C++ Redistributable (usually preinstalled).

### Build commands

```cmd
git clone https://github.com/Bisura16/medWatch.git
cd medWatch
git checkout main
py -3.13 -m venv .venv-desktop
.venv-desktop\Scripts\activate
python -m pip install --upgrade pip wheel setuptools
pip install -r api\requirements.txt
pip install pyinstaller==6.20.0
pyinstaller medwatch_desktop.spec --clean --noconfirm

copy dist\medwatch-backend.exe "installer-based app\resources\medwatch-backend.exe"
copy dist\medwatch-backend.exe "portable-app\resources\medwatch-backend.exe"

cd "installer-based app"
npm install
npx electron-builder --win nsis

cd ..\"portable-app"
npm install
npx electron-builder --win portable
```

Drop `drugs.db` (246 MiB, SHA256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`) into both variant `resources/` directories before running electron-builder.

## Post-build verification on a Windows host

For each of the three `.exe` files, on a Windows machine:

1. `medwatch-backend.exe` standalone smoke:
   ```cmd
   set MEDWATCH_DESKTOP=1
   set MEDWATCH_DB_PATH=%TEMP%\medwatch-smoke.db
   medwatch-backend.exe
   ```
   Expect `MEDWATCH_BACKEND_PORT=<n>` on stdout within 10 seconds. Hit `http://127.0.0.1:<n>/api/health` from a browser; expect HTTP 200.

2. NSIS installer end-to-end:
   - Double click `MedWatch Setup x.y.z.exe`.
   - SmartScreen will warn on the unsigned binary. Click `More info` then `Run anyway`.
   - Wizard appears. Pick an install dir. Finish.
   - Confirm Desktop shortcut and Start Menu shortcut exist.
   - Launch MedWatch from the shortcut. Confirm the renderer loads, drug search works, side-effect lookup works.
   - Confirm `%APPDATA%\MedWatch\drugs.db` exists after first launch.
   - Uninstall via Settings -> Apps. Confirm the install directory and shortcuts are removed.

3. Portable end-to-end:
   - Double click `MedWatch x.y.z portable.exe`.
   - SmartScreen warning then Run anyway.
   - Confirm renderer loads, features work.
   - Confirm `%LOCALAPPDATA%\Temp` holds the extracted runtime.
   - Confirm `%APPDATA%\MedWatch\drugs.db` exists after first launch.

## Known gotchas

1. `--onefile` PyInstaller bundles extract to `%TEMP%` on first launch. First launch is 5 to 10 seconds. Subsequent launches reuse the cache. Do not interpret cold start as a hang.
2. Windows SmartScreen will flag the unsigned `.exe`. The end-user docs already cover the "More info, Run anyway" path. Code signing is out of scope for this mission.
3. UPX compression is disabled in `medwatch_desktop.spec` because UPX-packed binaries trip Defender heuristics much more aggressively.
4. If `pip install` errors on `bcrypt`, install `Microsoft C++ Build Tools` via the Visual Studio Installer and retry. Modern bcrypt ships prebuilt wheels for cp313, so this is rare.
5. The Electron main process (Wave 5) copies the bundled `drugs.db` from `process.resourcesPath` to `%APPDATA%\MedWatch\drugs.db` on first launch, leaving the bundled copy read-only and the user-side copy writable.

End of runbook.
