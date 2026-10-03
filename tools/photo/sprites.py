"""Frucht-Sprites aus Open-Images-Fotos (CC BY 2.0) freistellen.

Eingang: _work/oi/fruit/<id>.jpg und die BiRefNet-Masken <id>_birefn.png
(erzeugt mit rembg, Modell birefnet-general, je Bild ein eigener Prozess).
Heidelbeeren liegen dicht an dicht; sie werden als Kreise ausgeschnitten.
Ausgang: _work/photo/sprites/<name>.png (RGBA, Hintergrund transparent).
"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(os.environ.get('KARMA_SRC', os.path.join(ROOT, '_work')), 'oi', 'fruit')
OUT = os.path.join(ROOT, '_work', 'photo', 'sprites')
os.makedirs(OUT, exist_ok=True)


def rgba(fid):
    im = Image.open(os.path.join(SRC, fid + '.jpg')).convert('RGB')
    a = Image.open(os.path.join(SRC, fid + '_birefn.png')).getchannel('A')
    im.putalpha(a)
    return im


def largest(im, keep=1):
    """Nur die größten zusammenhängenden Flächen behalten (z. B. Münze neben der Erdbeere entfernen)."""
    a = np.asarray(im.getchannel('A')).astype(np.float32) / 255
    lab, n = ndimage.label(a > 0.35)
    if n <= keep:
        return im
    sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
    ids = 1 + np.argsort(sizes)[::-1][:keep]
    m = np.isin(lab, ids)
    m = ndimage.binary_dilation(m, iterations=3)
    a = a * m
    out = im.copy()
    out.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return out


def components(im, min_px=600):
    a = np.asarray(im.getchannel('A')).astype(np.float32) / 255
    lab, n = ndimage.label(a > 0.35)
    res = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        m = lab[sl] == i
        if m.sum() < min_px:
            continue
        m = ndimage.binary_dilation(m, iterations=2)
        box = (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        crop = im.crop(box)
        ca = np.asarray(crop.getchannel('A')).astype(np.float32) * m
        crop.putalpha(Image.fromarray(ca.astype(np.uint8)))
        res.append((box, crop))
    return res


def split_x(im):
    """Zwei nebeneinanderliegende Beeren an der schmalsten Stelle trennen."""
    a = np.asarray(im.getchannel('A')).astype(np.float32)
    col = a.sum(axis=0)
    w = im.width
    lo, hi = int(w * .3), int(w * .7)
    x = lo + int(np.argmin(col[lo:hi]))
    return [trim(im.crop((0, 0, x, im.height))), trim(im.crop((x, 0, w, im.height)))]


def circle(fid, cx, cy, r, feather=1.6):
    im = Image.open(os.path.join(SRC, fid + '.jpg')).convert('RGB')
    pad = 4
    box = (int(cx - r - pad), int(cy - r - pad), int(cx + r + pad), int(cy + r + pad))
    crop = im.crop(box)
    w, h = crop.size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - (cx - box[0])) ** 2 + (yy - (cy - box[1])) ** 2)
    a = np.clip((r - d) / feather + 0.5, 0, 1)
    crop.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return crop


def trim(im, pad=6):
    bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))
    return im


def fit(im, size):
    im = trim(im)
    k = size / max(im.size)
    if k < 1:
        im = premul_resize(im, (round(im.width * k), round(im.height * k)))
    return im


def premul_resize(im, size):
    a = np.asarray(im).astype(np.float32) / 255
    rgb = a[..., :3] * a[..., 3:4]
    pre = np.concatenate([rgb, a[..., 3:4]], axis=-1)
    out = []
    for c in range(4):
        ch = Image.fromarray((pre[..., c] * 255).astype(np.uint8))
        out.append(np.asarray(ch.resize(size, Image.LANCZOS)).astype(np.float32) / 255)
    pre = np.stack(out, axis=-1)
    al = np.clip(pre[..., 3:4], 1e-4, 1)
    rgb = np.clip(pre[..., :3] / al, 0, 1)
    res = np.concatenate([rgb, pre[..., 3:4]], axis=-1)
    return Image.fromarray((res * 255).round().astype(np.uint8), 'RGBA')


def blueberry_grade(im):
    """Die Beeren im Foto sind blass und rötlich: Helligkeit auf einen Heidelbeer-Verlauf
    (tiefes Blau, im Licht der typische graublaue Reif) abbilden, etwas Originalstruktur bleibt."""
    a = np.asarray(im).astype(np.float32) / 255
    rgb = a[..., :3]
    lum = np.clip(rgb @ np.array([0.3, 0.55, 0.15], dtype=np.float32), 0, 1)
    lum = np.clip((lum - 0.12) / 0.78, 0, 1) ** 1.1
    stops = np.array([[0.0, 14, 16, 30], [0.45, 44, 52, 88], [0.8, 112, 122, 156], [1.0, 186, 192, 212]], dtype=np.float32)
    out = np.zeros_like(rgb)
    for c in range(3):
        out[..., c] = np.interp(lum, stops[:, 0], stops[:, c + 1]) / 255
    gray = rgb.mean(axis=-1, keepdims=True)
    rgb = out * 0.88 + (rgb - gray + out.mean(axis=-1, keepdims=True)) * 0.12
    a[..., :3] = np.clip(rgb, 0, 1)
    return Image.fromarray((a * 255).round().astype(np.uint8), 'RGBA')


def main():
    sprites = {}
    # Erdbeeren
    sprites['strawberry_1'] = fit(largest(rgba('1b60f5284566fa1d')), 560)
    sprites['strawberry_2'] = fit(largest(rgba('0640c5f4d7cfd60e')), 460)
    # Himbeeren (fünf einzelne Beeren auf einem Teller)
    rs = sorted(components(rgba('d8050d9e3d814e16')), key=lambda t: t[0][0])
    singles = []
    for box, c in rs:
        if c.width > c.height * 1.5:
            singles.append(largest(split_x(c)[1]))  # linke Hälfte hat eine gerade Schnittkante
        else:
            singles.append(c)
    for i, c in enumerate(singles, start=1):
        sprites['raspberry_%d' % i] = fit(c, 260)
    # Heidelbeeren (Kreise)
    for i, (cx, cy, r) in enumerate([(292, 432, 91), (728, 590, 110), (403, 609, 94), (137, 547, 92), (568, 461, 88)], start=1):
        sprites['blueberry_%d' % i] = fit(blueberry_grade(circle('85272f33bdd562a0', cx, cy, r)), 220)
    for k, v in sprites.items():
        v.save(os.path.join(OUT, k + '.png'))
        print(k, v.size)


if __name__ == '__main__':
    main()
