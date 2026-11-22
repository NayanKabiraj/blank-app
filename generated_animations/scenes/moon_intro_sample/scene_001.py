"""Shot 1 (scenes 1-2): the Moon vanishes in a flash and the ocean's bulge collapses."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital, particles
from generated_animations.timed import level, show, window

T = {"gone": "GONE!", "tides": "tides shrink", "q": "?", "intro": "In this video"}


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
    show(ctx, ctx.text(T["tides"], 40, "#7FD6FF", 6.0).move_to(E + np.array([0.0, -R - 1.0, 0.0])), t_gone + 1.4, t_out=ctx.t_of(1) - 0.1, z=7)
    # scene 2 = the INTRO: a roadmap of what the video will show, one chip per promise, the presenter points at each
    from manim import RoundedRectangle, VGroup
    chips = [("tides", "#7FD6FF", 1), ("nights", "#FFD166", 2), ("Earth's tilt", "#9BE59B", 3)]
    label = ctx.text(T["intro"], 44, "#FFFFFF", 6.0).move_to(C + np.array([0.0, 5.0, 0.0]))
    show(ctx, label, ctx.t_of(1) + 0.1, t_out=None, z=7)
    for n, (name, col, k) in enumerate(chips):
        y = C[1] + 3.9 - 0.95 * n
        box = RoundedRectangle(corner_radius=0.3, width=4.2, height=0.8, stroke_color=col, stroke_width=5, fill_color="#10163A", fill_opacity=0.9)
        txt = ctx.text(f"{n + 1}  {name}", 38, col, 4.0)
        chip = VGroup(box, txt).move_to(np.array([C[0], y, 0.0]))
        t_k = ctx.tt(1, 0) + 1.1 + 0.85 * n
        show(ctx, chip, t_k, pop=0.25, z=7)
    ctx.avatar.look_at(lambda: mpos)
    ctx.play(gestures.point_at(ctx.avatar, lambda: mpos, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t_gone)
    sp.restart()
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
