"""Shot 2 (scene 3): theory one - a year as a slice of life: one eighth at age 8, one fortieth at 40 (two pies with shrinking wedges)."""
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


T = {"a8": "age 8", "a40": "age 40", "w8": "1/8 of your life", "w40": "1/40 of your life", "np": "never proven"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    for k, (key, wk, frac, col, xo) in enumerate((("a8", "w8", 1 / 8, "#7FD6FF", -2.0), ("a40", "w40", 1 / 40, "#FF8FA3", 2.0))):
        c = C + v(xo, 1.2)
        t_in = 0.4 + 1.9 * k
        show(ctx, Circle(radius=1.5, stroke_color="#3C4F7A", stroke_width=5, fill_color="#10163A", fill_opacity=0.9).move_to(c), t_in, pop=0, z=3)
        ang = lambda t_in=t_in, frac=frac: max(0.001, 2 * math.pi * frac * ease(level(ctx, t_in + 0.3, 1.6)))
        wedge = always_redraw(lambda c=c, ang=ang, col=col, t_in=t_in: Sector(radius=1.5, angle=ang(), start_angle=math.pi / 2, arc_center=c, fill_color=col, fill_opacity=0.95 * window(ctx, t_in, None)(), stroke_width=0))
        wedge._dynamic = True
        ctx.add(wedge, z=4)
        show(ctx, ctx.text(T[key], 40, col, 3.2).move_to(c + v(0, 2.2)), t_in, z=6)
        show(ctx, ctx.text(T[wk], 28, "#EAF6FF", 3.6).move_to(c + v(0, -2.2)), t_in + 0.9, z=6)
    show(ctx, ctx.text("1 year", 34, "#FFD166", 3.0).move_to(C + v(0, 1.2)), 1.0, z=7)
    show(ctx, ctx.text(T["np"], 48, "#FFD166", 7.0).move_to(C + v(0, -3.0)), ctx.tt(0, 2) + 0.2, z=7)
    ctx.avatar.look_at(C + v(0, 1.2))
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
