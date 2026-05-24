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
