// QA: Screenshots an festen Scroll-Punkten jeder Szene (Desktop + Handy). Aufruf: node tools/shoot.mjs [desktop|mobile] [ausgabeordner]
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
const mode = process.argv[2] || 'desktop';
const out = process.argv[3] || '_work/shots';
mkdirSync(out, { recursive: true });
const vp = mode === 'mobile' ? { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { width: 1440, height: 900, deviceScaleFactor: 1 };
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--disable-gpu-sandbox'] });
const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: vp.deviceScaleFactor, isMobile: vp.isMobile, hasTouch: vp.hasTouch });
const errors = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.type() + ': ' + m.text()); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
const external = new Set();
page.on('request', r => { const u = new URL(r.url()); if (!['localhost', '127.0.0.1'].includes(u.hostname) && u.protocol.startsWith('http')) external.add(u.origin); });
let bytes = 0;
page.on('response', async r => { try { const b = await r.body(); bytes += b.length; } catch (e) {} });
await page.goto('http://localhost:8790/', { waitUntil: 'load' });
await page.waitForFunction(() => document.documentElement.classList.contains('is-loaded'), null, { timeout: 20000 }).catch(() => errors.push('is-loaded nicht erreicht'));
await page.waitForTimeout(800);
await page.screenshot({ path: `${out}/${mode}-00-hero.jpg`, quality: 70 });
const pins = await page.evaluate(() => ScrollTrigger.getAll().filter(t => t.pin).map(t => ({ id: t.trigger.id || t.trigger.dataset.scene || 'opener', start: t.start, end: t.end })));
const points = process.env.POINTS ? process.env.POINTS.split(',').map(Number) : [0.12, 0.3, 0.5, 0.72, 0.95];
let n = 1;
for (const p of pins) {
  for (const f of points) {
    const y = Math.round(p.start + (p.end - p.start) * f);
    await page.evaluate(y => window.scrollTo(0, y), y);
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${out}/${mode}-${String(n++).padStart(2, '0')}-${p.id}-${Math.round(f * 100)}.jpg`, quality: 70 });
  }
}
const H = await page.evaluate(() => document.documentElement.scrollHeight);
const last = pins.length ? pins[pins.length - 1].end : 0;
for (let y = last + vp.height * 0.6; y < H; y += vp.height * 0.9) {
  await page.evaluate(y => window.scrollTo(0, y), Math.round(y));
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${out}/${mode}-${String(n++).padStart(2, '0')}-rest.jpg`, quality: 70 });
}
console.log(JSON.stringify({ pins, H, errors, external: [...external], megabytes: +(bytes / 1048576).toFixed(2) }, null, 1));
await browser.close();
