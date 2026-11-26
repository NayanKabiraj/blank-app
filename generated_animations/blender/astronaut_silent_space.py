"""Blender sample, "space storytelling" style (3D cartoon character, Pixar-like): an astronaut explains why space is silent. 45 s, vertical, every frame designed in code.

    python astronaut_silent_space.py OUT_DIR [--scale 0.375] [--spp 12] [--stills 60,180]   # full render, or only the listed frames
Rendered at 12 fps (video = frames shown on twos, 24 fps) in low resolution so a 45 s Short costs ~540 Cycles frames. Silent; narration would be added by the pipeline.
"""
import math
import random
import sys

import bpy

out = sys.argv[1]
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
scale, spp, stills = arg("--scale", 0.375), arg("--spp", 12), arg("--stills", "")
FPS, DUR = 12, 45
N = FPS * DUR
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples, sc.cycles.use_denoising, sc.cycles.device = spp, True, "CPU"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, int(scale * 100)
sc.render.fps, sc.frame_start, sc.frame_end = FPS, 1, N
sc.render.image_settings.file_format, sc.render.filepath = "PNG", out + "/f_"
sc.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
nt = world.node_tree; bg = nt.nodes["Background"]
tc, ramp = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeValToRGB")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
ramp.color_ramp.elements[0].color = (0.30, 0.10, 0.38, 1); ramp.color_ramp.elements[1].color = (0.01, 0.03, 0.12, 1)
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.45, 0.85
bg.inputs[1].default_value = 1.0


def mat(name, col, rough=0.5, emit=None, es=1.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col; b.inputs["Roughness"].default_value = rough; b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = emit; b.inputs["Emission Strength"].default_value = es
    return m


def obj(kind, mt, loc=(0, 0, 0), parent=None, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(location=loc, **kw)
    o = bpy.context.object
    if kind in ("uv_sphere", "ico_sphere", "cylinder"):
        bpy.ops.object.shade_smooth()
    o.data.materials.append(mt)
    if parent:
        o.parent = parent
    return o


def empty(loc, parent=None):
    bpy.ops.object.empty_add(location=loc); e = bpy.context.object
    if parent:
        e.parent = parent
    return e


def key(o, path, f):
    o.keyframe_insert(path, frame=f)


# ---- planet ground (pink/violet noise), rocks, sky bodies, stars
gm = bpy.data.materials.new("ground"); gm.use_nodes = True
g = gm.node_tree; nz = g.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
rr = g.nodes.new("ShaderNodeValToRGB"); rr.color_ramp.elements[0].color = (0.55, 0.22, 0.45, 1); rr.color_ramp.elements[1].color = (0.9, 0.5, 0.6, 1)
g.links.new(nz.outputs["Fac"], rr.inputs["Fac"]); g.links.new(rr.outputs["Color"], g.nodes["Principled BSDF"].inputs["Base Color"]); g.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
tcg = g.nodes.new("ShaderNodeTexCoord"); g.links.new(tcg.outputs["Object"], nz.inputs["Vector"])
obj("uv_sphere", gm, (0, 0, -300), radius=300, segments=128, ring_count=64)
rock = mat("rock", (0.35, 0.22, 0.38, 1), 0.9)
for _ in range(40):
    r = obj("ico_sphere", rock, (random.uniform(-8, 40), random.uniform(-6, 14), 0), radius=random.uniform(0.12, 0.5), subdivisions=2)
    r.scale = (1, random.uniform(0.7, 1.2), random.uniform(0.4, 0.7))
pm = mat("planet", (0.95, 0.7, 0.4, 1), 0.7, emit=(0.9, 0.55, 0.25, 1), es=0.35)
obj("uv_sphere", pm, (-30, 95, 38), radius=15, segments=48, ring_count=24)
ring = obj("torus", mat("pring", (0.95, 0.8, 0.6, 1), 0.7, emit=(0.8, 0.6, 0.4, 1), es=0.3), (-30, 95, 38), major_radius=24, minor_radius=1.3, major_segments=96, minor_segments=8)
ring.scale = (1, 1, 0.08); ring.rotation_euler = (math.radians(70), math.radians(12), 0)
obj("uv_sphere", mat("moon2", (0.6, 0.65, 0.8, 1), 0.8, emit=(0.4, 0.5, 0.8, 1), es=0.4), (60, 90, 22), radius=6, segments=32, ring_count=16)
star = mat("star", (1, 1, 1, 1), emit=(1, 1, 0.9, 1), es=5)
for _ in range(120):
    a, e = random.uniform(0, math.tau), random.uniform(0.15, 1.2)
    obj("ico_sphere", star, (150 * math.cos(a), 150 * abs(math.sin(a)) + 20, 150 * math.sin(e) * 0.8 + 8), radius=random.uniform(0.2, 0.6), subdivisions=1)

# ---- lights
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), math.radians(10), math.radians(-35))
rim = bpy.data.lights.new("rim", "AREA"); rim.energy = 2200; rim.color = (0.6, 0.55, 1); rim.size = 8
ro = bpy.data.objects.new("rim", rim); sc.collection.objects.link(ro); ro.location = (20, 10, 7); ro.rotation_euler = (math.radians(70), 0, math.radians(160))

