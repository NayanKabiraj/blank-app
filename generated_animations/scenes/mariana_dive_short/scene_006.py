"""Shot 6 (scene 7): the quiz - a 1960 bathyscaphe sinks while a clock ring fills to 4 h 47 min; the right answer lights up."""
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


T = {"q": "How long did the first dive down take?", "o1": "47 minutes", "o2": "4 h 47 min", "o3": "a whole day", "yr": "1960"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    top, bot = C[1] + H / 2 - 0.4, C[1] - H / 2 + 0.2
    show(ctx, bands(C, W, H, 10, 0.2, 1.0), 0.0, pop=0, z=0)
    t_q = ctx.tt(0, 1)
    t_ans = ctx.tt(0, 2)
    cx, cy = C[0] + 1.6, C[1] + 1.6
    ring_bg = Circle(radius=1.35, stroke_color="#3C4F7A", stroke_width=10, fill_opacity=0).move_to(v(cx, cy))
    show(ctx, ring_bg, 0.3, z=3)
    frac = lambda: level(ctx, t_q, (t_ans - t_q) + 1.8)
    ring = always_redraw(lambda: Arc(radius=1.35, start_angle=math.pi / 2, angle=-2 * math.pi * max(0.001, frac()), stroke_color="#FFD166", stroke_width=12, stroke_opacity=window(ctx, 0.3, None)()).move_to(v(cx, cy)))
    ring._dynamic = True
    ctx.add(ring, z=4)
    show(ctx, ctx.text(T["yr"], 36, "#FFFFFF", 2.0).move_to(v(cx, cy)), 0.4, z=5)
    pos = lambda: v(C[0] - 2.4 + 0.2 * math.sin(tl.t * 1.4), top - (top - bot - 1.0) * level(ctx, 0.3, t_ans + 1.8))
    sub = always_redraw(lambda: submarine(pos(), 0.8, lamp=0.6, a=window(ctx, 0.2, None)(), tilt=-1.5708 + 0.05 * math.sin(tl.t * 2)))
    sub._dynamic = True
    ctx.add(sub, z=4)
    show(ctx, ctx.text(T["q"], 30, "#EAF6FF", 7.0).move_to(C + v(0.5, -0.4)), t_q, z=6)
    from manim import RoundedRectangle as RR
    for i, (key, col) in enumerate((("o1", "#7FD6FF"), ("o2", "#9BE59B"), ("o3", "#FFD166"))):
        chip = VGroup(RR(corner_radius=0.28, width=3.2, height=0.75, stroke_color=col, stroke_width=5, fill_color="#0A1330", fill_opacity=0.92), ctx.text(T[key], 28, col, 2.8)).move_to(C + v(1.0, -1.3 - 0.95 * i))
        show(ctx, chip, t_q + 0.5 + 0.3 * i, pop=0.2, z=6)
    glow = always_redraw(lambda: RR(corner_radius=0.3, width=3.5, height=0.95, stroke_color="#9BE59B", stroke_width=9, fill_opacity=0, stroke_opacity=level(ctx, t_ans, 0.3) * (0.6 + 0.4 * math.sin(tl.t * 6))).move_to(C + v(1.0, -2.25)))
    glow._dynamic = True
    ctx.add(glow, z=7)
    ctx.avatar.look_at(v(cx, cy))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t_ans)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), run_time=0.4)
