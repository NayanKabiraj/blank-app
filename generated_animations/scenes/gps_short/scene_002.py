"""Shot 2 (scene 3): about thirty satellites circle the Earth, each shouting its clock time."""
from __future__ import annotations

import numpy as np
from manim import DashedLine, ValueTracker, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, particles
from generated_animations.shared.motion import orbit_point
from generated_animations.timed import show

T = {"en": {"alt": "~20,200 km up", "orb": "2 orbits a day", "ok": "each one broadcasts its clock"},
     "hi": {"alt": "~20,200 किमी ऊपर", "orb": "दिन में 2 चक्कर", "ok": "हर एक अपनी घड़ी बताता है"}}
ORBITS = [(2.9, 0.50, 0.3, 0.85), (3.6, 0.42, 2.2, 0.8), (3.2, -0.46, 4.0, 0.75),
          (3.9, 0.38, 5.2, 0.85), (2.6, -0.55, 1.2, 0.8), (3.7, 0.35, 3.1, 0.7)]


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    grow = ValueTracker(0.01)
    earth = diagrams.earth(C, 1.25, tl, grow=grow)
    ctx.add(earth, z=2)
    fns = []
    for r, w, a0, tilt in ORBITS:
        fn = (lambda r=r, w=w, a0=a0, tilt=tilt: orbit_point(C, r, a0 + tl.t * w, tilt))
        sat = always_redraw(lambda fn=fn: diagrams.satellite(fn(), 0.36 * grow.get_value()))
        sat._dynamic = True
        ctx.add(sat, z=4)
        fns.append(fn)
    for fn in fns[:4]:
        ctx.add(particles.pulse_rings(fn, tl, "#F4C95D", n=2, period=1.7, max_radius=1.0, width=2.4), z=1)
    show(ctx, DashedLine(C + np.array([0, 1.4, 0]), C + np.array([0, 3.9, 0]), color="#7FD6FF", stroke_width=2, dash_length=0.12), 0.8, pop=0)
    show(ctx, ctx.text(L["alt"], 32, "#7FD6FF").move_to(C + np.array([0, 4.3, 0])), 0.9)
    show(ctx, ctx.text(L["orb"], 34, "#F4C95D").move_to(C + np.array([0, -3.2, 0])), 2.2)
    ctx.avatar.look_at(fns[0])
    ctx.play(grow.animate.set_value(1.0), run_time=1.0)
    ctx.play(gestures.point_at(ctx.avatar, fns[0], 0.5), expressions.set_expression(ctx.avatar, "excited", 0.4), run_time=0.6)
