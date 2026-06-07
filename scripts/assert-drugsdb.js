/**
 * Build-time guard for the bundled drug catalog.
 *
 * Shipping an installer with a missing or empty drugs.db is the worst
 * regression this project has hit (the catalog silently disappears). This
 * asserts the catalog is present and sane and FAILS the build (exit 1 / throw)
 * otherwise, so a broken installer is never produced.
 *
 * Always-on checks (pure fs, work on any runner): file exists and is larger
 * than 150 MB. Deeper checks (row count 20,828 and an FTS5 probe) run when
 * node:sqlite is available and are skipped, not failed, when it is not.
 *
 * Usage (CLI):   node scripts/assert-drugsdb.js path/to/drugs.db
 * Usage (hook):  const { assertDb } = require("../scripts/assert-drugsdb.js")
 */
"use strict";

const fs = require("fs");

const MIN_BYTES = 150 * 1024 * 1024; // 150 MB
const EXPECTED_ROWS = 20828;

function assertDb(dbPath) {
  if (!fs.existsSync(dbPath)) {
    throw new Error(`drugs.db missing at ${dbPath}`);
  }
  const size = fs.statSync(dbPath).size;
  if (size < MIN_BYTES) {
    throw new Error(`drugs.db too small at ${dbPath}: ${size} bytes (< ${MIN_BYTES})`);
  }
  try {
    const { DatabaseSync } = require("node:sqlite");
    const db = new DatabaseSync(dbPath, { readOnly: true });
    try {
      const n = db.prepare("SELECT COUNT(*) AS n FROM drugs").get().n;
      const fts = db
        .prepare("SELECT COUNT(*) AS n FROM drugs_fts WHERE drugs_fts MATCH 'aspirin*'")
        .get().n;
      if (n !== EXPECTED_ROWS) {
        throw new Error(`drugs.db row count ${n} != ${EXPECTED_ROWS} at ${dbPath}`);
      }
      if (!(fts > 0)) {
        throw new Error(`drugs.db FTS5 probe failed (aspirin* -> ${fts}) at ${dbPath}`);
      }
      console.log(`OK ${dbPath}: ${size} bytes, ${n} rows, FTS5 ok`);
    } finally {
      db.close();
    }
  } catch (e) {
    const msg = String((e && e.message) || e);
    if (e && (e.code === "ERR_UNKNOWN_BUILTIN_MODULE" || /node:sqlite/.test(msg))) {
      console.log(`OK ${dbPath}: ${size} bytes (size-only; node:sqlite unavailable)`);
    } else {
      throw e;
    }
  }
}

module.exports = { assertDb, MIN_BYTES, EXPECTED_ROWS };

if (require.main === module) {
  const target = process.argv[2] || "resources/drugs.db";
  try {
    assertDb(target);
  } catch (e) {
    console.error("DRUGS.DB ASSERTION FAILED:", (e && e.message) || e);
    process.exit(1);
  }
}
