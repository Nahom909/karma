"""Berechnet Bildkoordinaten (0..1) wichtiger Punkte für die Beschriftungen (z. B. Matcha-Schichten)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import klib as K
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import matcha as M
K.reset()
cam = K.camera()
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 1100, 1500
bpy.context.view_layer.update()
def proj(p):
    v = world_to_camera_view(sc, cam, Vector(p))
    return round(v.x, 4), round(1 - v.y, 4)
out = {}
zs = {'puree': (0.003 + M.Z_PUREE) / 2, 'milk': (M.Z_PUREE + M.Z_MILK) / 2, 'matcha': (M.Z_MILK + M.Z_TOP) / 2}
for k, z in zs.items():
    xr, yr = proj((K.cup_r(z), 0, z))
    xc, yc = proj((0, -K.cup_r(z), z))
    out[k] = {'x': xr, 'y': yc}
out['rim'] = {'y': proj((0, -K.CUP_RT, K.CUP_H))[1]}
out['bottom'] = {'y': proj((0, -K.CUP_RB, 0))[1]}
out['rim_left'] = {'x': proj((-K.CUP_RT, 0, K.CUP_H))[0]}
out['rim_right'] = {'x': proj((K.CUP_RT, 0, K.CUP_H))[0]}
json.dump(out, open(os.path.join(K.WORK, 'points.json'), 'w'), indent=1)
print(json.dumps(out))
