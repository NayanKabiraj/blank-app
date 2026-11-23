"""Shot 5 (chapter 5, scenes 21-26): landing station to a data centre, the page returns, the whole trip, a network of networks, the offline quarter, the closing question."""
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


T = {"ls": "landing station", "dc": "data centre", "step": ["lookup", "request", "packets", "page rebuilt"], "net": "a network of networks", "off": "> 25 % still offline", "q": "Which step surprised you?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t20, t21, t22, t23, t24, t25 = [ctx.t_of(i) for i in range(6)]
    # scenes 21-22: coast -> landing station -> data centre; packets flow along, then come back
    sea = Rectangle(width=4.2, height=5.3, stroke_width=0, fill_color="#14407A", fill_opacity=0.85).move_to(C + v(-3.3, 0.0))
    show(ctx, sea, 0.2, t_out=t22 - 0.2, pop=0, z=1)
    ls = VGroup(Rectangle(width=1.1, height=0.9, stroke_color="#FFD166", stroke_width=4, fill_color="#10163A", fill_opacity=1), Polygon(v(-0.6, 0.45), v(0.6, 0.45), v(0, 0.95), stroke_color="#FFD166", stroke_width=4, fill_opacity=0)).move_to(C + v(-1.0, 0.0))
    show(ctx, ls, 0.5, t_out=t22 - 0.2, z=4)
    show(ctx, ctx.text(T["ls"], 24, "#FFD166", 3.5).move_to(C + v(-1.0, -1.0)), 0.6, t_out=t22 - 0.2, z=6)
    dc = VGroup(*[Rectangle(width=0.5, height=1.7, stroke_color="#7FD6FF", stroke_width=3, fill_color="#10163A", fill_opacity=1).move_to(C + v(3.2 + 0.6 * i, 0.0)) for i in range(5)])
    show(ctx, dc, ctx.tt(0, 0) + 0.8, t_out=t22 - 0.2, z=4)
    show(ctx, ctx.text(T["dc"], 24, "#7FD6FF", 3.5).move_to(C + v(4.4, -1.2)), ctx.tt(0, 0) + 1.0, t_out=t22 - 0.2, z=6)
    show(ctx, Line(C + v(-5.4, 0.0), C + v(-1.5, 0.0), color="#FFD166", stroke_width=7), 0.4, t_out=t22 - 0.2, pop=0, z=3)
    show(ctx, Line(C + v(-0.5, 0.0), C + v(2.9, 0.0), color="#3C4F7A", stroke_width=4), 1.0, t_out=t22 - 0.2, pop=0, z=3)
    flow = always_redraw(lambda: VGroup(*[Dot(radius=0.12, color="#FFD166").set_opacity(window(ctx, 0.6, t22 - 0.3)()).move_to(C + v(-5.4 + 8.4 * ((tl.t * 0.3 + k / 5) % 1.0), 0.0)) for k in range(5)]))
    flow._dynamic = True
    ctx.add(flow, z=6)
    back = always_redraw(lambda: VGroup(*[Dot(radius=0.1, color="#9BE59B").set_opacity(window(ctx, t21 + 0.8, t22 - 0.3)()).move_to(C + v(3.0 - 8.4 * ((tl.t * 0.3 + k / 5) % 1.0), -0.35)) for k in range(5)]))
    back._dynamic = True
    ctx.add(back, z=6)
    # scene 23: the whole trip in four steps
    for i, key in enumerate(T["step"]):
        show(ctx, chip(ctx, f"{i + 1}  {key}", ("#7FD6FF", "#FFD166", "#FF8FA3", "#9BE59B")[i], C + v(-3.9 + 2.6 * i, 1.2), 2.5, 21), t22 + 0.4 + 0.9 * i, pop=0.25, z=6)
    clockbar = always_redraw(lambda: Rectangle(width=max(0.02, 9.0 * ease(level(ctx, t22 + 0.6, 4.0))), height=0.4, stroke_width=0, fill_color="#FFD166", fill_opacity=0.9 * window(ctx, t22, t23 - 0.2)()).move_to(C + v(-4.5 + max(0.02, 9.0 * ease(level(ctx, t22 + 0.6, 4.0))) / 2, -0.6)))
    clockbar._dynamic = True
    ctx.add(clockbar, z=4)
    show(ctx, ctx.text("well under a second", 36, "#FFFFFF", 7.0).move_to(C + v(0.5, -1.6)), t22 + 2.5, t_out=t23 - 0.2, z=6)
    # scene 24: a network of networks - nodes with pulses
    rng = np.random.default_rng(5)
    ns = [C + v(rng.uniform(-4.8, 5.0), rng.uniform(-1.6, 1.8)) for _ in range(12)]
    edges = [(i, (i + 1) % 12) for i in range(12)] + [(0, 5), (2, 8), (3, 10), (1, 7)]
    for a, b in edges:
        show(ctx, Line(ns[a], ns[b], color="#3C4F7A", stroke_width=3), t23 + 0.3 + 0.05 * a, t_out=t24 - 0.2, pop=0, z=3)
    for i, p in enumerate(ns):
        show(ctx, node(p, 0.22, ("#7FD6FF", "#FFD166", "#FF8FA3", "#9BE59B")[i % 4]), t23 + 0.3 + 0.1 * i, t_out=t24 - 0.2, pop=0.15, z=4)
    pl = always_redraw(lambda: VGroup(*[Dot(radius=0.09, color="#FFFFFF").set_opacity(window(ctx, t23 + 1.0, t24 - 0.3)()).move_to(ns[a] + (ns[b] - ns[a]) * ((tl.t * 0.5 + k * 0.23) % 1.0)) for k, (a, b) in enumerate(edges[:8])]))
    pl._dynamic = True
    ctx.add(pl, z=6)
    show(ctx, ctx.text(T["net"], 40, "#FFFFFF", 8.0).move_to(C + v(0.5, 2.4)), t23 + 0.6, t_out=t24 - 0.2, z=7)
    # scene 25: more than a quarter is still offline
    for i in range(20):
        col = "#7FD6FF" if i < 14 else "#3C4F7A"
        x, y = C[0] - 3.2 + 0.62 * (i % 10) + 0.4, C[1] + 0.5 - 0.9 * (i // 10) + 0.3
        show(ctx, VGroup(Circle(radius=0.16, stroke_width=0, fill_color=col, fill_opacity=1).move_to(v(x, y + 0.22)), Rectangle(width=0.3, height=0.34, stroke_width=0, fill_color=col, fill_opacity=0.95).move_to(v(x, y - 0.05))), t24 + 0.3 + 0.07 * i, t_out=t25 - 0.2, pop=0.12, z=5)
    show(ctx, ctx.text(T["off"], 44, "#FFD166", 8.0).move_to(C + v(0.5, 2.1)), t24 + 0.6, t_out=t25 - 0.2, z=7)
    # scene 26: the closing question over the globe
    gc = C + v(1.0, 0.0)
    al = window(ctx, t25, None)
    gl = always_redraw(lambda: globe(gc, 2.0, al()))
    gl._dynamic = True
    ctx.add(gl, z=2)
    show(ctx, ctx.text(T["q"], 50, "#FFD166", 9.0).move_to(C + v(1.0, 2.3)), t25 + 0.6, z=7)
    pulse = always_redraw(lambda: Circle(radius=2.0 + 0.5 * ((tl.t * 0.7) % 1.0), stroke_color="#FFD166", stroke_width=4, fill_opacity=0, stroke_opacity=0.5 * (1 - ((tl.t * 0.7) % 1.0)) * level(ctx, t25 + 0.6, 0.5)).move_to(gc))
    pulse._dynamic = True
    ctx.add(pulse, z=5)
    ctx.avatar.look_at(gc)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t25)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
