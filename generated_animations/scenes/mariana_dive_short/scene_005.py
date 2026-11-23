"""Shot 5 (scene 6): the myth 'nothing lives down there' - a fish limit line near 8,200 m, snailfish above it, amphipods swarming below."""
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


T = {"myth": "Nothing lives down there", "life": "Life!", "fish": "fish stop near 8,200 m", "snail": "snailfish", "amph": "amphipods swarm the bottom", "bot": "10,935 m"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    top, bot = C[1] + H / 2, C[1] - H / 2
    y_of = lambda d: top - (top - bot) * d / 11000.0
    show(ctx, bands(C, W, H, 10, 0.75, 1.0), 0.0, pop=0, z=0)
    t_fact, t_amph, t_fish = ctx.tt(0, 1), ctx.tt(0, 2), ctx.tt(0, 3)
    myth = ctx.text(T["myth"], 38, "#FF8FA3", 7.0).move_to(C + v(0.0, H / 2 - 0.6))
    show(ctx, myth, 0.3, t_out=t_fact + 0.3, z=6)
    show(ctx, Line(myth.get_left() + v(-0.1, 0), myth.get_right() + v(0.1, 0), color="#FF4D6D", stroke_width=7), 0.9, t_out=t_fact + 0.3, pop=0.1, z=7)
    show(ctx, ctx.text(T["life"], 56, "#9BE59B", 6.0).move_to(C + v(0.0, H / 2 - 0.7)), t_fact + 0.3, z=6)
    # the fish limit line
    show(ctx, DashedLine(v(C[0] - W / 2 + 0.2, y_of(8200)), v(C[0] + W / 2 - 0.2, y_of(8200)), color="#FFD166", stroke_width=4, dash_length=0.2), t_fish - 0.2, pop=0, z=5)
    show(ctx, ctx.text(T["fish"], 28, "#FFD166", 6.0).move_to(v(C[0] + 0.6, y_of(8200) + 0.4)), t_fish, z=6)
    # snailfish drifting above the line
    for k, (x0, d) in enumerate(((-2.0, 7200), (1.6, 7700))):
        fn = (lambda x0=x0, d=d, k=k: v(C[0] + x0 + 0.5 * math.sin(tl.t * 0.7 + k * 2), y_of(d) + 0.12 * math.sin(tl.t * 1.1 + k)))
        fish = always_redraw(lambda fn=fn, k=k: snailfish(fn(), 0.9, tl.t * 6 + k, window(ctx, t_fact + 0.3, None)()))
        fish._dynamic = True
        ctx.add(fish, z=4)
    show(ctx, ctx.text(T["snail"], 26, "#F6B8C8", 3.0).move_to(v(C[0] - 1.9, y_of(7200) + 0.65)), t_fact + 0.6, z=6)
    # amphipods swarm at the very bottom
    base = [v(C[0] - 3.0 + 0.7 * (k % 9), y_of(10150) + 0.35 * (k // 9)) for k in range(18)]
    swarm = always_redraw(lambda: VGroup(*[amphipod(p + v(0.3 * math.sin(tl.t * 1.3 + i), 0.18 * math.cos(tl.t * 1.7 + i * 1.3)), 1.0, tl.t * 8 + i, window(ctx, t_amph - 0.3, None)()) for i, p in enumerate(base)]))
    swarm._dynamic = True
    ctx.add(swarm, z=4)
    show(ctx, ctx.text(T["amph"], 28, "#F29A52", 7.0).move_to(v(C[0], y_of(9000))), t_amph, z=6)
    show(ctx, ctx.text(T["bot"], 26, "#EAF6FF", 3.0).move_to(v(C[0] + W / 2 - 1.0, bot + 0.3)), t_amph + 0.2, z=6)
    ctx.avatar.look_at(v(C[0], y_of(9800)))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), gestures.point_at(ctx.avatar, v(C[0], y_of(9800)), 0.5), run_time=0.6)
