"""Karma 3D-Produktszene: Bibliothek für Becher, Füllungen, Toppings, Licht und Kamera.
Alle Maße in Metern. Aufruf über die Szenen-Skripte in diesem Ordner (python3 <skript>.py)."""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Euler, noise

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, '..', '..', '_work'))
TEX = os.path.join(WORK, 'tex')

# Becher (16 oz PET, wie im Referenzbild)
CUP_H = 0.123
CUP_RT = 0.0475
CUP_RB = 0.0368
WALL = 0.00038


def cup_r(z):
    """Außenradius des Bechers in Höhe z."""
    t = max(0.0, min(1.0, z / CUP_H))
    return CUP_RB + (CUP_RT - CUP_RB) * t


# ---------------------------------------------------------------- Grundlagen

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(4)
    _mat_cache.clear()


def setup_render(rx, ry, samples=128, transparent=True, glass=True):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.015
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 16
    sc.cycles.transmission_bounces = 16
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.glossy_bounces = 6
    sc.cycles.diffuse_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.film_transparent = transparent
    sc.cycles.film_transparent_glass = glass
    sc.cycles.film_transparent_roughness = 0.12
    sc.render.resolution_x = rx
    sc.render.resolution_y = ry
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '8'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = -1.1
    sc.cycles.seed = 3
    return sc


def setup_world(strength=0.12, color=(0.93, 0.9, 0.86)):
    w = bpy.data.worlds.new('studio')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    # weicher Studioverlauf: oben heller, unten dunkler (für glaubwürdige Reflexionen im Plastik)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (color[0] * 0.08, color[1] * 0.08, color[2] * 0.08, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*color, 1)
    mp = nt.nodes.new('ShaderNodeMapRange')
    mp.inputs['From Min'].default_value = -1
    mp.inputs['From Max'].default_value = 1
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area_light(name, loc, target, size, size_y, energy, color=(1, 1, 1), shape='RECTANGLE', spread=None):
    l = bpy.data.lights.new(name, 'AREA')
    l.shape = shape
    l.size = size
    l.size_y = size_y
    l.energy = energy
    l.color = color
    if spread is not None:
        l.spread = spread
    o = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def studio_lights(scale=1.0):
    tgt = (0, 0, 0.07)
    k = area_light('key', (-0.5, -0.6, 0.26), tgt, 0.6, 0.9, 22 * scale, (1.0, 0.96, 0.9))
    k.visible_glossy = False
    # Reflexionskarten: nur im Plastik sichtbar, erzeugen die typischen weichen Streifen
    for nm, loc, w, e in (('cardL', (-0.30, -0.55, 0.09), 0.045, 7), ('cardR', (0.36, -0.5, 0.09), 0.03, 4)):
        c = area_light(nm, loc, tgt, w, 0.42, e * scale)
        c.visible_diffuse = False
        c.data.energy = e * scale
    fr = area_light('front', (0.05, -0.85, 0.12), tgt, 0.9, 0.5, 5 * scale, (1.0, 0.98, 0.96))
    fr.visible_glossy = False
    fl = area_light('fill', (0.65, -0.5, 0.18), tgt, 0.45, 0.7, 5 * scale, (0.95, 0.97, 1.0))
    fl.visible_glossy = False
    # schmale Streiflichter für die typischen Kantenreflexe auf dem Plastik
    area_light('rimL', (-0.32, 0.30, 0.16), tgt, 0.05, 0.6, 12 * scale)
    area_light('rimR', (0.34, 0.28, 0.16), tgt, 0.05, 0.6, 11 * scale)
    area_light('stripFront', (-0.16, -0.70, 0.16), tgt, 0.035, 0.55, 4 * scale)
    tp = area_light('top', (0.05, -0.1, 0.65), tgt, 0.5, 0.5, 5 * scale, (1, 0.98, 0.95), shape='DISK')
    tp.visible_glossy = False


def camera(dist=0.76, height=0.17, target_z=0.085, focal=85, shift_y=0.0):
    cam = bpy.data.cameras.new('cam')
    cam.lens = focal
    cam.sensor_fit = 'VERTICAL'
    cam.sensor_height = 24
    cam.shift_y = shift_y
    o = bpy.data.objects.new('cam', cam)
    bpy.context.scene.collection.objects.link(o)
    o.location = (0, -dist, height)
    look_at(o, (0, 0, target_z))
    bpy.context.scene.camera = o
    return o


def shadow_catcher(size=8.0):
    me = bpy.data.meshes.new('floor')
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
    bm.to_mesh(me)
    o = bpy.data.objects.new('floor', me)
    bpy.context.scene.collection.objects.link(o)
    o.is_shadow_catcher = True
    return o


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- Shader-Hilfen

class N:
    """Kleiner Node-Builder."""

    def __init__(self, mat):
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.nt.nodes.new('ShaderNodeOutputMaterial')

    def n(self, t, **kw):
        node = self.nt.nodes.new(t)
        for k, v in kw.items():
            if k in node.inputs:
                node.inputs[k].default_value = v
            else:
                setattr(node, k, v)
        return node

    def l(self, a, b):
        self.nt.links.new(a, b)

    def ramp(self, stops):
        r = self.nt.nodes.new('ShaderNodeValToRGB')
        cr = r.color_ramp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (p, c) in zip(cr.elements, stops):
            el.position = p
            el.color = (*c, 1) if len(c) == 3 else c
        return r

    def mix(self, fac, a, b, blend='MIX'):
        m = self.nt.nodes.new('ShaderNodeMix')
        m.data_type = 'RGBA'
        m.blend_type = blend
        self._in(m.inputs[0], fac)
        self._in(m.inputs[6], a)
        self._in(m.inputs[7], b)
        return m.outputs[2]

    def mixf(self, fac, a, b):
        m = self.nt.nodes.new('ShaderNodeMix')
        m.data_type = 'FLOAT'
        self._in(m.inputs[0], fac)
        self._in(m.inputs[2], a)
        self._in(m.inputs[3], b)
        return m.outputs[0]

    def math(self, op, a, b=None, c=None, clamp=False):
        m = self.nt.nodes.new('ShaderNodeMath')
        m.operation = op
        m.use_clamp = clamp
        self._in(m.inputs[0], a)
        if b is not None:
            self._in(m.inputs[1], b)
        if c is not None:
            self._in(m.inputs[2], c)
        return m.outputs[0]

    def _in(self, sock, v):
        if hasattr(v, 'is_output') or type(v).__name__.startswith('NodeSocket'):
            self.nt.links.new(v, sock)
        else:
            sock.default_value = v


