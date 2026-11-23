"""Vox look - shot 1 (scenes 1-2): the hook (a torn card with a racing clock, 'ENDLESS' on a marker swipe) and the intro roadmap as tape labels."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, Sector, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import vox
from generated_animations.shared.vox import BLUE, CREAM, GREEN, INK, ORANGE, PINK, RED, YEL
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def clock(c, r, angle, a=1.0):
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=7, fill_color=CREAM, fill_opacity=a).move_to(c),
               *[Line(c + (0.82 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), c + (0.95 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), color=INK, stroke_width=4) for k in range(12)],
               Line(c, c + (0.76 * r) * v(math.sin(angle), math.cos(angle)), color=RED, stroke_width=8),
               Line(c, c + (0.5 * r) * v(math.sin(angle / 12), math.cos(angle / 12)), color=INK, stroke_width=10),
               Circle(radius=0.07 * r, stroke_width=0, fill_color=INK, fill_opacity=1).move_to(c))
    g.set_stroke(opacity=a)
    return g


T = {"a": "A YEAR FELT", "b": "ENDLESS", "c": "NOW: A BLINK", "r1": "2 OLD THEORIES", "r2": "A MEMORY TRICK", "r3": "HOW TO SLOW IT DOWN"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    card = vox.torn_card(5.6, 3.3, seed=4, rot=-1.5)
    card.move_to(C + v(0.1, 1.2))
    show(ctx, card, 0.2, pop=0.2, z=2)
    ang = lambda: 0.3 * tl.t + 0.28 * tl.t * tl.t
    al = window(ctx, 0.4, None)
    face = always_redraw(lambda: clock(C + v(0.1, 1.2), 1.15, ang(), al()))
    face._dynamic = True
    ctx.add(face, z=4)
    h1 = ctx.text(T["a"], 56, INK, 6.5).move_to(C + v(0, 3.4))
    h2 = ctx.text(T["b"], 78, INK, 6.5).move_to(C + v(0, -0.7))
    show(ctx, h1, 0.3, z=5)
    show(ctx, h2, 0.8, t_out=ctx.tt(0, 1) + 0.2, z=5)
    vox.marker(ctx, h2, 1.0, 0.8)
    h3 = ctx.text(T["c"], 66, RED, 6.5).move_to(C + v(0, -0.7))
    show(ctx, h3, ctx.tt(0, 1) + 0.4, z=5)
    show(ctx, vox.doodle_arrow(C + v(-3.1, -0.7), C + v(-2.0, 0.8), RED, 0.9), ctx.tt(0, 1) + 0.8, z=5)
    # intro: three tape labels
    for n, (key, col, rot) in enumerate(((T["r1"], BLUE, 2.0), (T["r2"], ORANGE, -2.0), (T["r3"], GREEN, 1.5))):
        show(ctx, vox.tape(ctx, key, C + v(0.0, -1.6 - 0.85 * n + 0.0), col, 4.8, 28, rot), t1 + 0.9 + 1.3 * n, pop=0.25, z=6)
    ctx.avatar.look_at(C + v(0.1, 1.2))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
