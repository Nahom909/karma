// QA: Screenshots der ganzen Seite in Bildschirmhöhen-Schritten (Desktop + Handy), Konsolenfehler, externe Anfragen.
// Aufruf: node tools/shoot.mjs [desktop|mobile|reduced] [ausgabeordner]   (vorher: node tools/serve.mjs)
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
const mode = process.argv[2] || 'desktop';
const out = process.argv[3] || '_work/shots';
mkdirSync(out, { recursive: true });
const vp = mode === 'mobile' ? { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { width: 1440, height: 900, deviceScaleFactor: 1 };
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--disable-gpu-sandbox'] });
const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: vp.deviceScaleFactor, isMobile: vp.isMobile, hasTouch: vp.hasTouch, reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference' });
const errors = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.type() + ': ' + m.text()); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
const external = new Set();
page.on('request', r => { const u = new URL(r.url()); if (!['localhost', '127.0.0.1'].includes(u.hostname) && u.protocol.startsWith('http')) external.add(u.origin); });
let bytes = 0;
page.on('response', async r => { try { const b = await r.body(); bytes += b.length; } catch (e) {} });
await page.goto('http://localhost:8790/', { waitUntil: 'load' });
await page.waitForTimeout(2600);
let n = 0;
const H = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < H; y += vp.height * 0.9) {
  await page.evaluate(y => window.scrollTo(0, y), Math.round(y));
  await page.waitForTimeout(n ? 1100 : 0);
  await page.screenshot({ path: `${out}/${mode}-${String(n++).padStart(2, '0')}.jpg`, quality: 72 });
}
console.log(JSON.stringify({ H, shots: n, errors, external: [...external], megabytes: +(bytes / 1048576).toFixed(2) }, null, 1));
await browser.close();
