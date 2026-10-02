// QA: Screenshots der Abschnitte nach den Szenen. Aufruf: node tools/lower-shots.mjs <desktop|mobile> <prefix>
import { chromium } from 'playwright';
const mob = process.argv[2] === 'mobile'; const prefix = process.argv[3];
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: mob ? { width: 390, height: 844 } : { width: 1440, height: 900 }, deviceScaleFactor: mob ? 2 : 1 });
await p.goto('http://localhost:8790/', { waitUntil: 'load' });
await p.waitForFunction(() => document.documentElement.classList.contains('is-loaded'), null, { timeout: 30000 });
for (const [i, sel, off] of [[0, '#impressionen', 0], [1, '#impressionen', 0.7], [2, '#karte', -0.05], [3, '#karte', 0.8], [4, '#besuch', 0], [5, '#besuch', 0.9]]) {
  await p.evaluate(([sel, off]) => { const el = document.querySelector(sel); const y = el.getBoundingClientRect().top + scrollY + el.offsetHeight * off; scrollTo(0, y); }, [sel, off]);
  await p.waitForTimeout(1500);
  await p.screenshot({ path: `${prefix}-${i}.jpg`, quality: 65 });
}
await b.close();
