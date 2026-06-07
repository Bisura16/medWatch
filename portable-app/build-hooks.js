"use strict";

const path = require("path");
const { assertDb } = require("../scripts/assert-drugsdb.js");

// electron-builder beforeBuild hook. Fails the build (throws) when the bundled
// drug catalog is missing or empty, so an installer with no catalog is never
// produced. Returning true lets the normal native-dependency step proceed.
exports.default = async function beforeBuild() {
  assertDb(path.join(__dirname, "resources", "drugs.db"));
  return true;
};
