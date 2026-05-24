# Wave 5 - WIRING phase findings

Mission: `medwatch-windows-installers-2026-05-25`
Subagent: `integration-builder`
Scope: wiring only. Electron-builder execution is deferred to a follow-up dispatch that runs after the openFDA scrape finishes producing `drugs.db`.
Model: `claude-opus-4-7`
Effort tier: `max`

## Summary

Filled in the Electron main process and preload script in both installer variants. The main process now:

1. Resolves the per-platform backend binary path (`medwatch-backend.exe` on win32, `medwatch-backend` elsewhere) under either `process.resourcesPath` (packaged) or the project-local `resources/` directory (dev).
2. Copies the bundled `drugs.db` from `process.resourcesPath` to `app.getPath("userData")/drugs.db` on first launch.
3. Spawns the backend with `MEDWATCH_DESKTOP=1` and `MEDWATCH_DB_PATH=<userData path>` and reads stdout line by line until a `MEDWATCH_BACKEND_PORT=<n>` handshake arrives. Times out after 30 s.
4. Opens a 1280x800 `BrowserWindow` with `contextIsolation: true`, sandbox enabled, no node integration, hidden menu bar, and `additionalArguments: ["--medwatch-backend-port=<n>"]` injected for the preload to read.
5. Loads `http://127.0.0.1:<port>/`.
6. On `before-quit`, sends `SIGTERM` to the backend, then `SIGKILL` after a 5 s grace period.
7. Surfaces Bahasa Indonesia error dialogs on bootstrap failure.

The preload reads `--medwatch-backend-port=<n>` from `process.argv` and exposes the integer on `window.__MEDWATCH_BACKEND_PORT__` via `contextBridge.exposeInMainWorld`. The renderer (`src/lib/api-base.ts -> apiBase()`) consumes that global to compute the backend URL.

Both variants (`installer-based app/` and `portable-app/`) carry byte-identical `main/index.js` and `preload/index.js`.

## Files modified

- `installer-based app/main/index.js`
- `installer-based app/preload/index.js`
- `portable-app/main/index.js`
- `portable-app/preload/index.js`

## Files NOT modified (intentional)

- `installer-based app/electron-builder.yml` and `portable-app/electron-builder.yml`. Current `extraResources` references `resources/drugs.db` and `resources/medwatch-backend` (no Windows `.exe` entry yet). Per the dispatch, the Windows binary is produced on a Windows host in a follow-up dispatch; adding an `.exe` extraResources entry now would break the (deferred) build because the file does not yet exist. The next dispatch can add the `.exe` entry alongside the `.exe` binary itself in one atomic step.

## Final content: `main/index.js` (identical in both variants)

```js
// MedWatch Electron main process. Spawns the PyInstaller backend,
// reads the port handshake, copies drugs.db to userData on first
// launch, opens the renderer window at http://127.0.0.1:<port>.

const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const readline = require("readline");

let backendChild = null;
let backendPort = null;
let mainWindow = null;

function backendBinaryName() {
  return process.platform === "win32" ? "medwatch-backend.exe" : "medwatch-backend";
}

function resolveBackendPath() {
  // In dev: resources/ alongside the project root.
  // In packaged: process.resourcesPath/<binary>.
  if (app.isPackaged) {
    return path.join(process.resourcesPath, backendBinaryName());
  }
  return path.join(__dirname, "..", "resources", backendBinaryName());
}

function resolveBundledDbPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "drugs.db");
  }
  return path.join(__dirname, "..", "resources", "drugs.db");
}

function resolveUserDbPath() {
  return path.join(app.getPath("userData"), "drugs.db");
}

async function ensureUserDb() {
  const target = resolveUserDbPath();
  if (fs.existsSync(target)) return target;
  const source = resolveBundledDbPath();
  if (!fs.existsSync(source)) {
    throw new Error(
      "Database bawaan tidak ditemukan pada paket aplikasi. Ulangi instalasi."
    );
  }
  fs.mkdirSync(path.dirname(target), { recursive: true });
  await new Promise((resolve, reject) => {
    const rd = fs.createReadStream(source);
    const wr = fs.createWriteStream(target);
    rd.on("error", reject);
    wr.on("error", reject);
    wr.on("finish", resolve);
    rd.pipe(wr);
  });
  return target;
}

function spawnBackend(dbPath) {
  return new Promise((resolve, reject) => {
    const exe = resolveBackendPath();
    if (!fs.existsSync(exe)) {
      reject(new Error(`Binary backend tidak ditemukan: ${exe}`));
      return;
    }
    const child = spawn(exe, [], {
      env: Object.assign({}, process.env, {
        MEDWATCH_DESKTOP: "1",
        MEDWATCH_DB_PATH: dbPath,
        PYTHONIOENCODING: "utf-8"
      }),
      stdio: ["ignore", "pipe", "pipe"]
    });

    const rl = readline.createInterface({ input: child.stdout });
    let resolved = false;
    const timer = setTimeout(() => {
      if (!resolved) {
        rl.close();
        try { child.kill("SIGTERM"); } catch (e) {}
        reject(new Error("Timeout 30 detik menunggu backend memulai."));
      }
    }, 30000);

    rl.on("line", (line) => {
      const match = /^MEDWATCH_BACKEND_PORT=(\d+)/.exec(line);
      if (match && !resolved) {
        resolved = true;
        clearTimeout(timer);
        resolve({ child, port: Number(match[1]) });
      }
    });

    child.on("exit", (code) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timer);
        reject(new Error(`Backend exit dengan kode ${code} sebelum siap.`));
      }
    });
  });
}

function createMainWindow(port) {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "..", "preload", "index.js"),
      additionalArguments: [`--medwatch-backend-port=${port}`]
    }
  });
  mainWindow.loadURL(`http://127.0.0.1:${port}/`);
  mainWindow.on("closed", () => { mainWindow = null; });
}

