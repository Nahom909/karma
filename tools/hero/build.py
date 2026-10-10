"""Hero- und Highlight-Becher aus dem vom Auftraggeber bereitgestellten Bild (vier Becher auf Weiß).

  python3 tools/hero/build.py cut     -> _work/hero/cut.png  (BiRefNet über rembg, läuft lokal, braucht ca. 3 Minuten)
  python3 tools/hero/build.py         -> assets/hero/*.webp, Vorschaubilder der Karte, assets/img/og-image.jpg

Eingang: _work/hero/src.png (das Originalbild, 1536 x 1024). Metadaten werden nicht übernommen.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, '_work', 'hero')
DST = os.path.join(ROOT, 'assets', 'hero')
KARTE = os.path.join(ROOT, 'assets', 'img', 'karte')
FONTS = os.path.join(ROOT, '_work', 'fonts')
# von links nach rechts im Originalbild
NAMES = ['matcha', 'mango', 'karma', 'pink']
TILE = (236, 223, 205, 255)
CREAM = (245, 237, 227)


def cut():
    from rembg import remove, new_session
    s = new_session('birefnet-general')
    im = Image.open(os.path.join(WORK, 'src.png')).convert('RGB')
    remove(im, session=s, post_process_mask=False).save(os.path.join(WORK, 'cut.png'))


def cups():
    """Die vier Becher einzeln ausschneiden (größte zusammenhängende Flächen, links nach rechts)."""
    im = Image.open(os.path.join(WORK, 'cut.png')).convert('RGBA')
    a = np.asarray(im.getchannel('A'))
    lab, n = ndimage.label(a > 40)
    objs = [(sl, (lab[sl] == i).sum(), i) for i, sl in enumerate(ndimage.find_objects(lab), 1)]
    objs = sorted([o for o in objs if o[1] > a.size * 0.02], key=lambda o: o[0][1].start)[:4]
    out = {}
    for name, (sl, _, i) in zip(NAMES, objs):
        mask = ndimage.binary_dilation(lab == i, iterations=4)
        alpha = (a * mask).astype(np.uint8)
        pad = 6
        y0, y1 = max(0, sl[0].start - pad), min(a.shape[0], sl[0].stop + pad)
        x0, x1 = max(0, sl[1].start - pad), min(a.shape[1], sl[1].stop + pad)
        c = im.crop((x0, y0, x1, y1))
        c.putalpha(Image.fromarray(alpha[y0:y1, x0:x1]))
        out[name] = c
    return out


def webp(img, path, q=86):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'WEBP', quality=q, method=6, exact=False)
    print(os.path.relpath(path, ROOT), img.size, os.path.getsize(path) // 1024, 'KB')


def thumb(cup, out, top=0.04, size=0.92):
    """Quadratisches Vorschaubild für die Karte: oberer Teil des Bechers mit Topping."""
    w, h = cup.size
    side = round(w * size)
    cx = w / 2
    y0 = round(h * top)
    crop = cup.crop((round(cx - side / 2), y0, round(cx + side / 2), y0 + side))
    bg = Image.new('RGBA', crop.size, TILE)
    bg.alpha_composite(crop)
    webp(bg.convert('RGB').resize((160, 160), Image.LANCZOS), out, 82)


def og(c):
    W, H = 1200, 630
    img = Image.new('RGBA', (W, H), CREAM + (255,))
    k = 400 / max(x.height for x in c.values())
    gap = 14
    total = sum(round(round(c[n].width * k) * 0.98) for n in NAMES) + gap * (len(NAMES) - 1)
    x = (W - total) // 2
    for name in NAMES:
        cup = c[name].resize((round(c[name].width * k), round(c[name].height * k)), Image.LANCZOS)
        sh = Image.new('L', (cup.width + 80, 60), 0)
        ImageDraw.Draw(sh).ellipse((30, 18, cup.width + 50, 42), fill=90)
        sh = sh.filter(ImageFilter.GaussianBlur(12))
        shadow = Image.new('RGBA', sh.size, (60, 35, 20, 0))
        shadow.putalpha(sh)
        img.alpha_composite(shadow, (x - 40, 600 - 40))
        img.alpha_composite(cup, (x, 600 - cup.height))
        x += round(cup.width * 0.98) + gap
    d = ImageDraw.Draw(img)
    bod = ImageFont.truetype(os.path.join(FONTS, 'bodoni.ttf'), 120)
    sans = ImageFont.truetype(os.path.join(FONTS, 'instrument.ttf'), 26)
    gold = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    t = 'Karma'
    tw = gd.textlength(t, font=bod)
    for i in range(7, 0, -1):
        gd.text(((W - tw) / 2 + i * 0.4, 30 + i), t, font=bod, fill=(120 - i * 8, 82 - i * 6, 22, 255))
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).text(((W - tw) / 2, 30), t, font=bod, fill=255)
    grad = Image.new('RGBA', (W, H))
    stops = [(0, (255, 244, 196)), (.3, (226, 182, 82)), (.5, (150, 104, 30)), (.62, (214, 168, 70)), (.85, (255, 236, 170)), (1, (184, 138, 46))]
    gy = np.linspace(0, 1, 150)
    col = np.array([np.interp(gy, [s[0] for s in stops], [s[1][j] for s in stops]) for j in range(3)]).T
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = 255
    band = np.repeat(col[:, None, :], W, 1).astype(np.uint8)
    arr[52:202, :, :3] = band
    grad = Image.fromarray(arr)
    gold.paste(grad, (0, 0), m)
    img.alpha_composite(gold)
    sc = 'SPECIALTY COFFEE · LANGEN'
    d.text(((W - d.textlength(sc, font=sans)) / 2, 178), sc, font=sans, fill=(142, 98, 32))
    img.convert('RGB').save(os.path.join(ROOT, 'assets', 'img', 'og-image.jpg'), quality=86, optimize=True, progressive=True)
    print('assets/img/og-image.jpg')


def main():
    if sys.argv[1:] == ['cut']:
        cut()
        return
    c = cups()
    for name, cup in c.items():
        webp(cup, os.path.join(DST, f'cup-{name}.webp'))
    thumb(c['karma'], os.path.join(KARTE, 'cup-karma.webp'))
    thumb(c['mango'], os.path.join(KARTE, 'cup-mango.webp'))
    thumb(c['matcha'], os.path.join(KARTE, 'drink-strawberry-matcha.webp'), 0.03)
    thumb(c['pink'], os.path.join(KARTE, 'smoothie-pink.webp'), 0.14)
    og(c)


if __name__ == '__main__':
    main()
