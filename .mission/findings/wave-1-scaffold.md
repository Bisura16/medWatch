# Wave 1 Scaffold Findings

Mission: `medwatch-windows-installers-2026-05-25`
Wave: 1
Subagent: scaffold-builder
Model: claude-opus-4-7
Date: 2026-05-25

## Summary

Created two top-level Electron variant folders inside the backend repo
(`/Users/ghaisan/Documents/MedWatchIntegration/medWatch`) with all skeleton
files needed for Waves 2 through 5 to drop their artifacts in. No binaries
were built; only source tree, configs, and skeletons.

## Variant folders

The folder names use the literal naming the user requested:

- `installer-based app/` (folder name contains a space)
- `portable-app/` (folder name uses a hyphen)

## Directory tree

### installer-based app/

```
./README.md
./electron-builder.yml
./main/index.js
./package.json
./preload/index.js
./resources/.gitkeep
./resources/renderer/.gitkeep
```

### portable-app/

```
./README.md
./electron-builder.yml
./main/index.js
./package.json
./preload/index.js
./resources/.gitkeep
./resources/renderer/.gitkeep
```

Both trees are identical in shape. The variant-specific differences live
inside `electron-builder.yml` (NSIS vs portable target) and `package.json`
(name plus build scripts).

## Dependency versions selected

The dispatch asked for electron pinned to the latest stable major in the v36
line, with v35 as a fallback if v36 was unavailable, plus electron-builder
on the latest 25.x or 26.x stable.

I ran `npm view electron versions --json | tail` and `npm view electron@36
version` to enumerate published v36 releases.

Selected versions:

- `electron`: `36.9.5` (latest patch in the v36 line at time of scaffold;
  v36 was available so no fallback to v35 needed).
- `electron-builder`: `26.11.1` (latest patch in the 26.x line, released
  ahead of the 27 alpha tags).

Both are pinned without a caret so npm always resolves to the exact version
recorded here. This avoids supply chain surprises across the remaining
waves and across the two variant folders.

## File contents at a glance

- `electron-builder.yml`: declares `appId`, `productName`, `directories.output`,
  `files`, `extraResources` for `drugs.db` and `medwatch-backend`, plus
  `win.icon` and the variant-specific `win.target`. NSIS variant has the
  `nsis.*` block (oneClick false, allowToChangeInstallationDirectory true,
  desktop and start menu shortcuts, shortcut name MedWatch). Portable variant
  has the `portable.artifactName` set to `MedWatch-${version}-portable.exe`.
- `package.json`: `name`, `version`, `description`, `main`, `author`,
  `license: MIT`, `private: true`, scripts for `dev`, `build:installer` (or
  `build:portable`), and a mac-target script for cross-config readiness.
- `main/index.js`: Electron main process skeleton. Opens a 1280x800
  BrowserWindow with `contextIsolation: true` and a preload script. Loads
  `resources/renderer/index.html` (placeholder until Wave 3). Has a one-line
  top comment that points at the Wave 5 work. Quits on all windows closed
  except on darwin.
- `preload/index.js`: two-line comment placeholder. Wave 5 may inject a
  backend port via contextBridge here.
- `resources/.gitkeep`: empty file so the resources directory is tracked in
  git. Wave 4 lands `drugs.db` here. Wave 5 lands `medwatch-backend` here.
- `resources/renderer/.gitkeep`: empty file so the renderer directory exists.
  Wave 3 drops the Next.js static export contents here.
- `README.md`: English prose, no em dash, no emoji, sections per spec
  (Output, Build steps, What this contains, First-run SmartScreen warning,
  Offline operation, Database location, Maintainer).

## Verification

### npm install --dry-run installer

Command:

```
cd '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/installer-based app' && npm install --dry-run
```

Tail of output:

```
add electron-builder 26.11.1
add universalify 2.0.1
add jsonfile 6.2.1
add fs-extra 10.1.0
add electron 36.9.5

added 391 packages in 13s

65 packages are looking for funding
  run `npm fund` for details
```

Result: 391 packages resolved, exit code 0, no errors, no peer warnings
that abort. Funding notice is informational.

### npm install --dry-run portable

Command:

```
cd '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/portable-app' && npm install --dry-run
```

Tail of output:

```
add electron-builder 26.11.1
add universalify 2.0.1
add jsonfile 6.2.1
add fs-extra 10.1.0
add electron 36.9.5

added 391 packages in 768ms
add electron-builder 26.11.1
add universalify 2.0.1
add jsonfile 6.2.1
add fs-extra 10.1.0
add electron 36.9.5

added 391 packages in 824ms

65 packages are looking for funding
  run `npm fund` for details
```

The second run completed faster because the npm cache was already warm
from the installer-variant dry-run. Both runs resolved the same 391 package
graph. Exit code 0, no errors.

### Final tree after the verification step

```
/Users/ghaisan/Documents/MedWatchIntegration/medWatch/installer-based app:
total 24
-rw-r--r--  README.md
-rw-r--r--  electron-builder.yml
drwxr-xr-x  main
-rw-r--r--  package.json
drwxr-xr-x  preload
drwxr-xr-x  resources

/Users/ghaisan/Documents/MedWatchIntegration/medWatch/portable-app:
total 24
-rw-r--r--  README.md
-rw-r--r--  electron-builder.yml
drwxr-xr-x  main
-rw-r--r--  package.json
drwxr-xr-x  preload
drwxr-xr-x  resources
```

No `node_modules` directory was created (because `--dry-run` was used).

### Em dash and en dash scan

Searched both variant folders with `grep -rn` for em dash, en dash, and
the UTF-8 mojibake `EUR"`. Zero hits.

## Deviations from the spec

None. Every numbered item in the dispatch was honored:

1. `electron-builder.yml` written per spec for each variant including the
   shortcutName and the portable artifactName.
2. `package.json` written with the exact author, license, private flag, and
   the dev plus mac scripts for cross-platform config readiness.
3. `main/index.js` matches the exact JavaScript skeleton in the dispatch
   verbatim, including the top comment line.
4. `preload/index.js` matches the two-line preload comment block.
5. `resources/.gitkeep` and `resources/renderer/.gitkeep` were both created.
6. `README.md` written per the section list in the dispatch.

## Files created (relative to repo root)

- `installer-based app/electron-builder.yml`
- `installer-based app/package.json`
- `installer-based app/main/index.js`
- `installer-based app/preload/index.js`
- `installer-based app/resources/.gitkeep`
- `installer-based app/resources/renderer/.gitkeep`
- `installer-based app/README.md`
- `portable-app/electron-builder.yml`
- `portable-app/package.json`
- `portable-app/main/index.js`
- `portable-app/preload/index.js`
- `portable-app/resources/.gitkeep`
- `portable-app/resources/renderer/.gitkeep`
- `portable-app/README.md`

## Handover notes for the next waves

- Wave 2 lands the PyInstaller backend at
  `installer-based app/resources/medwatch-backend` and at
  `portable-app/resources/medwatch-backend`. On Windows the extension is
  `.exe`. The `extraResources` block already references the base name.
- Wave 3 drops the Next.js static export (an `out/` style folder) into
  `resources/renderer/` for each variant. The main process already loads
  `resources/renderer/index.html`.
- Wave 4 produces `drugs.db` and places it at `resources/drugs.db` for
  each variant.
- Wave 5 fills in `main/index.js` with backend spawn, port handshake, and
  the first-launch DB copy logic. It also drops the real `resources/icon.ico`.
- The `dev` script (`electron .`) lets Wave 5 do a smoke test from the
  source tree without producing a binary. `build:installer` and
  `build:portable` produce the artifacts under `dist/`.
