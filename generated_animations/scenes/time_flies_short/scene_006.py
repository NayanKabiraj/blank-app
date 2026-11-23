"""Shot 6 (scene 7): quiz - a grey routine year (identical blocks) against a year of colourful firsts; the right answer is highlighted."""
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


T = {"a": "a routine year", "b": "a year of firsts"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_q, t_a = ctx.tt(0, 1), ctx.tt(0, 2)
    cols = ["#FF8FA3", "#FFD166", "#9BE59B", "#7FD6FF", "#C792EA", "#FF8A5B"]
    for k, (key, xo) in enumerate((("a", -2.0), ("b", 2.0))):
        show(ctx, ctx.text(T[key], 28, "#EAF6FF", 3.6).move_to(C + v(xo, 3.1)), 0.3, z=6)
        for i in range(12):
            x, y = C[0] + xo - 0.7 + 0.7 * (i % 3), C[1] + 2.1 - 0.62 * (i // 3)
            col = "#8892B0" if k == 0 else cols[i % len(cols)]
            show(ctx, RoundedRectangle(corner_radius=0.1, width=0.6, height=0.5, stroke_width=0, fill_color=col, fill_opacity=0.95).move_to(v(x, y)), 0.6 + 0.2 * i, pop=0.15, z=5)
    stars = always_redraw(lambda: VGroup(*[Dot(radius=0.07, color="#FFFFFF").set_opacity(window(ctx, t_q, None)() * (0.5 + 0.5 * math.sin(tl.t * 4 + i))).move_to(C + v(2.0 - 0.7 + 0.7 * (i % 3), 2.1 - 0.62 * (i // 3) + 0.38)) for i in range(12)]))
    stars._dynamic = True
    ctx.add(stars, z=6)
    glow = always_redraw(lambda: RoundedRectangle(corner_radius=0.2, width=2.6, height=2.9, stroke_color="#9BE59B", stroke_width=9, fill_opacity=0, stroke_opacity=level(ctx, t_a, 0.3) * (0.6 + 0.4 * math.sin(tl.t * 6))).move_to(C + v(2.0, 1.0)))
    glow._dynamic = True
    ctx.add(glow, z=7)
    show(ctx, ctx.text("firsts!", 60, "#9BE59B", 5.0).move_to(C + v(0, -1.0)), t_a, z=7)
    ctx.avatar.look_at(C + v(2.0, 1.0))
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.4), run_time=0.5)
