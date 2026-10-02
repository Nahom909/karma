// QA: viele Bilder einer einzelnen Szene. Aufruf: node tools/scene-shots.mjs <szene-index> <desktop|mobile> <ausgabeprefix> [punkte]
import { chromium } from 'playwright';
const idx = +process.argv[2]; const mob = process.argv[3] === 'mobile'; const prefix = process.argv[4];
const pts = (process.argv[5] || '0.02,0.1,0.18,0.26,0.34,0.42,0.5,0.6,0.7,0.8,0.9,0.98').split(',').map(Number);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: mob ? { width: 390, height: 844 } : { width: 1440, height: 900 }, deviceScaleFactor: mob ? 2 : 1 });
await p.goto('http://localhost:8790/', { waitUntil: 'load' });
await p.waitForFunction(() => document.documentElement.classList.contains('is-loaded'), null, { timeout: 30000 });
await p.waitForTimeout(2500);
const pin = await p.evaluate(i => { const t = ScrollTrigger.getAll().filter(t => t.pin)[i]; return { s: t.start, e: t.end }; }, idx);
for (const f of pts) {
  await p.evaluate(y => window.scrollTo(0, y), Math.round(pin.s + (pin.e - pin.s) * f));
  await p.waitForTimeout(1700);
  await p.screenshot({ path: `${prefix}-${String(Math.round(f * 100)).padStart(2, '0')}.jpg`, quality: 65 });
}
await b.close();
