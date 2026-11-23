"""Shot 2 (chapter 2, scenes 6-10): Greenland - 3 km of ice, +7 m next to a house, the ways it loses ice, the ice-cube myth, the year-3000 clock."""
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


T = {"km": "up to 3 km thick", "g": "Greenland", "seven": "+7 m", "w1": "warm air melts the top", "w2": "warm sea eats the edges", "w3": "glaciers slide faster",
     "m2": "water level stays the same", "y": "year 3000", "p": "72-100 % of the ice (one study)", "now": "today"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t5, t6, t7, t8, t9 = ctx.t_of(0), ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    base = C[1] - H / 2
    dome = lambda: Polygon(*[v(C[0] - 3.0 + 6.0 * k / 24, base + 0.6 + 2.2 * math.sin(math.pi * k / 24) ** 0.7 * (1 - 0.3 * level(ctx, t6 + 0.5, 5.0))) for k in range(25)], stroke_width=0, fill_color=ICE, fill_opacity=window(ctx, 0.2, t7 - 0.2)())
    dm = always_redraw(dome)
    dm._dynamic = True
    ctx.add(dm, z=3)
    show(ctx, Rectangle(width=6.4, height=0.5, stroke_width=0, fill_color="#5A4A3A", fill_opacity=1).move_to(v(C[0], base + 0.35)), 0.2, t_out=t7 - 0.2, pop=0, z=2)
    show(ctx, ctx.text(T["g"], 40, "#FFFFFF", 5.0).move_to(v(C[0], base + 3.2)), 0.4, t_out=t7 - 0.2, z=6)
    show(ctx, ctx.text(T["km"], 28, "#7FD6FF", 6.0).move_to(v(C[0] - 2.6, base + 2.6)), 1.2, t_out=t6 - 0.2, z=6)
    show(ctx, Arrow(v(C[0] - 3.6, base + 0.6), v(C[0] - 3.6, base + 2.8), buff=0, color="#7FD6FF", stroke_width=5), 1.0, t_out=t6 - 0.2, z=6)
    hx = C[0] + 2.8
    col_h = lambda: 2.1 * ease(level(ctx, t6 + 0.4, 2.0))
    water = always_redraw(lambda: Rectangle(width=1.4, height=max(0.01, col_h()), stroke_width=0, fill_color=SEA, fill_opacity=0.75 * window(ctx, t6, t7 - 0.2)()).move_to(v(hx - 1.3, base + 0.4 + max(0.01, col_h()) / 2)))
    water._dynamic = True
    ctx.add(water, z=4)
    show(ctx, VGroup(Rectangle(width=1.2, height=2.1, stroke_color="#C9CFE0", stroke_width=3, fill_color="#1A2040", fill_opacity=0.9), Polygon(v(-0.7, 1.05), v(0.7, 1.05), v(0, 1.7), stroke_color="#C9CFE0", stroke_width=3, fill_color="#8A5A44", fill_opacity=1),
                     Line(v(-0.6, 0.0), v(0.6, 0.0), color="#C9CFE0", stroke_width=3)).move_to(v(hx + 0.4, base + 0.4 + 1.2)), t6 + 0.2, t_out=t7 - 0.2, z=4)
    show(ctx, ctx.text(T["seven"], 60, "#FFD166", 4.0).move_to(v(hx - 1.3, base + 3.1)), t6 + 1.8, t_out=t7 - 0.2, z=6)
    show(ctx, ctx.text(T["w1"], 30, "#FFB38A", 6.0).move_to(C + v(0.0, 2.35)), t7 + 0.2, t_out=t8 - 0.2, z=6)
    sun_x = C[0] - 2.6
    show(ctx, Circle(radius=0.35, fill_color="#FFD84D", fill_opacity=1, stroke_width=0).move_to(v(sun_x, base + 3.3)), t7 + 0.2, t_out=t8 - 0.2, z=6)
    rays = always_redraw(lambda: VGroup(*[Line(v(sun_x, base + 3.3) + 0.5 * v(math.cos(a + tl.t), math.sin(a + tl.t)), v(sun_x, base + 3.3) + (0.75 + 0.1 * math.sin(tl.t * 4 + k)) * v(math.cos(a + tl.t), math.sin(a + tl.t)), color="#FFD84D", stroke_width=3, stroke_opacity=window(ctx, t7 + 0.2, t8 - 0.2)())
                                          for k, a in enumerate(np.linspace(0, 2 * math.pi, 8, endpoint=False))]))
    rays._dynamic = True
    ctx.add(rays, z=6)
    show(ctx, ctx.text(T["w2"], 28, "#7FD6FF", 6.0).move_to(C + v(3.0, -1.0)), ctx.tt(2, 1) + 0.3, t_out=t8 - 0.2, z=6)
    show(ctx, ctx.text(T["w3"], 28, "#FFD166", 6.0).move_to(C + v(-0.6, -0.4)), ctx.tt(2, 2) + 0.3, t_out=t8 - 0.2, z=6)
    flow = always_redraw(lambda: VGroup(*[Arrow(v(C[0] - 2.2 + 4.2 * ((tl.t * 0.4 + k / 3) % 1.0), base + 1.4 - 0.5 * ((tl.t * 0.4 + k / 3) % 1.0)), v(C[0] - 1.7 + 4.2 * ((tl.t * 0.4 + k / 3) % 1.0), base + 1.3 - 0.5 * ((tl.t * 0.4 + k / 3) % 1.0)), buff=0, color="#FFD166", stroke_width=5,
                                          max_tip_length_to_length_ratio=0.5, stroke_opacity=window(ctx, ctx.tt(2, 2) + 0.2, t8 - 0.2)()).set_fill(opacity=window(ctx, ctx.tt(2, 2) + 0.2, t8 - 0.2)()) for k in range(3)]))
    flow._dynamic = True
    ctx.add(flow, z=6)
    gx = C[0] - 0.5
    show(ctx, Polygon(v(gx - 1.1, base + 3.0), v(gx + 1.1, base + 3.0), v(gx + 0.85, base + 0.7), v(gx - 0.85, base + 0.7), stroke_color="#EAF6FF", stroke_width=5, fill_color=SEA, fill_opacity=0.45), t8 + 0.3, t_out=t9 - 0.2, z=4)
    cube = always_redraw(lambda: Rectangle(width=0.9 * (1 - 0.8 * level(ctx, t8 + 1.0, 4.0)) + 0.1, height=0.8 * (1 - 0.7 * level(ctx, t8 + 1.0, 4.0)) + 0.1, stroke_color="#FFFFFF", stroke_width=3, fill_color=ICE, fill_opacity=0.9 * window(ctx, t8 + 0.4, t9 - 0.2)(),
                                          stroke_opacity=window(ctx, t8 + 0.4, t9 - 0.2)()).move_to(v(gx, base + 2.45)))
    cube._dynamic = True
    ctx.add(cube, z=5)
    show(ctx, DashedLine(v(gx - 1.6, base + 2.45), v(gx + 1.6, base + 2.45), color="#FFD166", stroke_width=4, dash_length=0.15), t8 + 1.2, t_out=t9 - 0.2, pop=0, z=6)
    show(ctx, ctx.text(T["m2"], 28, "#FFD166", 6.5).move_to(v(gx + 3.6, base + 2.45)), ctx.tt(3, 2) + 0.2, t_out=t9 - 0.2, z=6)
    x0, x1, y = C[0] - 4.0, C[0] + 4.0, base + 1.8
    show(ctx, Line(v(x0, y), v(x1, y), color="#EAF6FF", stroke_width=5), t9 + 0.3, pop=0, z=5)
    prog = always_redraw(lambda: Line(v(x0, y), v(x0 + (x1 - x0) * level(ctx, t9 + 0.8, 5.0), y), color="#FF8FA3", stroke_width=12, stroke_opacity=window(ctx, t9 + 0.3, None)()))
    prog._dynamic = True
    ctx.add(prog, z=6)
    show(ctx, ctx.text(T["now"], 28, "#EAF6FF", 3.0).move_to(v(x0, y - 0.5)), t9 + 0.3, z=6)
    show(ctx, ctx.text(T["y"], 34, "#FF8FA3", 4.0).move_to(v(x1, y - 0.55)), t9 + 0.5, z=6)
    show(ctx, ctx.text(T["p"], 32, "#FFD166", 8.0).move_to(v(C[0], y + 1.2)), ctx.tt(4, 1) + 0.2, z=6)
    ctx.avatar.look_at(v(C[0], base + 2.0))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t8)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
