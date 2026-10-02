"""Iced Strawberry Matcha: Erdbeerpüree unten, Milch, Matcha oben, Eiswürfel."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klib as K
from klib import srgb

H = K.CUP_H
Z_PUREE = 0.030
Z_MILK = 0.084
Z_TOP = 0.110


def level_at(t):
    """t 0..1 -> Füllhöhe: erst Püree, dann Milch, dann Matcha."""
    def ease(x):
        return 1 - (1 - max(0.0, min(1.0, x))) ** 2
    if t < 0.3:
        return 0.003 + (Z_PUREE - 0.003) * ease(t / 0.3)
    if t < 0.66:
        return Z_PUREE + (Z_MILK - Z_PUREE) * ease((t - 0.3) / 0.36)
    return Z_MILK + (Z_TOP - Z_MILK) * ease((t - 0.66) / 0.34)


def build(t=1.0, logo=True):
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera()
    K.make_cup()
    layers = [
        (Z_PUREE, 'liquid', srgb('#9E1426'), srgb('#D23040'), 0.25, 0.35, 0.0035),
        (Z_MILK, 'liquid', srgb('#F1ECE2'), srgb('#FBF8F2'), 0.2, 0.7, 0.006),
        (H, 'liquid', srgb('#5E7F2C'), srgb('#8AA645'), 0.25, 0.5, 0.005),
    ]
    mat = K.mat_layers('matcha_layers', layers, seed=5.0, spec=0.25)
    lv = level_at(t)
    if lv > 0.0035:
        K.make_fill('fill', mat, z1=lv, inset=0.0002)
    rnd = random.Random(11)
    # Eiswürfel locker im ganzen Becher verteilt (an der Wand und dazwischen)
    k = 0
    for row, z in enumerate((0.014, 0.034, 0.054, 0.074, 0.094)):
        n = 4
        off = rnd.uniform(0, 6.28)
        for j in range(n):
            a = off + 2 * math.pi * j / n + rnd.uniform(-0.35, 0.35)
            wall = K.cup_r(z) - K.WALL - 0.012
            rr = wall * rnd.uniform(0.55, 0.95)
            s_ = rnd.uniform(0.016, 0.019)
            K.place(K.make_ice(f'ice_{k}', s=s_, seed=k), (rr * math.cos(a), rr * math.sin(a), z + rnd.uniform(-0.004, 0.004)),
                    (rnd.uniform(-35, 35), rnd.uniform(-35, 35), rnd.uniform(0, 90)))
            k += 1
    if logo:
        K.make_logo_decal()
    return {}


if __name__ == '__main__':
    out = sys.argv[-1] if sys.argv[-1].endswith('.png') else os.path.join(K.WORK, 'render', 'matcha_test.png')
    tt = float(sys.argv[-2]) if len(sys.argv) > 2 else 1.0
    build(tt)
    K.setup_render(330, 450, samples=20, glass=True)
    K.render(out)
