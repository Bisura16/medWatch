// MedWatch Electron main process. Wave 5 wires the backend spawn and DB copy here.
const { app, BrowserWindow } = require("electron");
const path = require("path");

// Wave 5 will fill this in (spawn backend, port handshake, DB copy).
function createPlaceholderWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, "..", "preload", "index.js")
    }
  });
  win.loadFile(path.join(__dirname, "..", "resources", "renderer", "index.html"));
}

app.on("ready", createPlaceholderWindow);
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
