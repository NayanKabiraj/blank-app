"""Shot 7 (scene 8): the Moon fades in and out of an Earth that would be quieter, darker and wobblier - would you miss it?"""
from __future__ import annotations

import math

import numpy as np

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"q": "Would you miss it?", "a": "weaker tides", "b": "darker nights", "c": "a wobblier future"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    E = C + np.array([0.0, 0.7, 0.0])
    R = 1.5
    ph = lambda: 0.7 * tl.t
    ctx.add(orbital.ocean_earth(E, R, bulge=ph, amp=lambda: 0.1 + 0.26 * (0.5 + 0.5 * math.sin(tl.t * 1.4)), rot=lambda: 0.5 * tl.t, alpha=window(ctx, 0.1, None)), z=3)
    from manim import always_redraw
    mm = always_redraw(lambda: orbital.moon(E + 2.5 * np.array([math.cos(ph()), math.sin(ph()), 0.0]), 0.34).set_opacity(0.15 + 0.85 * (0.5 + 0.5 * math.sin(tl.t * 1.4))))
    mm._dynamic = True
    ctx.add(mm, z=4)
    t = ctx.tt(0, 0)
    show(ctx, ctx.text(T["a"], 36, "#7FD6FF", 5.0).move_to(C + np.array([-2.2, 3.9, 0.0])), 0.8)
    show(ctx, ctx.text(T["b"], 36, "#E6E6E6", 5.0).move_to(C + np.array([2.0, 3.5, 0.0])), 1.6)
    show(ctx, ctx.text(T["c"], 36, "#FF8FA3", 5.5).move_to(C + np.array([0.0, -2.3, 0.0])), 2.4)
    show(ctx, ctx.text(T["q"], 52, "#FFD166", 7.5).move_to(C + np.array([0.0, -3.2, 0.0])), ctx.tt(0, 1))
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
