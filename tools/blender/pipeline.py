"""Render-Pipeline: erzeugt alle Bild-Assets einer Szene in _work/out/<name>/ (PNG, danach Konvertierung zu WebP).
Aufruf: python3 tools/blender/pipeline.py <szene> [schnell]"""
import sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import klib as K

HERO = (1100, 1500)     # Endbild / Ebenen
SEQ = (840, 1146)       # Sequenzbilder
if os.environ.get('KARMA_TEST'):
    HERO = SEQ = (176, 240)


def out_dir(name):
    d = os.path.join(K.WORK, 'out-test' if os.environ.get('KARMA_TEST') else 'out', name)
    os.makedirs(d, exist_ok=True)
    return d


def objs(names):
    return [bpy.data.objects[n] for n in names if n in bpy.data.objects]


def set_render(o, on):
    o.hide_render = not on


def cup_group():
    return objs(['cup', 'fill', 'mound', 'logo', 'fill2', 'fill3', 'fill4', 'mound2'])


def render_layers(d, tops, res, samples, prefix=''):
    """Jedes Topping einzeln rendern (gleiche Kamera, gleiches Licht) -> passgenaue Ebenen."""
    sc = K.setup_render(*res, samples=samples, glass=False)
    sc.render.use_persistent_data = True
    allobj = [o for o in bpy.data.objects if o.type == 'MESH']
    for name, ob in tops.items():
        for o in allobj:
            set_render(o, o == ob)
        K.render(os.path.join(d, 'layer_' + prefix + name + '.png'))
    for o in allobj:
        set_render(o, True)


def render_shadow(d, res, casters, samples=32, name='shadow.png'):
    sc = K.setup_render(*res, samples=samples, glass=False)
    fl = K.shadow_catcher()
    allobj = [o for o in bpy.data.objects if o.type == 'MESH' and o != fl]
    keep = {}
    for o in allobj:
        keep[o.name] = (o.visible_camera, o.hide_render)
        o.visible_camera = False
        o.hide_render = o not in casters
    K.render(os.path.join(d, name))
    for o in allobj:
        o.visible_camera, o.hide_render = keep[o.name]
    bpy.data.objects.remove(fl)


def classic(fast=False):
    import classic as S
    d = out_dir('classic')
    tops = S.build()
    smp = 16 if fast else 96
    # 1) Endbild (Hero) mit Toppings
    K.setup_render(*HERO, samples=smp, glass=False)
    K.render(os.path.join(d, 'final.png'))
    # 2) Ebenen
    render_layers(d, tops, HERO, 16 if fast else 64)
    # 3) Schatten (nur Becher-Inhalt)
    render_shadow(d, HERO, objs(['fill', 'mound']))
    # 4) Drehsequenz ohne Toppings
    for o in tops.values():
        o.hide_render = True
    sc = K.setup_render(*SEQ, samples=10 if fast else 34, glass=False)
    sc.render.use_persistent_data = True
    grp = cup_group()
    n = 8 if fast else 48
    sd = os.path.join(d, 'seq')
    os.makedirs(sd, exist_ok=True)
    for i in range(n):
        a = 2 * math.pi * i / n
        for o in grp:
            o.rotation_euler = (0, 0, a)
        K.render(os.path.join(sd, f'{i:03d}.png'))
    for o in grp:
        o.rotation_euler = (0, 0, 0)
    json.dump({'frames': n, 'hero': HERO, 'seq': SEQ}, open(os.path.join(d, 'meta.json'), 'w'))


def render_group_layer(d, objs_on, res, samples, name):
    sc = K.setup_render(*res, samples=samples, glass=False)
    allobj = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in allobj:
        o.hide_render = o not in objs_on
    K.render(os.path.join(d, 'layer_' + name + '.png'))
    for o in allobj:
        o.hide_render = False


def tropical(fast=False):
    import tropical as S
    d = out_dir('tropical')
    smp = 16 if fast else 96
    tops = S.build(level=1.0)
    K.setup_render(*HERO, samples=smp, glass=True)
    K.render(os.path.join(d, 'final.png'))
    single = {k: v for k, v in tops.items() if not k.startswith('coconut')}
    render_layers(d, single, HERO, 16 if fast else 40)
    render_group_layer(d, [v for k, v in tops.items() if k.startswith('coconut')], HERO, 16 if fast else 40, 'coconut')
    render_shadow(d, HERO, objs(['fill', 'mound']))
    n = 6 if fast else 26
    sd = os.path.join(d, 'seq')
    os.makedirs(sd, exist_ok=True)
    for i in range(n):
        t = i / (n - 1)
        S.build(level=t, toppings=False, mound=(i == n - 1))
        sc = K.setup_render(*SEQ, samples=10 if fast else 24, glass=True)
        K.render(os.path.join(sd, f'{i:03d}.png'))
    json.dump({'frames': n, 'hero': HERO, 'seq': SEQ}, open(os.path.join(d, 'meta.json'), 'w'))


def peanut(fast=False):
    import peanut as S
    d = out_dir('peanut')
    smp = 16 if fast else 96
    S.build(drip=1.0)
    K.setup_render(*HERO, samples=smp, glass=False)
    K.render(os.path.join(d, 'final.png'))
    render_shadow(d, HERO, objs(['fill', 'mound']))
    n = 6 if fast else 24
    sd = os.path.join(d, 'seq')
    os.makedirs(sd, exist_ok=True)
    for i in range(n):
        t = i / (n - 1)
        e = t * t * (3 - 2 * t)
        S.build(drip=e)
        K.setup_render(*SEQ, samples=10 if fast else 24, glass=False)
        K.render(os.path.join(sd, f'{i:03d}.png'))
    json.dump({'frames': n, 'hero': HERO, 'seq': SEQ}, open(os.path.join(d, 'meta.json'), 'w'))


def berry(fast=False):
    import berry as S
    d = out_dir('berry')
    smp = 16 if fast else 96
    tops = S.build()
    K.setup_render(*HERO, samples=smp, glass=False)
    K.render(os.path.join(d, 'final.png'))
    single = {k: v for k, v in tops.items() if not k.startswith('coconut')}
    render_layers(d, single, HERO, 16 if fast else 48)
    render_group_layer(d, [v for k, v in tops.items() if k.startswith('coconut')], HERO, 16 if fast else 48, 'coconut')
    render_shadow(d, HERO, objs(['fill', 'mound']))
    for o in tops.values():
        o.hide_render = True
    K.setup_render(*HERO, samples=smp, glass=False)
    K.render(os.path.join(d, 'base.png'))
    json.dump({'hero': HERO}, open(os.path.join(d, 'meta.json'), 'w'))


def matcha(fast=False):
    import matcha as S
    d = out_dir('matcha')
    smp = 16 if fast else 96
    S.build(1.0)
    K.setup_render(*HERO, samples=smp, glass=True)
    K.render(os.path.join(d, 'final.png'))
    render_shadow(d, HERO, objs(['fill']))
    n = 6 if fast else 34
    sd = os.path.join(d, 'seq')
    os.makedirs(sd, exist_ok=True)
    for i in range(n):
        S.build(i / (n - 1))
        K.setup_render(*SEQ, samples=10 if fast else 26, glass=True)
        K.render(os.path.join(sd, f'{i:03d}.png'))
    json.dump({'frames': n, 'hero': HERO, 'seq': SEQ}, open(os.path.join(d, 'meta.json'), 'w'))


if __name__ == '__main__':
    scene = sys.argv[1]
    fast = 'schnell' in sys.argv
    t = time.time()
    globals()[scene](fast)
    print('PIPELINE_DONE', scene, round(time.time() - t), 's')