def principled(n, **kw):
    p = n.n('ShaderNodeBsdfPrincipled')
    for k, v in kw.items():
        p.inputs[k].default_value = v
    n.l(p.outputs[0], n.out.inputs['Surface'])
    return p


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


# ---------------------------------------------------------------- Materialien

def mat_plastic():
    m = bpy.data.materials.new('plastic')
    n = N(m)
    p = principled(n, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.02, 'IOR': 1.49,
                         'Transmission Weight': 1.0, 'Specular IOR Level': 0.5})
    # winzige Unregelmäßigkeiten im Kunststoff
    tc = n.n('ShaderNodeTexCoord')
    nz = n.n('ShaderNodeTexNoise', Scale=60.0, Detail=2.0)
    n.l(tc.outputs['Object'], nz.inputs['Vector'])
    b = n.n('ShaderNodeBump', Strength=0.04, Distance=0.0002)
    n.l(nz.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_logo(alpha=0.9):
    m = bpy.data.materials.new('logo')
    n = N(m)
    img = bpy.data.images.load(os.path.join(TEX, 'logo.png'))
    tx = n.n('ShaderNodeTexImage')
    tx.image = img
    tx.interpolation = 'Cubic'
    tx.extension = 'CLIP'
    p = n.n('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (0.86, 0.85, 0.83, 1)
    p.inputs['Roughness'].default_value = 0.4
    p.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    p.inputs['Emission Strength'].default_value = 0.35
    tr = n.n('ShaderNodeBsdfTransparent')
    mx = n.n('ShaderNodeMixShader')
    a = n.math('MULTIPLY', tx.outputs['Alpha'], alpha)
    n.l(a, mx.inputs[0])
    n.l(tr.outputs[0], mx.inputs[1])
    n.l(p.outputs[0], mx.inputs[2])
    n.l(mx.outputs[0], n.out.inputs['Surface'])
    return m


def _obj_vec(n, scale=(1, 1, 1), loc=(0, 0, 0)):
    tc = n.n('ShaderNodeTexCoord')
    mp = n.n('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = scale
    mp.inputs['Location'].default_value = loc
    n.l(tc.outputs['Object'], mp.inputs['Vector'])
    return mp.outputs['Vector'], tc


def mat_swirl(name, base_dark, base_light, swirl_col, swirl_amt=0.42, seed=0.0, top_band=0.0,
              stretch=3.4, bottom_layer=None, rough=0.42, swirl_scale=34.0, ribbons=5, halo=None,
              frost=None, twist=70.0, spec=0.06):
    """Gefrorene Masse (Açaí o. ä.), von innen an die Becherwand gedrückt, mit weichen Swirl-Bändern."""
    m = bpy.data.materials.new(name)
    n = N(m)
    vec, tc = _obj_vec(n, scale=(swirl_scale, swirl_scale, swirl_scale / stretch), loc=(seed, seed * 0.7, seed * 1.3))
    sep = n.n('ShaderNodeSeparateXYZ')
    n.l(tc.outputs['Object'], sep.inputs[0])
    theta = n.math('ARCTAN2', sep.outputs['Y'], sep.outputs['X'])
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=4.0, Roughness=0.55, Distortion=0.6)
    n.l(vec, nz.inputs['Vector'])
    nz2 = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=2.0, Roughness=0.5)
    v2, _ = _obj_vec(n, scale=(18, 18, 9), loc=(seed * 2, 1, 0))
    n.l(v2, nz2.inputs['Vector'])
    ph = n.math('MULTIPLY_ADD', n.math('SUBTRACT', nz.outputs['Fac'], 0.5), 9.0, n.math('MULTIPLY', theta, float(ribbons)))
    ph = n.math('ADD', ph, n.math('MULTIPLY', sep.outputs['Z'], twist))
    rib = n.math('MULTIPLY_ADD', n.math('SINE', ph), 0.5, 0.5)
    zt = n.math('MULTIPLY', sep.outputs['Z'], 1.0 / CUP_H)
    fade = n.math('ADD', zt, n.math('MULTIPLY', n.math('SUBTRACT', nz2.outputs['Fac'], 0.5), 1.6))
    fade = n.math('SMOOTH_MIN', n.math('MULTIPLY', fade, 1.6), 1.0, 0.2)
    fac = n.math('MULTIPLY', rib, n.math('MAXIMUM', fade, 0.0))
    if top_band > 0:
        bandf = n.math('MAXIMUM', n.math('SUBTRACT', zt, 1.0 - top_band), 0.0)
        bandf = n.math('MULTIPLY', bandf, 1.0 / top_band)
        bandf = n.math('MULTIPLY', bandf, n.math('MULTIPLY_ADD', nz2.outputs['Fac'], 1.2, 0.2))
        fac = n.math('MAXIMUM', fac, bandf)
    # feine Störung der Kante, damit die Bänder nicht wie gemalt wirken
    ev, _ = _obj_vec(n, scale=(160, 160, 60), loc=(seed, 0, 0))
    en = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0, Roughness=0.6)
    n.l(ev, en.inputs['Vector'])
    fac = n.math('ADD', fac, n.math('MULTIPLY', n.math('SUBTRACT', en.outputs['Fac'], 0.5), 0.22))
    th = 1.0 - swirl_amt
    edge = n.ramp([(th - 0.012, (0, 0, 0)), (th + 0.012, (1, 1, 1))])
    n.l(fac, edge.inputs['Fac'])
    sw = edge.outputs['Color']
    hal = n.ramp([(th - 0.06, (0, 0, 0)), (th - 0.005, (1, 1, 1))])
    n.l(fac, hal.inputs['Fac'])
    # Grundmasse: Schlieren, Körnung, Eiskristalle
    gv, _ = _obj_vec(n, scale=(420, 420, 420))
    grain = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0, Roughness=0.7)
    n.l(gv, grain.inputs['Vector'])
    big = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0, Roughness=0.6)
    bv, _ = _obj_vec(n, scale=(50, 50, 9), loc=(seed + 3, 0, 0))
    n.l(bv, big.inputs['Vector'])
    gmix = n.math('ADD', n.math('MULTIPLY', grain.outputs['Fac'], 0.45), n.math('MULTIPLY', big.outputs['Fac'], 0.75))
    base_r = n.ramp([(0.42, base_dark), (0.78, base_light)])
    n.l(gmix, base_r.inputs['Fac'])
    col = base_r.outputs['Color']
    if frost:
        fm = n.ramp([(0.6, (0, 0, 0)), (0.7, (1, 1, 1))])
        n.l(grain.outputs['Fac'], fm.inputs['Fac'])
        col = n.mix(n.math('MULTIPLY', fm.outputs['Color'], 0.55), col, (*frost, 1))
    halo_c = halo or tuple(0.55 * a + 0.45 * b for a, b in zip(base_light, swirl_col))
    col = n.mix(n.math('MULTIPLY', hal.outputs['Color'], 0.5), col, (*halo_c, 1))
    sw_r = n.ramp([(0.3, tuple(c * 0.86 for c in swirl_col)), (0.8, swirl_col)])
    n.l(grain.outputs['Fac'], sw_r.inputs['Fac'])
    col = n.mix(sw, col, sw_r.outputs['Color'])
    # Luftbläschen an der Wand
    bub_v, _ = _obj_vec(n, scale=(700, 700, 700), loc=(seed, 2, 0))
    bub = n.n('ShaderNodeTexVoronoi')
    n.l(bub_v, bub.inputs['Vector'])
    bubm = n.math('LESS_THAN', bub.outputs['Distance'], 0.11)
    col = n.mix(n.math('MULTIPLY', bubm, 0.35), col, (0.02, 0.005, 0.02, 1))
    if bottom_layer:
        h, c1, c2 = bottom_layer
        vv, _ = _obj_vec(n, scale=(260, 260, 260))
        vor = n.n('ShaderNodeTexVoronoi')
        n.l(vv, vor.inputs['Vector'])
        gr = n.ramp([(0.0, c1), (1.0, c2)])
        n.l(vor.outputs['Distance'], gr.inputs['Fac'])
        wav = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=2.0)
        wv, _ = _obj_vec(n, scale=(70, 70, 70))
        n.l(wv, wav.inputs['Vector'])
        lim = n.math('ADD', h, n.math('MULTIPLY', n.math('SUBTRACT', wav.outputs['Fac'], 0.5), 0.008))
        bm = n.math('LESS_THAN', sep.outputs['Z'], lim)
        col = n.mix(bm, col, gr.outputs['Color'])
    # liegt direkt am Plastik an: kaum eigener Glanz (sonst grauer Schleier)
    p = principled(n, **{'Roughness': rough, 'Subsurface Weight': 0.12, 'Subsurface Scale': 0.0015,
                         'Subsurface Radius': (1.0, 0.35, 0.6), 'Specular IOR Level': spec})
    n.l(col, p.inputs['Base Color'])
    rr = n.mixf(sw, rough, rough - 0.1)
    n.l(rr, p.inputs['Roughness'])
    bump = n.n('ShaderNodeBump', Strength=0.4, Distance=0.0006)
    hb = n.math('ADD', n.math('MULTIPLY', grain.outputs['Fac'], 0.35), n.math('MULTIPLY', sw, 0.3))
    hb = n.math('ADD', hb, n.math('MULTIPLY', bubm, -0.4))
    n.l(hb, bump.inputs['Height'])
    n.l(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_sorbet_top(name, dark, light, rough=0.5):
    m = bpy.data.materials.new(name)
    n = N(m)
    gv, _ = _obj_vec(n, scale=(300, 300, 300))
    grain = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=4.0, Roughness=0.65)
    n.l(gv, grain.inputs['Vector'])
    r = n.ramp([(0.3, dark), (0.8, light)])
    n.l(grain.outputs['Fac'], r.inputs['Fac'])
    p = principled(n, **{'Roughness': rough, 'Subsurface Weight': 0.15, 'Subsurface Scale': 0.002})
    n.l(r.outputs['Color'], p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=0.8, Distance=0.0012)
    n.l(grain.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_strawberry_skin():
    m = bpy.data.materials.new('strawberry_skin')
    n = N(m)
    vec, tc = _obj_vec(n, scale=(260, 260, 260))
    vor = n.n('ShaderNodeTexVoronoi')
    n.l(vec, vor.inputs['Vector'])
    seed_mask = n.math('LESS_THAN', vor.outputs['Distance'], 0.16)
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0)
    v2, _ = _obj_vec(n, scale=(90, 90, 90))
    n.l(v2, nz.inputs['Vector'])
    red = n.ramp([(0.3, srgb('#8E0A16')), (0.75, srgb('#D21E2B'))])
    n.l(nz.outputs['Fac'], red.inputs['Fac'])
    col = n.mix(seed_mask, red.outputs['Color'], (*srgb('#E8C35A'), 1))
    p = principled(n, **{'Roughness': 0.22, 'Subsurface Weight': 0.25, 'Subsurface Scale': 0.003,
                         'Subsurface Radius': (1.0, 0.25, 0.2), 'Coat Weight': 0.35, 'Coat Roughness': 0.12})
    n.l(col, p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=0.6, Distance=0.0004)
    n.l(vor.outputs['Distance'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_image(name, file, rough=0.25, sss=0.25, sss_radius=(1, 0.4, 0.3), coat=0.25, bump=0.15):
    m = bpy.data.materials.new(name)
    n = N(m)
    tx = n.n('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(os.path.join(TEX, file))
    tx.interpolation = 'Cubic'
    tx.extension = 'EXTEND'
    p = principled(n, **{'Roughness': rough, 'Subsurface Weight': sss, 'Subsurface Scale': 0.003,
                         'Subsurface Radius': sss_radius, 'Coat Weight': coat, 'Coat Roughness': 0.1})
    n.l(tx.outputs['Color'], p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=bump, Distance=0.0004)
    n.l(tx.outputs['Color'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_simple(name, dark, light, scale=80, rough=0.4, sss=0.1, sss_radius=(1, 0.6, 0.4), bump=0.3,
               coat=0.0, detail=4.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    n = N(m)
    vec, _ = _obj_vec(n, scale=(scale, scale, scale))
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=detail, Roughness=0.6)
    n.l(vec, nz.inputs['Vector'])
    r = n.ramp([(0.3, dark), (0.75, light)])
    n.l(nz.outputs['Fac'], r.inputs['Fac'])
    p = principled(n, **{'Roughness': rough, 'Subsurface Weight': sss, 'Subsurface Scale': 0.003,
                         'Subsurface Radius': sss_radius, 'Coat Weight': coat, 'Coat Roughness': 0.15,
                         'Sheen Weight': sheen})
    n.l(r.outputs['Color'], p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=bump, Distance=0.0005)
    n.l(nz.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_granola():
    m = bpy.data.materials.new('granola')
    n = N(m)
    oi = n.n('ShaderNodeObjectInfo')
    vec, _ = _obj_vec(n, scale=(500, 500, 500))
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=5.0, Roughness=0.7)
    n.l(vec, nz.inputs['Vector'])
    attr = n.n('ShaderNodeAttribute')
    attr.attribute_name = 'piece'
    f = n.math('ADD', n.math('MULTIPLY', attr.outputs['Fac'], 0.75), n.math('MULTIPLY', nz.outputs['Fac'], 0.35))
    r = n.ramp([(0.05, srgb('#6E3D17')), (0.35, srgb('#A8692B')), (0.65, srgb('#CF9A4E')), (0.95, srgb('#E9CC8E'))])
    n.l(f, r.inputs['Fac'])
    p = principled(n, **{'Roughness': 0.5, 'Subsurface Weight': 0.15, 'Subsurface Scale': 0.0015,
                         'Subsurface Radius': (1, 0.6, 0.3), 'Coat Weight': 0.25, 'Coat Roughness': 0.25})
    n.l(r.outputs['Color'], p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=0.6, Distance=0.0003)
    n.l(nz.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_blueberry():
    m = bpy.data.materials.new('blueberry')
    n = N(m)
    vec, _ = _obj_vec(n, scale=(220, 220, 220))
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=4.0)
    n.l(vec, nz.inputs['Vector'])
    r = n.ramp([(0.25, srgb('#1B1F3E')), (0.6, srgb('#323C6B')), (0.9, srgb('#6C7AA6'))])
    n.l(nz.outputs['Fac'], r.inputs['Fac'])
    p = principled(n, **{'Roughness': 0.55, 'Sheen Weight': 0.6, 'Sheen Roughness': 0.4,
                         'Sheen Tint': (0.8, 0.85, 1.0, 1), 'Subsurface Weight': 0.1, 'Subsurface Scale': 0.002})
    n.l(r.outputs['Color'], p.inputs['Base Color'])
    b = n.n('ShaderNodeBump', Strength=0.2, Distance=0.0003)
    n.l(nz.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


# ---------------------------------------------------------------- Geometrie

def lathe(name, prof, seg=160, cap_bottom=False, cap_top=False, smooth=True):
    """prof: Liste (r, z) von unten nach oben. Erzeugt Rotationskörper um die Z-Achse."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            try:
                bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                pass
    if cap_bottom:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return bpy.data.objects.new(name, me)


def make_cup():
    """Klarer PET-Becher mit gerolltem Rand und Stapelring."""
    prof = []
    # Boden: leicht nach innen gewölbt
    for i in range(10):
        t = i / 9
        prof.append((0.012 + t * (CUP_RB - 0.0035 - 0.012), 0.0035 - 0.0015 * (1 - t) ** 2))
    prof.insert(0, (0.0, 0.0022))
    # Bodenkante (gerundet)
    for i in range(7):
        a = math.pi / 2 * (i / 6)
        prof.append((CUP_RB - 0.0035 + 0.0035 * math.sin(a), 0.0035 - 0.0035 * math.cos(a) + 0.0002))
    # Wand mit Stapelring knapp unter dem Rand
    for i in range(1, 41):
        z = 0.0037 + (CUP_H - 0.006 - 0.0037) * i / 40
        r = cup_r(z)
        zr = CUP_H - 0.0135
        r += 0.0007 * math.exp(-((z - zr) / 0.0012) ** 2)
        prof.append((r, z))
    # gerollter Rand (nach außen)
    cx, cz, rr = CUP_RT + 0.0011, CUP_H - 0.0008, 0.0012
    for i in range(14):
        a = math.pi + math.pi * 1.6 * i / 13   # von innen über oben nach außen
        prof.append((cx + rr * math.cos(a), cz - rr * math.sin(a) * -1))
    o = lathe('cup', prof, seg=180)
    sol = o.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = WALL
    sol.offset = -1
    sol.use_even_offset = True
    o.data.materials.append(mat_plastic())
    o.visible_shadow = False   # Licht soll die Füllung durch das Plastik erreichen
    return link(o)


def make_fill(name, mat, z0=0.0028, z1=CUP_H - 0.0015, inset=0.00016, seg=160, top_cap=True):
    """Füllung, die innen an der Becherwand anliegt."""
    prof = [(0.0, z0)]
    steps = 36
    for i in range(steps + 1):
        z = z0 + (z1 - z0) * i / steps
        prof.append((cup_r(z) - WALL - inset, z))
    if top_cap:
        prof.append((0.0, z1))
    o = lathe(name, prof, seg=seg)
    o.data.materials.append(mat)
    return link(o)


def make_mound(name, mat, z_base, height, radius, seed=1, lumps=1.0):
    """Gewölbte Oberseite (z. B. Açaí über dem Rand) mit Kugel-Löffel-Struktur."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        if z < 0:
            z = z * 0.05
        p = Vector((x * radius, y * radius, z * height))
        d = noise.noise(Vector((x * 2.2 + seed, y * 2.2, z * 2.2))) * 0.18 * lumps
        d2 = noise.noise(Vector((x * 6 + seed, y * 6, z * 6))) * 0.05 * lumps
        k = max(0.0, z)
        p.z += (d + d2) * height * (0.4 + k)
        p.x *= 1 + (d * 0.12) * k
        p.y *= 1 + (d * 0.12) * k
        p.z += z_base
        v.co = p
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat)
    return link(o)


def make_logo_decal(z_center=0.071, width=0.060, name='logo', angle_offset=0.0):
    """Aufdruck „THISISYOUR karma“ als dünne Folie direkt auf der Außenwand."""
    import bpy as _b
    img = _b.data.images.load(os.path.join(TEX, 'logo.png'), check_existing=True)
    aspect = img.size[1] / img.size[0]
    height = width * aspect
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap')
    nu, nv = 64, 12
    r_mid = cup_r(z_center)
    span = width / r_mid
    grid = []
    for j in range(nv + 1):
        row = []
        z = z_center - height / 2 + height * j / nv
        r = cup_r(z) + 0.00006
        for i in range(nu + 1):
            a = -math.pi / 2 - span / 2 + span * i / nu + angle_offset
            row.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            for loop, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                loop[uv].uv = (ii / nu, jj / nv)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat_logo())
    return link(o)


def strawberry_halfw(v):
    v = max(0.0, min(1.0, v))
    if v < 0.7:
        return 0.46 * (v / 0.7) ** 0.62
    return 0.46 * math.sqrt(max(0.0, 1 - ((v - 0.7) / 0.3) ** 2))


_mat_cache = {}


def cached(key, fn):
    if key not in _mat_cache:
        _mat_cache[key] = fn()
    return _mat_cache[key]


def make_strawberry_half(name, H=0.04, seed=0):
    """Längs halbierte Erdbeere; Schnittfläche zeigt in -Y (zur Kamera)."""
    seg = 96
    prof = []
    for i in range(41):
        v = i / 40
        prof.append((max(strawberry_halfw(v) * H, 1e-5), v * H))
    bm = bmesh.new()
    rings = []
    rnd = random.Random(seed)
    for (r, z) in prof:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            # leichte Unregelmäßigkeit
            wob = 1 + 0.035 * noise.noise(Vector((math.cos(a) * 2 + seed, math.sin(a) * 2, z / H * 3)))
            ring.append(bm.verts.new((r * wob * math.cos(a), r * wob * 0.92 * math.sin(a), z)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            try:
                bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
            except ValueError:
                pass
    bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0),
                                 plane_no=(0, -1, 0), clear_outer=True)
    edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    fill = bmesh.ops.edgeloop_fill(bm, edges=edges) if edges else {'faces': []}
    if not fill['faces']:
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        cut = abs(f.normal.y) > 0.98 and all(abs(v.co.y) < 1e-5 for v in f.verts)
        f.material_index = 1 if cut else 0
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x / H + 0.5, loop.vert.co.z / H)
    # Schnittfläche triangulieren für saubere Schattierung
    cutf = [f for f in bm.faces if f.material_index == 1]
    bmesh.ops.triangulate(bm, faces=cutf)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = p.material_index == 0
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('sskin', mat_strawberry_skin))
    o.data.materials.append(cached('scut', lambda: mat_image('strawberry_cut', 'strawberry_cut.png', rough=0.18,
                                                              sss=0.3, sss_radius=(1, 0.3, 0.25), coat=0.4, bump=0.25)))
    return link(o)


def make_banana_slice(name, R=0.0165, T=0.0072, seed=0):
    bm = bmesh.new()
    seg = 72
    uv = bm.loops.layers.uv.new('UVMap')
    top, bot = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        w = 1 + 0.03 * noise.noise(Vector((math.cos(a) * 1.5 + seed, math.sin(a) * 1.5, 0)))
        x, z = R * w * math.cos(a), R * w * math.sin(a)
        top.append(bm.verts.new((x, -T / 2, z)))
        bot.append(bm.verts.new((x, T / 2, z)))
    ft = bm.faces.new(list(reversed(top)))
    fb = bm.faces.new(bot)
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((top[i], top[j], bot[j], bot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x / (2.1 * R) + 0.5, loop.vert.co.z / (2.1 * R) + 0.5)
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if (e in ft.edges or e in fb.edges)], offset=0.0011,
                    segments=4, affect='EDGES', profile=0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('banana', lambda: mat_image('banana', 'banana_face.png', rough=0.32, sss=0.45,
                                                               sss_radius=(1, 0.85, 0.5), coat=0.2, bump=0.1)))
    return link(o)


def make_granola_cluster(name, size=0.011, pieces=42, seed=0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    lay = bm.verts.layers.float.new('piece')
    for k in range(pieces):
        sub = bmesh.new()
        bmesh.ops.create_icosphere(sub, subdivisions=2, radius=1.0)
        kind = rnd.random()
        if kind < 0.6:      # Haferflocke
            sc = Vector((rnd.uniform(0.003, 0.0045), rnd.uniform(0.0025, 0.0038), rnd.uniform(0.0008, 0.0012)))
        else:               # Nuss-/Knusperstück
            s = rnd.uniform(0.0018, 0.0032)
            sc = Vector((s, s * rnd.uniform(0.7, 1.0), s * rnd.uniform(0.6, 0.9)))
        rot = Euler((rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3))).to_matrix()
        # Position in einem abgeflachten Ellipsoid
        while True:
            p = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
            if p.length <= 1:
                break
        pos = Vector((p.x * size, p.y * size * 0.8, p.z * size * 0.6))
        pv = rnd.random()
        for v in sub.verts:
            c = v.co.copy()
            c += c * 0.25 * noise.noise(c * 3 + Vector((k, k * 0.3, 0)))
            c = Vector((c.x * sc.x, c.y * sc.y, c.z * sc.z))
            v.co = rot @ c + pos
        sub_me = bpy.data.meshes.new('tmp')
        sub.to_mesh(sub_me)
        sub.free()
        offset = len(bm.verts)
        vmap = [bm.verts.new(v.co) for v in sub_me.vertices]
        for v in vmap:
            v[lay] = pv
        for poly in sub_me.polygons:
            try:
                bm.faces.new([vmap[i] for i in poly.vertices])
            except ValueError:
                pass
        bpy.data.meshes.remove(sub_me)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    # Float-Layer als Attribut für den Shader
    attr = me.attributes.get('piece')
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('granola', mat_granola))
    return link(o)


