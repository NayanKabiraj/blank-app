"""Vox look - shot 1 (scenes 1-2): a chat box 'types' by guessing one word at a time (hook); the intro as three tape labels."""
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


T = {"h": "JUST GUESSING?", "q": "Why is the sky", "w": ["blue", "dark", "big"], "r1": "HOW IT GUESSES", "r2": "HOW IT LEARNED", "r3": "WHY IT MAKES THINGS UP"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    show(ctx, vox.torn_card(5.8, 3.2, seed=14, rot=-1.5).move_to(C + v(0, 1.4)), 0.2, pop=0.2, z=2)
    show(ctx, RoundedRectangle(corner_radius=0.2, width=5.0, height=0.9, stroke_color=INK, stroke_width=5, fill_color="#FFFFFF", fill_opacity=1).move_to(C + v(0, 1.4)), 0.5, pop=0.15, z=4)
    q = ctx.text(T["q"], 40, INK, 3.4).move_to(C + v(-0.9, 1.4))
    show(ctx, q, 0.7, z=5)
    # candidate words flick by, the last one sticks (the guess)
    cands = [ctx.text(w, 40, c, 1.6) for w, c in zip(T["w"], (RED, ORANGE, BLUE))]
    for i, m in enumerate(cands):
        m.next_to(q, direction=np.array([1.0, 0.0, 0.0]), buff=0.25)
        show(ctx, m, 1.0 + 0.55 * i, t_out=1.5 + 0.55 * i if i < 2 else None, pop=0.1, z=5)
    cur = always_redraw(lambda: Rectangle(width=0.07, height=0.6, stroke_width=0, fill_color=INK, fill_opacity=(1.0 if int(tl.t * 2.5) % 2 == 0 else 0.0) * window(ctx, 0.7, ctx.tt(0, 1))()).move_to(C + v(2.1, 1.4)))
    cur._dynamic = True
    ctx.add(cur, z=6)
    h = ctx.text(T["h"], 62, INK, 6.5).move_to(C + v(0, -0.9))
    show(ctx, h, ctx.tt(0, 1) - 0.3, z=5)
    vox.marker(ctx, h, ctx.tt(0, 1) + 0.0, 0.7)
    show(ctx, vox.doodle_arrow(C + v(-2.9, -1.0), C + v(-2.0, 0.6), RED, 0.9), ctx.tt(0, 1) + 0.4, z=5)
    for n, (key, col, rot) in enumerate(((T["r1"], BLUE, 2.0), (T["r2"], ORANGE, -2.0), (T["r3"], GREEN, 1.5))):
        show(ctx, vox.tape(ctx, key, C + v(0.0, -1.9 - 0.8 * n), col, 5.0, 26, rot), t1 + 0.9 + 1.3 * n, pop=0.25, z=6)
    ctx.avatar.look_at(C + v(0, 1.4))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(ctx.tt(0, 1))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
