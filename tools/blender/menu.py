"""Kleine Vorschaubilder für die Speisekarte: Smoothies, Matcha-Drinks, Kaffee, Extras.
(Die Açaí-Motive sind echte Becherfotos aus tools/photo/; Bowls werden nicht mehr gerendert.)
Ausgabe: _work/out/karte/<name>.png (quadratisch, transparent)."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import klib as K
from klib import srgb
from mathutils import Vector

OUT = os.path.join(K.WORK, 'out', 'karte')
RES = int(os.environ.get('KARMA_RES', 360))


def base_scene(elev=48, dist=0.42, target=(0, 0, 0.02), lens=60):
    K.reset()
    K.setup_world()
    K.studio_lights()
    cam = bpy.data.cameras.new('cam')
    cam.lens = lens
    cam.sensor_fit = 'VERTICAL'
    cam.sensor_height = 24
    o = bpy.data.objects.new('cam', cam)
    bpy.context.scene.collection.objects.link(o)
    a = math.radians(elev)
    o.location = (0, -dist * math.cos(a), target[2] + dist * math.sin(a))
    K.look_at(o, target)
    bpy.context.scene.camera = o
    K.shadow_catcher()


def side_scene():
    K.reset()
    K.setup_world()
    K.studio_lights()
    K.camera(dist=0.78, height=0.16, target_z=0.072)
    K.shadow_catcher()


def ceramic(name='ceramic', col='#F4EFE7'):
    return K.cached(name, lambda: K.mat_simple(name, srgb(col), srgb(col), scale=200, rough=0.18, sss=0.05, bump=0.02, coat=0.6))


def bowl(R=0.075, H=0.045):
    prof = [(0.0, 0.0), (R * 0.42, 0.0), (R * 0.45, 0.004)]
    for i in range(1, 15):
        t = i / 14
        prof.append((R * (0.45 + 0.55 * math.sin(t * math.pi / 2)), 0.004 + (H - 0.004) * (1 - math.cos(t * math.pi / 2)) ** 0.85))
    prof += [(R + 0.002, H), (R - 0.002, H + 0.0015)]
    for i in range(1, 12):
        t = i / 11
        prof.append(((R - 0.004) * (1 - 0.6 * t) ** 0.9, H - 0.004 - (H - 0.012) * t ** 1.4))
    prof.append((0.0, 0.008))
    o = K.lathe('bowl', prof, seg=128)
    o.data.materials.append(ceramic('bowl_ceramic', '#EFE8DC'))
    return K.link(o)


def cup_ceramic(r=0.042, h=0.058, saucer=True):
    prof = [(0.0, 0.006), (r * 0.55, 0.006)]
    for i in range(1, 14):
        t = i / 13
        prof.append((r * (0.55 + 0.45 * math.sin(t * math.pi / 2)), 0.006 + h * t))
    prof += [(r + 0.0015, 0.006 + h), (r - 0.003, 0.006 + h - 0.002), (r * 0.5, 0.012), (0.0, 0.012)]
    o = K.lathe('cupc', prof, seg=128)
    o.data.materials.append(ceramic())
    K.link(o)
    # Henkel
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, radius=1, segments=24)
    me = bpy.data.meshes.new('handle')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.015, minor_radius=0.0035, major_segments=40, minor_segments=14,
                                     location=(r + 0.008, 0, 0.006 + h * 0.55), rotation=(math.pi / 2, 0, 0))
    hd = bpy.context.active_object
    hd.data.materials.append(ceramic())
    for p in hd.data.polygons:
        p.use_smooth = True
    if saucer:
        sp = [(0.0, 0.0), (0.05, 0.0), (0.072, 0.006), (0.074, 0.008), (0.07, 0.0085), (0.05, 0.004), (0.0, 0.004)]
        s = K.lathe('saucer', sp, seg=128)
        s.data.materials.append(ceramic())
        K.link(s)
    return o


def surface(tex, r, z, name='surface'):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=r, segments=96)
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co.x / (2 * r) + 0.5, lp.vert.co.y / (2 * r) + 0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    o = bpy.data.objects.new(name, me)
    o.location = (0, 0, z)
    o.data.materials.append(K.mat_image(name, tex, rough=0.3, sss=0.2, coat=0.3, bump=0.05))
    return K.link(o)


def acai_bowl_fill(R, H):
    top = K.mat_sorbet_top('bowl_acai', srgb('#2E0C27'), srgb('#60204F'))
    K.make_mound('bfill', top, H - 0.012, 0.018, R - 0.008, seed=3, lumps=0.8)


def render(name):
    os.makedirs(OUT, exist_ok=True)
    sc = K.setup_render(RES, RES, samples=int(os.environ.get('KARMA_SMP', 40)), glass=True)
    sc.view_settings.exposure = -1.75
    K.render(os.path.join(OUT, name + '.png'))


def item(name):
    h = 0.045
    if name.startswith('bowl'):
        base_scene(elev=52, dist=0.36, target=(0, 0, 0.03))
        bowl()
        acai_bowl_fill(0.075, h)
        z = h + 0.006
        if name == 'bowl-classic':
            for i, (x, y, rz) in enumerate(((-0.03, -0.01, 30), (-0.02, -0.03, 10), (-0.035, 0.012, 50))):
                K.place(K.make_banana_slice(f'b{i}', R=0.014, seed=i), (x, y, z), (75, 0, rz))
            K.place(K.make_strawberry_half('s1', H=0.03, seed=1), (0.0, 0.01, z), (80, 0, 0))
            K.place(K.make_strawberry_half('s2', H=0.028, seed=2), (0.012, -0.022, z), (80, 0, 30))
            K.place(K.make_granola_cluster('g1', size=0.012, seed=1), (0.032, 0.006, z + 0.003), (0, 0, 0))
            K.place(K.make_granola_cluster('g2', size=0.01, seed=2), (0.028, -0.024, z + 0.002), (0, 0, 0))
        elif name == 'bowl-tropical':
            for i, (x, y) in enumerate(((-0.03, -0.01), (-0.018, 0.012), (-0.03, 0.026), (-0.012, -0.026))):
                K.place(K.make_mango_cube(f'm{i}', s=0.013, seed=i), (x, y, z + 0.004), (10 * i, 5, 20 * i))
            for i, (x, y) in enumerate(((0.014, 0.014), (0.024, -0.012))):
                K.place(K.make_pineapple_chunk(f'p{i}', s=0.015, seed=i), (x, y, z + 0.004), (90, 0, 30 * i))
            for i in range(6):
                K.place(K.make_coconut_flake(f'c{i}', seed=i), (0.034 + 0.004 * (i % 2), -0.03 + 0.012 * i, z + 0.003), (10, 20, 40 * i))
        else:
            K.place(K.make_pb_dollop('pb', R=0.016, seed=2), (-0.004, 0.006, z), (0, 0, 0))
            for i, (x, y, rz) in enumerate(((-0.034, -0.008, 20), (-0.026, -0.026, 0), (-0.034, 0.014, 40))):
                K.place(K.make_banana_slice(f'b{i}', R=0.014, seed=i), (x, y, z), (75, 0, rz))
            K.place(K.make_cacao_nibs('n', count=40, spread=0.014, seed=1), (0.026, -0.016, z + 0.002), (0, 0, 0))
            K.place(K.make_granola_cluster('g1', size=0.012, seed=3), (0.03, 0.016, z + 0.003), (0, 0, 0))
        render(name)
        return
    if name.startswith('smoothie') or name in ('drink-iced-matcha', 'coffee-iced-latte'):
        side_scene()
        K.make_cup()
        if name.startswith('smoothie'):
            c = {'smoothie-green': ('#5F8A2A', '#86B046'), 'smoothie-pink': ('#C4506A', '#E57E92'),
                 'smoothie-mango': ('#E88A1E', '#F7B246')}[name]
            mat = K.mat_simple(name, srgb(c[0]), srgb(c[1]), scale=40, rough=0.35, sss=0.4, bump=0.05)
            K.make_fill('fill', mat, z1=K.CUP_H - 0.006)
        else:
            if name == 'drink-iced-matcha':
                layers = [(0.07, 'liquid', srgb('#F1ECE2'), srgb('#FBF8F2'), 0.2, 0.7, 0.006),
                          (K.CUP_H, 'liquid', srgb('#5E7F2C'), srgb('#8AA645'), 0.25, 0.5, 0.008)]
            else:
                layers = [(0.06, 'liquid', srgb('#EFE6D8'), srgb('#F8F2E8'), 0.2, 0.7, 0.01),
                          (K.CUP_H, 'liquid', srgb('#6B3E1E'), srgb('#9A5E30'), 0.25, 0.4, 0.012)]
            K.make_fill('fill', K.mat_layers(name, layers, spec=0.25), z1=0.108)
            for i, z in enumerate((0.03, 0.055, 0.08, 0.1)):
                K.place(K.make_ice(f'ice{i}', s=0.02, seed=i), (0.012 * (-1) ** i, 0.006, z), (20 * i, 15, 30 * i))
        # Strohhalm
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.16, location=(0.012, 0.01, 0.12), rotation=(0, math.radians(-12), 0))
        st = bpy.context.active_object
        st.data.materials.append(K.mat_simple('straw', srgb('#F4EFE6'), srgb('#FFFFFF'), rough=0.4))
        K.make_logo_decal()
        render(name)
        return
    if name.startswith('coffee') or name in ('drink-matcha-latte', 'drink-chai'):
        base_scene(elev=50, dist=0.40, target=(0, 0, 0.028))
        if name == 'coffee-espresso':
            cup_ceramic(r=0.028, h=0.038)
            surface('espresso_crema.png', 0.0262, 0.006 + 0.038 - 0.006)
        else:
            cup_ceramic()
            tex = {'coffee-cappuccino': 'latte_heart.png', 'coffee-flatwhite': 'latte_rosetta.png',
                   'drink-matcha-latte': 'latte_matcha.png', 'drink-chai': 'latte_chai.png'}[name]
            surface(tex, 0.0395, 0.006 + 0.058 - 0.005)
        render(name)
        return
    if name.startswith('extra'):
        base_scene(elev=50, dist=0.26, target=(0, 0, 0.012))
        sp = [(0.0, 0.0), (0.04, 0.0), (0.055, 0.008), (0.057, 0.011), (0.052, 0.011), (0.04, 0.004), (0.0, 0.004)]
        d = K.lathe('dish', sp, seg=96)
        d.data.materials.append(ceramic('dish', '#3E2B22'))
        K.link(d)
        if name == 'extra-granola':
            for i, (x, y) in enumerate(((0, 0), (-0.016, 0.01), (0.016, 0.008), (0.004, -0.016), (-0.012, -0.012), (0.018, -0.01))):
                K.place(K.make_granola_cluster(f'g{i}', size=0.011, seed=i), (x, y, 0.012), (0, 0, 40 * i))
        elif name == 'extra-peanut':
            K.place(K.make_pb_dollop('pb', R=0.022, seed=4), (0, 0, 0.004), (0, 0, 0))
        elif name == 'extra-coconut':
            for i in range(26):
                a = i * 2.4
                rr = 0.004 + 0.0011 * i
                K.place(K.make_coconut_flake(f'c{i}', L=0.016, seed=i), (rr * math.cos(a), rr * math.sin(a), 0.006 + 0.0006 * (i % 5)),
                        (20 * (i % 3), 15 * (i % 4), 37 * i))
        else:
            K.place(K.make_strawberry_half('s1', H=0.03, seed=1), (-0.012, 0.002, 0.004), (80, 0, 10))
            K.place(K.make_strawberry_half('s2', H=0.026, seed=2), (0.006, 0.014, 0.004), (80, 0, -30))
            for i, (x, y) in enumerate(((0.014, -0.008), (0.022, 0.004), (0.002, -0.016), (0.016, 0.018))):
                K.place(K.make_blueberry(f'bb{i}', seed=i), (x, y, 0.010), (0, 0, 0))
            K.place(K.make_banana_slice('ba', R=0.014, seed=1), (-0.016, -0.016, 0.008), (70, 0, 20))
            K.place(K.make_mango_cube('mg', s=0.012, seed=1), (0.0, -0.002, 0.012), (10, 20, 30))
        render(name)
        return


ITEMS = ['smoothie-green', 'smoothie-pink', 'smoothie-mango',
         'drink-iced-matcha', 'drink-matcha-latte', 'drink-chai', 'coffee-espresso', 'coffee-cappuccino',
         'coffee-flatwhite', 'coffee-iced-latte', 'extra-granola', 'extra-peanut', 'extra-coconut', 'extra-fruit']

if __name__ == '__main__':
    todo = [a for a in sys.argv[1:] if a in ITEMS] or ITEMS
    for it in todo:
        item(it)
        print('MENU_DONE', it)