def make_blueberry(name, R=0.0068, seed=0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    for v in bm.verts:
        c = v.co.copy()
        c.z *= 0.86
        c *= 1 + 0.03 * noise.noise(c * 2.5 + Vector((seed, 0, 0)))
        # Krönchen oben
        if c.z > 0.8:
            a = math.atan2(c.y, c.x)
            c.z -= 0.12 * (c.z - 0.8) / 0.06 * (0.6 + 0.4 * math.cos(5 * a))
        v.co = c * R
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('blueberry', mat_blueberry))
    return link(o)


def place(o, loc, rot=(0, 0, 0), scale=1.0):
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    o.scale = (scale, scale, scale)
    return o


# ================================================================ weitere Zutaten

def mat_raspberry():
    m = bpy.data.materials.new('raspberry')
    n = N(m)
    vec, _ = _obj_vec(n, scale=(400, 400, 400))
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0)
    n.l(vec, nz.inputs['Vector'])
    r = n.ramp([(0.3, srgb('#7E0A26')), (0.75, srgb('#C8173E'))])
    n.l(nz.outputs['Fac'], r.inputs['Fac'])
    p = principled(n, **{'Roughness': 0.38, 'Subsurface Weight': 0.45, 'Subsurface Scale': 0.003,
                         'Subsurface Radius': (1.0, 0.2, 0.25), 'Sheen Weight': 0.35, 'Sheen Roughness': 0.3,
                         'Coat Weight': 0.15})
    n.l(r.outputs['Color'], p.inputs['Base Color'])
    return m


