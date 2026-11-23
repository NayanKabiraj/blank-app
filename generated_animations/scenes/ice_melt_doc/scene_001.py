"""Shot 1 (chapter 1, scenes 1-5): all the ice melts and the sea floods a city; intro roadmap; Antarctica holds 90 %; land ice vs floating ice."""
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


T = {"c1": "how much ice", "c2": "how high", "c3": "the new map", "c4": "how fast", "plus": "+65 m", "ant": "Antarctica", "pct": "90 %", "fw": "and 70 % of the fresh water",
     "a1": "Antarctica", "a2": "Greenland", "a3": "Mountain glaciers", "land": "ice on land: adds water", "float": "floating ice: no change"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1, t2, t3, t4 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    X1, base = C[0] + W / 2, C[1] - H / 2
    melt = lambda: level(ctx, 0.8, t1 + 3.0)
    al = window(ctx, 0.2, t2 - 0.2)
    scene = always_redraw(lambda: coast(C, W, H, melt(), al()))
    scene._dynamic = True
    ctx.add(scene, z=2)
    show(ctx, ctx.text(T["plus"], 72, "#FFD166", 5.0).move_to(C + v(3.2, 1.3)), t1 + 3.2, t_out=t2 - 0.2, z=7)
    for n, (key, col) in enumerate((("c1", "#7FD6FF"), ("c2", "#FFD166"), ("c3", "#9BE59B"), ("c4", "#FF8FA3"))):
        show(ctx, chip(ctx, f"{n + 1}  {T[key]}", col, v(C[0] - W / 2 + 1.5 + 2.75 * n, C[1] + H / 2 - 0.5), 2.6, 22), t1 + 0.6 + 1.3 * n, t_out=t2 - 0.3, pop=0.25, z=7)
    ring_c = C + v(1.0, 0.1)
    show(ctx, Circle(radius=1.6, stroke_color="#3C4F7A", stroke_width=14, fill_opacity=0).move_to(ring_c), t2 + 0.2, t_out=t3 - 0.2, pop=0, z=3)
    frac = lambda: ease(level(ctx, t2 + 0.5, 2.4)) * 0.9
    ring = always_redraw(lambda: Arc(radius=1.6, start_angle=math.pi / 2, angle=-2 * math.pi * max(0.001, frac()), stroke_color="#7FD6FF", stroke_width=14, stroke_opacity=window(ctx, t2 + 0.2, t3 - 0.2)()).move_to(ring_c))
    ring._dynamic = True
    ctx.add(ring, z=4)
    show(ctx, ctx.text(T["pct"], 64, "#FFFFFF", 4.0).move_to(ring_c), t2 + 0.6, t_out=t3 - 0.2, z=6)
    show(ctx, ctx.text(T["ant"], 40, "#7FD6FF", 5.0).move_to(ring_c + v(0, 2.3)), t2 + 0.6, t_out=t3 - 0.2, z=6)
    show(ctx, ctx.text(T["fw"], 30, "#FFD166", 8.0).move_to(ring_c + v(0, -2.3)), ctx.tt(2, 1) + 0.3, t_out=t3 - 0.2, z=6)
    for n, (key, col) in enumerate((("a1", "#7FD6FF"), ("a2", "#FFD166"), ("a3", "#9BE59B"))):
        c = chip(ctx, T[key], col, C + v(0.5, 1.3 - 1.15 * n), 4.4, 30)
        show(ctx, c, ctx.tt(3, 0) + 0.3 + 1.4 * n, t_out=t4 - 0.2, pop=0.25, z=6)
    al2 = window(ctx, t4, None)
    melt2 = lambda: 0.25 * level(ctx, t4 + 1.0, 6.0)
    scene2 = always_redraw(lambda: coast(C, W, H, melt2(), al2()))
    scene2._dynamic = True
    ctx.add(scene2, z=2)
    X0 = C[0] - W / 2
    drops = always_redraw(lambda: VGroup(*[Dot(radius=0.07, color="#BFE9FF").set_opacity(al2() * 0.9).move_to(v(X0 + 3.0 + 3.4 * ((tl.t * 0.35 + k / 8) % 1.0), base + 0.9 + 2.2 - 2.2 * ease(((tl.t * 0.35 + k / 8) % 1.0)))) for k in range(8)]))
    drops._dynamic = True
    ctx.add(drops, z=6)
    show(ctx, ctx.text(T["land"], 30, "#BFE9FF", 7.0).move_to(C + v(-1.2, 2.3)), t4 + 0.6, z=7)
    for k, x in enumerate((C[0] + 3.4, C[0] + 4.6)):
        show(ctx, Polygon(v(x - 0.4, base + 0.85), v(x + 0.4, base + 0.85), v(x + 0.25, base + 1.05), v(x - 0.25, base + 1.05), stroke_color=ICE, stroke_width=2, fill_color=ICE, fill_opacity=0.9), ctx.tt(4, 2) + 0.2 + 0.3 * k, z=7)
    show(ctx, ctx.text(T["float"], 24, "#FFD166", 5.0).move_to(C + v(2.6, 1.8)), ctx.tt(4, 2) + 0.4, z=7)
    ctx.avatar.look_at(v(C[0] + 2.5, C[1]))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t1)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), run_time=0.4)
    ctx.until(t4)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.6)
