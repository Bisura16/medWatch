# Wave 6 validation findings

Subagent: validator
Wave: 6
Date: 2026-05-25
Model: claude-opus-4-7 at effort=max
Working directory: `/Users/ghaisan/Documents/MedWatchIntegration/medWatch`
Mission-start SHA: `2334b0c` (Wave 0 bootstrap commit). Pre-mission anchor: `1ef862f`.

Read-only audit; no source files modified. Only artifact extraction to `/tmp/medwatch-validate-nsis/` and `/tmp/medwatch-validate-portable/` for offline inspection (scratch dirs, not committed).

---

## Summary table

| Check | Verdict |
|---|---|
| 1. Network isolation (backend runtime) | UNCONFIRMABLE on this host. Runbook provided. |
| 2. SQLite read-write persistence | UNCONFIRMABLE on this host. Runbook provided. |
| 3. Port collision handling | UNCONFIRMABLE on this host. Runbook provided. |
| 4. Build hygiene (no credential in dist) | PASS |
| 5. Git authorship | PASS |
| 6. No em dash, no emoji | PASS |
| 7. Teammate read-only | PASS |
| (extra) Binary structural sanity | PASS |

Aggregate verdict: **go** (the three unconfirmable items are expected per the documented placeholder backend limitation; checks 4 through 7 plus structural sanity all pass).

---

## Check 1: network isolation (backend-runtime)

### Status

UNCONFIRMABLE on this dev host.

### Why

Three blocking realities:

1. `dist-windows/medwatch-backend.exe` is a **257 KiB placeholder** PE32+ console executable, not a real PyInstaller bundle. It prints a diagnostic to stderr, opens a `MessageBoxA`, and exits 1. It does not bind a port, does not start Flask, and does not emit `MEDWATCH_BACKEND_PORT=...` on stdout for the Electron main process to parse. See `KNOWN_LIMITATION_BACKEND_EXE.md`.
2. The two installer .exe files (`MedWatch Setup 0.1.0.exe` and `MedWatch-0.1.0-portable.exe`) are NSIS-3 self-extracting archives for Windows x86-64. They cannot be executed on macOS arm64 (`darwin 25.3.0`).
3. macOS has no clean cross-platform analog of Linux `unshare -n` for sandboxing a Windows binary even via Wine; running this under Rosetta + Wine would itself fail because of the same QEMU/page-size assertion documented in Wave 5.

The Wave 5 builder explicitly recommended skipping this runtime test for the placeholder builds; see `.mission/findings/wave-5-build.md` "Lessons learned for Wave 6 validation" section.

### User-side runbook (replace placeholder first, then run on Windows)

```
# Step A: build a real medwatch-backend.exe (one-time)
#   Path A1: on a Windows machine with Python 3.13:
#     python -m pip install -r api/requirements.txt
#     python -m pip install pyinstaller==6.20.0
#     pyinstaller medwatch_desktop.spec --clean --noconfirm
#     copy dist\medwatch-backend.exe installer-based app\resources\medwatch-backend.exe
#     copy dist\medwatch-backend.exe portable-app\resources\medwatch-backend.exe
#   Path A2: trigger .github/workflows/windows-build.yml on a Windows-latest runner.

# Step B: rebuild the installers with the real backend
#   cd "installer-based app" && npx electron-builder --config electron-builder.yml --win nsis --x64 --publish=never
#   cd "portable-app"        && npx electron-builder --config electron-builder.yml --win portable --x64 --publish=never

# Step C: network-isolation test on a Windows VM
#   1. Boot Windows 10 / 11 VM with no NIC attached or with outbound firewall rule blocking all egress.
#   2. Install or unpack the .exe.
#   3. Launch MedWatch.exe.
#   4. Confirm: app window opens, drug search returns rows for "ibuprofen", "paracetamol", "aspirin"; side effects panel returns rows; recalls panel returns rows. All from the bundled drugs.db (237 MiB).
#   5. PASS if all panels return data with no network egress (check via VM monitoring tool).
```

---

## Check 2: SQLite read-write persistence

### Status

UNCONFIRMABLE on this dev host (same blockers as Check 1).

### User-side runbook

```
On a Windows VM after rebuilding with a real backend.exe per Check 1:
1. Launch MedWatch.exe via the NSIS installer.
2. Add a test patient via the Pasien CRUD UI.
3. Quit (File -> Exit, or close window).
4. Verify file exists at %APPDATA%\MedWatch\drugs.db (or whatever path api/desktop_entry.py
   configures for the user-writable database; see desktop_entry.py for path resolution).
5. Relaunch MedWatch.exe.
6. Confirm the test patient still appears.
7. PASS if data persists across the relaunch.
```

