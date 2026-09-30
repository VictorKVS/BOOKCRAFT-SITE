import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const requiredRoutes = [
  "/", "/create", "/mailing", "/podcast", "/video-avatar", "/images",
  "/analytics", "/books", "/scripts", "/features", "/examples",
  "/pricing", "/blog", "/studio", "/search", "/login"
];

const requiredFiles = [
  "src/App.jsx",
  "src/pages/HomePage.jsx",
  "src/pages/CreatePage.jsx",
  "src/pages/MailingPage.jsx",
  "src/pages/PodcastPage.jsx",
  "src/pages/VideoAvatarPage.jsx",
  "src/pages/ImagesPage.jsx",
  "src/pages/AnalyticsPage.jsx",
  "src/components/AppShell.jsx",
  "src/components/HeroStage.jsx",
  "src/components/AudienceGrowthHud.jsx",
  "src/components/ContentPlan.jsx",
  "src/components/PodcastHud.jsx",
  "src/components/VideoAvatarHud.jsx"
];

const errors = [];

for (const rel of requiredFiles) {
  if (!fs.existsSync(path.join(root, rel))) {
    errors.push(`MISSING FILE: ${rel}`);
  }
}

const appPath = path.join(root, "src/App.jsx");
const app = fs.existsSync(appPath) ? fs.readFileSync(appPath, "utf8") : "";

for (const route of requiredRoutes) {
  if (!app.includes(`path="${route}"`)) {
    errors.push(`MISSING ROUTE: ${route}`);
  }
}

const homePath = path.join(root, "src/pages/HomePage.jsx");
const home = fs.existsSync(homePath) ? fs.readFileSync(homePath, "utf8") : "";

for (const target of ["/books", "/scripts", "/video-avatar", "/images"]) {
  const escapedTarget = target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const targetPattern = new RegExp(`to\\s*:\\s*["']${escapedTarget}["']`);

  if (!targetPattern.test(home)) {
    errors.push(`HOME CARD TARGET MISSING: ${target}`);
  }
}

const shellPath = path.join(root, "src/components/AppShell.jsx");
const shell = fs.existsSync(shellPath) ? fs.readFileSync(shellPath, "utf8") : "";

for (const target of ["/features","/examples","/pricing","/blog","/studio","/search","/analytics","/login","/create"]) {
  if (!shell.includes(target)) {
    errors.push(`HEADER/MENU TARGET MISSING: ${target}`);
  }
}

if (errors.length) {
  console.error("\nCARCASS AUDIT: FAIL\n");
  for (const err of errors) console.error(`- ${err}`);
  process.exit(1);
}

console.log("\nCARCASS AUDIT: PASS");
console.log(`Routes checked: ${requiredRoutes.length}`);
console.log(`Core files checked: ${requiredFiles.length}`);
console.log("Home cards: OK");
console.log("Header/menu targets: OK");
console.log("Note: static route/file contract only; visual layout and backend/API behavior are separate checks.\n");
