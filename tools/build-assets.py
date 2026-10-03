"""Wandelt die Blender-Renderings (_work/out) in WebP-Dateien für die Website um und trägt sie in
assets/render/manifest.json ein (Bildfolgen, Ebenen, Schatten). Seit die Açaí Cups echte Fotos sind
(tools/photo/), gibt es hier nur noch die 3D-Matcha und die Karten-Motive.
Aufruf: python3 tools/build-assets.py [matcha] [karte]"""
import os, sys, json, glob
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('KARMA_SRC') or os.path.join(ROOT, '_work', 'out')
DST = os.path.join(ROOT, 'assets', 'render')
KARTE = os.path.join(ROOT, 'assets', 'img', 'karte')
SCENES = ['matcha']  # die Becher kommen aus tools/photo/build.py
MOBILE_W = 600
SEQ_M_W = 520


def save_webp(img, path, q=84):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'WEBP', quality=q, method=6, exact=False)


def save_seq(img, path, q, aq=55):
    """Bildfolgen: leicht entrauschen und den Alphakanal verlustbehaftet komprimieren (nur in Bewegung sichtbar)."""
    import subprocess, tempfile
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r, g, b, a = img.split()
    rgb = Image.merge('RGB', (r, g, b)).filter(ImageFilter.MedianFilter(3))
    img = Image.merge('RGBA', (*rgb.split(), a.filter(ImageFilter.MedianFilter(3))))
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        img.save(t.name)
    try:
        subprocess.run(['convert', t.name, '-define', f'webp:alpha-quality={aq}', '-define', 'webp:method=6',
                        '-quality', str(q), path], check=True)
    except Exception:
        img.save(path, 'WEBP', quality=q, method=6)
    os.unlink(t.name)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def resize_w(img, w):
    h = round(img.height * w / img.width)
    return img.resize((w, h), Image.LANCZOS)


