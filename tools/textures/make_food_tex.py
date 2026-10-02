"""Textur-Erzeugung für die 3D-Szenen. Ausgabe nach _work/tex/ (wird von tools/blender/klib.py gelesen)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX = os.path.join(ROOT, '_work', 'tex')
FONTS = os.path.join(ROOT, '_work', 'fonts')
os.makedirs(TEX, exist_ok=True)
import numpy as np
from PIL import Image, ImageFilter
rng=np.random.default_rng(7)
def fbm(shape,scale,oct=4,seed=0):
    r=np.random.default_rng(seed); out=np.zeros(shape); amp=1; tot=0
    for o in range(oct):
        s=max(2,int(scale*(2**o)))
        n=r.random((s,s)); im=Image.fromarray((n*255).astype(np.uint8)).resize(shape[::-1],Image.BICUBIC)
        out+=amp*np.asarray(im)/255; tot+=amp; amp*=0.5
    return out/tot
# ---------- strawberry longitudinal cut ----------
N=1024
v=np.linspace(1,0,N)[:,None]; u=np.linspace(0,1,N)[None,:]
# profile: half width as function of v (0 tip, 1 top) -- must match blender profile
def halfw(v):
    v=np.clip(v,0,1)
    lo=0.46*np.clip(v/0.7,0,1)**0.62
    hi=0.46*np.sqrt(np.clip(1-((v-0.7)/0.3)**2,0,1))
    return np.where(v<0.7,lo,hi)
hw=halfw(v)
d=np.abs(u-0.5)/np.maximum(hw,1e-4)  # 0 center ->1 edge
d=np.broadcast_to(d,(N,N)).copy()
n1=fbm((N,N),6,5,1); n2=fbm((N,N),24,3,2)
dn=d+ (n1-0.5)*0.12
col=np.zeros((N,N,3))
deep=np.array([0.62,0.02,0.08]); red=np.array([0.86,0.08,0.15]); pink=np.array([0.95,0.36,0.40]); pith=np.array([0.99,0.86,0.84]); white=np.array([1.0,0.93,0.91])
t=np.clip((dn-0.32)/0.4,0,1)[...,None]
col=pink*(1-t)+red*t
t2=np.clip((dn-0.86)/0.1,0,1)[...,None]
col=col*(1-t2)+deep*t2
# core / pith: elongated ellipse in upper 3/4
vv=np.broadcast_to(v,(N,N))
core=np.clip(1-(d/0.26)**2-((vv-0.62)/0.42)**2+ (n1-0.5)*0.5,0,1)
core=np.clip(core*2.2,0,1)[...,None]
col=col*(1-core)+pith*core
# vascular streaks radiating from core to edge
ang=np.arctan2(vv-0.62,(u-0.5))
streak=(np.sin(ang*22+n1*5)*0.5+0.5)**10
streak*=np.clip((dn-0.3)/0.3,0,1)*np.clip((0.92-dn)/0.2,0,1)
streak=np.asarray(Image.fromarray((streak*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)))/255
col=col*(1-streak[...,None]*0.38)+white*streak[...,None]*0.38
col*= (0.92+0.16*n2)[...,None]
alpha=(dn<1.02).astype(np.float32)
img=np.dstack([np.clip(col,0,1),alpha])
Image.fromarray((img*255).astype(np.uint8),'RGBA').save(os.path.join(TEX, 'strawberry_cut.png'))
# ---------- banana slice face ----------
M=1024
y,x=np.mgrid[-1:1:M*1j,-1:1:M*1j]
r=np.sqrt(x*x+y*y); a=np.arctan2(y,x)
n=fbm((M,M),8,5,3); n3=fbm((M,M),40,2,4)
base=np.array([0.96,0.90,0.66]); edge=np.array([0.93,0.83,0.50]); center=np.array([0.97,0.93,0.76])
col=base*(1-np.clip(r,0,1)[...,None])+edge*np.clip(r,0,1)[...,None]
# 3-lobed center
lobe=0.16+0.045*np.cos(3*(a+0.4))+ (n-0.5)*0.05
cm=np.clip((lobe-r)/0.05,0,1)[...,None]
col=col*(1-cm*0.6)+center*cm*0.6
# seeds ring
seedr=0.11+0.035*np.cos(3*(a+0.4))
ring=np.exp(-((r-seedr)/0.025)**2)
dots=(np.sin(a*30)*0.5+0.5)**6
sd=ring*dots
col=col*(1-sd[...,None]*0.6)+np.array([0.40,0.30,0.18])*sd[...,None]*0.6
# radial fibres
fib=(np.sin(a*90+n*8)*0.5+0.5)**4*np.clip(r-0.3,0,1)*0.035
col=col*(1-fib[...,None])
col*= (0.95+0.08*n3)[...,None]
Image.fromarray((np.clip(col,0,1)*255).astype(np.uint8)).save(os.path.join(TEX, 'banana_face.png'))
print('ok')
