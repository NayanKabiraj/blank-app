"""Shot 3 (chapter 3, scenes 11-15): Antarctica - 60 m of ice, west vs east bars, warm water creeping under, the order of loss, the white-ice feedback loop."""
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


T = {"a": "Antarctica: about 60 m", "w": "West: about 3 m", "e": "East: about 50 m +", "wc": "warm water creeps underneath", "q": "?", "r1": "centuries", "r2": "a thousand years +", "o1": "mountain glaciers", "o2": "Greenland's edges",
     "o3": "West Antarctica", "o4": "East Antarctica", "first": "first", "last": "last", "l1": "less ice", "l2": "more heat absorbed", "l3": "even more melting"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t10, t11, t12, t13, t14 = ctx.t_of(0), ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    base = C[1] - H / 2
    cx = v(C[0], base + 2.0)
    cont = always_redraw(lambda: VGroup(Ellipse(width=5.6 + 0.1 * math.sin(tl.t), height=3.0, fill_color=ICE, fill_opacity=0.95 * window(ctx, 0.2, t11 - 0.2)(), stroke_color="#BFE9FF", stroke_width=4, stroke_opacity=window(ctx, 0.2, t11 - 0.2)()).move_to(cx),
                                      *[Circle(radius=0.12, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.7 * window(ctx, 0.2, t11 - 0.2)() * (0.5 + 0.5 * math.sin(tl.t * 2 + k))).move_to(cx + v(1.8 * math.cos(k * 1.7 + tl.t * 0.3), 0.9 * math.sin(k * 1.7 + tl.t * 0.3))) for k in range(6)]))
    cont._dynamic = True
    ctx.add(cont, z=3)
    show(ctx, ctx.text(T["a"], 40, "#7FD6FF", 8.0).move_to(v(C[0], base + 4.2)), 0.5, t_out=t11 - 0.2, z=6)
    show(ctx, ctx.text("East", 34, "#0A1330", 3.0).move_to(cx + v(1.2, 0.0)), 1.2, t_out=t11 - 0.2, z=6)
    show(ctx, ctx.text("West", 34, "#0A1330", 3.0).move_to(cx + v(-1.8, 0.1)), 1.8, t_out=t11 - 0.2, z=6)
    for k, (key, hh, col, xo) in enumerate((("w", 0.3, "#FF8FA3", -1.6), ("e", 3.2, "#7FD6FF", 1.6))):
        t_in = t11 + 0.5 + 1.1 * k
        grow = (lambda t_in=t_in: ease(level(ctx, t_in, 1.4)))
        bar = always_redraw(lambda k=k, hh=hh, col=col, xo=xo, grow=grow: Rectangle(width=1.5, height=max(0.02, hh * grow()), stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t11, t12 - 0.2)()).move_to(v(C[0] + xo, base + 0.3 + max(0.02, hh * grow()) / 2)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 28, col, 3.2).move_to(v(C[0] + xo, base + 0.0)), t_in, t_out=t12 - 0.2, z=6)
    arrows = always_redraw(lambda: VGroup(*[Arrow(v(C[0] - 4.2 + 2.0 * ((tl.t * 0.5 + k / 3) % 1.0), base + 0.9), v(C[0] - 3.5 + 2.0 * ((tl.t * 0.5 + k / 3) % 1.0), base + 0.9), buff=0, color="#FF8A5B", stroke_width=6, max_tip_length_to_length_ratio=0.5,
                                            stroke_opacity=window(ctx, ctx.tt(1, 1), t12 - 0.2)()).set_fill(opacity=window(ctx, ctx.tt(1, 1), t12 - 0.2)()) for k in range(3)]))
    arrows._dynamic = True
    ctx.add(arrows, z=6)
    show(ctx, ctx.text(T["wc"], 26, "#FF8A5B", 5.0).move_to(v(C[0] - 3.2, base + 1.7)), ctx.tt(1, 1) + 0.2, t_out=t12 - 0.2, z=6)
    show(ctx, ctx.text(T["q"], 120, "#FFD166", 3.0).move_to(C + v(0, 0.9)), t12 + 0.5, t_out=t13 - 0.2, z=6)
    rb = always_redraw(lambda: Rectangle(width=max(0.02, 7.0 * ease(level(ctx, t12 + 1.0, 2.5))), height=0.55, stroke_width=0, fill_color="#FF8FA3", fill_opacity=0.9 * window(ctx, t12, t13 - 0.2)()).move_to(v(C[0] - 3.5 + 3.5 * ease(level(ctx, t12 + 1.0, 2.5)), base + 1.0)))
    rb._dynamic = True
    ctx.add(rb, z=4)
    show(ctx, ctx.text(T["r1"], 30, "#FFFFFF", 4.0).move_to(v(C[0] - 3.5, base + 0.45)), t12 + 1.0, t_out=t13 - 0.2, z=6)
    show(ctx, ctx.text(T["r2"], 30, "#FFFFFF", 5.0).move_to(v(C[0] + 3.0, base + 0.45)), t12 + 2.2, t_out=t13 - 0.2, z=6)
    for k, (key, col) in enumerate((("o1", "#7FD6FF"), ("o2", "#FFD166"), ("o3", "#FF8FA3"), ("o4", "#9BE59B"))):
        c = chip(ctx, f"{k + 1}  {T[key]}", col, v(C[0] - 3.9 + 2.65 * k, base + 2.5 - 0.35 * k), 2.6, 21)
        show(ctx, c, ctx.tt(3, 0) + 0.3 + 1.0 * k, t_out=t14 - 0.2, pop=0.25, z=6)
    show(ctx, ctx.text(T["first"], 30, "#7FD6FF", 3.0).move_to(v(C[0] - 3.9, base + 3.4)), ctx.tt(3, 1), t_out=t14 - 0.2, z=6)
    show(ctx, ctx.text(T["last"], 30, "#9BE59B", 3.0).move_to(v(C[0] + 4.0, base + 2.0)), ctx.tt(3, 2) + 0.5, t_out=t14 - 0.2, z=6)
    cc = v(C[0] + 0.3, base + 2.2)
    pts = [cc + v(2.7 * math.cos(a), 1.5 * math.sin(a)) for a in (math.pi / 2, math.pi / 2 + 2.094, math.pi / 2 + 4.189)]
    for k, key in enumerate(("l1", "l2", "l3")):
        show(ctx, chip(ctx, T[key], ("#EAF6FF", "#FFD166", "#FF8FA3")[k], pts[k], 3.4, 24), t14 + 0.4 + 1.1 * k, pop=0.25, z=6)
    ring = always_redraw(lambda: Circle(radius=0.12, stroke_width=0, fill_color="#FFFFFF", fill_opacity=window(ctx, t14 + 1.0, None)()).move_to(cc + v(2.7 * math.cos(math.pi / 2 - tl.t * 1.2), 1.5 * math.sin(math.pi / 2 - tl.t * 1.2))))
    ring._dynamic = True
    ctx.add(ring, z=7)
    show(ctx, Circle(radius=1.0, stroke_color="#3C4F7A", stroke_width=3, fill_opacity=0).move_to(cc), t14 + 0.3, pop=0, z=2)
    ctx.avatar.look_at(cx)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t12)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
