"""Vox look - shot 3 (scenes 6-7): the myth 'it looks facts up' vs 'it predicts likely words'; the UBS estimate as a newspaper clipping and a bar race (months to 100 million users)."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import vox
from generated_animations.shared.vox import BLUE, CREAM, GREEN, INK, ORANGE, PINK, RED, YEL
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


T = {"m": "LOOKS FACTS UP", "t": "PREDICTS LIKELY WORDS", "sure": "SOUNDS SURE", "wrong": "...CAN BE WRONG", "cg": "ChatGPT", "tt": "TikTok", "ig": "Instagram", "mo": "months to ~100M users"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t7 = ctx.t_of(1)
    # ---- scene 6: the myth
    show(ctx, vox.torn_card(3.1, 3.4, seed=33, rot=-3).move_to(C + v(-1.9, 1.4)), 0.2, t_out=t7 - 0.2, pop=0.2, z=2)
    show(ctx, vox.torn_card(3.1, 3.4, seed=34, rot=3).move_to(C + v(1.9, 1.4)), 0.4, t_out=t7 - 0.2, pop=0.2, z=2)
    a = ctx.text(T["m"], 30, INK, 2.8).move_to(C + v(-1.9, 1.4))
    show(ctx, a, 0.6, t_out=t7 - 0.2, z=5)
    show(ctx, Line(a.get_left() + v(-0.1, 0), a.get_right() + v(0.1, 0), color=RED, stroke_width=9), ctx.tt(0, 1) + 0.2, t_out=t7 - 0.2, pop=0.1, z=6)
    b = ctx.text(T["t"], 30, INK, 2.8).move_to(C + v(1.9, 1.4))
    show(ctx, b, 0.8, t_out=t7 - 0.2, z=5)
    vox.marker(ctx, b, ctx.tt(0, 1) + 0.5, 0.8)
    show(ctx, vox.tape(ctx, T["sure"], C + v(-1.4, -1.0), BLUE, 3.4, 28, -3.0), ctx.tt(0, 2) + 0.1, t_out=t7 - 0.2, pop=0.25, z=7)
    show(ctx, vox.tape(ctx, T["wrong"], C + v(1.6, -1.9), RED, 4.0, 28, 3.0), ctx.tt(0, 2) + 1.0, t_out=t7 - 0.2, pop=0.25, z=7)
    # ---- scene 7: the clipping, then the bars
    paper = vox.newspaper(ctx, "The Curious Loop Times", "ChatGPT hits ~100 million users in two months", "FEB 2023 - UBS ESTIMATE", w=5.0, h=4.1, seed=12, rot=3)
    paper.move_to(C + v(0, 1.0))
    vox.arrive(ctx, paper, t7 + 0.1, t_out=t7 + 2.2, side="left", z=8)
    show(ctx, vox.torn_card(6.0, 4.6, seed=36, rot=-1.0).move_to(C + v(0, 0.7)), t7 + 2.4, pop=0.2, z=2)
    show(ctx, ctx.text(T["mo"], 28, INK, 5.4).move_to(C + v(0, 2.4)), t7 + 2.6, z=5)
    for i, (key, months, col) in enumerate(((T["cg"], 2, RED), (T["tt"], 9, BLUE), (T["ig"], 30, ORANGE))):
        y = C[1] + 1.4 - 1.1 * i
        t_in = t7 + 2.8 + 0.7 * i
        wd = (lambda months=months, t_in=t_in: max(0.15, 3.6 * months / 30.0) * ease(level(ctx, t_in, 1.1)))
        bar = always_redraw(lambda col=col, y=y, wd=wd: Rectangle(width=max(0.02, wd()), height=0.6, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=window(ctx, t7 + 2.4, None)()).move_to(v(C[0] - 1.2 + max(0.02, wd()) / 2, y)))
        bar._dynamic = True
        ctx.add(bar, z=5)
        show(ctx, ctx.text(key, 26, INK, 1.8).move_to(v(C[0] - 2.4, y)), t_in, z=6)
        show(ctx, ctx.text(f"{months}", 30, INK, 1.0).move_to(v(C[0] - 1.2 + max(0.15, 3.6 * months / 30.0) + 0.45, y)), t_in + 0.9, z=6)
    ctx.avatar.look_at(C + v(0, 1.0))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t7)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
