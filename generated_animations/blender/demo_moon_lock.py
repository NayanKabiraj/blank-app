"""Blender (bpy) feasibility sample: a real 3D vertical Short scene written entirely as Python.

    /path/to/venv/bin/python generated_animations/blender/demo_moon_lock.py OUT_DIR [--frames 144] [--engine CYCLES|BLENDER_EEVEE] [--scale 0.5]

Earth + a tidally locked Moon (child of a rotating empty, so the red marker always faces Earth), a sun lamp, a slow camera push-in and 3D title text.
Renders PNG frames to OUT_DIR; assemble with ffmpeg (see README.md in this folder).
"""
import math
import sys

import bpy

out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/blender_out"
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
frames, engine, scale = arg("--frames", 144), arg("--engine", "CYCLES"), arg("--scale", 0.5)
FPS = 24
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = engine
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, int(scale * 100)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, frames
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = out + "/f_"
if engine == "CYCLES":
    sc.cycles.samples, sc.cycles.use_denoising, sc.cycles.device = 24, True, "CPU"
    sc.cycles.use_adaptive_sampling = True

# world: deep navy
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.02, 0.05, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6


def mat(name, base, emit=None, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = base; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = emit; b.inputs["Emission Strength"].default_value = 2.0
    return m


def noise_mat(name, c1, c2, scale_, detail=8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale_; n.inputs["Detail"].default_value = detail
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = 0.45, 0.55
    r.color_ramp.elements[0].color, r.color_ramp.elements[1].color = c1, c2
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    return m


# Earth (ocean/land from noise), Moon (grey craters from noise), marker on the near side
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32); earth = bpy.context.object; bpy.ops.object.shade_smooth()
earth.data.materials.append(noise_mat("earth", (0.05, 0.22, 0.65, 1), (0.25, 0.55, 0.22, 1), 3.2))
R = 2.3
bpy.ops.object.empty_add(location=(0, 0, 0)); pivot = bpy.context.object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=48, ring_count=24, location=(R, 0, 0)); moon = bpy.context.object; bpy.ops.object.shade_smooth()
moon.data.materials.append(noise_mat("moon", (0.32, 0.32, 0.34, 1), (0.72, 0.72, 0.7, 1), 9.0)); moon.parent = pivot
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(R - 0.27, 0, 0)); mark = bpy.context.object
mark.data.materials.append(mat("mark", (0.9, 0.1, 0.1, 1), emit=(1, 0.1, 0.1, 1))); mark.parent = pivot
pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", frame=1)
pivot.rotation_euler = (0, 0, 2 * math.pi); pivot.keyframe_insert("rotation_euler", frame=frames)
earth.rotation_euler = (math.radians(15), 0, 0); earth.keyframe_insert("rotation_euler", frame=1)
earth.rotation_euler = (math.radians(15), 0, 8 * math.pi); earth.keyframe_insert("rotation_euler", frame=frames)

# orbit ring (thin torus)
bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=0.008, major_segments=128, minor_segments=8); ring = bpy.context.object
ring.data.materials.append(mat("ring", (0.9, 0.9, 1, 1), emit=(0.8, 0.85, 1, 1)))

# sun lamp from the left, strong; faint fill
bpy.ops.object.light_add(type="SUN", location=(-6, -3, 5)); sun = bpy.context.object; sun.data.energy = 6.0; sun.rotation_euler = (math.radians(55), 0, math.radians(-60))
bpy.ops.object.light_add(type="AREA", location=(4, -4, 3)); fill = bpy.context.object; fill.data.energy = 120; fill.data.color = (0.5, 0.6, 1)

# 3D text (title above, caption below)
def text(s, y, size, col, frame_in):
    bpy.ops.object.text_add(location=(0, y, 0.05)); t = bpy.context.object; t.data.body = s; t.data.size = size
    t.data.align_x = "CENTER"; t.data.extrude = 0.03; t.rotation_euler = (math.radians(40), 0, 0)
    t.data.materials.append(mat("t" + s[:3], col, emit=col))
    t.scale = (0, 0, 0); t.keyframe_insert("scale", frame=frame_in)
    t.scale = (1, 1, 1); t.keyframe_insert("scale", frame=frame_in + 10)
    return t
text("ONE MOON.", 3.9, 0.52, (1, 0.84, 0.25, 1), 6)
text("ONE FACE.", -3.9, 0.52, (1, 0.35, 0.3, 1), 40)

# camera: portrait, slow push-in
bpy.ops.object.camera_add(location=(0, -6.0, 6.9)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 24
tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
cam.keyframe_insert("location", frame=1); cam.location = (0, -4.8, 5.6); cam.keyframe_insert("location", frame=frames)
bpy.ops.render.render(animation=True)
print("RENDERED", frames, "frames ->", out)
