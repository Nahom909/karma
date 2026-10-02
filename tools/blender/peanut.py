"""Peanut Power: Açaí, Erdnussbutter-Schicht, Chiapudding, Blaubeeren, Erdbeere, Erdnussbutter-Drip, Kakao-Nibs."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klib as K
from klib import srgb

H = K.CUP_H
DRIPS = [(-math.pi / 2 - 0.42, 0.050, 0.0034), (-math.pi / 2 + 0.10, 0.034, 0.0030), (-math.pi / 2 + 0.62, 0.062, 0.0036),
         (-math.pi / 2 - 0.95, 0.024, 0.0026)]


def build(drip=1.0, toppings=True, logo=True):
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera()
    K.make_cup()
    layers = [
        (0.042, 'acai', srgb('#2A0923'), srgb('#5E1E50'), 0.45, 0.12, 0.004),
        (0.074, 'smooth', srgb('#B9772F'), srgb('#D6994E'), 0.25, 0.35, 0.004),
        (H, 'chia', srgb('#D9CDB7'), srgb('#EFE6D3'), 0.4, 0.3, 0.004),
    ]
    mat = K.mat_layers('peanut_layers', layers, seed=2.0)
    K.make_fill('fill', mat, z1=H - 0.0012)
    top = K.mat_sorbet_top('chia_top', srgb('#CFC2AA'), srgb('#EDE3CF'))
    K.make_mound('mound', top, H - 0.003, 0.010, K.CUP_RT - 0.0012, seed=11)
    if logo:
        K.make_logo_decal()
    tops = {}
    if toppings:
        tops['pb_dollop'] = K.place(K.make_pb_dollop('pb_dollop', R=0.021, seed=1), (-0.002, -0.012, H + 0.008), (0, 0, 30))
        tops['rim_pb'] = K.make_rim_blob('rim_pb', -math.pi / 2 - 1.0, -math.pi / 2 + 0.7, H + 0.0008, thick=0.0034)
        bb = [(0.024, -0.016, H + 0.010), (0.034, -0.004, H + 0.008), (0.016, -0.026, H + 0.009), (-0.030, -0.012, H + 0.008),
              (-0.020, -0.024, H + 0.010), (0.010, 0.012, H + 0.016)]
        for i, p in enumerate(bb):
            tops[f'blueberry_{i+1}'] = K.place(K.make_blueberry(f'blueberry_{i+1}', R=0.0068, seed=20 + i), p,
                                                (12 * i, 25 * i, 40 * i))
        tops['strawberry_1'] = K.place(K.make_strawberry_half('strawberry_1', H=0.032, seed=7), (0.024, 0.012, H + 0.010), (0, 14, -34))
        tops['strawberry_2'] = K.place(K.make_strawberry_half('strawberry_2', H=0.028, seed=8), (-0.026, 0.010, H + 0.010), (0, -16, 38))
        tops['cacao'] = K.place(K.make_cacao_nibs('cacao', seed=3), (0.0, -0.012, H + 0.012), (0, 0, 0))
        if drip > 0:
            for i, (a, L, r) in enumerate(DRIPS):
                ln = L * drip
                if ln > 0.002:
                    tops[f'drip_{i+1}'] = K.make_drip(f'drip_{i+1}', a, H + 0.0005, ln, r0=r, seed=i)
    return tops


if __name__ == '__main__':
    out = sys.argv[-1] if sys.argv[-1].endswith('.png') else os.path.join(K.WORK, 'render', 'peanut_test.png')
    build()
    K.setup_render(330, 450, samples=20, glass=False)
    K.render(out)
