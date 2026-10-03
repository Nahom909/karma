"""Becherfotos und Frucht-Sprites als WebP nach assets/photo/ schreiben und die Foto-Szenen
in assets/render/manifest.json eintragen (die 3D-Szene „matcha“ bleibt unverändert).

Reihenfolge:  python3 tools/photo/cups.py && python3 tools/photo/sprites.py && python3 tools/photo/build.py
"""
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, '_work', 'photo')
DST = os.path.join(ROOT, 'assets', 'photo')
MAN = os.path.join(ROOT, 'assets', 'render', 'manifest.json')
KARTE = os.path.join(ROOT, 'assets', 'img', 'karte')
SCENES = ['classic', 'caramel', 'peanut', 'berry']
MOBILE = 600 / 1100

# Frucht-Sprites: Ausgabename -> Arbeitsdatei (Auswahl der saubersten Ausschnitte)
FRUIT = {
    'strawberry_1': 'strawberry_1', 'strawberry_2': 'strawberry_2',
    'raspberry_1': 'raspberry_2', 'raspberry_2': 'raspberry_3',
    'blueberry_1': 'blueberry_2', 'blueberry_2': 'blueberry_4', 'blueberry_3': 'blueberry_5',
}


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def webp(img, path, q=86):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Keine Metadaten (EXIF/XMP) übernehmen: PIL schreibt sie nur, wenn man sie ausdrücklich übergibt
    img.save(path, 'WEBP', quality=q, method=6, exact=False)


def scaled(img, k):
    return img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.LANCZOS)


def main():
    meta = json.load(open(os.path.join(WORK, 'cups', 'meta.json')))
    man = json.load(open(MAN))
    for old in ('tropical',):
        man.pop(old, None)
    for name in SCENES:
        src = os.path.join(WORK, 'cups', name)
        d = os.path.join(DST, name)
        fin = Image.open(os.path.join(src, 'final.png')).convert('RGBA')
        W, H = fin.size
        webp(fin, os.path.join(d, 'final.webp'), 86)
        webp(scaled(fin, MOBILE), os.path.join(d, 'final-m.webp'), 84)
        sh = Image.open(os.path.join(src, 'shadow.png'))
        webp(sh, os.path.join(d, 'shadow.webp'), 80)
        e = dict(type='photo', final=rel(os.path.join(d, 'final.webp')), finalM=rel(os.path.join(d, 'final-m.webp')),
                 size=[W, H], shadow=rel(os.path.join(d, 'shadow.webp')), layers=[],
                 rim=meta[name]['rim'], bbox=meta[name]['bbox'])
        for L in meta[name]['layers']:
            im = Image.open(os.path.join(src, L['name'] + '.png'))
            p = os.path.join(d, L['name'] + '.webp')
            pm = os.path.join(d, L['name'] + '-m.webp')
            webp(im, p, 86)
            webp(scaled(im, MOBILE), pm, 84)
            e['layers'].append(dict(L, src=rel(p), srcM=rel(pm)))
        g = os.path.join(src, 'ghost.png')
        if os.path.exists(g):
            im = Image.open(g)
            webp(im, os.path.join(d, 'ghost.webp'), 80)
            webp(scaled(im, MOBILE), os.path.join(d, 'ghost-m.webp'), 78)
            e['ghost'] = rel(os.path.join(d, 'ghost.webp'))
            e['ghostM'] = rel(os.path.join(d, 'ghost-m.webp'))
        man[name] = e
        # Vorschaubild für die Speisekarte (quadratischer Ausschnitt des Bechers)
        box = fin.getbbox()
        cx = (box[0] + box[2]) / 2
        side = max(box[2] - box[0], (box[3] - box[1]) * 0.8)
        top = box[1] - 12
        crop = fin.crop((int(cx - side / 2), int(top), int(cx + side / 2), int(top + side)))
        bg = Image.new('RGBA', crop.size, (235, 221, 203, 255))
        bg.alpha_composite(crop)
        webp(bg.convert('RGB').resize((160, 160), Image.LANCZOS), os.path.join(KARTE, f'cup-{name}.webp'), 82)
        print('✓', name, [l['name'] for l in e['layers']])
    fruit = []
    for out, work in FRUIT.items():
        im = Image.open(os.path.join(WORK, 'sprites', work + '.png'))
        p = os.path.join(DST, 'fruit', out + '.webp')
        webp(im, p, 84)
        fruit.append(dict(name=out, src=rel(p), w=im.width, h=im.height))
    man['fruit'] = fruit
    order = ['classic', 'caramel', 'peanut', 'berry', 'matcha', 'points', 'fruit']
    man = {k: man[k] for k in order if k in man}
    json.dump(man, open(MAN, 'w'), ensure_ascii=False, indent=1)
    print('✓ fruit', len(fruit), '· manifest')


if __name__ == '__main__':
    main()
