// node shoot.js <html-url> <out.png>   (1280x640, @1x)
// Needs playwright-core and a Chromium; set CHROME to its path.
const { chromium } = require("playwright-core");
(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: process.env.CHROME });
  const page = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.screenshot({ path: out });
  await browser.close();
})();
