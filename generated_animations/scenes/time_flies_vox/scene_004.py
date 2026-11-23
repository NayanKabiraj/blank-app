"""Vox look - shot 4 (scenes 7-8): the quiz as two paper strips (grey routine vs colourful firsts) with a red marker circle on the answer; the close is a calendar sticker."""
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


T = {"a": "A ROUTINE YEAR", "b": "A YEAR OF FIRSTS", "first": "FIRSTS!", "cal": "TRY ONE NEW THING", "wk": "THIS WEEK"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    t_q, t_a = ctx.tt(0, 1), ctx.tt(0, 2)
    cols = [PINK, YEL, GREEN, BLUE, ORANGE, "#C792EA"]
    for k, (key, xo) in enumerate(((T["a"], -2.0), (T["b"], 2.0))):
        show(ctx, vox.torn_card(3.4, 4.6, seed=31 + k, rot=-2 + 4 * k).move_to(C + v(xo, 0.9)), 0.2, t_out=t1 - 0.2, pop=0.2, z=2)
        show(ctx, ctx.text(key, 28, INK, 3.1).move_to(C + v(xo, 2.7)), 0.3, t_out=t1 - 0.2, z=5)
        for i in range(12):
            x, y = C[0] + xo - 0.8 + 0.8 * (i % 3), C[1] + 1.7 - 0.7 * (i // 3)
            col = "#B7AE9C" if k == 0 else cols[i % len(cols)]
            show(ctx, RoundedRectangle(corner_radius=0.08, width=0.66, height=0.54, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=1).move_to(v(x, y)), 0.5 + 0.18 * i, t_out=t1 - 0.2, pop=0.15, z=5)
    ring = always_redraw(lambda: Ellipse(width=3.7, height=5.0, stroke_color=RED, stroke_width=9, fill_opacity=0, stroke_opacity=level(ctx, t_a, 0.35) * window(ctx, 0.2, t1 - 0.2)()).move_to(C + v(2.0, 0.9)).rotate(0.04))
    ring._dynamic = True
    ctx.add(ring, z=7)
    show(ctx, vox.tape(ctx, T["first"], C + v(0, -2.0), GREEN, 3.0, 44, -4.0), t_a, t_out=t1 - 0.2, pop=0.25, z=8)
    # close: a calendar sticker
    cal = VGroup(vox.torn_card(5.4, 4.6, seed=41, rot=1.5), Rectangle(width=5.0, height=0.9, stroke_width=0, fill_color=RED, fill_opacity=1).shift(v(0, 1.8)))
    show(ctx, cal.move_to(C + v(0, 0.7)), t1 + 0.2, pop=0.25, z=2)
    for i in range(7):
        show(ctx, RoundedRectangle(corner_radius=0.1, width=0.58, height=0.58, stroke_color=INK, stroke_width=3, fill_color=cols[i % len(cols)], fill_opacity=1).move_to(C + v(-1.95 + 0.65 * i, 0.9)), t1 + 0.6 + 0.3 * i, pop=0.2, z=5)
    big = ctx.text(T["cal"], 46, INK, 5.2).move_to(C + v(0, -0.5))
    show(ctx, big, t1 + 0.8, z=5)
    vox.marker(ctx, big, t1 + 1.2, 0.8)
    show(ctx, ctx.text(T["wk"], 34, RED, 5.0).move_to(C + v(0, -1.4)), t1 + 1.6, z=5)
    ctx.avatar.look_at(C + v(2.0, 0.9))
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.4), run_time=0.5)
    ctx.until(t1)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
