"""Shot 1 (scenes 1-2): the Moon vanishes in a flash and the ocean's bulge collapses."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital, particles
from generated_animations.timed import level, show, window

T = {"gone": "GONE!", "tides": "tides shrink", "q": "?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    E = C + np.array([0.0, -0.6, 0.0])
    R = 1.7
    t_gone = ctx.tt(0, 1) - 0.2                 # the Moon disappears as the second sentence starts
    mpos = C + np.array([-2.6, 3.0, 0.0])
    ctx.add(orbital.ocean_earth(E, R, bulge=lambda: math.pi * 0.72, amp=lambda: 0.38 - 0.28 * level(ctx, t_gone + 0.2, 1.8), rot=lambda: 0.35 * tl.t,
                                alpha=window(ctx, 0.1, None)), z=3)
    show(ctx, orbital.moon(mpos, 0.7), 0.3, t_out=t_gone + 0.15, z=4)
    show(ctx, Arrow(E + np.array([-1.4, 1.1, 0.0]), mpos + np.array([0.6, -0.5, 0.0]), buff=0, color="#FFD166", stroke_width=7), 0.6, t_out=t_gone, z=4)
    sp = particles.Sparkle(mpos, tl, "#E6E6E6", n=34, speed=2.6, life=1.3)
    ctx.add(sp, z=6)
    show(ctx, ctx.text(T["gone"], 72, "#FF8FA3", 6.0).move_to(C + np.array([0.0, 4.1, 0.0])), t_gone + 0.2, t_out=ctx.t_of(1) - 0.1, z=7)
    show(ctx, ctx.text(T["tides"], 40, "#7FD6FF", 6.0).move_to(E + np.array([0.0, -R - 1.0, 0.0])), t_gone + 1.4, z=7)
    # scene 2: question marks around the Earth while the answer is worked out
    base = [E + np.array([2.7 * math.cos(a), 2.3 * math.sin(a), 0.0]) for a in (0.2, 1.0, 2.4, 3.3, 4.2, 5.3)]
    from manim import VGroup
    qs = VGroup(*[ctx.text("?", 60, "#FFD166", 1.0).move_to(p) for p in base])

    def drift(m):
        for k, (q, p) in enumerate(zip(m, base)):
            q.move_to(p + np.array([0.2 * math.sin(tl.t * 1.2 + k), 0.25 * math.cos(tl.t + k * 1.9), 0.0]))
    drift(qs)
    qs.add_updater(drift)
    show(ctx, qs, ctx.t_of(1) + 0.2, pop=0)
    ctx.avatar.look_at(lambda: mpos)
    ctx.play(gestures.point_at(ctx.avatar, lambda: mpos, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t_gone)
    sp.restart()
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
