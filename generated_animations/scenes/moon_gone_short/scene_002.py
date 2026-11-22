"""Shot 2 (scene 3): ocean tides with and without the Moon - two live tide graphs."""
from __future__ import annotations

import math

import numpy as np
from manim import Line, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"both": "Moon + Sun", "sun": "Sun only", "tide": "tide height", "day": "time"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t0 = ctx.tt(0, 1) - 0.2
    o = C + np.array([-3.3, -1.2, 0.0])
    gw, gh = 6.6, 1.2
    show(ctx, orbital.axes(o, gw, gh), 0.2, pop=0)
    show(ctx, ctx.text(T["tide"], 26, "#9AA8C7", 4.0, "NORMAL").move_to(o + np.array([0.7, gh + 0.5, 0.0])), 0.3)
    fn_a = lambda u: math.cos(2 * math.pi * (u * 4)) * 0.62 + math.cos(2 * math.pi * (u * 4) * 0.93) * 0.38      # Moon + Sun: tall
    fn_b = lambda u: math.cos(2 * math.pi * (u * 4)) * 0.28                                                             # Sun only: small
    ctx.add(orbital.curve(o, gw, gh, fn_a, lambda: level(ctx, 0.6, max(4.0, t0)), "#2EC5FF", 8, alpha=window(ctx, 0.4, None)), z=4)
    ctx.add(orbital.curve(o + np.array([0.0, -0.0, 0.0]), gw, gh, fn_b, lambda: level(ctx, t0 + 0.6, 4.0), "#FFC93C", 8, alpha=window(ctx, t0 + 0.5, None)), z=5)
    show(ctx, ctx.text(T["both"], 32, "#2EC5FF", 4.0).move_to(o + np.array([gw - 1.0, gh + 0.75, 0.0])), 1.0)
    show(ctx, ctx.text(T["sun"], 32, "#FFC93C", 4.0).move_to(o + np.array([gw - 1.0, -gh - 0.55, 0.0])), t0 + 1.0)
    show(ctx, orbital.moon(C + np.array([-3.3, 3.6, 0.0]), 0.55), 0.3, t_out=t0, z=3)
    show(ctx, orbital.sun(C + np.array([3.4, 3.6, 0.0]), 0.5), 0.3, z=3)
    ctx.avatar.look_at(None)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(t0 + 0.8)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
