"""Shot 4 (chapter 4, scenes 16-21): 65 m - the city floods, the waterline moves inland, height comparison, land springing back, fresh water and currents, the quiz."""
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


T = {"n": "+65 m", "ft": "nearly 215 ft", "inl": "the waterline moves inland", "h": "house", "t": "10-storey tower", "all": "total melt", "up": "ground springs back", "p": "ice presses down", "fw": "fresh meltwater", "cur": "ocean currents may slow",
     "g": "Greenland", "wa": "West Antarctica", "gv": "7 m", "wv": "3 m", "ok": "Greenland!"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t16, t17, t18, t19, t20, t21 = [ctx.t_of(i) for i in range(6)]
    base = C[1] - H / 2
    melt = lambda: level(ctx, 0.5, 5.0)
    al = window(ctx, 0.2, t18 - 0.2)
    sc = always_redraw(lambda: coast(C, W, H, melt(), al(), rise=2.2, ice_t=1.5))
    sc._dynamic = True
    ctx.add(sc, z=2)
    show(ctx, ctx.text(T["n"], 90, "#FFD166", 5.0).move_to(C + v(3.2, 1.7)), 1.0, t_out=t18 - 0.2, z=7)
    show(ctx, ctx.text(T["ft"], 30, "#EAF6FF", 6.0).move_to(C + v(3.2, 0.7)), 1.8, t_out=t18 - 0.2, z=7)
    show(ctx, ctx.text(T["inl"], 32, "#BFE9FF", 8.0).move_to(C + v(-1.4, 2.5)), t17 + 0.3, t_out=t18 - 0.2, z=7)
    show(ctx, Arrow(C + v(1.2, 1.2), C + v(-2.0, 1.2), buff=0, color="#BFE9FF", stroke_width=7), t17 + 0.5, t_out=t18 - 0.2, z=7)
    for k, (key, hh, col) in enumerate((("h", 0.45, "#7FD6FF"), ("t", 1.5, "#FFD166"), ("all", 3.6, "#FF8FA3"))):
        t_in = t18 + 0.4 + 1.3 * k
        grow = (lambda t_in=t_in: ease(level(ctx, t_in, 1.2)))
        xo = -2.8 + 2.8 * k
        bar = always_redraw(lambda hh=hh, col=col, xo=xo, grow=grow: Rectangle(width=1.5, height=max(0.02, hh * grow()), stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t18, t19 - 0.2)()).move_to(v(C[0] + xo + 1.0, base + 0.5 + max(0.02, hh * grow()) / 2)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 26, col, 3.4).move_to(v(C[0] + xo + 1.0, base + 0.2)), t_in, t_out=t19 - 0.2, z=6)
        show(ctx, ctx.text(("7 m", "30 m", "65 m")[k], 40, col, 3.0).move_to(v(C[0] + xo + 1.0, base + 0.5 + hh + 0.5)), t_in + 0.8, t_out=t19 - 0.2, z=6)
    gx = C[0] + 0.8
    ground = always_redraw(lambda: Rectangle(width=6.0, height=1.0, stroke_width=0, fill_color="#5A4A3A", fill_opacity=window(ctx, t19, t20 - 0.2)()).move_to(v(gx, base + 1.1 + 0.9 * ease(level(ctx, t19 + 2.5, 5.0)))))
    ground._dynamic = True
    ctx.add(ground, z=3)
    icecap = always_redraw(lambda: Rectangle(width=6.0, height=1.4 * (1 - ease(level(ctx, t19 + 1.0, 3.0))) + 0.01, stroke_width=0, fill_color=ICE, fill_opacity=window(ctx, t19, t20 - 0.2)()).move_to(v(gx, base + 1.6 + 0.9 * ease(level(ctx, t19 + 2.5, 5.0)) + (1.4 * (1 - ease(level(ctx, t19 + 1.0, 3.0))) + 0.01) / 2)))
    icecap._dynamic = True
    ctx.add(icecap, z=4)
    show(ctx, ctx.text(T["p"], 28, "#BFE9FF", 6.0).move_to(v(gx, base + 3.9)), t19 + 0.3, t_out=ctx.tt(3, 1), z=6)
    show(ctx, Arrow(v(gx + 3.6, base + 1.2), v(gx + 3.6, base + 2.5), buff=0, color="#9BE59B", stroke_width=8), t19 + 3.0, t_out=t20 - 0.2, z=6)
    show(ctx, ctx.text(T["up"], 30, "#9BE59B", 6.0).move_to(v(gx, base + 3.2)), ctx.tt(3, 1) + 0.3, t_out=t20 - 0.2, z=6)
    cc = v(C[0] + 0.8, base + 2.1)
    show(ctx, Circle(radius=1.6, stroke_color="#3C4F7A", stroke_width=3, fill_color=SEA, fill_opacity=0.35).move_to(cc), t20 + 0.2, t_out=t21 - 0.2, pop=0, z=3)
    arrows = always_redraw(lambda: VGroup(*[Arrow(cc + 1.6 * v(math.cos(tl.t * 2.0 / (1.0 + 0.9 * level(ctx, t20 + 3.0, 6.0)) + a), math.sin(tl.t * 2.0 / (1.0 + 0.9 * level(ctx, t20 + 3.0, 6.0)) + a)),
                                            cc + 1.6 * v(math.cos(tl.t * 2.0 / (1.0 + 0.9 * level(ctx, t20 + 3.0, 6.0)) + a + 0.5), math.sin(tl.t * 2.0 / (1.0 + 0.9 * level(ctx, t20 + 3.0, 6.0)) + a + 0.5)), buff=0, color="#7FD6FF", stroke_width=7,
                                            max_tip_length_to_length_ratio=0.5, stroke_opacity=window(ctx, t20 + 0.2, t21 - 0.2)()).set_fill(opacity=window(ctx, t20 + 0.2, t21 - 0.2)()) for a in (0, 2.094, 4.189)]))
    arrows._dynamic = True
    ctx.add(arrows, z=5)
    show(ctx, ctx.text(T["fw"], 32, "#EAF6FF", 6.0).move_to(cc + v(-4.0, 1.4)), t20 + 0.4, t_out=t21 - 0.2, z=6)
    show(ctx, ctx.text(T["cur"], 30, "#FFD166", 6.0).move_to(cc + v(4.0, -1.2)), ctx.tt(4, 1) + 0.3, t_out=t21 - 0.2, z=6)
    for k, (key, hh, col, val) in enumerate((("g", 2.6, "#7FD6FF", "gv"), ("wa", 1.1, "#FF8FA3", "wv"))):
        t_in = t21 + 0.8 + 1.2 * k
        grow = (lambda t_in=t_in: ease(level(ctx, t_in, 1.2)))
        xo = -1.6 + 3.2 * k
        bar = always_redraw(lambda hh=hh, col=col, xo=xo, grow=grow: Rectangle(width=1.7, height=max(0.02, hh * grow()), stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t21, None)()).move_to(v(C[0] + xo + 1.0, base + 0.5 + max(0.02, hh * grow()) / 2)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 26, col, 3.6).move_to(v(C[0] + xo + 1.0, base + 0.2)), t_in, z=6)
        show(ctx, ctx.text(T[val], 44, col, 3.0).move_to(v(C[0] + xo + 1.0, base + 0.5 + hh + 0.55)), t_in + 0.9, z=6)
    show(ctx, ctx.text(T["ok"], 48, "#9BE59B", 5.0).move_to(C + v(-3.2, 1.9)), ctx.tt(5, 2), z=7)
    ctx.avatar.look_at(v(C[0], base + 2.0))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t20)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