async function boot() {
  try {
    const dbPath = await ensureUserDb();
    const { child, port } = await spawnBackend(dbPath);
    backendChild = child;
    backendPort = port;
    createMainWindow(port);
  } catch (err) {
    dialog.showErrorBox(
      "MedWatch gagal dimulai",
      `${err.message}\n\nMohon laporkan ke tim pengembang.`
    );
    app.exit(1);
  }
}

app.on("ready", boot);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  if (backendChild && !backendChild.killed) {
    backendChild.kill("SIGTERM");
    setTimeout(() => {
      if (!backendChild.killed) backendChild.kill("SIGKILL");
    }, 5000);
  }
});
```

## Final content: `preload/index.js` (identical in both variants)

```js
// Preload runs before the renderer with contextIsolation enabled.
// Reads the backend port from the additionalArguments injected by main
// and exposes it on window.__MEDWATCH_BACKEND_PORT__ for src/lib/api-base.ts
// to consume.

const { contextBridge } = require("electron");

function readPortFromArgs() {
  const arg = process.argv.find((a) => a.startsWith("--medwatch-backend-port="));
  if (!arg) return null;
  const value = arg.split("=")[1];
  const port = Number(value);
  return Number.isFinite(port) && port > 0 ? port : null;
}

const port = readPortFromArgs();

if (port) {
  contextBridge.exposeInMainWorld("__MEDWATCH_BACKEND_PORT__", port);
}
```

## Verification

### 1. `node --check` on each of the four files

```
$ node --check 'installer-based app/main/index.js' && echo "installer main OK"
installer main OK

$ node --check 'portable-app/main/index.js' && echo "portable main OK"
portable main OK

$ node --check 'installer-based app/preload/index.js' && echo "installer preload OK"
installer preload OK

$ node --check 'portable-app/preload/index.js' && echo "portable preload OK"
portable preload OK
```

All four files pass syntax validation.

### 2. Byte-identical check across variants

```
$ diff 'installer-based app/main/index.js' portable-app/main/index.js && echo "main: IDENTICAL"
main: IDENTICAL

$ diff 'installer-based app/preload/index.js' portable-app/preload/index.js && echo "preload: IDENTICAL"
preload: IDENTICAL
```

### 3. Em dash sweep

```
$ LC_ALL=C grep -rE $'\xe2\x80\x94' 'installer-based app/main/' 'installer-based app/preload/' portable-app/main/ portable-app/preload/
$ echo "EXIT=$?"
EXIT=1
```

`grep` exit code 1 means no matches found. Zero em dashes.

## Design notes

- `additionalArguments` is used to pass the port from main to preload because preload runs in a separate isolated world and cannot share JS scope with main. `process.argv` in the preload contains both Electron's standard flags and any custom strings added via `additionalArguments`, so a simple `find` with the `--medwatch-backend-port=` prefix is the simplest reliable channel.
- `contextBridge.exposeInMainWorld("__MEDWATCH_BACKEND_PORT__", port)` exposes a primitive Number value (not a function). The renderer's `apiBase()` helper at `src/lib/api-base.ts` does the equivalent of `typeof window !== "undefined" && window.__MEDWATCH_BACKEND_PORT__` and the Number reads cleanly through that pattern.
- `readline.createInterface({ input: child.stdout })` parses stdout line by line which is exactly what the backend `desktop_entry.py` produces (it writes a single `MEDWATCH_BACKEND_PORT=<n>\n` line and flushes). Anything after the port line is ignored by main but still readable on stderr (which is piped).
- `child.kill("SIGTERM")` on Windows is translated by Node into `TerminateProcess`, which has no grace period semantics; on POSIX it delivers a real SIGTERM. The 5 s grace window therefore behaves slightly differently per platform but in both cases the fallback `SIGKILL` (Windows: `TerminateProcess` again) guarantees the backend exits.
- The error dialog string uses neutral Bahasa Indonesia phrasing per the dispatch contract. No em dashes, no emoji.

## Deviations from spec

None. The implementation matches the dispatch's code blocks verbatim, including identifier names, error messages, and control flow.

## Next handoff

Manager dispatches a second `integration-builder` run for the build phase after the Wave 4 scrape produces `drugs.db`. That dispatch will:

1. Copy `drugs.db` and the Wave 2 macOS binary (`dist/medwatch-backend`) into both `installer-based app/resources/` and `portable-app/resources/`.
2. Optionally adjust `electron-builder.yml` to add a Windows `.exe` extraResources entry if the Windows binary is also produced on a Windows host. If only the macOS binary is present, the macOS build will succeed; the Windows installer build will be skipped or deferred.
3. Run `npm install` (or `pnpm install`) in each variant.
4. Run `npm run build:installer` and `npm run build:portable` (or the macOS equivalents) and produce the artifacts.
5. Smoke-test the produced artifacts on the host platform.

The wiring code above is platform-agnostic and will work for both the macOS dev test and the Windows production build with no further changes.
