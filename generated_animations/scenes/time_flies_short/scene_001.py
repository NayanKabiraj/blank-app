"""Shot 1 (scenes 1-2): a clock whose hand starts slow (age 8) and races (now); the intro lists what the video shows."""
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


T = {"a8": "age 8", "a40": "now", "intro": "In this video", "c1": "two old theories", "c2": "a memory trick", "c3": "how to slow it down"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    cc = C + v(0, 2.3)
    ang = lambda: 0.35 * tl.t + 0.32 * tl.t * tl.t          # starts slow, keeps accelerating
    al = window(ctx, 0.2, None)
    face = always_redraw(lambda: clock(cc, 1.4, ang(), al()))
    face._dynamic = True
    ctx.add(face, z=3)
    show(ctx, ctx.text(T["a8"], 44, "#7FD6FF", 4.0).move_to(C + v(-2.6, 3.0)), 0.4, t_out=ctx.tt(0, 1) + 0.2, z=6)
    show(ctx, ctx.text(T["a40"], 44, "#FF8FA3", 4.0).move_to(C + v(2.6, 3.0)), ctx.tt(0, 1) + 0.4, z=6)
    trail = always_redraw(lambda: VGroup(*[Arc(radius=1.65, start_angle=math.pi / 2 - ang(), angle=-0.4 - 0.08 * k, stroke_color="#FFD166", stroke_width=6 - k, stroke_opacity=0.35 * al() * min(1.0, tl.t / 6.0)).move_to(cc) for k in range(3)]))
    trail._dynamic = True
    ctx.add(trail, z=2)
    show(ctx, ctx.text(T["intro"], 38, "#FFFFFF", 5.0).move_to(C + v(0, 0.35)), t1 + 0.1, z=7)
    for n, (key, col) in enumerate((("c1", "#7FD6FF"), ("c2", "#FFD166"), ("c3", "#9BE59B"))):
        show(ctx, chip(ctx, f"{n + 1}  {T[key]}", col, C + v(0, -0.6 - 0.95 * n), 4.4, 28), t1 + 1.0 + 1.1 * n, pop=0.25, z=7)
    ctx.avatar.look_at(cc)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(ctx.tt(0, 1))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
