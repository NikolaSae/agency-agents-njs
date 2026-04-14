const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:8000/hero-section.html');
  await page.screenshot({ path: 'public/qa-screenshots/hero-section-screenshot.png', fullPage: true });
  await browser.close();
})();