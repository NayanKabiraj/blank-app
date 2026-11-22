"""Scene 1 - hook: a phone that somehow knows where it is."""
from __future__ import annotations

from manim import Create, FadeIn, GrowFromCenter, Indicate

from generated_animations.avatar import expressions, gestures, movement
from generated_animations.runtime import STAGE_Y
from generated_animations.shared import diagrams, particles, typography
from generated_animations.shared.motion import ease_out_back


def _v(x, y, z=0.0):
    import numpy as _np
    return _np.array([x, y, z], dtype=float)


TITLE = "The hook"


def animate(ctx):
    tl = ctx.timeline
    ctx.headline("How does GPS work?")
    phone = diagrams.phone((0, STAGE_Y, 0), scale=1.7)
    dot = diagrams.location_dot(phone.get_center() + (0, 0.1, 0))
    rings = particles.pulse_rings(dot, tl, "#FF4D6D", n=3, period=1.8, max_radius=1.5)
    q = typography.text("Where am I?", 46, "#FFD166", max_width=5)
    q.move_to((0, STAGE_Y + 2.7, 0))
    ctx.add(phone, z=2)
    ctx.add(rings, z=1)
    ctx.add(dot, z=3)
    ctx.add(q, z=3)
    ctx.avatar.look_at(phone)

    ctx.play(Create(phone[0]), FadeIn(phone[1:]), GrowFromCenter(dot), FadeIn(q, shift=_v(0, 0.3, 0)),
             expressions.set_expression(ctx.avatar, "curious", 0.5), run_time=1.1, rate_func=ease_out_back)
    ctx.beat(0)
    ctx.play(gestures.point_at(ctx.avatar, phone, 0.6), Indicate(dot, color="#FFFFFF"), run_time=0.9)
    ctx.camera_push = ctx.rig.push_in(phone, 1.2, 1.6)
    ctx.beat(1)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), Indicate(phone, scale_factor=1.06), run_time=0.7)
    ctx.pad(reserve=0.5)
