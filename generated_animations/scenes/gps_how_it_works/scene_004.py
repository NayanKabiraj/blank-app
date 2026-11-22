"""Scene 4 - circles from three satellites cross at one point (trilateration)."""
from __future__ import annotations

import numpy as np
from manim import Circle, Create, FadeIn, GrowFromCenter, Indicate, Transform

from generated_animations.avatar import expressions, gestures, movement
from generated_animations.runtime import STAGE_Y
from generated_animations.shared import diagrams, lighting, particles, typography
from generated_animations.shared.motion import ease_out_back

TITLE = "Where the circles cross"


def animate(ctx):
    tl = ctx.timeline
    ctx.headline("Distance → position")
    me = np.array([0.15, STAGE_Y + 0.2, 0.0])
    sats = [np.array(p, float) for p in ((-2.6, STAGE_Y + 3.0, 0), (2.7, STAGE_Y + 2.4, 0), (-0.4, STAGE_Y - 2.5, 0))]
    cols = ["#7FD6FF", "#F4C95D", "#FF8FA3"]
    sat_m = [diagrams.satellite(p, 0.45) for p in sats]
    ctx.add(*sat_m, z=4)
    ctx.play(*[FadeIn(s, scale=0.5) for s in sat_m], run_time=0.6)
    ctx.avatar.look_at(me)

    circles = []
    for p, c in zip(sats, cols):
        circles.append(Circle(radius=float(np.linalg.norm(p - me)), stroke_color=c, stroke_width=4, stroke_opacity=0.9).move_to(p))
    ctx.beat(0)
    ctx.add(circles[0], z=1)
    ctx.play(Create(circles[0]), run_time=1.3)
    ctx.beat(1)
    ctx.add(circles[1], z=1)
    ctx.play(Create(circles[1]), gestures.point_at(ctx.avatar, sats[1], 0.5), run_time=1.3)
    ctx.beat(2)
    ctx.add(circles[2], z=1)
    ctx.play(Create(circles[2]), gestures.point_at(ctx.avatar, me, 0.5), run_time=1.3)
    marker = diagrams.location_dot(me, "#4CD97B", 0.16)
    glow = lighting.glow(me, "#4CD97B", 0.7)
    spark = particles.Sparkle(me, tl, "#FFD166", n=22, speed=1.6, life=1.0)
    ctx.add(glow, marker, spark, z=5)
    ctx.beat(3)
    spark.restart()
    ctx.rig.push_in(me, 1.25, 1.2)
    ctx.play(GrowFromCenter(marker), expressions.set_expression(ctx.avatar, "excited", 0.3),
             Indicate(marker, color="#FFFFFF"), movement.hop(ctx.avatar, 0.45, 0.6), run_time=0.9)
    ctx.pad(reserve=0.5)
