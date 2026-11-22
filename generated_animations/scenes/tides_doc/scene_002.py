"""Shot 2 (chapter 2, scenes 5-6): the Moon is about thirty Earths away."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, Line

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import show, window

T = {"en": {"km": "384,400 km", "n": "about 30 Earths", "moon": "Moon", "earth": "Earth"},
     "hi": {"km": "384,400 किमी", "n": "लगभग 30 धरतियाँ", "moon": "चाँद", "earth": "धरती"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    # scene 5: what does the Moon do to the ocean? (Earth, Moon, a pulsing pull)
    E = C + np.array([1.6, 0.0, 0.0])
    ctx.add(orbital.ocean_earth(E, 1.3, bulge=lambda: math.pi, amp=lambda: 0.1 + 0.05 * math.sin(tl.t * 2), rot=lambda: 0.2 * tl.t, alpha=window(ctx, 0.1, t1 - 0.2)), z=3)
    M = C + np.array([-2.8, 0.1, 0.0])
    show(ctx, orbital.moon(M, 0.5), 0.3, t_out=t1 - 0.2)
    show(ctx, Arrow(E + np.array([-1.5, 0.0, 0.0]), M + np.array([0.7, 0.0, 0.0]), buff=0, color="#FFD166", stroke_width=7), 0.8, t_out=t1 - 0.2)
    show(ctx, ctx.text("?", 100, "#FF8FA3", 2.0).move_to(C + np.array([0.6, 2.2, 0.0])), 1.0, t_out=t1 - 0.2)

    # scene 6: the Moon is about thirty Earths away: a row of thirty Earths between them
    x0, y = C[0] - W / 2 + 0.6, C[1] - 0.2
    r = 0.16
    show(ctx, orbital.moon(np.array([x0 + 0.5 + 30 * 2 * r + 0.25, y, 0.0]), 0.05 * 3.5), t1 + 0.2)
    big = Circle(radius=0.45, stroke_color="#7FD6FF", stroke_width=4, fill_color="#1F6FB5", fill_opacity=1).move_to((x0, y, 0))
    show(ctx, big, t1 + 0.2, pop=0.3)
    show(ctx, ctx.text(L["earth"], 26, "#7FD6FF", 2.0).move_to((x0, y - 0.9, 0)), t1 + 0.4)
    t_row = ctx.tt(1, 0) + 0.5
    for k in range(30):
        ex = x0 + 0.5 + r + 2 * r * k
        show(ctx, Circle(radius=r, stroke_color="#7FD6FF", stroke_width=2, fill_color="#1F6FB5", fill_opacity=0.95).move_to((ex, y, 0)), t_row + 0.09 * k, dur=0.15, pop=0.5)
    x_end = x0 + 0.5 + 60 * r
    show(ctx, ctx.text(L["moon"], 26, "#E6E6E6", 2.0).move_to((x_end + 0.25, y - 0.9, 0)), t_row + 2.9)
    dim_y = y + 1.1
    show(ctx, Line((x0, dim_y, 0), (x_end + 0.25, dim_y, 0), color="#FFD166", stroke_width=5), t_row + 2.7, pop=0)
    show(ctx, ctx.text(L["km"], 46, "#FFD166", 5.0).move_to(((x0 + x_end) / 2, dim_y + 0.6, 0)), t_row + 2.9)
    show(ctx, ctx.text(L["n"], 36, "#F5F7FA", 5.0).move_to(((x0 + x_end) / 2, y - 1.7, 0)), t_row + 3.1)
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t_row + 2.8)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
