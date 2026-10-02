// Nimmt ein Scroll-Video der Seite auf (echtes Mausrad-Scrollen mit Lenis). Aufruf: node tools/record.mjs [desktop|mobile] [ausgabe.webm]
import { chromium } from 'playwright';
import { renameSync, mkdirSync, readdirSync } from 'node:fs';
const mode = process.argv[2] || 'desktop';
const out = process.argv[3] || `_work/video-${mode}.webm`;
const mob = mode === 'mobile';
const size = mob ? { width: 390, height: 844 } : { width: 1440, height: 900 };
const dir = '_work/video-tmp-' + mode;
mkdirSync(dir, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: size, deviceScaleFactor: 1, recordVideo: { dir, size } });
const page = await ctx.newPage();
await page.goto('http://localhost:8791/', { waitUntil: 'load' });
await page.waitForFunction(() => document.documentElement.classList.contains('is-loaded'), null, { timeout: 30000 });
await page.waitForTimeout(1200);
const end = await page.evaluate(() => {
  const t = ScrollTrigger.getAll().filter(t => t.pin);
  return t.length ? t[t.length - 1].end + innerHeight * 0.5 : document.documentElement.scrollHeight;
});
const total = process.env.FULL ? await page.evaluate(() => document.documentElement.scrollHeight - innerHeight) : end;
await page.mouse.move(size.width / 2, size.height / 2);
// gleichmäßig scrollen: ca. 900 px pro Sekunde (Desktop), 700 px (Handy)
const speed = mob ? 700 : 900;
const step = 60;
let y = 0;
while (y < total) {
  if (mob) await page.evaluate(d => window.scrollBy(0, d), speed * step / 1000);
  else await page.mouse.wheel(0, speed * step / 1000);
  y += speed * step / 1000;
  await page.waitForTimeout(step);
}
await page.waitForTimeout(1500);
await ctx.close();
await browser.close();
const f = readdirSync(dir).filter(n => n.endsWith('.webm'))[0];
renameSync(`${dir}/${f}`, out);
console.log('video', out);
