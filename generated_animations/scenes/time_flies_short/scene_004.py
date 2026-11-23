"""Shot 4 (scene 5): the holiday effect - a trip timeline gets crowded with firsts (many ticks), the same stretch at home stays sparse; looking back, the trip is long."""
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


T = {"trip": "the trip", "home": "ordinary weeks", "back": "looking back..."}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_q = ctx.tt(0, 1)
    for k, (key, n, col, yo) in enumerate((("trip", 24, "#FFD166", 1.8), ("home", 5, "#8892B0", -0.6))):
        y = C[1] + yo
        x0, x1 = C[0] - 3.2, C[0] + 3.2
        show(ctx, Line(v(x0, y), v(x1, y), color="#EAF6FF", stroke_width=5), 0.3, pop=0, z=3)
        show(ctx, ctx.text(T[key], 32, col, 4.0).move_to(v(C[0], y + 0.9)), 0.4, z=6)
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5) / n
            show(ctx, VGroup(Line(v(x, y - 0.3), v(x, y + 0.3), color=col, stroke_width=5), Circle(radius=0.09, stroke_width=0, fill_color=col, fill_opacity=1).move_to(v(x, y + 0.45))), 0.6 + (t_q - 0.4) * i / n if k == 0 else 0.6 + 2.5 * i / n, pop=0.15, z=5)
    arr = always_redraw(lambda: Arrow(v(C[0] - 3.2, C[1] - 2.3), v(C[0] - 3.2 + 6.4 * ease(level(ctx, t_q, 2.0)) + 0.05, C[1] - 2.3), buff=0, color="#7FD6FF", stroke_width=8, stroke_opacity=window(ctx, t_q, None)()).set_fill(opacity=window(ctx, t_q, None)()))
    arr._dynamic = True
    ctx.add(arr, z=5)
    show(ctx, ctx.text(T["back"], 34, "#7FD6FF", 6.0).move_to(C + v(0, -3.0)), t_q + 0.2, z=6)
    ctx.avatar.look_at(C + v(0, 1.8))
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), run_time=0.5)
