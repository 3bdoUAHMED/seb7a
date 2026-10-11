// Exports every banner on index.html as a PNG at its exact size.
// Usage (from this folder):  node render.mjs
// Output: output/<offer-id>/<device>-<lang>-<W>x<H>.png
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 3200, height: 1400 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(join(here, "index.html")).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);

const banners = await page.locator(".banner").all();
for (const banner of banners) {
  const file = join(here, "output", await banner.getAttribute("data-file"));
  mkdirSync(dirname(file), { recursive: true });
  await banner.screenshot({ path: file });
  console.log("✔", file.slice(here.length + 1));
}
await browser.close();
console.log(`Done — ${banners.length} banners.`);
