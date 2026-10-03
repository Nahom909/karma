"""Vorschaubild für Link-Vorschauen (1200 x 630) aus dem Classic-Becherfoto.
Schriften: TTF-Fassungen aus tools/textures/fonts.py (liegen in _work/fonts/)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(ROOT, '_work', 'fonts')
W, H = 1200, 630
CREAM, INK, ACAI, SOFT = (245, 237, 227), (42, 27, 21), (78, 29, 71), (110, 92, 84)

img = Image.new('RGBA', (W, H), CREAM + (255,))
cup = Image.open(os.path.join(ROOT, '_work', 'photo', 'cups', 'classic', 'final.png'))
sh = Image.open(os.path.join(ROOT, '_work', 'photo', 'cups', 'classic', 'shadow.png')).resize(cup.size, Image.BILINEAR)
stage = Image.new('RGBA', cup.size, (0, 0, 0, 0))
stage.alpha_composite(sh)
stage.alpha_composite(cup)
bb = cup.getbbox()
stage = stage.crop((bb[0] - 40, bb[1] - 20, bb[2] + 40, bb[3] + 60))
k = 600 / stage.height
stage = stage.resize((round(stage.width * k), round(stage.height * k)), Image.LANCZOS)
img.alpha_composite(stage, (W - stage.width - 40, 18))

d = ImageDraw.Draw(img)
bod = ImageFont.truetype(os.path.join(F, 'bodoni.ttf'), 150)
bodi = ImageFont.truetype(os.path.join(F, 'bodoni-italic.ttf'), 150)
sans = ImageFont.truetype(os.path.join(F, 'instrument.ttf'), 30)
d.text((72, 120), 'Gutes', font=bod, fill=INK)
d.text((72, 270), 'Karma.', font=bodi, fill=ACAI)
d.text((76, 474), 'Açaí, Matcha & Specialty Coffee', font=sans, fill=SOFT)
d.text((76, 514), 'Bahnstraße 4 · Langen (Hessen)', font=sans, fill=SOFT)
img.convert('RGB').save(os.path.join(ROOT, 'assets', 'img', 'og-image.jpg'), quality=86, optimize=True, progressive=True)
print('og-image.jpg')
