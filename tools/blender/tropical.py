"""Tropical: Açaí mit Mango-Swirl, Mango, Ananas, Kokos."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klib as K
from klib import srgb

H = K.CUP_H


def fill_mat():
    return K.mat_swirl('acai_tropical', srgb('#2A0923'), srgb('#6A2259'), srgb('#F2A238'), swirl_amt=0.34,
                       seed=4.2, top_band=0.10, ribbons=4, twist=55.0, frost=srgb('#9A6A94'),
                       halo=srgb('#B5523F'))


def build(level=1.0, toppings=True, logo=True, mound=True):
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera()
    K.make_cup()
    mat = fill_mat()
    z1 = 0.0028 + (H - 0.0012 - 0.0028) * level
    if level > 0.01:
        K.make_fill('fill', mat, z1=z1)
        top = K.mat_sorbet_top('acai_top_t', srgb('#2A0A24'), srgb('#5C1E4E'))
        if mound:
            K.make_mound('mound', top, H - 0.003, 0.011, K.CUP_RT - 0.0012, seed=5)
        else:
            K.make_mound('mound', top, z1 - 0.0015, 0.003 + 0.002 * level, K.cup_r(z1) - K.WALL - 0.0004, seed=5, lumps=0.6)
    if logo:
        K.make_logo_decal()
    tops = {}
    if toppings:
        tops['mango_1'] = K.place(K.make_mango_cube('mango_1', s=0.015, seed=1), (-0.012, -0.016, H + 0.013), (12, 8, 20))
        tops['mango_2'] = K.place(K.make_mango_cube('mango_2', s=0.016, seed=2), (0.016, -0.010, H + 0.016), (-8, 14, -25))
        tops['mango_3'] = K.place(K.make_mango_cube('mango_3', s=0.014, seed=3), (-0.028, 0.004, H + 0.012), (20, -10, 40))
        tops['mango_4'] = K.place(K.make_mango_cube('mango_4', s=0.015, seed=4), (0.002, 0.008, H + 0.028), (30, 5, 10))
        tops['mango_5'] = K.place(K.make_mango_cube('mango_5', s=0.013, seed=5), (0.030, 0.006, H + 0.012), (-20, 30, 60))
        tops['pineapple_1'] = K.place(K.make_pineapple_chunk('pineapple_1', s=0.018, seed=1), (0.032, -0.016, H + 0.010), (70, 10, 30))
        tops['pineapple_2'] = K.place(K.make_pineapple_chunk('pineapple_2', s=0.017, seed=2), (-0.006, -0.004, H + 0.036), (80, 20, -40))
        tops['pineapple_3'] = K.place(K.make_pineapple_chunk('pineapple_3', s=0.016, seed=3), (-0.034, -0.014, H + 0.008), (75, -20, 70))
        for i, (p, r) in enumerate((((-0.016, -0.020, H + 0.020), (30, 10, 20)), ((0.010, -0.020, H + 0.024), (-20, 40, 70)),
                                     ((0.024, 0.004, H + 0.024), (40, -20, 120)), ((-0.020, 0.000, H + 0.024), (-30, 10, 150)),
                                     ((0.008, -0.022, H + 0.034), (20, 30, 60)), ((0.036, -0.002, H + 0.022), (50, 0, 10)))):
            tops[f'coconut_{i+1}'] = K.place(K.make_coconut_flake(f'coconut_{i+1}', seed=i), p, r)
    return tops


if __name__ == '__main__':
    out = sys.argv[-1] if sys.argv[-1].endswith('.png') else os.path.join(K.WORK, 'render', 'tropical_test.png')
    build()
    K.setup_render(330, 450, samples=20, glass=False)
    K.render(out)