# ---- ship + air dome (centre x=16, radius 6)
DX, DR = 16.0, 6.0
hull = mat("hull", (0.9, 0.9, 0.95, 1), 0.4); red = mat("red", (0.85, 0.15, 0.15, 1), 0.5)
obj("cylinder", hull, (DX, 0, 1.0), radius=0.9, depth=2.0)
obj("cone", red, (DX, 0, 2.7), radius1=0.9, radius2=0.0, depth=1.4)
for sx in (-1, 1):
    f = obj("cube", red, (DX, sx * 1.05, 0.55), size=1); f.scale = (0.12, 0.35, 1.1); f.rotation_euler = (math.radians(sx * -20), 0, 0)
dome = obj("uv_sphere", mat("dome", (0.5, 0.75, 1, 1), 0.1, emit=(0.4, 0.7, 1, 1), es=0.04, alpha=0.07), (DX, 0, 0), radius=DR, segments=48, ring_count=24)

edge = obj("torus", mat("edge", (0.5, 0.8, 1, 1), emit=(0.5, 0.8, 1, 1), es=1.5), (DX, 0, 0), major_radius=DR, minor_radius=0.03, major_segments=96, minor_segments=6)
edge.rotation_euler = (math.radians(90), 0, 0)

# ---- astronaut rig (faces +X, side-on to camera)
white, glove, visor = mat("suit", (0.96, 0.96, 0.98, 1), 0.45), mat("glove", (0.85, 0.12, 0.2, 1), 0.5), mat("visor", (0.02, 0.05, 0.12, 1), 0.08)
root = empty((0, 0, 0))
torso = obj("uv_sphere", white, (0, 0, 1.15), parent=root, radius=0.5); torso.scale = (0.8, 0.75, 1.0)
head = obj("uv_sphere", white, (0.05, 0, 1.9), parent=root, radius=0.4)
vis = obj("uv_sphere", visor, (0.24, 0, 1.9), parent=root, radius=0.3); vis.scale = (0.75, 1.0, 0.85)
eyes = []
for sy in (-1, 1):
    e = obj("uv_sphere", mat("eye", (1, 1, 1, 1), emit=(1, 1, 1, 1), es=2), (0.41, sy * 0.1, 1.95), parent=root, radius=0.055)
    p = obj("uv_sphere", mat("pup", (0, 0, 0, 1)), (0.455, sy * 0.1, 1.95), parent=root, radius=0.028)
    eyes.append((e, p))
obj("cube", mat("pack", (0.7, 0.72, 0.8, 1), 0.5), (-0.42, 0, 1.25), parent=root, size=1).scale = (0.2, 0.34, 0.38)
legs, arms = [], []
for sy in (-1, 1):
    hp = empty((0, sy * 0.17, 0.78), root)
    obj("cylinder", white, (0, 0, -0.3), parent=hp, radius=0.13, depth=0.6)
    obj("uv_sphere", glove, (0.05, 0, -0.62), parent=hp, radius=0.16).scale = (1.4, 1, 0.8)
    legs.append(hp)
    sp = empty((0, sy * 0.46, 1.42), root)
    obj("cylinder", white, (0, 0, -0.28), parent=sp, radius=0.1, depth=0.56)
    obj("uv_sphere", glove, (0, 0, -0.6), parent=sp, radius=0.12)
    arms.append(sp)
radio = obj("cube", mat("radio", (0.15, 0.15, 0.18, 1), 0.4), (0.08, 0.0, -0.72), parent=arms[1], size=1); radio.scale = (0.14, 0.1, 0.22)
ant = obj("cylinder", mat("ant", (0.9, 0.9, 0.2, 1), emit=(1, 1, 0.3, 1), es=3), (0.08, 0.0, -0.45), parent=arms[1], radius=0.012, depth=0.25)
radio.hide_render = ant.hide_render = True

