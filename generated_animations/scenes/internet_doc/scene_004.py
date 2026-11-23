"""Shot 4 (chapter 4, scenes 16-20): the sea-floor cables - cable curves drawn between continents, ~570 systems, a hose-thin cable with a hair-thin glass core carrying light, delay vs distance bars, cables vs satellites."""
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


T = {"n570": "~570 cable systems", "hose": "as thick as a garden hose", "core": "glass thinner than a hair", "light": "light: 2/3 of full speed", "ms": "ms one way", "c": "cables", "s": "satellites", "most": "almost all"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t15, t16, t17, t18, t19 = ctx.t_of(0), ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    # scenes 15-16: two continents and many cables drawn across the sea
    for x, w, h in ((-3.8, 2.6, 2.0), (4.2, 2.6, 2.0), (1.0, 1.6, 1.2)):
        show(ctx, Ellipse(width=w, height=h, stroke_width=0, fill_color="#3FA76B", fill_opacity=0.9).move_to(C + v(x, -0.2)), 0.2, t_out=t17 - 0.2, pop=0, z=2)
    for k in range(7):
        y0 = -1.0 + 0.3 * k
        pa, pm, pb = C + v(-2.9, y0), C + v(1.0, -2.0 - 0.15 * k + 0.9), C + v(3.6, 0.6 - 0.3 * k)
        prog = (lambda k=k: ease(level(ctx, 0.5 + 0.35 * k, 1.6)))
        cab = always_redraw(lambda pa=pa, pm=pm, pb=pb, prog=prog: VGroup(*[Line(bez(pa, pm, pb, 0.04 * i * prog()), bez(pa, pm, pb, 0.04 * (i + 1) * prog()), color="#FFD166", stroke_width=4, stroke_opacity=window(ctx, 0.3, t17 - 0.2)()) for i in range(25)]))
        cab._dynamic = True
        ctx.add(cab, z=4)
    show(ctx, ctx.text(T["n570"], 52, "#FFD166", 8.0).move_to(C + v(1.0, 2.2)), t16 + 0.2, t_out=t17 - 0.2, z=7)
    # scene 17: a cable cross-section and light pulses inside the glass
    cx = C + v(0.5, 0.2)
    show(ctx, VGroup(Circle(radius=1.4, stroke_color="#8892B0", stroke_width=6, fill_color="#2A2F3A", fill_opacity=1), Circle(radius=0.18, stroke_color="#BFE9FF", stroke_width=3, fill_color="#BFE9FF", fill_opacity=0.9)).move_to(cx + v(-3.4, 0.0)), t17 + 0.2, t_out=t18 - 0.2, z=4)
    show(ctx, ctx.text(T["hose"], 26, "#EAF6FF", 4.5).move_to(cx + v(-3.4, -1.9)), t17 + 0.4, t_out=t18 - 0.2, z=6)
    show(ctx, Rectangle(width=6.0, height=0.34, stroke_color="#BFE9FF", stroke_width=3, fill_color="#10163A", fill_opacity=0.9).move_to(cx + v(1.7, 0.0)), t17 + 0.5, t_out=t18 - 0.2, z=4)
    pulses = always_redraw(lambda: VGroup(*[Rectangle(width=0.5, height=0.2, stroke_width=0, fill_color="#FFF3B0", fill_opacity=window(ctx, t17 + 0.8, t18 - 0.2)()).move_to(cx + v(-1.2 + 5.8 * ((tl.t * 0.35 + k / 4) % 1.0), 0.0)) for k in range(4)]))
    pulses._dynamic = True
    ctx.add(pulses, z=6)
    show(ctx, ctx.text(T["core"], 28, "#BFE9FF", 6.0).move_to(cx + v(1.7, -0.9)), ctx.tt(2, 1) + 0.2, t_out=t18 - 0.2, z=6)
    show(ctx, ctx.text(T["light"], 32, "#FFD166", 7.0).move_to(cx + v(1.7, 1.2)), ctx.tt(2, 1) + 0.9, t_out=t18 - 0.2, z=6)
    # scene 18: delay grows with distance (5, 35, 69 ms one way)
    for k, (lab, val, col) in enumerate((("1,000 km", 5, "#7FD6FF"), ("7,000 km", 35, "#FFD166"), ("14,000 km", 69, "#FF8FA3"))):
        t_in = t18 + 0.5 + 1.1 * k
        w = (lambda val=val, t_in=t_in: 6.0 * (val / 69.0) * ease(level(ctx, t_in, 1.4)))
        bar = always_redraw(lambda k=k, col=col, w=w: Rectangle(width=max(0.02, w()), height=0.62, stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t18, t19 - 0.2)()).move_to(C + v(-3.0 + max(0.02, w()) / 2, 1.6 - 1.05 * k)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(lab, 24, col, 3.0).move_to(C + v(-4.3, 1.6 - 1.05 * k)), t_in, t_out=t19 - 0.2, z=6)
        txt = ctx.text(f"{val} {T['ms']}", 26, col, 4.0).move_to(v(0, C[1] + 1.6 - 1.05 * k))
        txt.shift(v(C[0] - 3.0 + 6.0 * (val / 69.0) + 0.25 - txt.get_left()[0], 0))
        show(ctx, txt, t_in + 0.9, t_out=t19 - 0.2, z=6)
    # scene 19: cables carry almost all, satellites a small share
    for k, (key, wd, col) in enumerate((("c", 9.0, "#FFD166"), ("s", 0.7, "#8892B0"))):
        t_in = t19 + 0.8 + 1.2 * k
        w = (lambda wd=wd, t_in=t_in: wd * ease(level(ctx, t_in, 1.4)))
        bar = always_redraw(lambda k=k, col=col, w=w: Rectangle(width=max(0.02, w()), height=0.8, stroke_width=0, fill_color=col, fill_opacity=0.95 * window(ctx, t19, None)()).move_to(C + v(-4.2 + max(0.02, w()) / 2, 0.8 - 1.4 * k)))
        bar._dynamic = True
        ctx.add(bar, z=4)
        show(ctx, ctx.text(T[key], 32, col, 4.0).move_to(C + v(-4.2 + 1.0, 1.55 - 1.4 * k)), t_in, z=6)
    show(ctx, ctx.text(T["most"], 56, "#FFD166", 6.0).move_to(C + v(2.5, -1.8)), t19 + 2.4, z=7)
    ctx.avatar.look_at(C + v(0.5, 0.5))
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t17)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
