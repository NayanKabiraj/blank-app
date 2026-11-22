"""Scene 2 - the satellites overhead, each broadcasting the time."""
from __future__ import annotations

import numpy as np
from manim import Circle, DashedLine, FadeIn, ValueTracker, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.runtime import STAGE_Y
from generated_animations.shared import diagrams, particles, typography
from generated_animations.shared.motion import orbit_point


def _v(x, y, z=0.0):
    import numpy as _np
    return _np.array([x, y, z], dtype=float)


TITLE = "Satellites overhead"

ORBITS = [  # (radius, rad/s, start angle, tilt) - drawn not to scale
    (2.9, 0.50, 0.3, 0.85), (3.6, 0.42, 2.2, 0.8), (3.2, -0.46, 4.0, 0.75),
    (3.9, 0.38, 5.2, 0.85), (2.6, -0.55, 1.2, 0.8), (3.7, 0.35, 3.1, 0.7),
]


def animate(ctx):
    tl = ctx.timeline
    centre = np.array([0.0, STAGE_Y, 0.0])
    ctx.headline("Satellites overhead")
    grow = ValueTracker(0.01)
    earth = diagrams.earth(centre, 1.3, tl, grow=grow)
    ctx.add(earth, z=2)
    orbit_rings = [Circle(radius=r, stroke_color="#FFFFFF", stroke_width=1.5, stroke_opacity=0.18)
                   .stretch(tilt, 1).move_to(centre) for r, _, _, tilt in ORBITS[:3]]
    ctx.add(*orbit_rings, z=0)

    sats, pos_fns = [], []
    for i, (r, w, a0, tilt) in enumerate(ORBITS):
        fn = (lambda r=r, w=w, a0=a0, tilt=tilt: orbit_point(centre, r, a0 + tl.t * w, tilt))
        sat = always_redraw(lambda fn=fn: diagrams.satellite(fn(), 0.34 * grow.get_value()))
        sat._dynamic = True
        sats.append(sat); pos_fns.append(fn)
    ctx.add(*sats, z=4)
    ctx.add(*[particles.pulse_rings(fn, tl, "#F4C95D", n=2, period=1.7, max_radius=0.9, width=2.2)
              for fn in pos_fns[:3]], z=1)

    tag = typography.text("~20,200 km up", 30, "#7FD6FF", max_width=4)
    tag.move_to(centre + (0, 4.15, 0))
    leader = DashedLine(centre + (0, 1.4, 0), centre + (0, 3.85, 0), color="#7FD6FF", stroke_width=2, dash_length=0.12)
    ctx.add(leader, tag, z=3)
    ctx.play(grow.animate.set_value(1.0), FadeIn(tag), run_time=1.3)
    ctx.avatar.look_at(pos_fns[0])
    ctx.beat(0)
    ctx.play(gestures.point_at(ctx.avatar, pos_fns[0], 0.6), expressions.set_expression(ctx.avatar, "excited", 0.4),
             run_time=0.8)
    ctx.rig.push_in(centre + (0, 0.3, 0), 1.15, 2.0)
    stat = typography.text("2 orbits a day", 34, "#F4C95D", max_width=5)
    stat.move_to(centre + (0, -2.55, 0))
    ctx.add(stat, z=3)
    ctx.play(FadeIn(stat, shift=_v(0, 0.2, 0)), run_time=0.5)
    ctx.pad(reserve=0.5)
