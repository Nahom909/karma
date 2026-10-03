// QA: Einzelbilder der Lade-Animation (Zeitlupe). Aufruf: node tools/intro-shots.mjs [desktop|mobile]
import { chromium } from 'playwright';
const mob = process.argv[2] === 'mobile';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: mob ? { width: 390, height: 844 } : { width: 1440, height: 900 } });
await p.goto('http://localhost:8790/', { waitUntil: 'domcontentloaded' });
await p.waitForFunction(() => window.gsap && document.querySelector('.stage__layers'), null, { timeout: 20000 });
await p.evaluate(() => { gsap.globalTimeline.timeScale(0.25); });
const t0 = Date.now();
for (const t of [0.9, 1.5, 1.9, 2.1, 2.4, 3.3]) {
  const wait = t * 4000 - (Date.now() - t0);
  if (wait > 0) await p.waitForTimeout(wait);
  await p.screenshot({ path: `_work/intro-${mob ? 'm' : 'd'}-${t}.jpg`, quality: 60 });
}
await b.close();
