"""Shot 3 (scene 4): theory two - new things become many memory dots that fill a jar; routine gives a few and the jar stays low."""
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


T = {"new": "new things", "rt": "same again", "jar1": "long-feeling year", "jar2": "short-feeling year"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_in = ctx.tt(0, 1)
    for k, (key, jk, n, col, xo) in enumerate((("new", "jar1", 26, "#FFD166", -2.0), ("rt", "jar2", 5, "#8892B0", 2.0))):
        c = C + v(xo, 0.0)
        show(ctx, Polygon(c + v(-0.95, 2.0), c + v(0.95, 2.0), c + v(0.8, -1.8), c + v(-0.8, -1.8), stroke_color="#EAF6FF", stroke_width=5, fill_color="#10163A", fill_opacity=0.55), 0.3, z=3)
        show(ctx, ctx.text(T[key], 32, col, 3.4).move_to(c + v(0, 2.7)), 0.4, z=6)
        fill = lambda n=n, t_in=t_in: min(1.0, n / 26.0) * ease(level(ctx, t_in - 0.4, 4.5))
        liquid = always_redraw(lambda c=c, col=col, fill=fill: Rectangle(width=1.5, height=max(0.02, 3.5 * fill()), stroke_width=0, fill_color=col, fill_opacity=0.55 * window(ctx, 0.3, None)()).move_to(c + v(0, -1.8 + max(0.02, 3.5 * fill()) / 2)))
        liquid._dynamic = True
        ctx.add(liquid, z=4)
        drops = always_redraw(lambda c=c, col=col, n=n: VGroup(*[Circle(radius=0.11, stroke_width=0, fill_color=col, fill_opacity=window(ctx, 0.5, None)() * (1 if ((tl.t * (0.9 if n > 10 else 0.25) + i / 6) % 1.0) < 0.85 else 0)).move_to(c + v(0.5 * math.sin(i * 2.3), 3.0 - 4.6 * ((tl.t * (0.9 if n > 10 else 0.25) + i / 6) % 1.0))) for i in range(6)]))
        drops._dynamic = True
        ctx.add(drops, z=5)
        show(ctx, ctx.text(T[jk], 26, col, 3.6).move_to(c + v(0, -2.5)), t_in + 2.2, z=6)
    ctx.avatar.look_at(C + v(-2.0, 0.0))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
