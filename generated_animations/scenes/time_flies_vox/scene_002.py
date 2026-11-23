"""Vox look - shot 2 (scenes 3-4): theory one as two torn pie cards with a red NEVER PROVEN stamp; theory two as two jars filling with memory dots."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, Sector, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import vox
from generated_animations.shared.vox import BLUE, CREAM, GREEN, INK, ORANGE, PINK, RED, YEL
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def clock(c, r, angle, a=1.0):
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=7, fill_color=CREAM, fill_opacity=a).move_to(c),
               *[Line(c + (0.82 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), c + (0.95 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), color=INK, stroke_width=4) for k in range(12)],
               Line(c, c + (0.76 * r) * v(math.sin(angle), math.cos(angle)), color=RED, stroke_width=8),
               Line(c, c + (0.5 * r) * v(math.sin(angle / 12), math.cos(angle / 12)), color=INK, stroke_width=10),
               Circle(radius=0.07 * r, stroke_width=0, fill_color=INK, fill_opacity=1).move_to(c))
    g.set_stroke(opacity=a)
    return g


T = {"a8": "AGE 8", "a40": "AGE 40", "s8": "1/8 of your life", "s40": "1/40 of your life", "np": "NEVER PROVEN", "new": "NEW THINGS", "rt": "SAME AGAIN"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.t_of(1)
    for k, (key, sk, frac, col, xo) in enumerate(((T["a8"], T["s8"], 1 / 8, BLUE, -2.0), (T["a40"], T["s40"], 1 / 40, RED, 2.0))):
        c = C + v(xo, 1.0)
        t_in = 0.4 + 1.6 * k
        card = vox.torn_card(3.3, 4.2, seed=7 + k, rot=-2 + 4 * k).move_to(c)
        show(ctx, card, t_in, pop=0.2, z=2)
        show(ctx, ctx.text(key, 44, INK, 3.0).move_to(c + v(0, 1.6)), t_in + 0.1, z=5)
        show(ctx, Circle(radius=1.05, stroke_color=INK, stroke_width=6, fill_color="#FFFFFF", fill_opacity=1).move_to(c + v(0, 0.1)), t_in + 0.2, pop=0, z=4)
        ang = lambda t_in=t_in, frac=frac: max(0.001, 2 * math.pi * frac * ease(level(ctx, t_in + 0.4, 1.4)))
        wedge = always_redraw(lambda c=c, ang=ang, col=col, t_in=t_in: Sector(radius=1.05, angle=ang(), start_angle=math.pi / 2, arc_center=c + v(0, 0.1), fill_color=col, fill_opacity=window(ctx, t_in, t1 - 0.2)(), stroke_width=0))
        wedge._dynamic = True
        ctx.add(wedge, z=5)
        show(ctx, ctx.text(sk, 26, INK, 3.0).move_to(c + v(0, -1.6)), t_in + 0.9, z=5)
    stamp = vox.tape(ctx, T["np"], C + v(0, -1.0), RED, 4.4, 34, -6.0)
    show(ctx, stamp, ctx.tt(0, 1) + 0.2, pop=0.25, z=7)
    # theory two: jars
    for k, (key, n, col, xo) in enumerate(((T["new"], 26, ORANGE, -2.0), (T["rt"], 5, "#8A8070", 2.0))):
        c = C + v(xo, 0.6)
        show(ctx, vox.torn_card(3.3, 4.8, seed=11 + k, rot=2 - 4 * k).move_to(c), t1 + 0.2, pop=0.2, z=2)
        show(ctx, ctx.text(key, 34, INK, 3.0).move_to(c + v(0, 2.0)), t1 + 0.3, z=5)
        show(ctx, Polygon(c + v(-0.8, 1.5), c + v(0.8, 1.5), c + v(0.7, -1.7), c + v(-0.7, -1.7), stroke_color=INK, stroke_width=5, fill_color="#FFFFFF", fill_opacity=1), t1 + 0.4, pop=0, z=4)
        fill = lambda n=n: min(1.0, n / 26.0) * ease(level(ctx, t1 + 1.0, 4.5))
        liquid = always_redraw(lambda c=c, col=col, fill=fill: Rectangle(width=1.25, height=max(0.02, 3.0 * fill()), stroke_width=0, fill_color=col, fill_opacity=0.85 * window(ctx, t1 + 0.4, None)()).move_to(c + v(0, -1.7 + max(0.02, 3.0 * fill()) / 2)))
        liquid._dynamic = True
        ctx.add(liquid, z=5)
        drops = always_redraw(lambda c=c, col=col, n=n: VGroup(*[Circle(radius=0.1, stroke_width=0, fill_color=col, fill_opacity=window(ctx, t1 + 0.6, None)() * (1 if ((tl.t * (0.9 if n > 10 else 0.25) + i / 5) % 1.0) < 0.85 else 0)).move_to(c + v(0.4 * math.sin(i * 2.3), 1.9 - 3.4 * ((tl.t * (0.9 if n > 10 else 0.25) + i / 5) % 1.0))) for i in range(5)]))
        drops._dynamic = True
        ctx.add(drops, z=6)
    ctx.avatar.look_at(C + v(0, 1.0))
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
