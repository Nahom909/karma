"""Berry Blast: Açaí mit Kokos-Joghurt-Swirl, Blaubeeren, Himbeeren, Erdbeere, Kokos."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klib as K
from klib import srgb

H = K.CUP_H


def build(toppings=True, logo=True):
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera()
    K.make_cup()
    mat = K.mat_swirl('acai_berry', srgb('#280820'), srgb('#661F55'), srgb('#F6F3EC'), swirl_amt=0.44,
                      seed=7.7, top_band=0.16, ribbons=6, twist=40.0, frost=srgb('#9A6A94'))
    K.make_fill('fill', mat, z1=H - 0.0012)
    top = K.mat_sorbet_top('acai_top_b', srgb('#2A0A24'), srgb('#5C1E4E'))
    K.make_mound('mound', top, H - 0.003, 0.012, K.CUP_RT - 0.0012, seed=8)
    if logo:
        K.make_logo_decal()
    tops = {}
    if toppings:
        bb = [(-0.026, -0.016, H + 0.009), (-0.012, -0.024, H + 0.012), (0.004, -0.026, H + 0.011),
              (0.020, -0.020, H + 0.012), (0.033, -0.010, H + 0.008), (-0.034, -0.004, H + 0.007),
              (-0.004, -0.010, H + 0.024), (0.014, -0.006, H + 0.026), (-0.020, 0.004, H + 0.021)]
        for i, p in enumerate(bb):
            tops[f'blueberry_{i+1}'] = K.place(K.make_blueberry(f'blueberry_{i+1}', R=0.0066 + 0.0008 * (i % 3), seed=i),
                                                p, (10 * i, 20 + 13 * i, 33 * i))
        rb = [((-0.017, -0.012, H + 0.024), (160, 10, 0)), ((0.026, 0.002, H + 0.020), (150, -20, 40)),
              ((0.006, 0.010, H + 0.032), (170, 5, 80)), ((-0.031, 0.010, H + 0.016), (140, 25, 120))]
        for i, (p, r) in enumerate(rb):
            tops[f'raspberry_{i+1}'] = K.place(K.make_raspberry(f'raspberry_{i+1}', seed=i), p, r)
        tops['strawberry_1'] = K.place(K.make_strawberry_half('strawberry_1', H=0.034, seed=5),
                                       (0.004, 0.008, H + 0.012), (4, 10, -10))
        for i, (p, r) in enumerate((((-0.008, -0.020, H + 0.030), (30, 10, 20)), ((0.020, -0.012, H + 0.032), (-20, 40, 70)),
                                     ((-0.026, -0.006, H + 0.026), (40, -20, 120)), ((0.012, -0.024, H + 0.020), (-10, 20, 160)))):
            tops[f'coconut_{i+1}'] = K.place(K.make_coconut_flake(f'coconut_{i+1}', L=0.010, seed=10 + i), p, r)
    return tops


if __name__ == '__main__':
    out = sys.argv[-1] if sys.argv[-1].endswith('.png') else os.path.join(K.WORK, 'render', 'berry_test.png')
    build()
    K.setup_render(330, 450, samples=20, glass=False)
    K.render(out)
