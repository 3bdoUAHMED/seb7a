import { chromium } from "../node_modules/playwright/index.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1400, height: 3000 }, deviceScaleFactor: 2 });
await p.goto(pathToFileURL(resolve("variants.html")).href, { waitUntil: "networkidle" });
await p.evaluate(() => document.fonts.ready);
for (const v of ["v1", "v2", "v3"]) await p.locator("#" + v).screenshot({ path: `raw-${v}.png`, omitBackground: true });
await b.close();
