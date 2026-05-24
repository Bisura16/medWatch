---
name: scaffold-builder
description: Wave 1 subagent that creates the two Electron variant folders (`installer-based app/` and `portable-app/`) with electron-builder configs, package.json, and minimal main/preload skeletons. Does not produce a binary; only the source tree.
model: claude-opus-4-7
effort: xhigh
permissionMode: acceptEdits
tools: Read, Write, Edit, Bash, Glob, Grep
---

# scaffold-builder

## Purpose

Wave 1 of mission `medwatch-windows-installers-2026-05-25`. Create the two variant folder structures so Waves 2-5 have a place to drop their artifacts.

## What to create

In the backend repo root, two top-level folders (literal names with the space and hyphen as specified by the user):

- `installer-based app/`
- `portable-app/`

Inside EACH:

1. `electron-builder.yml` (YAML preferred over JS config for diff readability).
   - `appId: com.medwatch.desktop.<variant>`
   - `productName: MedWatch`
   - `directories.output: dist`
   - `files`: include `main/`, `preload/`, `resources/renderer/**`
   - `extraResources`: copy `resources/drugs.db` and `resources/medwatch-backend*` (the backend binary lands here in Wave 5)
   - For `installer-based app/`: `win.target: nsis`, `nsis.oneClick: false`, `nsis.allowToChangeInstallationDirectory: true`, `nsis.createDesktopShortcut: true`, `nsis.createStartMenuShortcut: true`.
   - For `portable-app/`: `win.target: portable`, `portable.artifactName: MedWatch-${version}-portable.exe`.
   - Both: `win.icon: resources/icon.ico` (placeholder for now; real icon added later if available).

2. `package.json`:
   - `name`: `medwatch-installer` or `medwatch-portable`.
   - `version`: `0.1.0`.
   - `main`: `main/index.js`.
   - `scripts`: `build:installer` and `build:portable` invoke `electron-builder --config electron-builder.yml`.
   - `devDependencies`: `electron@^36`, `electron-builder@^25`. Pin exact compatible versions.

3. `main/index.js`:
   - Electron main process skeleton.
   - On `app.ready`: TODO (Wave 5 fills in: spawn backend, read port, open BrowserWindow).
   - Quit on all windows closed (except mac).

4. `main/preload.js`:
   - Empty preload skeleton with `contextIsolation: true` defaults documented.

5. `resources/.gitkeep`:
   - Placeholder so the directory exists in git. Wave 4 drops `drugs.db` here. Wave 5 drops `medwatch-backend.exe`. Wave 3 drops `renderer/`.

6. `README.md`:
   - Variant name, what it produces, how to build (when Waves 4/5 complete), SmartScreen note, troubleshooting placeholder.
   - English. No em dash, no emoji.

## Verification

After scaffolding, run from each variant folder:

```bash
cd 'installer-based app' && npm install --dry-run 2>&1 | tail -5
cd ../'portable-app' && npm install --dry-run 2>&1 | tail -5
```

Both should report a valid dependency graph with no errors. If either errors, fix and re-run.

## Constraints

- No em dash, no emoji.
- Cannot spawn further subagents.
- Do not run `npm install` for real yet (no need to download packages until Wave 5).
- Do not touch any teammate folder (`anggota2..5/`).

## Output contract

Write findings to `.mission/findings/wave-1-scaffold.md` documenting the directory tree, the version pins chosen for electron and electron-builder, and the `npm install --dry-run` output.

Return ONLY this ferry-back JSON:

```json
{
  "subagent": "scaffold-builder",
  "wave": 1,
  "phase_status": "complete" | "blocked" | "partial",
  "model_used": "claude-opus-4-7",
  "effort_used": "xhigh",
  "files_created": ["installer-based app/electron-builder.yml", "..."],
  "files_modified": [],
  "commands_run": ["..."],
  "tests_passed": ["npm install --dry-run installer", "npm install --dry-run portable"],
  "tests_failed": [],
  "evidence_path": ".mission/findings/wave-1-scaffold.md",
  "unresolved_blockers": [],
  "next_handoff_to": "manager",
  "notes": "..."
}
```
