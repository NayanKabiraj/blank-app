"""Shot 5 (scene 6): the survey - a row of people from 14 to 94 appears (colour by age), then two decade bars: the older felt it pass faster."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Arrow, Circle, DashedLine, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, Sector, VGroup,
                   always_redraw)

from generated_animations.avatar import expressions, gestures
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def chip(ctx, text, color, center, w=3.6, size=30):
    return VGroup(RoundedRectangle(corner_radius=0.26, width=w, height=0.78, stroke_color=color, stroke_width=5, fill_color="#0A1330", fill_opacity=0.92),
                  ctx.text(text, size, color, w - 0.4)).move_to(center)


def clock(c, r, angle, a=1.0, hand="#FFD166"):
    """A round clock face with one fast hand and one slow hand (angle in radians, clockwise from 12)."""
    g = VGroup(Circle(radius=r, stroke_color="#EAF6FF", stroke_width=6, fill_color="#10163A", fill_opacity=0.95 * a).move_to(c),
               *[Line(c + (0.86 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), c + (0.96 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), color="#EAF6FF", stroke_width=3) for k in range(12)],
               Line(c, c + (0.78 * r) * v(math.sin(angle), math.cos(angle)), color=hand, stroke_width=7),
               Line(c, c + (0.5 * r) * v(math.sin(angle / 12), math.cos(angle / 12)), color="#FF8FA3", stroke_width=9),
               Circle(radius=0.07 * r, stroke_width=0, fill_color="#FFFFFF", fill_opacity=1).move_to(c))
    g.set_stroke(opacity=a)
    return g


T = {"n": "499 people", "r": "aged 14 to 94", "y": "a decade, younger", "o": "a decade, older", "f": "felt faster"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_n = ctx.tt(0, 0)
    show(ctx, ctx.text(T["n"], 56, "#FFFFFF", 6.0).move_to(C + v(0, 3.2)), 0.3, z=6)
    show(ctx, ctx.text(T["r"], 34, "#FFD166", 6.0).move_to(C + v(0, 2.4)), 0.8, z=6)
    N = 15
    for i in range(N):
        f = i / (N - 1)
        col = "#7FD6FF" if f < 0.34 else ("#FFD166" if f < 0.67 else "#FF8A5B")
        x = C[0] - 3.2 + 6.4 * f
        show(ctx, VGroup(Circle(radius=0.2, stroke_width=0, fill_color=col, fill_opacity=1).move_to(v(x, C[1] + 1.3)), Rectangle(width=0.32, height=0.5, stroke_width=0, fill_color=col, fill_opacity=0.9).move_to(v(x, C[1] + 0.85))), 0.9 + 0.12 * i, pop=0.12, z=5)
    for k, (key, wd, col, yo) in enumerate((("y", 6.0, "#7FD6FF", -0.4), ("o", 3.4, "#FF8A5B", -1.7))):
        t_in = t_n + 1.0 + 1.0 * k
        w = lambda wd=wd, t_in=t_in: wd * ease(level(ctx, t_in, 1.6))
        bar = always_redraw(lambda wd=wd, col=col, yo=yo, w=w: Rectangle(width=max(0.02, w()), height=0.6, stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, 0.3, None)()).move_to(v(C[0] - 3.2 + max(0.02, w()) / 2, C[1] + yo)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 28, col, 5.0).move_to(v(C[0], C[1] + yo + 0.6)), t_in, z=6)
    show(ctx, ctx.text(T["f"], 44, "#FF8A5B", 6.0).move_to(C + v(0, -3.0)), t_n + 3.2, z=7)
    ctx.avatar.look_at(C + v(0, 0.5))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