# ---- air particles
air_m = mat("air", (0.6, 0.85, 1, 1), emit=(0.5, 0.8, 1, 1), es=3)
parts = []
for i in range(46):
    a = random.uniform(0, math.pi); b2 = random.uniform(0, math.tau); r = DR * random.uniform(0.15, 0.95) ** 0.5
    p = obj("ico_sphere", air_m, (DX + r * math.cos(a), r * math.sin(a) * math.sin(b2) * 0.3, max(0.3, r * math.sin(a) * math.cos(b2) * 0.8 + 0.6)), radius=0.055, subdivisions=1)
    parts.append((p, p.location.copy(), random.uniform(0, 6.28), random.uniform(1.5, 3.0)))
sparse = []
for i in range(7):
    p = obj("ico_sphere", air_m, (DX + random.choice((-1, 1)) * random.uniform(DR + 2, DR + 9), random.uniform(-1, 1), random.uniform(0.8, 4)), radius=0.055, subdivisions=1)
    sparse.append((p, p.location.copy(), random.uniform(0, 6.28), 3))

# ---- sound rings and radio pulses (pools, hidden by scale 0 when unused)
ring_m = mat("sring", (1, 0.85, 0.2, 1), emit=(1, 0.75, 0.1, 1), es=2.2)
rings = [obj("torus", ring_m, (0, 0, 0), major_radius=1.0, minor_radius=0.03, major_segments=64, minor_segments=6) for _ in range(8)]
for r in rings:
    r.rotation_euler = (math.radians(90), 0, 0); r.scale = (0, 0, 0)
pulse_m = mat("pulse", (0.3, 1, 0.9, 1), emit=(0.3, 1, 0.9, 1), es=6)
pulses = [obj("uv_sphere", pulse_m, (0, 0, 0), radius=0.13, segments=12, ring_count=8) for _ in range(6)]
for p in pulses:
    p.scale = (0, 0, 0)

# ---- timeline functions
smooth = lambda x: (lambda c: c * c * (3 - 2 * c))(max(0.0, min(1.0, x)))


def lerp(a, b, k):
    return a + (b - a) * k


def ax(t):                                              # astronaut x
    if t < 10: return 1.4 * t
    if t < 20: return 14.0
    if t < 26: return lerp(14.0, 24.0, smooth((t - 20) / 6)) if True else 0
    return 24.0


def walking(t): return t < 10 or 20 <= t < 26.2


CLAPS_IN, CLAPS_OUT = (12.0, 14.5, 17.0), (28.0, 30.0)
RADIO_T0 = 33.0
cam_keys = [(0, (2, -6.5, 1.8), (3.2, 0, 1.5)), (10, (13, -9.5, 2.2), (14.2, 0, 2.0)), (19, (15, -11.5, 2.8), (15, 0, 2.2)), (26, (19, -21, 5.5), (19, 0, 2.0)),
            (32, (22, -19, 4.5), (22, 0, 2.0)), (45, (22, -18, 4.0), (22, 0, 2.2))]


def cam_at(t):
    for (t0, c0, g0), (t1, c1, g1) in zip(cam_keys, cam_keys[1:]):
        if t0 <= t <= t1:
            k = smooth((t - t0) / (t1 - t0))
            return [lerp(a, b, k) for a, b in zip(c0, c1)], [lerp(a, b, k) for a, b in zip(g0, g1)]
    return list(cam_keys[-1][1]), list(cam_keys[-1][2])


bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 26
tgt = empty((0, 0, 0)); tc2 = cam.constraints.new("TRACK_TO"); tc2.target = tgt; tc2.track_axis = "TRACK_NEGATIVE_Z"; tc2.up_axis = "UP_Y"

# ---- captions (children of the camera)
CAPS = []


def caption(s, t0, t1, size=0.52):
    bpy.ops.object.text_add(location=(0, 2.7, -6)); t = bpy.context.object
    t.data.body, t.data.size, t.data.align_x, t.data.align_y, t.data.extrude = s, size, "CENTER", "CENTER", 0.02
    t.data.materials.append(mat("cap", (1, 0.9, 0.3, 1), emit=(1, 0.88, 0.25, 1), es=2.5)); t.parent = cam
    for fl in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_shadow", "visible_volume_scatter"):
        setattr(t, fl, False)                      # captions are seen by the camera only (no letters lighting the ship/ground)
    CAPS.append((t, t0, t1))


