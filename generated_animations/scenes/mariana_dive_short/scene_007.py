"""Shot 7 (scene 8): the close - the sub rests on the floor, its lamp sweeping over swarming amphipods; the question hangs in the water."""
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


T = {"q": "Would you dive?", "dark": "dark", "cold": "cold", "crush": "crushing"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    show(ctx, bands(C, W, H, 10, 0.85, 1.0), 0.0, pop=0, z=0)
    floor_y = C[1] - H / 2 + 1.0
    show(ctx, Polygon(v(C[0] - W / 2, floor_y - 1.0), v(C[0] - W / 2, floor_y), v(C[0] - 1.5, floor_y + 0.15), v(C[0] + 1.0, floor_y - 0.05), v(C[0] + W / 2, floor_y + 0.2), v(C[0] + W / 2, floor_y - 1.0),
                      stroke_width=0, fill_color="#2A2F3A", fill_opacity=1), 0.0, pop=0, z=1)
    pos = lambda: v(C[0] - 1.4, floor_y + 0.65 + 0.06 * math.sin(tl.t * 1.2))
    lamp = lambda: 0.75 + 0.25 * math.sin(tl.t * 2.0)
    sub = always_redraw(lambda: submarine(pos(), 1.0, lamp=lamp(), a=window(ctx, 0.2, None)()))
    sub._dynamic = True
    ctx.add(sub, z=4)
    base = [v(C[0] + 0.8 + 0.6 * (k % 6), floor_y + 0.4 + 0.45 * (k // 6)) for k in range(12)]
    swarm = always_redraw(lambda: VGroup(*[amphipod(p + v(0.25 * math.sin(tl.t * 1.2 + i), 0.12 * math.cos(tl.t * 1.6 + i)), 1.0, tl.t * 8 + i, window(ctx, 0.5, None)()) for i, p in enumerate(base)]))
    swarm._dynamic = True
    ctx.add(swarm, z=3)
    for i, (key, col) in enumerate((("dark", "#FFFFFF"), ("cold", "#7FD6FF"), ("crush", "#FF8FA3"))):
        show(ctx, ctx.text(T[key], 36, col, 4.0).move_to(C + v(-2.4 + 2.4 * i, 3.0)), ctx.t_of(0) + 0.5 + 0.7 * i, z=6)
    q = ctx.text(T["q"], 60, "#FFD166", 7.0).move_to(C + v(0.0, 1.4))
    show(ctx, q, ctx.tt(0, 1), z=7)
    pulse = always_redraw(lambda: Circle(radius=1.0 + 0.4 * ((tl.t * 0.8) % 1.0), stroke_color="#FFD166", stroke_width=4, fill_opacity=0,
                                         stroke_opacity=0.5 * (1 - ((tl.t * 0.8) % 1.0)) * level(ctx, 2.0, 0.5)).move_to(C + v(0.0, 1.4)))
    pulse._dynamic = True
    ctx.add(pulse, z=5)
    ctx.avatar.look_at(v(C[0], C[1] + 1.4))
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
