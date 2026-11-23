"""Shot 2 (scene 3): light dies with depth - sunlight shafts fade, the sub's lamp switches on below 1,000 m."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, DashedLine, Dot, Ellipse, Line, ManimColor, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw, interpolate_color

from generated_animations.avatar import expressions, gestures
from generated_animations.timed import level, show, window

TOP, BOT = "#2AA7DF", "#02050F"


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def bands(C, W, H, n=10, z0=0.0, z1=1.0):
    """The water column as stacked bands, bright at the top, near-black at the bottom (z0..z1 = how much of the gradient)."""
    g = VGroup()
    for i in range(n):
        f = z0 + (z1 - z0) * (i / (n - 1))
        col = interpolate_color(ManimColor(TOP), ManimColor(BOT), min(1.0, f ** 0.65))
        g.add(Rectangle(width=W, height=H / n + 0.02, stroke_width=0, fill_color=col, fill_opacity=1).move_to(C + v(0, H / 2 - (i + 0.5) * H / n)))
    return g


def submarine(p, s=1.0, lamp=0.0, a=1.0, tilt=0.0):
    """A small yellow research sub facing right; `lamp` 0..1 lights a headlight cone."""
    body = VGroup(
        RoundedRectangle(corner_radius=0.36 * s, width=1.5 * s, height=0.8 * s, fill_color="#F4C95D", fill_opacity=1, stroke_color="#8A6A12", stroke_width=3).move_to(p),
        Circle(radius=0.2 * s, fill_color="#BFE9FF", fill_opacity=1, stroke_color="#33425B", stroke_width=3).move_to(p + v(0.36 * s, 0.04 * s)),
        Rectangle(width=0.26 * s, height=0.26 * s, fill_color="#C99A1E", fill_opacity=1, stroke_width=0).move_to(p + v(-0.2 * s, 0.52 * s)),
        Rectangle(width=0.1 * s, height=0.4 * s, fill_color="#8A6A12", fill_opacity=1, stroke_width=0).move_to(p + v(-0.8 * s, 0.0)),
    )
    body.set_opacity(a)
    cone = Polygon(p + v(0.78 * s, 0.1 * s), p + v(2.8 * s, 1.0 * s), p + v(2.8 * s, -0.9 * s), p + v(0.78 * s, -0.02 * s),
                   stroke_width=0, fill_color="#FFF6C8", fill_opacity=0.32 * lamp * a)
    g = VGroup(cone, body)
    if tilt:
        g.rotate(tilt, about_point=p)
    return g


def bubbles(p_fn, tl, n=6, a_fn=None):
    g = VGroup()
    a = 1.0 if a_fn is None else a_fn()
    p = p_fn()
    for k in range(n):
        ph = (tl.t * 0.9 + k / n) % 1.0
        g.add(Circle(radius=0.05 + 0.03 * ((k * 7) % 3), stroke_color="#D8F3FF", stroke_width=2, fill_opacity=0).move_to(p + v(-0.9 - 0.12 * math.sin(k * 2 + tl.t * 3), 0.2 + 1.3 * ph)).set_stroke(opacity=a * (1 - ph) * 0.8))
    return g


def amphipod(p, s=1.0, ph=0.0, a=1.0):
    """A shrimp-like amphipod: curved orange body, a few legs."""
    g = VGroup(Ellipse(width=0.34 * s, height=0.15 * s, fill_color="#F29A52", fill_opacity=1, stroke_color="#A85A1E", stroke_width=1.5).move_to(p),
               Ellipse(width=0.16 * s, height=0.1 * s, fill_color="#F7B27A", fill_opacity=1, stroke_width=0).move_to(p + v(0.17 * s, 0.03 * s)),
               Line(p + v(-0.1 * s, -0.06 * s), p + v((-0.15 + 0.05 * math.sin(ph)) * s, -0.18 * s), color="#A85A1E", stroke_width=2),
               Line(p + v(0.05 * s, -0.06 * s), p + v((0.0 + 0.05 * math.sin(ph + 1)) * s, -0.18 * s), color="#A85A1E", stroke_width=2))
    return g.set_opacity(a)


def snailfish(p, s=1.0, ph=0.0, a=1.0):
    """A pale pink snailfish with a wavy tail."""
    w = 0.1 * math.sin(ph)
    g = VGroup(Ellipse(width=0.95 * s, height=0.5 * s, fill_color="#F6B8C8", fill_opacity=1, stroke_color="#B56378", stroke_width=2).move_to(p),
               Polygon(p + v(-0.42 * s, 0), p + v(-0.85 * s, (0.3 + w) * s), p + v(-0.85 * s, (-0.3 + w) * s), fill_color="#EFA2B6", fill_opacity=1, stroke_color="#B56378", stroke_width=2),
               Circle(radius=0.05 * s, fill_color="#2B2B2B", fill_opacity=1, stroke_width=0).move_to(p + v(0.25 * s, 0.07 * s)))
    return g.set_opacity(a)


T = {"sun": "SUNLIGHT  0-200 m", "tw": "TWILIGHT  to 1,000 m", "dk": "PITCH DARK", "dk2": "below 1,000 m"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    top, bot = C[1] + H / 2, C[1] - H / 2
    scale = 2000.0                                          # this shot shows 0-2,000 m
    y_of = lambda d: top - (top - bot) * d / scale
    show(ctx, bands(C, W, H, 10, 0.0, 0.95), 0.0, pop=0, z=0)
    t_tw, t_dk = ctx.tt(0, 1), ctx.tt(0, 2)
    # sun disc and shafts that shimmer, brightest at the top
    show(ctx, Circle(radius=0.55, fill_color="#FFD84D", fill_opacity=1, stroke_width=0).move_to(v(C[0] + 2.6, top - 0.1)), 0.2, z=2)
    shafts = always_redraw(lambda: VGroup(*[Polygon(v(C[0] + 2.6 - 0.35, top - 0.3), v(C[0] + 2.6 + 0.35, top - 0.3),
                                                    v(C[0] + 2.0 - 1.1 * k + 0.35, y_of(260 + 40 * k)), v(C[0] + 2.0 - 1.1 * k - 0.35, y_of(260 + 40 * k)),
                                                    stroke_width=0, fill_color="#FFF3B0", fill_opacity=(0.22 + 0.1 * math.sin(tl.t * 2 + k)) * window(ctx, 0.3, t_dk)()) for k in range(4)]))
    shafts._dynamic = True
    ctx.add(shafts, z=1)
    for d, txt, col, t in ((100, T["sun"], "#FFF3B0", 0.6), (600, T["tw"], "#9FD8FF", t_tw), (1500, T["dk"], "#FFFFFF", t_dk)):
        show(ctx, ctx.text(txt, 34, col, 6.0).move_to(v(C[0] - 0.6, y_of(d))), t, z=6)
    show(ctx, ctx.text(T["dk2"], 28, "#FFD166", 5.0).move_to(v(C[0] - 0.6, y_of(1500) - 0.5)), t_dk + 0.4, z=6)
    for d in (200, 1000):                                     # the two boundaries
        show(ctx, DashedLine(v(C[0] - W / 2 + 0.3, y_of(d)), v(C[0] + W / 2 - 0.3, y_of(d)), color="#FFFFFF", stroke_width=2, dash_length=0.15), 0.5 if d == 200 else t_tw + 0.3, pop=0, z=5)
    f = lambda: level(ctx, 0.3, ctx.t_of(0) + 6.0)
    pos = lambda: v(C[0] - 2.6 + 0.2 * math.sin(tl.t * 1.5), y_of(60 + 1500 * f()))
    lamp = lambda: level(ctx, t_dk + 0.2, 0.6)
    sub = always_redraw(lambda: submarine(pos(), 0.8, lamp=lamp(), a=window(ctx, 0.2, None)(), tilt=0.04 * math.sin(tl.t * 2)))
    sub._dynamic = True
    ctx.add(sub, z=4)
    ctx.avatar.look_at(pos)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t_dk)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
