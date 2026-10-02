"""Classic: Açaí mit Bananen-Swirl, Erdbeere, Banane, Granola."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import klib as K
from klib import srgb


def build(toppings=True, logo=True):
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera()
    K.make_cup()
    acai = K.mat_swirl('acai_classic', srgb('#2A0923'), srgb('#6A2259'), srgb('#F3EAD2'), swirl_amt=0.36, frost=srgb('#9A6A94'),
                       seed=1.7, top_band=0.13, bottom_layer=(0.011, srgb('#A9692A'), srgb('#E3B866')))
    K.make_fill('fill', acai, z1=K.CUP_H - 0.0012)
    top = K.mat_sorbet_top('acai_top', srgb('#2A0A24'), srgb('#5C1E4E'))
    K.make_mound('mound', top, K.CUP_H - 0.003, 0.012, K.CUP_RT - 0.0012, seed=2)
    if logo:
        K.make_logo_decal()
    tops = {}
    if toppings:
        h = K.CUP_H
        tops['strawberry_1'] = K.place(K.make_strawberry_half('strawberry_1', H=0.043, seed=1),
                                       (-0.004, -0.010, h + 0.002), (8, -12, 4))
        tops['strawberry_2'] = K.place(K.make_strawberry_half('strawberry_2', H=0.036, seed=2),
                                       (0.020, 0.012, h + 0.006), (-6, 18, -28))
        tops['banana_1'] = K.place(K.make_banana_slice('banana_1', seed=1),
                                   (0.031, -0.010, h + 0.010), (10, 8, -58))
        tops['banana_2'] = K.place(K.make_banana_slice('banana_2', R=0.0155, seed=2),
                                   (-0.031, -0.002, h + 0.008), (0, -14, 60))
        tops['granola_1'] = K.place(K.make_granola_cluster('granola_1', size=0.011, seed=1),
                                    (0.008, -0.002, h + 0.021), (0, 0, 0))
        tops['granola_2'] = K.place(K.make_granola_cluster('granola_2', size=0.010, pieces=36, seed=2),
                                    (-0.019, -0.008, h + 0.018), (0, 20, 40))
        tops['granola_3'] = K.place(K.make_granola_cluster('granola_3', size=0.008, pieces=26, seed=3),
                                    (0.017, -0.016, h + 0.009), (10, 0, 70))
    return tops


if __name__ == '__main__':
    out = sys.argv[-1] if sys.argv[-1].endswith('.png') else os.path.join(K.WORK, 'render', 'classic_test.png')
    build()
    K.setup_render(550, 750, samples=48, glass=False)
    import time
    t = time.time()
    K.render(out)
    print('RENDER_S', round(time.time() - t, 1))
