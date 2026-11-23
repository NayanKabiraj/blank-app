"""Shot 4 (scene 5): is it hot? A thermometer falls from warm surface water to near-freezing at the bottom; ice specks drift."""
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


T = {"s": "surface  28 C", "b": "bottom  1-4 C", "q": "hot?", "n": "no: nearly freezing"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    show(ctx, bands(C, W, H, 10, 0.7, 1.0), 0.0, pop=0, z=0)
    tx, tb = C[0] - 1.2, C[1] - H / 2 + 1.5
    tube_h = 4.3
    show(ctx, VGroup(RoundedRectangle(corner_radius=0.3, width=0.7, height=tube_h + 0.5, stroke_color="#EAF6FF", stroke_width=5, fill_color="#0A1330", fill_opacity=0.8).move_to(v(tx, tb + tube_h / 2)),
                     Circle(radius=0.55, stroke_color="#EAF6FF", stroke_width=5, fill_color="#0A1330", fill_opacity=0.8).move_to(v(tx, tb - 0.3))), 0.2, z=2)
    t_fall = ctx.tt(0, 1)
    frac = lambda: 1.0 - 0.93 * level(ctx, t_fall, 2.2)
    col = lambda: interpolate_color(ManimColor("#7FD6FF"), ManimColor("#FF8A5B"), max(0.0, frac() - 0.07) / 0.93)
    merc = always_redraw(lambda: VGroup(Rectangle(width=0.32, height=max(0.04, tube_h * frac()), stroke_width=0, fill_color=col(), fill_opacity=window(ctx, 0.3, None)()).move_to(v(tx, tb + tube_h * frac() / 2)),
                                        Circle(radius=0.4, stroke_width=0, fill_color=col(), fill_opacity=window(ctx, 0.3, None)()).move_to(v(tx, tb - 0.3))))
    merc._dynamic = True
    ctx.add(merc, z=3)
    for k in range(7):
        show(ctx, Line(v(tx + 0.4, tb + tube_h * k / 6), v(tx + 0.7, tb + tube_h * k / 6), color="#EAF6FF", stroke_width=3), 0.3, pop=0, z=3)
    show(ctx, ctx.text(T["s"], 32, "#FF8A5B", 4.0).move_to(v(tx + 2.5, tb + tube_h - 0.2)), 0.5, t_out=t_fall + 1.0, z=5)
    show(ctx, ctx.text(T["b"], 40, "#7FD6FF", 5.0).move_to(v(tx + 2.5, tb + 0.4)), t_fall + 2.0, z=5)
    flakes = always_redraw(lambda: VGroup(*[Circle(radius=0.05 + 0.02 * (k % 3), stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.8 * level(ctx, t_fall + 0.8, 1.0))
                                            .move_to(v(C[0] - 3.4 + (k * 0.56 + 0.15 * math.sin(tl.t + k)) % 6.8, C[1] + H / 2 - ((tl.t * (0.6 + 0.1 * (k % 4)) + k * 0.7) % H))) for k in range(14)]))
    flakes._dynamic = True
    ctx.add(flakes, z=2)
    ctx.avatar.look_at(v(tx, tb + 2.0))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t_fall + 1.5)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
