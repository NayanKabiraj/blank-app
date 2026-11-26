# Blender (bpy) feasibility sample - 26 Nov 2026

`pip install bpy` (Blender 5.3 as a Python module, 427 MB wheel, Python 3.13, no GPU needed) works in this container. `demo_moon_lock.py` builds a real 3D vertical Short scene
(Earth, tidally locked Moon, sun lamp, 3D text, push-in camera) in about 100 lines and renders it with Cycles on 4 CPU cores:
540x960, 24 samples + denoise, 144 frames (6 s) took about 8 minutes (~3.4 s/frame); the 1080x1920 final is roughly 4x that (~30 min per 6 s). A 40 s Short would be
~1 h at 1080p on CPU: too slow for the daily 6-video batch as is. Options: EEVEE on a GPU runner, fewer samples, 720p, or Blender only for hero shots mixed with the Manim pack.

    python3 -m venv /tmp/bpyenv && /tmp/bpyenv/bin/pip install bpy numpy
    /tmp/bpyenv/bin/python generated_animations/blender/demo_moon_lock.py /tmp/out --frames 144 --scale 0.5
    ffmpeg -framerate 24 -i /tmp/out/f_%04d.png -c:v libx264 -pix_fmt yuv420p out.mp4

Not wired into the pipeline (no pack format, no narration timing, no Hindi text/fonts yet). Status: sample only.
