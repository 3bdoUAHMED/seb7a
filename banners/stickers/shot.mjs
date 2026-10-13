import { chromium } from "../node_modules/playwright/index.mjs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1800, height: 1100 }, deviceScaleFactor: 2 });
await p.goto(pathToFileURL(resolve("b2g2-ar.html")).href, { waitUntil: "networkidle" });
await p.evaluate(() => document.fonts.ready);
await p.locator("#s").screenshot({ path: "b2g2-ar-raw.png", omitBackground: true });
await b.close();
