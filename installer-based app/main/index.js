// MedWatch Electron main process. Spawns the PyInstaller backend,
// reads the port handshake, copies drugs.db to userData on first
// launch, opens the renderer window at http://127.0.0.1:<port>.

const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const readline = require("readline");

// Disable GPU/hardware acceleration before the app becomes ready. Target
// machines (puskesmas) may have no GPU or a flaky driver; forcing CPU
// rendering avoids GPU-process crashes. This is paired with renderer-side
// reduced-motion / "Mode Ringan" fallbacks so visuals degrade gracefully.
app.disableHardwareAcceleration();

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

function resolveRendererDir() {
  // The Next.js static export is shipped as an extra resource and served
  // by the Flask backend over the loopback port as a single-page app.
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "renderer");
  }
  return path.join(__dirname, "..", "resources", "renderer");
}

function resolveDataDir() {
  // Writable per-user directory for users.json / patients.json so records
  // persist across restarts (the backend seeds it from its bundled copy).
  return path.join(app.getPath("userData"), "data");
}

async function ensureUserDb() {
  const target = resolveUserDbPath();
  const source = resolveBundledDbPath();
  if (!fs.existsSync(source)) {
    throw new Error(
      "Database bawaan tidak ditemukan pada paket aplikasi. Ulangi instalasi."
    );
  }
  // Copy on first launch, and refresh when the bundled catalog differs in size
  // from the user copy. After an app upgrade that ships a newer catalog, the
  // old per-user copy must not be reused, or the app would serve a stale
  // catalog from a previous version.
  let needCopy = !fs.existsSync(target);
  if (!needCopy) {
    try {
      if (fs.statSync(target).size !== fs.statSync(source).size) needCopy = true;
    } catch (e) {
      needCopy = true;
    }
  }
  if (!needCopy) return target;
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
        MEDWATCH_RENDERER_DIR: resolveRendererDir(),
        MEDWATCH_DATA_DIR: resolveDataDir(),
        PYTHONIOENCODING: "utf-8"
      }),
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true
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
  const targetUrl = `http://127.0.0.1:${port}/`;
  mainWindow.loadURL(targetUrl);
  // Retry once on a transient load failure (backend accepting connections
  // a moment after the port handshake). -3 is ERR_ABORTED, ignored.
  mainWindow.webContents.on("did-fail-load", (_e, errorCode) => {
    if (errorCode !== -3 && mainWindow) {
      setTimeout(() => {
        if (mainWindow) mainWindow.loadURL(targetUrl);
      }, 600);
    }
  });
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
