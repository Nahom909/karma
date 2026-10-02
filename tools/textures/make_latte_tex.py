"""Textur-Erzeugung für die 3D-Szenen. Ausgabe nach _work/tex/ (wird von tools/blender/klib.py gelesen)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX = os.path.join(ROOT, '_work', 'tex')
FONTS = os.path.join(ROOT, '_work', 'fonts')
os.makedirs(TEX, exist_ok=True)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
N=768
def base(c_center, c_edge, seed=0, tiger=False):
    y,x=np.mgrid[-1:1:N*1j,-1:1:N*1j]; r=np.sqrt(x*x+y*y)
    rng=np.random.default_rng(seed)
    n=np.asarray(Image.fromarray((rng.random((48,48))*255).astype(np.uint8)).resize((N,N),Image.BICUBIC))/255
    col=np.array(c_center)*(1-r[...,None]**1.6)+np.array(c_edge)*(r[...,None]**1.6)
    col*= (0.93+0.12*n)[...,None]
    if tiger:
        a=np.arctan2(y,x); st=(np.sin(a*40+n*12)*0.5+0.5)**3*0.18*r
        col*=(1-st)[...,None]
    return Image.fromarray((np.clip(col,0,1)*255).astype(np.uint8))
def foam_layer(draw_fn, blur=6):
    m=Image.new('L',(N,N),0); d=ImageDraw.Draw(m); draw_fn(d); return m.filter(ImageFilter.GaussianBlur(blur))
def comp(img, mask, foam=(0.97,0.94,0.89)):
    f=Image.new('RGB',(N,N),tuple(int(c*255) for c in foam))
    return Image.composite(f,img,mask)
import math
def heart(d, s=1.0, cy=0.0):
    c=N/2; k=N*0.0145*s; oy=N*cy
    pts=[]
    for i in range(200):
        t=2*math.pi*i/200
        x=16*math.sin(t)**3; y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((c+x*k, c-y*k*0.92+oy))
    d.polygon(pts, fill=255)
    # weißer Schaumrand
    d.ellipse((N*0.06,N*0.06,N*0.94,N*0.94), outline=255, width=int(N*0.035))
def rosetta(d):
    # Tulpe: drei gestapelte Bögen und ein Kopf
    c=N/2
    for i,(w,yy) in enumerate(((0.27,0.20),(0.22,0.06),(0.17,-0.07))):
        d.chord((c-N*w, c+N*yy-N*0.12, c+N*w, c+N*yy+N*0.12), 180, 360, fill=255)
        d.chord((c-N*w*0.8, c+N*yy-N*0.06, c+N*w*0.8, c+N*yy+N*0.08), 180, 360, fill=0)
    d.ellipse((c-N*0.1, c-N*0.27, c+N*0.1, c-N*0.1), fill=255)
    d.line((c, c-N*0.2, c, c+N*0.3), fill=0, width=8)
    d.ellipse((N*0.06,N*0.06,N*0.94,N*0.94), outline=255, width=int(N*0.03))
coffee=base((0.62,0.40,0.22),(0.36,0.22,0.11),1)
comp(coffee, foam_layer(lambda d: heart(d,1.55,-0.02), 5)).save(os.path.join(TEX, 'latte_heart.png'))
comp(coffee, foam_layer(lambda d: (heart(d,1.3,0.08), heart(d,0.8,-0.2)), 5)).save(os.path.join(TEX, 'latte_rosetta.png'))
m=base((0.56,0.66,0.30),(0.40,0.50,0.20),2)
comp(m, foam_layer(lambda d: heart(d,1.45,-0.02), 5)).save(os.path.join(TEX, 'latte_matcha.png'))
chai=base((0.86,0.74,0.56),(0.70,0.55,0.36),3)
arr=np.asarray(chai).astype(float); rng=np.random.default_rng(4); sp=rng.random(arr.shape[:2])>0.985
arr[sp]=arr[sp]*0.45; Image.fromarray(arr.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)).save(os.path.join(TEX, 'latte_chai.png'))
base((0.72,0.46,0.22),(0.40,0.22,0.09),5,tiger=True).save(os.path.join(TEX, 'espresso_crema.png'))
print('ok')
