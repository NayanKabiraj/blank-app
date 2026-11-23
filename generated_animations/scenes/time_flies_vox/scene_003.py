"""Vox look - shot 3 (scenes 5-6): the holiday effect as two paper timelines (crowded vs sparse); the 499-person survey as cut-out people and two decade bars."""
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


T = {"trip": "THE TRIP", "home": "ORDINARY WEEKS", "back": "LOOKING BACK...", "n": "499 PEOPLE", "r": "aged 14 to 94", "y": "a decade, younger", "o": "a decade, older", "f": "FELT FASTER"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    show(ctx, vox.torn_card(7.0, 5.4, seed=21, rot=-1).move_to(C + v(0, 0.5)), 0.2, pop=0.2, z=2, t_out=t1 - 0.2)
    for k, (key, n, col, yo) in enumerate(((T["trip"], 22, ORANGE, 1.3), (T["home"], 5, "#8A8070", -1.0))):
        y = C[1] + yo
        x0, x1 = C[0] - 2.9, C[0] + 2.9
        show(ctx, Line(v(x0, y), v(x1, y), color=INK, stroke_width=6), 0.4, t_out=t1 - 0.2, pop=0, z=4)
        show(ctx, ctx.text(key, 34, INK, 5.0).move_to(v(C[0], y + 0.95)), 0.5, t_out=t1 - 0.2, z=5)
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5) / n
            show(ctx, VGroup(Line(v(x, y - 0.28), v(x, y + 0.28), color=col, stroke_width=6), Circle(radius=0.1, stroke_color=INK, stroke_width=2, fill_color=col, fill_opacity=1).move_to(v(x, y + 0.42))), 0.7 + (2.2 if k == 0 else 3.0) * i / n, t_out=t1 - 0.2, pop=0.15, z=5)
    arr = vox.doodle_arrow(C + v(-2.8, -2.3), C + v(2.4, -2.1), BLUE, -0.5)
    show(ctx, arr, ctx.tt(0, 1) + 0.2, t_out=t1 - 0.2, z=6)
    lab = ctx.text(T["back"], 32, BLUE, 5.0).move_to(C + v(0, -2.9))
    show(ctx, lab, ctx.tt(0, 1) + 0.3, t_out=t1 - 0.2, z=6)
    # survey
    show(ctx, vox.torn_card(7.0, 5.4, seed=23, rot=1).move_to(C + v(0, 0.5)), t1 + 0.2, pop=0.2, z=2)
    n_txt = ctx.text(T["n"], 58, INK, 6.0).move_to(C + v(0, 2.6))
    show(ctx, n_txt, t1 + 0.3, z=5)
    vox.marker(ctx, n_txt, t1 + 0.6, 0.7)
    show(ctx, ctx.text(T["r"], 30, INK, 5.0).move_to(C + v(0, 1.9)), t1 + 0.7, z=5)
    N = 14
    for i in range(N):
        f = i / (N - 1)
        col = BLUE if f < 0.34 else (YEL if f < 0.67 else ORANGE)
        x = C[0] - 2.7 + 5.4 * f
        person = VGroup(Circle(radius=0.2, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=1).move_to(v(x, C[1] + 1.1)), RoundedRectangle(corner_radius=0.1, width=0.36, height=0.5, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=1).move_to(v(x, C[1] + 0.65)))
        show(ctx, vox.cutout(person, 5), t1 + 1.0 + 0.1 * i, pop=0.12, z=5)
    for k, (key, wd, col, yo) in enumerate(((T["y"], 5.4, BLUE, -0.4), (T["o"], 3.0, ORANGE, -1.5))):
        t_in = ctx.tt(1, 0) + 0.6 + 1.0 * k
        w = lambda wd=wd, t_in=t_in: wd * ease(level(ctx, t_in, 1.5))
        bar = always_redraw(lambda col=col, yo=yo, w=w: Rectangle(width=max(0.02, w()), height=0.55, stroke_color=INK, stroke_width=3, fill_color=col, fill_opacity=window(ctx, t1 + 0.3, None)()).move_to(v(C[0] - 2.7 + max(0.02, w()) / 2, C[1] + yo)))
        bar._dynamic = True
        ctx.add(bar, z=5)
        show(ctx, ctx.text(key, 26, INK, 5.0).move_to(v(C[0], C[1] + yo + 0.5)), t_in, z=6)
    show(ctx, vox.tape(ctx, T["f"], C + v(0.4, -2.5), RED, 3.8, 34, -3.0), ctx.tt(1, 0) + 3.0, pop=0.25, z=7)
    ctx.avatar.look_at(C + v(0, 0.5))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
