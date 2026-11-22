"""Scene 3 - the phone listens and measures how long each signal took."""
from __future__ import annotations

import numpy as np
from manim import Create, FadeIn, Line

from generated_animations.avatar import expressions, gestures
from generated_animations.runtime import STAGE_Y
from generated_animations.shared import diagrams, particles, typography


def _v(x, y, z=0.0):
    import numpy as _np
    return _np.array([x, y, z], dtype=float)


TITLE = "Timing the signals"


def animate(ctx):
    tl = ctx.timeline
    ctx.headline("Listen. Time it.")
    phone_c = np.array([0.0, STAGE_Y - 0.9, 0.0])
    phone = diagrams.phone(phone_c, 0.95)
    dot = diagrams.location_dot(phone_c, "#4CD97B", 0.1)
    sat_pts = [np.array(p, float) for p in ((-2.9, STAGE_Y + 2.1, 0), (0.1, STAGE_Y + 2.9, 0), (2.9, STAGE_Y + 1.8, 0))]
    fracs = [0.30, 0.55, 0.85]   # shorter ring = shorter delay (illustrative, not measured)
    cols = ["#7FD6FF", "#F4C95D", "#FF8FA3"]
    sats = [diagrams.satellite(p, 0.42) for p in sat_pts]
    ctx.add(phone, dot, z=2)
    ctx.add(*sats, z=3)
    ctx.play(FadeIn(phone, shift=_v(0, -0.3, 0)), FadeIn(dot), *[FadeIn(s, shift=_v(0, 0.3, 0)) for s in sats], run_time=0.9)
    ctx.avatar.look_at(phone)
    ctx.beat(0)

    lines, packets, timers = [], [], []
    for p, col, fr in zip(sat_pts, cols, fracs):
        sp = p + (0, -0.25, 0)
        lines.append(particles.signal_path(lambda sp=sp: sp, lambda: phone_c + (0, 0.9, 0), col, 2.0, 0.35))
        packets.append(particles.signal_packets(lambda sp=sp: sp, lambda: phone_c + (0, 0.9, 0), tl, col,
                                                n=3, period=1.5 + fr, size=0.1))
        timers.append(diagrams.timer_ring(p + (0.0, 0.75, 0), fr, col, 0.27))
    ctx.add(*lines, z=1)
    ctx.add(*packets, z=4)
    ctx.beat(1)
    ctx.rig.push_in(_v(0.0, STAGE_Y + 0.3), 1.12, 1.4)
    ctx.play(*[FadeIn(t, scale=0.5) for t in timers], gestures.present(ctx.avatar, 0.5), run_time=0.8)
    ctx.add(*timers, z=4)
    lab = typography.text("delay = distance", 38, "#FFFFFF", max_width=5.5)
    lab.move_to((0, -1.35, 0))
    ctx.rig.pin(lab)
    ctx.add(lab, z=3)
    ctx.play(FadeIn(lab, shift=_v(0, 0.2, 0)), run_time=0.5)
    ctx.beat(2)
    far = sat_pts[2]
    ctx.rig.push_in(_v(0.0, STAGE_Y + 0.3), 1.1, 1.2)
    ctx.play(gestures.point_at(ctx.avatar, far, 0.6), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.8)
    ctx.avatar.look_at(far)
    ctx.pad(reserve=0.5)