caption("WHY IS\nSPACE\nSILENT?", 0.3, 9.6)
caption("SOUND NEEDS\nAIR TO\nTRAVEL", 10.3, 19.6)
caption("OUT HERE\nTHE AIR\nIS GONE", 20.3, 26.4)
caption("NO AIR =\nNO SOUND", 26.6, 32.3)
caption("RADIO IS\nLIGHT,\nNOT SOUND", 33.0, 44.7)

frames = [int(x) for x in stills.split(",")] if stills else range(1, N + 1)
want = set(frames)
for f in range(1, N + 1):
    t = (f - 1) / FPS
    x = ax(t)
    root.location = (x, 0, 0.04 * abs(math.sin(t * 7.5)) if walking(t) else 0.0); key(root, "location", f)
    ph = t * 2 * math.pi * 1.15
    sw = math.radians(34) if walking(t) else 0.0
    legs[0].rotation_euler = (0, math.sin(ph) * sw, 0); legs[1].rotation_euler = (0, -math.sin(ph) * sw, 0)
    for l in legs: key(l, "rotation_euler", f)
    ca = min([abs(t - c) for c in CLAPS_IN + CLAPS_OUT] or [9])
    if ca < 0.7:                                                # clap: both arms swing forward and back
        up = math.sin(math.pi * ca / 0.7 * 0.0 + (1 - ca / 0.7) * math.pi)
        a0 = a1 = math.radians(-75) * up
    elif RADIO_T0 - 0.6 <= t:
        k = smooth((t - (RADIO_T0 - 0.6)) / 0.6)
        a0, a1 = -math.sin(ph) * math.radians(10) * (1 - k), math.radians(-100) * k
    elif walking(t):
        a0, a1 = -math.sin(ph) * math.radians(28), math.sin(ph) * math.radians(28)
    else:
        a0 = a1 = 0.0
    arms[0].rotation_euler = (0, a0, 0); arms[1].rotation_euler = (0, a1, 0)
    for a in arms: key(a, "rotation_euler", f)
    radio.hide_render = ant.hide_render = t < RADIO_T0 - 0.6
    radio.keyframe_insert("hide_render", frame=f); ant.keyframe_insert("hide_render", frame=f)
    blink = 0.1 if (t % 3.1) < 0.14 else 1.0
    for e, p in eyes:
        e.scale = (1, 1, blink); p.scale = (1, 1, blink); key(e, "scale", f); key(p, "scale", f)
    for t_, c0, c1 in CAPS:
        t_.hide_render = not (c0 <= t <= c1); t_.keyframe_insert("hide_render", frame=f)
    # camera
    cp, gp = cam_at(t); cam.location = cp; tgt.location = gp; key(cam, "location", f); key(tgt, "location", f)
    # air particles jitter
    for lst, dens in ((parts, 1.0), (sparse, 0.35)):
        for p, base, ph0, sp in lst:
            p.location = (base[0] + 0.12 * math.sin(t * sp + ph0), base[1] + 0.05 * math.sin(t * sp * 1.3 + ph0), base[2] + 0.12 * math.cos(t * sp * 0.9 + ph0)); key(p, "location", f)
    # sound rings: inside the dome they expand to the edge and fade; outside they die at once
    for i, r in enumerate(rings):
        s = 0.0
        if i < 3:
            c = CLAPS_IN[i]; age = t - c
            hx = CLAPS_IN[i] and 14.6
            if 0 <= age < 2.4:
                rad = 0.3 + 3.4 * age; s = rad if hx + rad < DX + DR + 0.0 else 0.0
                r.location = (hx, 0, 1.4); 
        elif i < 5:
            c = CLAPS_OUT[i - 3]; age = t - c
            if 0 <= age < 0.35:
                s = 0.25 + 1.0 * age; r.location = (24.6, 0, 1.4)
        r.scale = (s, s, s); key(r, "scale", f); key(r, "location", f)
    # radio pulses from astronaut to ship
    for i, p in enumerate(pulses):
        age = (t - RADIO_T0 - i * 0.9) % 5.4 if t >= RADIO_T0 else -1
        k = age / 1.8
        if 0 <= k <= 1:
            p.location = (lerp(24.2, DX + 1.0, k), 0, lerp(1.7, 1.2, k)); p.scale = (1, 1, 1)
        else:
            p.scale = (0, 0, 0)
        key(p, "location", f); key(p, "scale", f)

if stills:
    for f in sorted(want):
        sc.frame_set(f); sc.render.filepath = f"{out}/s_{f:04d}.png"; bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("RENDERED", len(want), "frames ->", out)
