"""Shot 1 (chapter 1, scenes 1-5): a tap sends a glowing packet around the globe; intro roadmap; 6 billion people online; the cloud is machines; names become numbers."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Arrow, Circle, DashedLine, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw)

from generated_animations.avatar import expressions, gestures
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def chip(ctx, text, color, center, w=3.4, size=24):
    return VGroup(RoundedRectangle(corner_radius=0.26, width=w, height=0.78, stroke_color=color, stroke_width=5, fill_color="#0A1330", fill_opacity=0.92),
                  ctx.text(text, size, color, w - 0.4)).move_to(center)


def bez(p0, p1, p2, f):
    return (1 - f) ** 2 * p0 + 2 * (1 - f) * f * p1 + f * f * p2


def node(p, r, col, a=1.0):
    return Circle(radius=r, stroke_color=col, stroke_width=4, fill_color="#10163A", fill_opacity=0.95 * a).move_to(p).set_stroke(opacity=a)


def globe(c, r, a=1.0):
    g = VGroup(Circle(radius=r, stroke_color="#7FD6FF", stroke_width=4, fill_color="#14407A", fill_opacity=0.9 * a).move_to(c),
               *[Ellipse(width=w * r, height=h * r, stroke_width=0, fill_color="#3FA76B", fill_opacity=0.95 * a).move_to(c + r * v(dx, dy))
                 for w, h, dx, dy in ((0.9, 0.7, -0.35, 0.3), (0.6, 0.9, 0.1, -0.25), (0.55, 0.4, 0.5, 0.45), (0.5, 0.35, 0.45, -0.5))])
    g.set_stroke(opacity=a)
    return g


def phone(p, a=1.0):
    return VGroup(RoundedRectangle(corner_radius=0.12, width=0.5, height=0.9, stroke_color="#EAF6FF", stroke_width=3, fill_color="#10163A", fill_opacity=a).move_to(p),
                  Circle(radius=0.04, stroke_width=0, fill_color="#EAF6FF", fill_opacity=a).move_to(p + v(0, -0.35))).set_stroke(opacity=a)


def rack(p, a=1.0, col="#7FD6FF"):
    return VGroup(*[Rectangle(width=0.9, height=0.22, stroke_color=col, stroke_width=2, fill_color="#10163A", fill_opacity=a).move_to(p + v(0, 0.3 - 0.27 * i)) for i in range(4)]).set_stroke(opacity=a)


T = {"c1": "names to numbers", "c2": "packets", "c3": "cables under the sea", "six": "6 billion online", "pct": "about 74 % of people", "cloud": "the cloud", "real": "wires, buildings, machines",
     "name": "example.com", "num": "203.0.113.7", "tr": "translation"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1, t2, t3, t4 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    gc = C + v(1.5, -0.1)
    al = window(ctx, 0.2, t2 - 0.2)
    gl = always_redraw(lambda: globe(gc, 2.0, al()))
    gl._dynamic = True
    ctx.add(gl, z=2)
    ph = always_redraw(lambda: phone(C + v(-3.9, -0.6), al()))
    ph._dynamic = True
    ctx.add(ph, z=4)
    sv = always_redraw(lambda: rack(C + v(4.9, 0.7), al()))
    sv._dynamic = True
    ctx.add(sv, z=4)
    p0, p1, p2 = C + v(-3.6, -0.3), C + v(0.8, 3.6), C + v(4.5, 0.9)
    pk = always_redraw(lambda: VGroup(*[Circle(radius=0.14 - 0.03 * k, stroke_width=0, fill_color="#FFD166", fill_opacity=al() * (1 - 0.3 * k)).move_to(bez(p0, p1, p2, max(0.0, ((tl.t * 0.3) % 1.0) - 0.04 * k))) for k in range(4)]))
    pk._dynamic = True
    ctx.add(pk, z=6)
    show(ctx, ctx.text("tap", 30, "#FFD166", 2.0).move_to(C + v(-3.9, -1.4)), 0.4, t_out=t2 - 0.2, z=6)
    for n, (key, col) in enumerate((("c1", "#7FD6FF"), ("c2", "#FFD166"), ("c3", "#9BE59B"))):
        show(ctx, chip(ctx, f"{n + 1}  {T[key]}", col, C + v(-3.6 + 3.6 * n, 2.55), 3.4, 22), t1 + 0.8 + 1.4 * n, t_out=t2 - 0.3, pop=0.25, z=7)
    # six billion people online: 15 of 20 lit
    for i in range(20):
        x, y = C[0] - 3.6 + 0.62 * (i % 10) + 0.5, C[1] + 0.9 - 0.9 * (i // 10) + 0.3
        col = "#7FD6FF" if i < 15 else "#3C4F7A"
        show(ctx, VGroup(Circle(radius=0.16, stroke_width=0, fill_color=col, fill_opacity=1).move_to(v(x, y + 0.22)), Rectangle(width=0.3, height=0.34, stroke_width=0, fill_color=col, fill_opacity=0.95).move_to(v(x, y - 0.05))), t2 + 0.4 + 0.08 * i, t_out=t3 - 0.2, pop=0.12, z=5)
    show(ctx, ctx.text(T["six"], 56, "#FFFFFF", 7.0).move_to(C + v(1.5, 2.3)), t2 + 0.5, t_out=t3 - 0.2, z=6)
    show(ctx, ctx.text(T["pct"], 30, "#FFD166", 6.0).move_to(C + v(1.5, -1.0)), ctx.tt(2, 1) - 0.3, t_out=t3 - 0.2, z=6)
    # the cloud is wires, buildings and machines
    cl = VGroup(Circle(radius=0.6, fill_color="#EAF6FF", fill_opacity=0.95, stroke_width=0).move_to(C + v(-2.2, 0.6)), Circle(radius=0.8, fill_color="#EAF6FF", fill_opacity=0.95, stroke_width=0).move_to(C + v(-1.4, 0.8)),
                Circle(radius=0.6, fill_color="#EAF6FF", fill_opacity=0.95, stroke_width=0).move_to(C + v(-0.6, 0.6)))
    show(ctx, cl, t3 + 0.3, t_out=ctx.tt(3, 2) - 0.1, z=5)
    show(ctx, ctx.text(T["cloud"], 30, "#0A1330", 3.0).move_to(C + v(-1.4, 0.7)), t3 + 0.4, t_out=ctx.tt(3, 2) - 0.1, z=6)
    show(ctx, Line(C + v(-2.9, 1.4), C + v(-0.0, -0.1), color="#FF4D6D", stroke_width=9), t3 + 1.2, t_out=ctx.tt(3, 2) - 0.1, z=7)
    for k in range(4):
        show(ctx, rack(C + v(1.5 + 1.2 * k, 0.4), 1.0), ctx.tt(3, 2) + 0.2 + 0.3 * k, t_out=t4 - 0.2, z=5)
    show(ctx, Line(C + v(0.9, -0.3), C + v(5.3, -0.3), color="#FFD166", stroke_width=6), ctx.tt(3, 2) + 0.8, t_out=t4 - 0.2, pop=0, z=4)
    show(ctx, ctx.text(T["real"], 34, "#9BE59B", 8.0).move_to(C + v(2.5, -1.3)), ctx.tt(3, 2) + 0.6, t_out=t4 - 0.2, z=6)
    # names become numbers
    show(ctx, chip(ctx, T["name"], "#7FD6FF", C + v(-1.2, 1.0), 3.6, 28), t4 + 0.4, pop=0.25, z=6)
    show(ctx, Arrow(C + v(0.9, 1.0), C + v(2.2, 1.0), buff=0, color="#FFD166", stroke_width=8), t4 + 1.4, z=6)
    show(ctx, chip(ctx, T["num"], "#FFD166", C + v(4.2, 1.0), 3.6, 28), t4 + 2.0, pop=0.25, z=6)
    show(ctx, ctx.text(T["tr"], 44, "#FFFFFF", 6.0).move_to(C + v(1.5, -0.6)), ctx.tt(4, 2), z=6)
    ctx.avatar.look_at(gc)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t1)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), run_time=0.4)
    ctx.until(t4)
    ctx.play(gestures.present(ctx.avatar, 0.5), run_time=0.6)
