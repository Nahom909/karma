"""Echte Becher aus den Café-Fotos freistellen und für die Scroll-Szenen in Ebenen zerlegen.

Eingang (nicht im Repository, vom Café bereitgestellt):
  _work/real/ig1.jpg, ig2.jpg, ig3.jpg  und die BiRefNet-Masken *_birefn.png
  (rembg, Modell birefnet-general).
Auf den Fotos stehen mehrere Becher dicht beieinander; jeder Becher wird über einen
Umriss (Polygon) vom Nachbarn getrennt. Verdeckte Randstücke werden spiegelbildlich
von der anderen Becherseite ergänzt (Becher sind rotationssymmetrisch).

Ausgang: _work/photo/cups/<szene>/*.png in Bühnenkoordinaten (1100 x 1500) plus meta.json.
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(os.environ.get('KARMA_SRC', os.path.join(ROOT, '_work')), 'real')
OUT = os.path.join(ROOT, '_work', 'photo', 'cups')
W, H = 1100, 1500
BOTTOM_Y = 1400      # Becherboden auf der Bühne
BODY_H = 760         # Rand bis Boden auf der Bühne


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def load(name):
    rgb = np.asarray(Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')).astype(np.float32) / 255
    a = np.asarray(Image.open(os.path.join(SRC, name + '_birefn.png')).getchannel('A')).astype(np.float32) / 255
    return rgb, a


def poly(shape, pts, feather=1.2):
    h, w = shape
    k = 4
    m = Image.new('L', (w * k, h * k), 0)
    ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in pts], fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m).astype(np.float32) / 255


def rim_y(x, left, right, sag):
    """Untere (vordere) Kante der Randellipse: Gerade zwischen den Randenden plus Durchhang."""
    (x0, y0), (x1, y1) = left, right
    u = np.clip((x - (x0 + x1) / 2) / ((x1 - x0) / 2), -1, 1)
    line = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return line + sag * np.sqrt(1 - u * u)


# ---------------------------------------------------------------------------
# Becher-Definitionen (Koordinaten im jeweiligen Quellfoto)
# ---------------------------------------------------------------------------

CUPS = {
    # B: Açaí mit Kokos-Swirl, Heidelbeeren, Kokosraspeln, Erdbeeren (ig2 links)
    'classic': dict(
        src='ig2',
        poly=[(0, 60), (270, 60), (300, 90), (330, 108), (350, 118), (367, 115), (382, 126), (390, 150), (386, 168),
              (372, 174), (368, 190), (345, 196), (342, 215), (341, 300), (330, 400), (318, 500), (305, 600), (292, 640),
              (0, 640)],
        fade_left=dict(x=12, y1=200),
        rim=dict(left=(3, 172), right=(355, 172), sag=24, lift=7),
        bottom=(179, 626), rimc=180, body_h=900,
    ),
    # C: Açaí mit Karamell-Swirl, Vanille-Topping, Mandelblättchen (ig2 rechts)
    'caramel': dict(
        src='ig2',
        poly=[(322, 180), (345, 178), (383, 157), (413, 147), (440, 147), (467, 140), (483, 127), (497, 105), (500, 83),
              (507, 70), (518, 62), (535, 55), (550, 45), (562, 35), (578, 26), (595, 20), (615, 15), (645, 17), (660, 38),
              (690, 48), (700, 66), (706, 90), (716, 108), (736, 128), (742, 150), (742, 190), (750, 210), (754, 232), (754, 240), (724, 300),
              (700, 450), (672, 600), (648, 700), (560, 726), (388, 706), (372, 560), (362, 450), (352, 350), (342, 250),
              (330, 205)],
        rim=dict(left=(322, 184), right=(752, 222), sag=30, lift=9),
        bottom=(520, 712), rimc=228, body_h=800,
    ),
    # A: Açaí-Boden, Chia-Pudding mit Erdnussbutter, Beeren, Banane, Mandeln (ig1)
    'peanut': dict(
        src='ig1',
        poly=None,
        rim=dict(left=(8, 130), right=(470, 152), sag=22, lift=7),
        bands=[332, 505],
        bottom=(238, 668), rimc=150, body_h=860,
    ),
    # D: Açaí mit Chia und Kokos-Streifen, Erdbeeren, Heidelbeeren, Kakaonibs, weiße Sauce (ig3 vorne)
    'berry': dict(
        src='ig3',
        poly=[(0, 300), (30, 297), (75, 295), (82, 252), (110, 247), (135, 265), (150, 280), (190, 275), (225, 282),
              (250, 300), (272, 317), (285, 335), (287, 365), (280, 372), (300, 378), (318, 388), (332, 405), (336, 440),
              (330, 470), (322, 510), (307, 540), (300, 560), (292, 600), (285, 650), (279, 700), (274, 750), (270, 800),
              (262, 850), (255, 880), (240, 905), (220, 930), (130, 942), (0, 942)],
        not_orange=(262, 360, 360, 940),
        extend_left=dict(axis=128, pad=100, ramp=26, seam=14, wobble=12),
        rim=dict(left=(-80, 410), right=(336, 410), sag=112, lift=12),
        bottom=(128, 930), rimc=510, body_h=740,
    ),
}


def isolate(c):
    rgb, a = load(c['src'])
    h, w = a.shape
    if c.get('poly'):
        a = a * poly((h, w), c['poly'])
    if c.get('not_orange'):
        # Mittlerer Becher (Erdnussbutter, orange) schaut rechts neben dem Becher hervor
        x0, y0, x1, y1 = c['not_orange']
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        orange = smooth(0.10, 0.22, r - b) * smooth(0.05, 0.14, g - b) * smooth(0.45, 0.6, r)
        orange = ndimage.gaussian_filter(orange, 2.0)
        zone = np.zeros_like(a)
        zone[y0:y1, x0:x1] = 1
        zone = ndimage.gaussian_filter(zone, 3)
        a = a * (1 - np.clip(orange * 1.6, 0, 1) * zone)
    if c.get('fade_left'):
        # am linken Bildrand abgeschnittene Beeren weich auslaufen lassen statt gerader Kante
        f = c['fade_left']
        xs = np.arange(w, dtype=np.float32)
        yy = np.arange(h, dtype=np.float32)
        wy = 1 - smooth(f['y1'] - 20, f['y1'], yy)
        fade = smooth(-2, f['x'], xs)[None, :]
        a = a * (1 - wy[:, None] * (1 - fade))
    if c.get('mirror'):
        m = c['mirror']
        ys = slice(m['y0'], m['y1'])
        xs = np.arange(m['x0'], m['x1'])
        sx = np.clip(2 * m['axis'] - xs, 0, w - 1)
        wx = smooth(m['x0'], m['x0'] + m['ramp'], xs)[None, :]
        yy = np.arange(m['y0'], m['y1'])
        wy = (smooth(m['y0'], m['y0'] + 8, yy) * (1 - smooth(m['y1'] - 8, m['y1'], yy)))[:, None]
        wt = wx * wy
        src_rgb = rgb[ys][:, sx]
        src_a = a[ys][:, sx]
        rgb[ys, m['x0']:m['x1']] = rgb[ys, m['x0']:m['x1']] * (1 - wt[..., None]) + src_rgb * wt[..., None]
        a[ys, m['x0']:m['x1']] = a[ys, m['x0']:m['x1']] * (1 - wt) + src_a * wt
    ox = 0
    if c.get('extend_left'):
        e = c['extend_left']
        pad = e['pad']
        rgb2 = np.zeros((h, w + pad, 3), np.float32)
        a2 = np.zeros((h, w + pad), np.float32)
        rgb2[:, pad:] = rgb
        a2[:, pad:] = a
        # fehlender linker Rand: Spiegelbild der rechten Becherseite (um die Becherachse)
        span = e['seam'] + e['wobble'] + e['ramp']
        xn = np.arange(0, pad + span)
        xo = (xn - pad).astype(np.float32)
        sx = np.clip(2 * e['axis'] - xo, 0, w - 1).astype(int)
        # unregelmäßige Naht, damit keine senkrechte Linie sichtbar wird
        rng = np.random.default_rng(4)
        nz = ndimage.gaussian_filter1d(rng.standard_normal(h), 9)
        nz = nz / (np.abs(nz).max() + 1e-6)
        seam = e['seam'] + e['wobble'] * nz
        wt = 1 - smooth(seam[:, None] - e['ramp'] / 2, seam[:, None] + e['ramp'] / 2, xo[None, :])
        wt = np.where(xo[None, :] < 0, 1.0, wt)
        rgb2[:, xn] = rgb2[:, xn] * (1 - wt[..., None]) + rgb[:, sx] * wt[..., None]
        a2[:, xn] = a2[:, xn] * (1 - wt) + a[:, sx] * wt
        rgb, a, ox = rgb2, a2, pad
    return rgb, a, ox


def premul_resize(rgb, a, size):
    pre = np.concatenate([rgb * a[..., None], a[..., None]], axis=-1)
    chans = []
    for i in range(4):
        im = Image.fromarray(np.clip(pre[..., i] * 65535, 0, 65535).astype(np.uint16).astype(np.int32), 'I')
        im = im.convert('F').resize(size, Image.LANCZOS)
        chans.append(np.asarray(im) / 65535)
    pre = np.clip(np.stack(chans, -1), 0, 1)
    al = pre[..., 3]
    rgb = np.where(al[..., None] > 1e-4, pre[..., :3] / np.maximum(al[..., None], 1e-4), 0)
    return np.clip(rgb, 0, 1), al


def unsharp(rgb, radius=1.1, amount=0.45):
    blur = np.stack([ndimage.gaussian_filter(rgb[..., i], radius) for i in range(3)], -1)
    return np.clip(rgb + (rgb - blur) * amount, 0, 1)


def to_img(rgb, a):
    arr = np.concatenate([rgb, a[..., None]], -1)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


def place(name, c):
    rgb, a, ox = isolate(c)
    bx, by = c['bottom'][0] + ox, c['bottom'][1]
    s = c.get('body_h', BODY_H) / (by - c['rimc'])
    h, w = a.shape
    nw, nh = round(w * s), round(h * s)
    rgb, a = premul_resize(rgb, a, (nw, nh))
    rgb = unsharp(rgb)
    # auf die Bühne setzen
    dx = round(W / 2 - bx * s)
    dy = round(BOTTOM_Y - by * s)
    R = np.zeros((H, W, 3), np.float32)
    A = np.zeros((H, W), np.float32)
    sx0, sy0 = max(0, -dx), max(0, -dy)
    tx0, ty0 = max(0, dx), max(0, dy)
    cw = min(nw - sx0, W - tx0)
    ch = min(nh - sy0, H - ty0)
    R[ty0:ty0 + ch, tx0:tx0 + cw] = rgb[sy0:sy0 + ch, sx0:sx0 + cw]
    A[ty0:ty0 + ch, tx0:tx0 + cw] = a[sy0:sy0 + ch, sx0:sx0 + cw]
    A[A < 0.02] = 0

    def to_stage(x, y):
        return (x + ox) * s + dx, y * s + dy

    return R, A, s, to_stage


def rim_mask(c, to_stage, s, feather=3.0):
    """1 unterhalb der Randkante (Becher), 0 darüber (Topping)."""
    r = c['rim']
    xs = np.arange(W, dtype=np.float32)
    # Bühnen-x zurück in Quell-x
    x0s, _ = to_stage(0, 0)
    src_x = (xs - x0s) / s
    left = r['left']; right = r['right']
    ysrc = rim_y(src_x, left, right, r['sag']) - r['lift']
    ystage = ysrc * s + to_stage(0, 0)[1]
    yy = np.arange(H, dtype=np.float32)[:, None]
    return smooth(-feather, feather, yy - ystage[None, :])


def wave_mask(y_src, to_stage, s, amp=6, period=140, phase=0.0, feather=4.0):
    xs = np.arange(W, dtype=np.float32)
    y0 = to_stage(0, y_src)[1]
    ystage = y0 + amp * s * np.sin(xs / (period * s) * 2 * np.pi + phase)
    yy = np.arange(H, dtype=np.float32)[:, None]
    return smooth(-feather * s, feather * s, yy - ystage[None, :])


def bbox(a, thr=0.02):
    ys, xs = np.where(a > thr)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def save_layer(d, key, R, A, meta, pad=4):
    if A.max() < 0.05:
        return
    x0, y0, x1, y1 = bbox(A)
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(W, x1 + pad), min(H, y1 + pad)
    to_img(R[y0:y1, x0:x1], A[y0:y1, x0:x1]).save(os.path.join(d, key + '.png'))
    meta['layers'].append(dict(name=key, x=round(x0 / W, 5), y=round(y0 / H, 5), w=round((x1 - x0) / W, 5), h=round((y1 - y0) / H, 5)))


def shadow(A, d):
    """Weicher Kontaktschatten unter dem Becherboden (Bühnengröße, halbe Auflösung)."""
    ys, xs = np.where(A > 0.5)
    bot = ys.max()
    row = xs[ys > bot - 30]
    cx, half = (row.min() + row.max()) / 2, (row.max() - row.min()) / 2
    h2, w2 = H // 2, W // 2
    yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32) * 2
    core = np.exp(-(((xx - cx) / (half * 1.05)) ** 2 + ((yy - bot + 4) / 16) ** 2) * 2.2)
    wide = np.exp(-(((xx - cx) / (half * 1.9)) ** 2 + ((yy - bot + 10) / 46) ** 2) * 1.6)
    a = np.clip(core * 0.55 + wide * 0.28, 0, 1)
    rgb = np.zeros((h2, w2, 3), np.float32) + np.array([42, 22, 26], np.float32) / 255
    to_img(rgb, a).save(os.path.join(d, 'shadow.png'))


def ghost(R, A):
    """Entsättigte, helle Vorschau des Bechers (Szene 2: der Becher füllt sich mit Farbe)."""
    lum = R @ np.array([0.3, 0.55, 0.15], np.float32)
    g = 0.62 + lum[..., None] * 0.38
    tint = np.array([0.97, 0.94, 0.92], np.float32)
    return np.clip(g * tint, 0, 1), A * 0.42


def main():
    os.makedirs(OUT, exist_ok=True)
    allmeta = {}
    for name, c in CUPS.items():
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        R, A, s, to_stage = place(name, c)
        to_img(R, A).save(os.path.join(d, 'final.png'))
        meta = dict(layers=[], scale=round(s, 4))
        body = rim_mask(c, to_stage, s)
        top_a = A * (1 - body)
        body_a = A * body
        if c.get('bands'):
            # Peanut: Becher in waagerechte Schichten mit welliger, weicher Kante
            cuts = [wave_mask(y, to_stage, s, phase=i * 1.7) for i, y in enumerate(c['bands'])]
            prev = np.ones_like(A)
            parts = []
            for m in cuts:
                parts.append(prev * (1 - m))
                prev = m
            parts.append(prev)
            for i, p in enumerate(parts):
                save_layer(d, 'band_%d' % (i + 1), R, body_a * p, meta)
        else:
            save_layer(d, 'body', R, body_a, meta)
        save_layer(d, 'top', R, top_a, meta)
        if name == 'caramel':
            gR, gA = ghost(R, A)
            to_img(gR, gA).save(os.path.join(d, 'ghost.png'))
        shadow(A, d)
        x0, y0, x1, y1 = bbox(A, 0.5)
        meta['bbox'] = [round(x0 / W, 4), round(y0 / H, 4), round(x1 / W, 4), round(y1 / H, 4)]
        rx0, ry = to_stage(c['rim']['left'][0], c['rim']['left'][1])
        rx1, _ = to_stage(c['rim']['right'][0], c['rim']['right'][1])
        meta['rim'] = [round(rx0 / W, 4), round(rx1 / W, 4), round(to_stage(0, c['rimc'])[1] / H, 4)]
        allmeta[name] = meta
        print(name, 'scale', round(s, 3), 'bbox', meta['bbox'], [l['name'] for l in meta['layers']])
    json.dump(allmeta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