Note: the canonical write location is currently inside the install dir for the installer-based variant and inside `%LOCALAPPDATA%\MedWatch` or the portable extract dir for the portable variant. `api/desktop_entry.py` resolves this at runtime.

---

## Check 3: Port collision handling

### Status

UNCONFIRMABLE on this dev host (same blockers as Check 1).

### User-side runbook

```
On a Windows VM after rebuilding with a real backend.exe per Check 1:
1. Pre-occupy ports 5000 and 8000 using e.g. `python -m http.server 5000` and `python -m http.server 8000`.
2. Launch MedWatch.exe.
3. Confirm app starts. Backend is expected to bind 127.0.0.1:0 (any free port) and emit
   `MEDWATCH_BACKEND_PORT=<port>` on stdout. The Electron main parses this and uses the
   correct dynamic port.
4. PASS if app loads data normally; FAIL if app freezes or surfaces a port-bind error.
```

Static code reference: `installer-based app/main/index.js` and `portable-app/main/index.js` parse `MEDWATCH_BACKEND_PORT=` from the child process stdout. `api/desktop_entry.py` binds `127.0.0.1:0`. Both code paths were inspected in source by Wave 5; runtime confirmation is gated on a real backend.exe.

---

## Check 4: Build hygiene (no credential value in dist)

### Status

PASS.

### Commands run

```
# 1. Extract inner app-64.7z from both NSIS-wrapped installers:
7z e -o/tmp/medwatch-validate-nsis      "installer-based app/dist/MedWatch Setup 0.1.0.exe"      '$PLUGINSDIR/app-64.7z'
7z e -o/tmp/medwatch-validate-portable  "portable-app/dist/MedWatch-0.1.0-portable.exe"          '$PLUGINSDIR/app-64.7z'

# 2. Extract resources/app.asar, resources/drugs.db, resources/medwatch-backend.exe:
7z x -y -o/tmp/medwatch-validate-nsis/extracted     /tmp/medwatch-validate-nsis/app-64.7z      resources/app.asar resources/drugs.db resources/medwatch-backend.exe
7z x -y -o/tmp/medwatch-validate-portable/extracted /tmp/medwatch-validate-portable/app-64.7z  resources/app.asar resources/drugs.db resources/medwatch-backend.exe

# 3. Extract app.asar contents:
npx asar extract /tmp/medwatch-validate-nsis/extracted/resources/app.asar     /tmp/medwatch-validate-nsis/asar-extracted
npx asar extract /tmp/medwatch-validate-portable/extracted/resources/app.asar /tmp/medwatch-validate-portable/asar-extracted

# 4. Run credential grep over all extracted contents (asar files: js, json, html, css, etc.):
LC_ALL=C grep -rIaE "OPENFDA_API_KEY=[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]+|BEGIN .* PRIVATE KEY|JWT_SECRET=[A-Za-z0-9_-]{5,}" /tmp/medwatch-validate-nsis/asar-extracted /tmp/medwatch-validate-portable/asar-extracted

# 5. SQLite credential scan:
sqlite3 /tmp/medwatch-validate-nsis/extracted/resources/drugs.db ".dump" | LC_ALL=C grep -E "OPENFDA_API_KEY|sk-|ghp_|AKIA|BEGIN .* PRIVATE KEY|JWT_SECRET"

# 6. Strings scan over raw .exe binaries:
strings -a "installer-based app/dist/MedWatch Setup 0.1.0.exe" | LC_ALL=C grep -E "OPENFDA_API_KEY=|sk-|ghp_|AKIA|xox|BEGIN .* PRIVATE KEY|JWT_SECRET="
strings -a "portable-app/dist/MedWatch-0.1.0-portable.exe"     | LC_ALL=C grep -E "OPENFDA_API_KEY=|sk-|ghp_|AKIA|xox|BEGIN .* PRIVATE KEY|JWT_SECRET="
strings -a "dist-windows/medwatch-backend.exe"                 | LC_ALL=C grep -E "OPENFDA_API_KEY=|sk-|ghp_|AKIA|xox|BEGIN .* PRIVATE KEY|JWT_SECRET="

# 7. Service-account JSON shape probes:
LC_ALL=C grep -rIaE '"private_key":\s*"-----BEGIN'                                            /tmp/medwatch-validate-nsis/asar-extracted /tmp/medwatch-validate-portable/asar-extracted
LC_ALL=C grep -rIaE '"client_email":\s*"[a-z0-9_-]+@[a-z0-9.-]+\.iam\.gserviceaccount\.com"'  /tmp/medwatch-validate-nsis/asar-extracted /tmp/medwatch-validate-portable/asar-extracted
LC_ALL=C grep -rIaE '"(refresh_token|access_token)":\s*"[A-Za-z0-9_.-]{20,}"'                 /tmp/medwatch-validate-nsis/asar-extracted /tmp/medwatch-validate-portable/asar-extracted
LC_ALL=C grep -rIaE "OPENFDA_API_KEY"                                                          /tmp/medwatch-validate-nsis/asar-extracted /tmp/medwatch-validate-portable/asar-extracted
```