def build_scene(name, man):
    s = os.path.join(SRC, name)
    if not os.path.isdir(s):
        return
    d = os.path.join(DST, name)
    os.makedirs(d, exist_ok=True)
    entry = {}
    fin = os.path.join(s, 'final.png')
    if os.path.exists(fin):
        im = Image.open(fin).convert('RGBA')
        W, H = im.size
        save_webp(im, os.path.join(d, 'final.webp'), 86)
        save_webp(resize_w(im, MOBILE_W), os.path.join(d, 'final-m.webp'), 84)
        entry['final'] = rel(os.path.join(d, 'final.webp'))
        entry['finalM'] = rel(os.path.join(d, 'final-m.webp'))
        entry['size'] = [W, H]
        # Vorschaubild für die Speisekarte (Becher-Ausschnitt, quadratisch)
        box = im.getbbox()
        if box:
            cx = (box[0] + box[2]) / 2
            side = max(box[2] - box[0], (box[3] - box[1]) * 0.78)
            top = box[1] - 10
            crop = im.crop((int(cx - side / 2), int(top), int(cx + side / 2), int(top + side)))
            bg = Image.new('RGBA', crop.size, (235, 221, 203, 255))
            bg.alpha_composite(crop)
            os.makedirs(KARTE, exist_ok=True)
            thumb = bg.convert('RGB').resize((160, 160), Image.LANCZOS)
            save_webp(thumb, os.path.join(KARTE, f'cup-{name}.webp'), 82)
            if name == 'matcha':
                save_webp(thumb, os.path.join(KARTE, 'drink-strawberry-matcha.webp'), 82)
    base = os.path.join(s, 'base.png')
    if os.path.exists(base):
        im = Image.open(base).convert('RGBA')
        save_webp(im, os.path.join(d, 'base.webp'), 86)
        save_webp(resize_w(im, MOBILE_W), os.path.join(d, 'base-m.webp'), 84)
        entry['base'] = rel(os.path.join(d, 'base.webp'))
        entry['baseM'] = rel(os.path.join(d, 'base-m.webp'))
    sh = os.path.join(s, 'shadow.png')
    if os.path.exists(sh):
        im = Image.open(sh).convert('RGBA')
        # nur die Schattenform behalten, schwaches Rauschen weg
        a = im.getchannel('A').point(lambda v: 0 if v < 6 else min(255, int((v - 6) * 1.15)))
        out = Image.new('RGBA', im.size, (42, 27, 21, 0))
        out.putalpha(a.filter(ImageFilter.GaussianBlur(3)))
        save_webp(out.resize((550, 750), Image.LANCZOS), os.path.join(d, 'shadow.webp'), 70)
        entry['shadow'] = rel(os.path.join(d, 'shadow.webp'))
    layers = []
    for lp in sorted(glob.glob(os.path.join(s, 'layer_*.png'))):
        im = Image.open(lp).convert('RGBA')
        W, H = im.size
        bb = im.getchannel('A').point(lambda v: 255 if v > 3 else 0).getbbox()
        if not bb:
            continue
        pad = 8
        bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(W, bb[2] + pad), min(H, bb[3] + pad))
        crop = im.crop(bb)
        nm = os.path.basename(lp)[6:-4]
        save_webp(crop, os.path.join(d, 'layers', nm + '.webp'), 86)
        layers.append({'name': nm, 'src': rel(os.path.join(d, 'layers', nm + '.webp')),
                       'x': round(bb[0] / W, 5), 'y': round(bb[1] / H, 5),
                       'w': round((bb[2] - bb[0]) / W, 5), 'h': round((bb[3] - bb[1]) / H, 5)})
    if layers:
        entry['layers'] = layers
    frames = sorted(glob.glob(os.path.join(s, 'seq', '*.png')))
    if frames:
        n = len(frames)
        step_m = 2 if n > 30 else 1
        for i, fp in enumerate(frames):
            im = Image.open(fp).convert('RGBA')
            save_seq(im, os.path.join(d, 'seq', f'{i:03d}.webp'), 78)
            if i % step_m == 0:
                save_seq(resize_w(im, SEQ_M_W), os.path.join(d, 'seq-m', f'{i // step_m:03d}.webp'), 72, 50)
        entry['seq'] = {'count': n, 'dir': rel(os.path.join(d, 'seq')) + '/', 'countM': (n + step_m - 1) // step_m,
                        'dirM': rel(os.path.join(d, 'seq-m')) + '/'}
    man[name] = entry
    print('✓', name, ', '.join(k for k in entry))


def build_karte():
    """Speisekarten-Motive: auf die Kachelfarbe setzen, quadratisch zuschneiden, 160 px (für 64 px bei 2x+)."""
    src = os.path.join(SRC, 'karte')
    if not os.path.isdir(src):
        return
    os.makedirs(KARTE, exist_ok=True)
    for fp in sorted(glob.glob(os.path.join(src, '*.png'))):
        im = Image.open(fp).convert('RGBA')
        bg = Image.new('RGBA', im.size, (235, 221, 203, 255))
        bg.alpha_composite(im)
        save_webp(bg.convert('RGB').resize((160, 160), Image.LANCZOS), os.path.join(KARTE, os.path.basename(fp)[:-4] + '.webp'), 82)
    print('✓ karte', len(glob.glob(os.path.join(src, '*.png'))))


def main():
    mp = os.path.join(DST, 'manifest.json')
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    for name in (sys.argv[1:] or SCENES + ['karte']):
        if name == 'karte':
            build_karte()
            continue
        build_scene(name, man)
    pts = os.path.join(ROOT, '_work', 'points.json')
    if os.path.exists(pts):
        man['points'] = json.load(open(pts))
    os.makedirs(DST, exist_ok=True)
    json.dump(man, open(mp, 'w'), indent=1)
    print('manifest.json geschrieben')


if __name__ == '__main__':
    main()