def make_raspberry(name, R=0.0085, seed=0):
    """Himbeere aus einzelnen Steinfrüchtchen, Öffnung nach unten."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    rows = 7
    for i in range(rows):
        v = i / (rows - 1)            # 0 = Spitze oben, 1 = Öffnung
        z = R * (1.15 - 1.5 * v)
        rr = R * (0.35 + 0.65 * math.sin(math.pi * (0.25 + 0.6 * v)))
        cnt = max(5, int(6 + 8 * math.sin(math.pi * (0.2 + 0.6 * v))))
        for k in range(cnt):
            a = 2 * math.pi * (k + 0.5 * (i % 2)) / cnt + rnd.uniform(-0.08, 0.08)
            dr = R * 0.24 * rnd.uniform(0.9, 1.1)
            sub = bmesh.new()
            bmesh.ops.create_icosphere(sub, subdivisions=2, radius=dr)
            for vv in sub.verts:
                vv.co += Vector((rr * math.cos(a), rr * math.sin(a), z))
            tmp = bpy.data.meshes.new('t')
            sub.to_mesh(tmp)
            sub.free()
            vm = [bm.verts.new(x.co) for x in tmp.vertices]
            for poly in tmp.polygons:
                bm.faces.new([vm[j] for j in poly.vertices])
            bpy.data.meshes.remove(tmp)
    # Kern, damit keine Lücken durchscheinen
    core = bmesh.new()
    bmesh.ops.create_uvsphere(core, u_segments=24, v_segments=12, radius=R * 0.78)
    for vv in core.verts:
        vv.co.z = vv.co.z * 1.25 + R * 0.05
    tmp = bpy.data.meshes.new('t')
    core.to_mesh(tmp)
    core.free()
    vm = [bm.verts.new(x.co) for x in tmp.vertices]
    for poly in tmp.polygons:
        bm.faces.new([vm[j] for j in poly.vertices])
    bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('raspberry', mat_raspberry))
    return link(o)


def _rounded_box(bm, sx, sy, sz, bevel, seed=0, wob=0.08):
    res = bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=4, affect='EDGES', profile=0.5)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts:
        c = v.co
        v.co = c + c.normalized() * wob * min(sx, sy, sz) * noise.noise(c * (6 / max(sx, sy, sz)) + Vector((seed, 0, 0)))


def make_mango_cube(name, s=0.0115, seed=0):
    bm = bmesh.new()
    rnd = random.Random(seed)
    _rounded_box(bm, s * rnd.uniform(0.9, 1.1), s * rnd.uniform(0.85, 1.05), s * rnd.uniform(0.8, 1.0), s * 0.16, seed)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('mango', lambda: mat_simple('mango', srgb('#E7861A'), srgb('#FFB43A'), scale=140,
                                                               rough=0.25, sss=0.5, sss_radius=(1, 0.55, 0.15),
                                                               bump=0.25, coat=0.3)))
    return link(o)


def make_pineapple_chunk(name, s=0.013, seed=0):
    bm = bmesh.new()
    # Keil: Dreiecksprisma
    pts = [(-s * 0.55, -s * 0.4), (s * 0.55, -s * 0.4), (0.0, s * 0.6)]
    vs = []
    for (x, y) in pts:
        vs.append(bm.verts.new((x, y, -s * 0.45)))
    for (x, y) in pts:
        vs.append(bm.verts.new((x, y, s * 0.45)))
    bm.faces.new((vs[0], vs[2], vs[1]))
    bm.faces.new((vs[3], vs[4], vs[5]))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((vs[i], vs[j], vs[j + 3], vs[i + 3]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=s * 0.1, segments=3, affect='EDGES', profile=0.5)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    for v in bm.verts:
        c = v.co
        v.co = c + c.normalized() * 0.06 * s * noise.noise(c * (5 / s) + Vector((seed, 0, 0)))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)

    def mk():
        m = bpy.data.materials.new('pineapple')
        n = N(m)
        vec, _ = _obj_vec(n, scale=(60, 60, 600))
        wv = n.n('ShaderNodeTexWave', Scale=1.0, Distortion=4.0, Detail=3.0)
        wv.wave_type = 'RINGS'
        n.l(vec, wv.inputs['Vector'])
        r = n.ramp([(0.2, srgb('#E9B52A')), (0.8, srgb('#FBDB6A'))])
        n.l(wv.outputs['Fac'], r.inputs['Fac'])
        p = principled(n, **{'Roughness': 0.22, 'Subsurface Weight': 0.5, 'Subsurface Scale': 0.003,
                             'Subsurface Radius': (1, 0.85, 0.3), 'Coat Weight': 0.35})
        n.l(r.outputs['Color'], p.inputs['Base Color'])
        b = n.n('ShaderNodeBump', Strength=0.35, Distance=0.0004)
        n.l(wv.outputs['Fac'], b.inputs['Height'])
        n.l(b.outputs['Normal'], p.inputs['Normal'])
        return m
    o.data.materials.append(cached('pineapple', mk))
    return link(o)


def make_coconut_flake(name, L=0.012, seed=0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    nu, nv = 10, 4
    W = L * rnd.uniform(0.35, 0.5)
    T = 0.0007
    grid = {}
    for side in (0, 1):
        for i in range(nu + 1):
            for j in range(nv + 1):
                u = i / nu - 0.5
                v = j / nv - 0.5
                x = u * L
                y = v * W * (1 - 0.6 * (2 * abs(u)) ** 2)
                z = 0.25 * L * (u * u) * 2 + (T if side else 0)
                grid[(side, i, j)] = bm.verts.new((x, y, z))
    for side in (0, 1):
        for i in range(nu):
            for j in range(nv):
                q = [grid[(side, i, j)], grid[(side, i + 1, j)], grid[(side, i + 1, j + 1)], grid[(side, i, j + 1)]]
                bm.faces.new(q if side else list(reversed(q)))
    for i in range(nu):
        for j in (0, nv):
            a, b = grid[(0, i, j)], grid[(0, i + 1, j)]
            c, d = grid[(1, i + 1, j)], grid[(1, i, j)]
            bm.faces.new((a, b, c, d))
    for j in range(nv):
        for i in (0, nu):
            a, b = grid[(0, i, j)], grid[(0, i, j + 1)]
            c, d = grid[(1, i, j + 1)], grid[(1, i, j)]
            bm.faces.new((a, b, c, d))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('coconut', lambda: mat_simple('coconut', srgb('#E9E2D3'), srgb('#FFFDF8'), scale=300,
                                                                 rough=0.5, sss=0.3, sss_radius=(1, 0.95, 0.9), bump=0.3)))
    return link(o)


def mat_pb():
    return cached('pb', lambda: mat_simple('peanutbutter', srgb('#A8682C'), srgb('#C98B45'), scale=60, rough=0.22,
                                           sss=0.35, sss_radius=(1, 0.6, 0.3), bump=0.08, coat=0.5, detail=2.0))


def make_pb_dollop(name, R=0.016, seed=0):
    """Erdnussbutter-Klecks: gedrehter Softeis-ähnlicher Haufen aus Metaballs."""
    mb = bpy.data.metaballs.new(name + '_mb')
    mb.resolution = 0.0012
    mb.render_resolution = 0.0008
    mb.threshold = 0.6
    rnd = random.Random(seed)
    turns = 2.2
    steps = 34
    for i in range(steps):
        t = i / (steps - 1)
        a = turns * 2 * math.pi * t
        rr = R * (1 - 0.85 * t)
        el = mb.elements.new()
        el.co = (rr * 0.75 * math.cos(a), rr * 0.75 * math.sin(a), R * 0.9 * t)
        el.radius = R * (0.62 - 0.32 * t) * rnd.uniform(0.95, 1.05)
    ob = bpy.data.objects.new(name + '_tmp', mb)
    link(ob)
    bpy.context.view_layer.objects.active = ob
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    o = bpy.data.objects.new(name, me)
    for p in me.polygons:
        p.use_smooth = True
    o.data.materials.append(mat_pb())
    return link(o)


def make_drip(name, angle, z_top, length, r0=0.0032, seed=0, bulb=1.35, mat=None):
    """Tropfen, der außen am Becher herunterläuft (folgt der Kegelwand)."""
    bm = bmesh.new()
    seg = 20
    steps = max(4, int(length / 0.0015))
    rings = []
    for i in range(steps + 1):
        t = i / steps
        z = z_top - length * t
        rr = r0 * (1 - 0.35 * t) * (1 + 0.12 * noise.noise(Vector((seed, t * 4, 0))))
        if t > 0.82:
            k = (t - 0.82) / 0.18
            rr *= 1 + (bulb - 1) * math.sin(k * math.pi * 0.85)
        wall = cup_r(z) + 0.0002
        a = angle + 0.04 * noise.noise(Vector((seed * 3, t * 2, 1)))
        ctr = Vector((math.cos(a) * wall, math.sin(a) * wall, z))
        nrm = Vector((math.cos(a), math.sin(a), 0))
        tan = Vector((-math.sin(a), math.cos(a), 0))
        ring = []
        for k2 in range(seg):
            b = 2 * math.pi * k2 / seg
            off = tan * math.cos(b) * rr + nrm * (math.sin(b) * rr * 0.55 + rr * 0.35)
            ring.append(bm.verts.new(ctr + off))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k2 in range(seg):
            j = (k2 + 1) % seg
            bm.faces.new((rings[i][k2], rings[i][j], rings[i + 1][j], rings[i + 1][k2]))
    # Kappe unten
    tip = bm.verts.new(sum((v.co for v in rings[-1]), Vector()) / seg - Vector((0, 0, r0 * 0.5)))
    for k2 in range(seg):
        j = (k2 + 1) % seg
        bm.faces.new((rings[-1][k2], rings[-1][j], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    sub = o.modifiers.new('sub', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    o.data.materials.append(mat or mat_pb())
    return link(o)


def make_rim_blob(name, angle0, angle1, z, thick=0.004, mat=None):
    """Erdnussbutter, die über den Rand quillt (Wulst entlang des Randes)."""
    bm = bmesh.new()
    seg = 16
    steps = 30
    rings = []
    for i in range(steps + 1):
        t = i / steps
        a = angle0 + (angle1 - angle0) * t
        rr = thick * math.sin(math.pi * t) ** 0.6 + 0.0004
        wall = CUP_RT + 0.0012
        ctr = Vector((math.cos(a) * wall, math.sin(a) * wall, z))
        nrm = Vector((math.cos(a), math.sin(a), 0))
        ring = []
        for k in range(seg):
            b = 2 * math.pi * k / seg
            off = nrm * math.cos(b) * rr * 0.8 + Vector((0, 0, 1)) * math.sin(b) * rr * 0.7
            ring.append(bm.verts.new(ctr + off))
        rings.append(ring)
    for i in range(steps):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat or mat_pb())
    return link(o)


def mat_layers(name, layers, seed=0.0, spec=0.06):
    """Geschichtete Füllung: layers = [(z_oben, art, farben...)] von unten nach oben.
    art: 'acai' (dunkel, Körnung), 'smooth' (glatt, z. B. Erdnussbutter), 'chia' (Pudding mit Samen),
         'liquid' (Milch/Matcha/Püree)."""
    m = bpy.data.materials.new(name)
    n = N(m)
    vec, tc = _obj_vec(n)
    sep = n.n('ShaderNodeSeparateXYZ')
    n.l(tc.outputs['Object'], sep.inputs[0])
    wv, _ = _obj_vec(n, scale=(70, 70, 70), loc=(seed, 0, 0))
    wav = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0, Roughness=0.55)
    n.l(wv, wav.inputs['Vector'])
    gv, _ = _obj_vec(n, scale=(420, 420, 420), loc=(seed, 1, 0))
    grain = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0, Roughness=0.7)
    n.l(gv, grain.inputs['Vector'])
    sv, _ = _obj_vec(n, scale=(900, 900, 900), loc=(seed, 2, 0))
    seeds = n.n('ShaderNodeTexVoronoi')
    n.l(sv, seeds.inputs['Vector'])
    zz = n.math('ADD', sep.outputs['Z'], n.math('MULTIPLY', n.math('SUBTRACT', wav.outputs['Fac'], 0.5), 0.012))
    col = None
    rough = None
    sss = None
    for (ztop, kind, c1, c2, r_, s_, soft) in layers:
        if kind == 'chia':
            cm = n.ramp([(0.3, c1), (0.8, c2)])
            n.l(grain.outputs['Fac'], cm.inputs['Fac'])
            dots = n.math('LESS_THAN', seeds.outputs['Distance'], 0.22)
            c = n.mix(dots, cm.outputs['Color'], (*srgb('#151313'), 1))
        else:
            cm = n.ramp([(0.3, c1), (0.8, c2)])
            n.l(grain.outputs['Fac'] if kind != 'smooth' else wav.outputs['Fac'], cm.inputs['Fac'])
            c = cm.outputs['Color']
        if col is None:
            col, rough, sss = c, r_, s_
        else:
            mk = n.ramp([(0.0, (0, 0, 0)), (1.0, (1, 1, 1))])
            # weicher Übergang um die Grenze
            lo = prev_top - soft
            hi = prev_top + soft
            mk.color_ramp.elements[0].position = 0.0
            fac = n.math('DIVIDE', n.math('SUBTRACT', zz, lo), hi - lo)
            fac = n.math('MINIMUM', n.math('MAXIMUM', fac, 0.0), 1.0)
            col = n.mix(fac, col, c)
            rough = n.mixf(fac, rough, r_)
            sss = n.mixf(fac, sss, s_)
        prev_top = ztop
    p = principled(n, **{'Specular IOR Level': spec, 'Subsurface Scale': 0.003, 'Subsurface Radius': (1, 0.7, 0.5)})
    n.l(col, p.inputs['Base Color'])
    n.l(rough if not isinstance(rough, float) else n.math('ADD', rough, 0.0), p.inputs['Roughness'])
    n.l(sss if not isinstance(sss, float) else n.math('ADD', sss, 0.0), p.inputs['Subsurface Weight'])
    b = n.n('ShaderNodeBump', Strength=0.25, Distance=0.0005)
    n.l(grain.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_ice():
    m = bpy.data.materials.new('ice')
    n = N(m)
    vec, _ = _obj_vec(n, scale=(150, 150, 150))
    nz = n.n('ShaderNodeTexNoise', Scale=1.0, Detail=3.0)
    n.l(vec, nz.inputs['Vector'])
    p = principled(n, **{'Base Color': (0.97, 0.99, 1.0, 1), 'Roughness': 0.06, 'IOR': 1.31,
                         'Transmission Weight': 1.0})
    rr = n.ramp([(0.4, (0.03, 0.03, 0.03)), (0.8, (0.18, 0.18, 0.18))])
    n.l(nz.outputs['Fac'], rr.inputs['Fac'])
    n.l(rr.outputs['Color'], p.inputs['Roughness'])
    b = n.n('ShaderNodeBump', Strength=0.25, Distance=0.0006)
    n.l(nz.outputs['Fac'], b.inputs['Height'])
    n.l(b.outputs['Normal'], p.inputs['Normal'])
    return m


def make_ice(name, s=0.021, seed=0):
    bm = bmesh.new()
    rnd = random.Random(seed)
    _rounded_box(bm, s * rnd.uniform(0.9, 1.05), s * rnd.uniform(0.9, 1.05), s * rnd.uniform(0.85, 1.0), s * 0.18, seed,
                 wob=0.05)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('ice', mat_ice))
    o.visible_shadow = False
    return link(o)


def make_cacao_nibs(name, count=26, spread=0.02, seed=0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    for k in range(count):
        sub = bmesh.new()
        bmesh.ops.create_icosphere(sub, subdivisions=1, radius=1.0)
        s = rnd.uniform(0.0012, 0.0022)
        rot = Euler((rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6))).to_matrix()
        pos = Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread) * 0.8, rnd.uniform(0, 0.004)))
        for v in sub.verts:
            c = Vector((v.co.x * s, v.co.y * s * 0.8, v.co.z * s * 0.55))
            v.co = rot @ c + pos
        tmp = bpy.data.meshes.new('t')
        sub.to_mesh(tmp)
        sub.free()
        vm = [bm.verts.new(x.co) for x in tmp.vertices]
        for poly in tmp.polygons:
            bm.faces.new([vm[j] for j in poly.vertices])
        bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(cached('cacao', lambda: mat_simple('cacao', srgb('#2B160C'), srgb('#5A3420'), scale=400,
                                                               rough=0.45, bump=0.5)))
    return link(o)