### Output

All seven greps returned ZERO matches across both installers and their components.

### Verdict

No credential values are bundled. The drugs.db is a pure data export (drug names, ingredients, side-effect terms, recall texts) with no embedded API key. The app.asar contains `main/index.js`, `preload/index.js`, `package.json`, and the static Next.js renderer at `resources/renderer/`. None of these contain credential strings. The placeholder `medwatch-backend.exe` is a minimal MinGW-compiled stub with diagnostic text only.

---

## Check 5: Git authorship

### Status

PASS.

### Command

```
git log --format='%an <%ae>' 2334b0c..HEAD | sort -u
```

### Output

```
Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>
```

### Confirmation

7 commits in the mission window. First (anchor): `2334b0c chore(installer-mission): wave 0 bootstrap and recon`. HEAD: `666eaf7 feat(installer): wave 5 build NSIS and portable, backend placeholder`. All by Ghaisan with the canonical email. Pre-mission anchor `1ef862f` also by Ghaisan. No second author, no Claude attribution, no co-authored-by trailer surfacing as a primary author.

---

## Check 6: No em dash, no emoji

### Status

PASS.

### 6a. Em dash in mission-scope files

Command:
```
LC_ALL=C grep -rE $'\xe2\x80\x94' \
  '.mission/' '.claude/agents/' \
  'installer-based app/main' 'installer-based app/preload' \
  'installer-based app/electron-builder.yml' 'installer-based app/README.md' \
  portable-app/main portable-app/preload portable-app/electron-builder.yml portable-app/README.md \
  scripts/ medwatch_desktop.spec api/desktop_entry.py KNOWN_LIMITATION_BACKEND_EXE.md anggota1/Hasil-Scrap/MANIFEST.md
```

Result: grep exit code 1 (no matches).

### 6b. Em dash in commit messages

Command:
```
git log --format=%B 2334b0c..HEAD | LC_ALL=C grep -E $'\xe2\x80\x94'
```

Result: grep exit code 1 (no matches).

### 6c. Emoji (pictograph Unicode ranges) in mission-scope files

Command (51 files scanned):
```
find <same paths as 6a> -type f | while read -r f; do
  perl -CSD -ne 'if (/[\x{1F300}-\x{1F9FF}\x{2600}-\x{27BF}\x{1F600}-\x{1F64F}]/) { print "$ARGV:$.: $_"; }' "$f"
done
```

Result: zero output.

### 6d. Emoji in commit messages

Command:
```
git log --format=%B 2334b0c..HEAD | perl -CSD -ne 'if (/[\x{1F300}-\x{1F9FF}\x{2600}-\x{27BF}\x{1F600}-\x{1F64F}]/) { print; }'
```

Result: zero output.

---

## Check 7: Teammate read-only

### Status

PASS.

### Command

```
git diff --name-only 2334b0c..HEAD -- 'anggota2*' 'anggota3*' 'anggota4*' 'anggota5*'
```

### Output

Empty (zero lines).

### Reference: full mission-window changed paths

`.gitignore`, `.mission/...`, `KNOWN_LIMITATION_BACKEND_EXE.md`, `anggota1/Hasil-Scrap/MANIFEST.md`, `api/desktop_entry.py`, `installer-based app/...`, `portable-app/...`. Only `anggota1` is touched in the anggota family, which is explicitly allowed for this mission per the role contract.

---

## Extra check: Binary structural sanity

### NSIS installer (`installer-based app/dist/MedWatch Setup 0.1.0.exe`)

```
file:    PE32 executable (GUI) Intel 80386, for MS Windows, Nullsoft Installer self-extracting archive
size:    145592112 bytes (139 MiB)
sha256:  ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470  (MATCHES state.json)
```

