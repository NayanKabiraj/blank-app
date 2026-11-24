"""Vox look - shot 2 (scenes 3-5): the guess (candidate chunks get scores, one is picked, repeat); the 2017 Transformer paper as a newspaper clipping; training as guess, compare, nudge."""
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


T = {"s": "THE CAT SAT ON THE", "c": [("mat", 62, GREEN), ("sofa", 20, BLUE), ("roof", 10, ORANGE), ("moon", 8, PINK)], "pick": "PICK ONE, THEN REPEAT", "g": "GUESS", "k": "COMPARE", "n": "NUDGE THE NUMBERS", "real": "mat"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t3, t4 = ctx.t_of(1), ctx.t_of(2)
    # ---- scene 3 (index 0): scored candidates
    show(ctx, vox.torn_card(6.0, 4.9, seed=24, rot=1.0).move_to(C + v(0, 0.7)), 0.2, t_out=t3 - 0.2, pop=0.2, z=2)
    s = ctx.text(T["s"], 38, INK, 5.4).move_to(C + v(0, 2.3))
    show(ctx, s, 0.4, t_out=t3 - 0.2, z=5)
    for i, (w, pct, col) in enumerate(T["c"]):
        y = C[1] + 1.2 - 0.85 * i
        t_in = ctx.tt(0, 0) + 0.5 + 0.35 * i
        wd = (lambda pct=pct, t_in=t_in: 3.6 * pct / 62.0 * ease(level(ctx, t_in, 1.0)))
        bar = always_redraw(lambda col=col, y=y, wd=wd: Rectangle(width=max(0.02, wd()), height=0.5, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=window(ctx, 0.3, t3 - 0.2)()).move_to(v(C[0] - 0.9 + max(0.02, wd()) / 2, y)))
        bar._dynamic = True
        ctx.add(bar, z=5)
        show(ctx, ctx.text(w, 30, INK, 1.6).move_to(v(C[0] - 2.3, y)), t_in, t_out=t3 - 0.2, z=6)
        show(ctx, ctx.text(f"{pct}%", 26, INK, 1.2).move_to(v(C[0] + 2.7, y)), t_in + 0.6, t_out=t3 - 0.2, z=6)
    ring = always_redraw(lambda: Rectangle(width=5.6, height=0.7, stroke_color=RED, stroke_width=7, fill_opacity=0, stroke_opacity=level(ctx, ctx.tt(0, 1), 0.3) * window(ctx, 0.2, t3 - 0.2)()).move_to(C + v(0, 1.2)))
    ring._dynamic = True
    ctx.add(ring, z=7)
    show(ctx, vox.tape(ctx, T["pick"], C + v(0, -1.9), RED, 4.8, 28, -3.0), ctx.tt(0, 1) + 0.3, t_out=t3 - 0.2, pop=0.25, z=7)
    # ---- scene 4 (index 1): the 2017 paper as a newspaper clipping
    paper = vox.newspaper(ctx, "The Curious Loop Times", "Google researchers publish the Transformer", "JUNE 2017 - ATTENTION IS ALL YOU NEED", w=5.0, h=4.1, seed=8, rot=-4)
    paper.move_to(C + v(0, 0.8))
    vox.arrive(ctx, paper, t3 + 0.15, t_out=t4 - 0.9, side="right", z=8)
    show(ctx, vox.tape(ctx, "8 RESEARCHERS", C + v(0, -1.7), BLUE, 3.6, 28, 3.0), t3 + 1.6, t_out=t4 - 0.9, pop=0.25, z=9)
    # ---- scene 5 (index 2): training = guess -> compare -> nudge
    show(ctx, vox.torn_card(6.0, 4.9, seed=26, rot=-1.0).move_to(C + v(0, 0.7)), t4 + 0.2, pop=0.2, z=2)
    for i, (key, col) in enumerate(((T["g"], BLUE), (T["k"], ORANGE), (T["n"], GREEN))):
        show(ctx, vox.tape(ctx, key, C + v(0, 2.2 - 1.15 * i), col, 4.2, 28, 2.0 - 2.0 * i), t4 + 0.5 + 1.3 * i, pop=0.25, z=6)
    for k in range(3):                                   # three dials whose needles get nudged
        c = C + v(-1.6 + 1.6 * k, -1.7)
        show(ctx, Circle(radius=0.55, stroke_color=INK, stroke_width=5, fill_color="#FFFFFF", fill_opacity=1).move_to(c), t4 + 2.4, pop=0.2, z=5)
        needle = always_redraw(lambda c=c, k=k: Line(c, c + 0.45 * v(math.sin(0.6 + 0.8 * k - 0.9 * ease(level(ctx, t4 + 3.4 + 0.3 * k, 0.8)) + 0.12 * math.sin(tl.t * 3 + k)), math.cos(0.6 + 0.8 * k - 0.9 * ease(level(ctx, t4 + 3.4 + 0.3 * k, 0.8)))), color=RED, stroke_width=7, stroke_opacity=window(ctx, t4 + 2.4, None)()))
        needle._dynamic = True
        ctx.add(needle, z=6)
    ctx.avatar.look_at(C + v(0, 1.0))
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
    ctx.until(t3)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
