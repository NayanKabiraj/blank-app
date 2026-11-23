"""Shot 5 (chapter 5, scenes 22-26): +10 cm since 1993 (a rising line), the rate doubled (two gauges), 'not by 2100' timeline, hard to reverse, the closing question over the flooded map."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Arrow, Circle, DashedLine, Dot, Ellipse, Line, ManimColor, Polygon, Rectangle, RoundedRectangle, VGroup,
                   always_redraw, interpolate_color)

from generated_animations.avatar import expressions, gestures
from generated_animations.timed import level, show, window

ICE, SEA, LAND, SKYLINE = "#EAF6FF", "#2E8BD8", "#3C6E47", "#C9CFE0"


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def coast(C, W, H, melt, a, rise=2.2, ice_t=1.5):
    """A cross-section: ice on a highland, a city on the coastal plain, the sea on the right.
    `melt` (0..1) shrinks the ice and raises the sea over the city. `a` = overall opacity. Constant part count."""
    X0, X1 = C[0] - W / 2, C[0] + W / 2
    base = C[1] - H / 2
    plain = base + 0.9
    xh, xp, xc = X0 + 3.0, C[0] + 0.1 - 1.0, C[0] + 1.6
    g = plain + 2.2
    m = ease(melt)
    L = plain - 0.05 + rise * m
    land = Polygon(v(X0, base), v(X0, g), v(xh, g), v(xp, plain), v(xc, plain), v(xc + 0.9, base + 0.2), v(X1, base + 0.2), v(X1, base),
                   stroke_width=0, fill_color=LAND, fill_opacity=a)
    T = ice_t * (1 - m) + 0.02
    ice = Polygon(v(X0, g), v(X0, g + T), v(xh - 0.6, g + T * 0.8), v(xh + 0.4, g), stroke_width=0, fill_color=ICE, fill_opacity=a)
    hs = [0.5, 0.9, 0.7, 1.3, 0.6, 1.0, 0.45]
    city = VGroup(*[Rectangle(width=0.36, height=h, stroke_width=0, fill_color=SKYLINE, fill_opacity=a).move_to(v(xp + 0.35 + 0.42 * i, plain + h / 2)) for i, h in enumerate(hs)])
    ocean = Rectangle(width=X1 - xc, height=max(0.01, L - base), stroke_width=0, fill_color=SEA, fill_opacity=0.72 * a).move_to(v((xc + X1) / 2, base + max(0.01, L - base) / 2))
    flood_h = max(0.0, L - plain)
    flood = Rectangle(width=xc - xp, height=max(0.001, flood_h), stroke_width=0, fill_color=SEA, fill_opacity=0.72 * a * (1 if flood_h > 0.001 else 0)).move_to(v((xp + xc) / 2, plain + max(0.001, flood_h) / 2))
    xe = max(xh, xp - flood_h * (xp - xh) / rise)
    slope = Polygon(v(xp, plain), v(xp, plain + max(0.001, flood_h)), v(xe, plain + max(0.001, flood_h)), stroke_width=0, fill_color=SEA, fill_opacity=0.72 * a * (1 if flood_h > 0.001 else 0))
    return VGroup(land, ice, city, ocean, flood, slope)


def chip(ctx, text, color, center, w=3.6, size=30):
    return VGroup(RoundedRectangle(corner_radius=0.26, width=w, height=0.78, stroke_color=color, stroke_width=5, fill_color="#0A1330", fill_opacity=0.92),
                  ctx.text(text, size, color, w - 0.4)).move_to(center)


def counter(ctx, text, color, center, size=60):
    return ctx.text(text, size, color, 6.0).move_to(center)


T = {"cm": "+10 cm", "since": "since 1993", "r93": "1993: 2.1 mm/yr", "rn": "now: 4.5 mm/yr", "cm2": "centuries to thousands of years", "rev": "slow, but hard to reverse", "q": "Which coast first?", "y": "1993", "n": "today"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t22, t23, t24, t25, t26 = [ctx.t_of(i) for i in range(5)]
    base = C[1] - H / 2
    x0, x1 = C[0] - 3.8, C[0] + 3.8
    show(ctx, Line(v(x0, base + 0.6), v(x1, base + 0.6), color="#EAF6FF", stroke_width=4), 0.2, t_out=t23 - 0.2, pop=0, z=3)
    show(ctx, ctx.text(T["y"], 26, "#EAF6FF", 3.0).move_to(v(x0, base + 0.2)), 0.3, t_out=t23 - 0.2, z=6)
    show(ctx, ctx.text(T["n"], 26, "#EAF6FF", 3.0).move_to(v(x1, base + 0.2)), 0.3, t_out=t23 - 0.2, z=6)
    prog = lambda: ease(level(ctx, 0.8, 4.5))
    curve = always_redraw(lambda: VGroup(*[Line(v(x0 + (x1 - x0) * k / 40 * prog(), base + 0.6 + 2.4 * ((k / 40 * prog()) ** 1.5)), v(x0 + (x1 - x0) * (k + 1) / 40 * prog(), base + 0.6 + 2.4 * (((k + 1) / 40 * prog()) ** 1.5)), color="#7FD6FF", stroke_width=9, stroke_opacity=window(ctx, 0.5, t23 - 0.2)()) for k in range(40)]))
    curve._dynamic = True
    ctx.add(curve, z=4)
    show(ctx, ctx.text(T["cm"], 80, "#FFD166", 5.0).move_to(C + v(-2.2, 2.0)), 2.2, t_out=t23 - 0.2, z=7)
    show(ctx, ctx.text(T["since"], 32, "#EAF6FF", 5.0).move_to(C + v(-2.2, 1.0)), 2.6, t_out=t23 - 0.2, z=7)
    for k, (key, val, col) in enumerate((("r93", 2.1, "#7FD6FF"), ("rn", 4.5, "#FF8FA3"))):
        y = base + 2.4 - 1.5 * k
        t_in = t23 + 0.4
        w = lambda val=val, t_in=t_in: 7.0 * (val / 4.5) * ease(level(ctx, t_in, 3.5))
        bar = always_redraw(lambda y=y, col=col, w=w: Rectangle(width=max(0.02, w()), height=0.7, stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t23, t24 - 0.2)()).move_to(v(C[0] - 3.8 + max(0.02, w()) / 2, y)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 32, col, 5.0).move_to(v(C[0] - 1.2, y + 0.65)), t_in, t_out=t24 - 0.2, z=6)
    show(ctx, ctx.text("2x", 90, "#FFD166", 4.0).move_to(C + v(3.8, 0.5)), ctx.tt(1, 1) + 0.3, t_out=t24 - 0.2, z=7)
    d = ctx.text("2100", 90, "#FF8FA3", 5.0).move_to(C + v(-2.4, 1.7))
    show(ctx, d, t24 + 0.3, t_out=t25 - 0.2, z=6)
    show(ctx, Line(d.get_left() + v(-0.2, 0), d.get_right() + v(0.2, 0), color="#FFFFFF", stroke_width=9), t24 + 1.5, t_out=t25 - 0.2, z=7)
    arr = always_redraw(lambda: Arrow(v(C[0] - 3.5, base + 1.0), v(C[0] - 3.5 + 7.2 * ease(level(ctx, t24 + 2.0, 3.0)) + 0.05, base + 1.0), buff=0, color="#FFD166", stroke_width=10, stroke_opacity=window(ctx, t24 + 1.0, t25 - 0.2)()).set_fill(opacity=window(ctx, t24 + 1.0, t25 - 0.2)()))
    arr._dynamic = True
    ctx.add(arr, z=5)
    show(ctx, ctx.text(T["cm2"], 32, "#FFD166", 9.0).move_to(C + v(0.2, base - C[1] + 1.9)), t24 + 2.4, t_out=t25 - 0.2, z=6)
    sh = lambda: ease(level(ctx, t25 + 0.6, 6.0))
    cap = always_redraw(lambda: Polygon(v(C[0] - 2.5, base + 1.0), v(C[0] - 2.5 + 5.0 * (1 - 0.7 * sh()), base + 1.0), v(C[0] - 2.5 + 3.0 * (1 - 0.7 * sh()), base + 1.0 + 1.4 * (1 - 0.5 * sh())), v(C[0] - 2.5 + 0.8, base + 1.0 + 1.0 * (1 - 0.5 * sh())),
                                       stroke_width=0, fill_color=ICE, fill_opacity=0.95 * window(ctx, t25, t26 - 0.2)()))
    cap._dynamic = True
    ctx.add(cap, z=4)
    show(ctx, ctx.text(T["rev"], 38, "#FFFFFF", 8.0).move_to(C + v(0.0, 2.6)), t25 + 0.4, t_out=t26 - 0.2, z=7)
    al = window(ctx, t26, None)
    sc = always_redraw(lambda: coast(C, W, H, 1.0, al()))
    sc._dynamic = True
    ctx.add(sc, z=2)
    show(ctx, ctx.text(T["q"], 68, "#FFD166", 8.0).move_to(C + v(1.0, 2.1)), t26 + 0.6, z=7)
    pulse = always_redraw(lambda: Circle(radius=1.0 + 0.5 * ((tl.t * 0.7) % 1.0), stroke_color="#FFD166", stroke_width=4, fill_opacity=0, stroke_opacity=0.5 * (1 - ((tl.t * 0.7) % 1.0)) * level(ctx, t26 + 0.6, 0.5)).move_to(C + v(3.2, -0.2)))
    pulse._dynamic = True
    ctx.add(pulse, z=6)
    ctx.avatar.look_at(v(C[0] + 2.0, C[1]))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t26)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