Inner `$PLUGINSDIR/app-64.7z` (LZMA2:20, 75 files, 2 folders) contains:
- `resources/app.asar` (2,160,939 bytes; contains `main/`, `preload/`, `package.json`, `resources/renderer/`)
- `resources/drugs.db` (248,926,208 bytes = 237 MiB; sha256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`, MATCHES Wave 4 capture)
- `resources/medwatch-backend.exe` (262,944 bytes; sha256 `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`, MATCHES placeholder source)
- `resources/elevate.exe` (107,520 bytes; Electron standard)
- `MedWatch.exe` (202,690,560 bytes; Electron runtime)
- Full Chromium locales/, ffmpeg.dll, libEGL.dll, libGLESv2.dll, vk_swiftshader.dll, vulkan-1.dll, d3dcompiler_47.dll, etc.

Renderer note: there is no top-level `resources/renderer/` directory in the outer 7z payload; the Next.js renderer assets are packaged inside `app.asar` at path `/resources/renderer/`. This is the standard Electron asar packaging pattern. `npx asar list` confirms 200+ renderer files including 404.html, _next/static/chunks/*, _next/static/media/*, and the build manifests.

### Portable installer (`portable-app/dist/MedWatch-0.1.0-portable.exe`)

```
file:    PE32 executable (GUI) Intel 80386, for MS Windows, Nullsoft Installer self-extracting archive
size:    117895251 bytes (113 MiB)
sha256:  c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab  (MATCHES state.json)
```

Inner `$PLUGINSDIR/app-64.7z` (LZMA2:26, solid, 75 files, 2 folders) contains the same payload as NSIS:
- `resources/app.asar` (2,160,932 bytes)
- `resources/drugs.db` (248,926,208 bytes; sha256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`)
- `resources/medwatch-backend.exe` (262,944 bytes; sha256 `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`)
- `resources/elevate.exe`, `MedWatch.exe`, full Chromium runtime.

The portable variant uses solid compression (LZMA2:26 solid=+) for stronger ratio, hence the lower size. NSIS uses non-solid (Solid=-) for faster random-access install.

### Placeholder backend (`dist-windows/medwatch-backend.exe`)

```
file:    PE32+ executable (console) x86-64, for MS Windows
size:    262944 bytes (257 KiB)
sha256:  77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371  (MATCHES state.json)
```

Strings scan shows expected MinGW-built console stub: section names, no API keys, no flask, no python. Behaves per `KNOWN_LIMITATION_BACKEND_EXE.md` description (writes diagnostic to stderr, calls MessageBoxA, returns exit 1).

---

## Files in dist directories

`installer-based app/dist/`:
- `MedWatch Setup 0.1.0.exe` (139 MiB)
- `MedWatch Setup 0.1.0.exe.blockmap` (149 KiB; electron-builder differential-update metadata)
- `builder-debug.yml` (7.4 KiB; electron-builder verbose log)
- `win-unpacked/` (intermediate; equivalent to the unpacked app payload before NSIS wrapping)

`portable-app/dist/`:
- `MedWatch-0.1.0-portable.exe` (113 MiB)
- `builder-debug.yml` (5.9 KiB)
- `win-unpacked/` (intermediate)

No stale 186 KiB first-pass NSIS uninstaller artifact present (those Docker-Wine failed runs from Wave 5 were cleaned up).

---

## Conclusion

All four "deterministic" checks pass (4 build hygiene, 5 git authorship, 6 em dash and emoji, 7 teammate read-only). The three "runtime" checks (1 network isolation, 2 SQLite persistence, 3 port collision handling) are unconfirmable on this macOS arm64 host because the backend.exe is the documented placeholder, and the deliverable .exes are Windows-only PE32 binaries that cannot be executed natively here. Each unconfirmable check has a user-side runbook the dosen / Ghaisan can follow on a Windows VM after rebuilding `medwatch-backend.exe` per `KNOWN_LIMITATION_BACKEND_EXE.md`.

Binary structural sanity is fully confirmed: both installer SHA256 values match `.mission/state.json`; both contain the canonical `resources/app.asar`, `resources/drugs.db`, and `resources/medwatch-backend.exe` payloads at the expected paths; drugs.db SHA256 matches the Wave 4 capture; placeholder backend.exe SHA256 matches the Wave 2 fallback capture; the Next.js renderer is correctly packaged inside `app.asar` at `/resources/renderer/`.

Verdict: **go** to Wave 7 (Handover and Phase H gate). The three runtime checks remain user-side TODOs documented in their respective runbooks above.
