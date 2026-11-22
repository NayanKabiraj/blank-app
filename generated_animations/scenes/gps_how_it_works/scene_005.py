"""Scene 5 - takeaway: a stopwatch and some geometry; the phone only listens."""
from __future__ import annotations

import numpy as np
from manim import Create, FadeIn, GrowFromCenter, Line, VGroup

from generated_animations.avatar import expressions, gestures
from generated_animations.runtime import STAGE_Y
from generated_animations.shared import diagrams, particles, typography


def _v(x, y, z=0.0):
    import numpy as _np
    return _np.array([x, y, z], dtype=float)


TITLE = "Takeaway"


def animate(ctx):
    tl = ctx.timeline
    ctx.headline("GPS = timing + geometry", "#FFD166")
    c = np.array([0.0, STAGE_Y + 0.3, 0.0])
    phone = diagrams.phone(c + (0, -0.6, 0), 1.2)
    sats = [diagrams.satellite(c + p, 0.42) for p in ((-2.7, 3.2, 0), (0.0, 3.8, 0), (2.7, 3.2, 0), (0.0, 2.2, 0))]
    cols = ["#7FD6FF", "#F4C95D", "#FF8FA3", "#4CD97B"]
    ctx.add(phone, z=2)
    ctx.add(*sats, z=3)
    ctx.avatar.look_at(phone)
    ctx.play(FadeIn(phone), *[GrowFromCenter(s) for s in sats], run_time=0.9)
    ctx.beat(0)
    top = c + (0, 0.6, 0)
    pk = [particles.signal_packets(lambda s=s: s.get_center() + (0, -0.2, 0), lambda: top, tl, col, n=2, period=1.6, size=0.1)
          for s, col in zip(sats, cols)]
    ctx.add(*pk, z=4)
    ctx.play(gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.beat(1)
    ctx.rig.push_in(c + _v(0, -1.0), 1.07, 1.6)
    badge = typography.text("4th satellite fixes the clock", 30, cols[3], max_width=7)
    badge.move_to(c + (0, -2.35, 0))
    ctx.add(badge, z=3)
    ctx.play(FadeIn(badge, shift=_v(0, 0.2, 0)), run_time=0.5)
    ctx.beat(2)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4),
             gestures.wave(ctx.avatar, 0.5), run_time=0.7)
    ctx.pad(reserve=0.5)
