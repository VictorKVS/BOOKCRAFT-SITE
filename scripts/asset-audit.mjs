import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const manifestPath = path.join(root, "public/assets/bookcraft/manifest.json");

if (!fs.existsSync(manifestPath)) {
  console.error("ASSET AUDIT: FAIL");
  console.error("- manifest.json not found");
  process.exit(1);
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const required = manifest.assets.filter((asset) => asset.status !== "optional");

let ready = 0;
let missing = 0;

console.log("\nBOOK-CRAFT ASSET AUDIT\n");

for (const asset of required) {
  const fullPath = path.join(root, "public/assets/bookcraft", asset.path);
  const exists = fs.existsSync(fullPath);

  if (exists) {
    ready++;
    console.log(`READY   ${asset.key}   ${asset.path}`);
  } else {
    missing++;
    console.log(`MISSING ${asset.key}   ${asset.path}`);
  }
}

console.log(`\nRequired assets: ${required.length}`);
console.log(`Ready: ${ready}`);
console.log(`Missing: ${missing}`);

if (missing > 0) {
  console.log("\nASSET STAGE: NOT READY — expected before visual pass.");
  process.exit(2);
}

console.log("\nASSET STAGE: READY");
