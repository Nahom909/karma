"""Textur-Erzeugung für die 3D-Szenen. Ausgabe nach _work/tex/ (wird von tools/blender/klib.py gelesen)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX = os.path.join(ROOT, '_work', 'tex')
FONTS = os.path.join(ROOT, '_work', 'fonts')
os.makedirs(TEX, exist_ok=True)
from PIL import Image, ImageDraw, ImageFont
W,H=2600,1400
img=Image.new('RGBA',(W,H),(255,255,255,0)); d=ImageDraw.Draw(img)
karma=ImageFont.truetype(os.path.join(FONTS, 'courier-regular.ttf'),600)
kb=d.textbbox((0,0),'karma',font=karma,stroke_width=5)
kw=kb[2]-kb[0]
x0=(W-kw)//2 - kb[0]; y0=560
d.text((x0,y0),'karma',font=karma,fill=(255,255,255,255),stroke_width=5,stroke_fill=(255,255,255,255))
txt='THISISYOUR'
# fit width to karma
size=200
for _ in range(30):
    top=ImageFont.truetype(os.path.join(FONTS, 'jost-500.ttf'),size)
    tb=d.textbbox((0,0),txt,font=top)
    tw=tb[2]-tb[0]
    if abs(tw-kw*0.86)<4: break
    size=int(size*(kw*0.86)/tw)
widths=[d.textlength(c,font=top) for c in txt]
track=(kw*0.97-sum(widths))/(len(txt)-1)
xs=x0+kb[0]+int(kw*0.015); ys=y0+kb[1]-(tb[3]-tb[1])-tb[1]-int(0.085*kw)
x=xs
for c,w in zip(txt,widths):
    d.text((x,ys),c,font=top,fill=(255,255,255,255)); x+=w+track
bb=img.getbbox()
img=img.crop((bb[0]-40,bb[1]-40,bb[2]+40,bb[3]+40))
img.save(os.path.join(TEX, 'logo.png')); print(img.size, 'top size', size)
bg=Image.new('RGBA',img.size,(70,25,58,255)); bg.alpha_composite(img); bg.convert('RGB').resize((img.size[0]*600//img.size[0],img.size[1]*600//img.size[0])).save(os.path.join(TEX, 'logo_preview.png'))
