"""Shot 2 (chapter 2, scenes 6-10): DNS - a question climbs a chain of servers and the answer comes back; 13 names / ~1,900 copies; helpers remember (<1 % reach the root); ~350 million names."""
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


T = {"phone": "phone", "help": "helper", "root": "root", "tld": ".com", "auth": "website", "q": "address?", "ans": "203.0.113.7", "n13": "13 names", "n19": "~1,900 copies", "ops": "12 operators",
     "no": "reach the root: < 1 %", "yes": "answered by a helper: > 99 %", "m": "~350 million names"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t5, t6, t7, t8, t9 = ctx.t_of(0), ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    xs = [-4.2, -2.2, -0.2, 1.8, 3.8]
    names = ("phone", "help", "root", "tld", "auth")
    cols = ("#EAF6FF", "#FFD166", "#FF8FA3", "#7FD6FF", "#9BE59B")
    pts = [C + v(x, 0.6) for x in xs]
    for k in range(5):
        show(ctx, node(pts[k], 0.55, cols[k]), 0.3 + 0.35 * k, t_out=t7 - 0.2, z=4)
        show(ctx, ctx.text(T[names[k]], 24, cols[k], 2.4).move_to(pts[k] + v(0, -1.0)), 0.4 + 0.35 * k, t_out=t7 - 0.2, z=6)
        if k < 4:
            show(ctx, Line(pts[k] + v(0.55, 0), pts[k + 1] + v(-0.55, 0), color="#3C4F7A", stroke_width=4), 0.3 + 0.35 * k, t_out=t7 - 0.2, pop=0, z=3)
    # the question climbs up the chain and the answer returns (looping dots)
    def mover(t0, t1_, up):
        def pos():
            f = ease(level(ctx, t0, t1_ - t0))
            a, b = (0, 4) if up else (4, 0)
            x = xs[a] + (xs[b] - xs[a]) * f
            return C + v(x, 0.6 + 0.0)
        return pos
    q = mover(t6 + 0.4, t6 + 3.4, True)
    ans = mover(t6 + 3.8, t6 + 6.0, False)
    qd = always_redraw(lambda: Dot(radius=0.16, color="#FFD166").set_opacity(window(ctx, t6 + 0.4, t6 + 3.6)()).move_to(q()))
    ad = always_redraw(lambda: Dot(radius=0.16, color="#9BE59B").set_opacity(window(ctx, t6 + 3.8, t7 - 0.3)()).move_to(ans()))
    for d in (qd, ad):
        d._dynamic = True
        ctx.add(d, z=7)
    show(ctx, ctx.text(T["q"], 28, "#FFD166", 3.0).move_to(C + v(-1.9, 1.8)), t6 + 0.4, t_out=t6 + 3.6, z=7)
    show(ctx, ctx.text(T["ans"], 28, "#9BE59B", 3.5).move_to(C + v(-1.9, 1.8)), t6 + 4.2, t_out=t7 - 0.3, z=7)
    # scene 7: 13 root names and about 1,900 copies around the world
    for i in range(13):
        x, y = C[0] - 3.4 + 0.55 * i, C[1] + 1.3
        show(ctx, RoundedRectangle(corner_radius=0.08, width=0.45, height=0.45, stroke_width=0, fill_color="#FF8FA3", fill_opacity=0.95).move_to(v(x, y)), t7 + 0.3 + 0.1 * i, t_out=t8 - 0.2, pop=0.12, z=5)
    show(ctx, ctx.text(T["n13"], 42, "#FF8FA3", 5.0).move_to(C + v(-2.5, 2.3)), t7 + 0.3, t_out=t8 - 0.2, z=6)
    rng = np.random.default_rng(3)
    cp = [v(rng.uniform(-5.0, 5.0), rng.uniform(-2.2, 0.5)) for _ in range(60)]
    for i, p in enumerate(cp):
        show(ctx, Dot(radius=0.06, color="#FFD166").move_to(C + p), ctx.tt(2, 1) + 0.5 + 0.03 * i, t_out=t8 - 0.2, pop=0.1, z=5)
    show(ctx, ctx.text(T["n19"], 40, "#FFD166", 6.0).move_to(C + v(2.5, 2.3)), ctx.tt(2, 1) + 1.0, t_out=t8 - 0.2, z=6)
    show(ctx, ctx.text(T["ops"], 28, "#EAF6FF", 4.0).move_to(C + v(0, -2.45)), ctx.tt(2, 1) + 2.0, t_out=t8 - 0.2, z=6)
    # scene 8: the myth - almost every question stops at a helper
    wd = lambda: 10.0 * ease(level(ctx, t8 + 0.6, 1.6))
    bar = always_redraw(lambda: Rectangle(width=max(0.02, wd() * 0.99), height=0.9, stroke_width=0, fill_color="#FFD166", fill_opacity=0.95 * window(ctx, t8, t9 - 0.2)()).move_to(C + v(-5.0 + max(0.02, wd() * 0.99) / 2, 0.4)))
    bar._dynamic = True
    ctx.add(bar, z=4)
    show(ctx, Rectangle(width=0.1, height=0.9, stroke_width=0, fill_color="#FF4D6D", fill_opacity=1).move_to(C + v(4.95, 0.4)), t8 + 2.2, t_out=t9 - 0.2, pop=0.2, z=5)
    show(ctx, ctx.text(T["yes"], 32, "#FFD166", 9.0).move_to(C + v(-0.4, 1.4)), t8 + 1.2, t_out=t9 - 0.2, z=6)
    show(ctx, ctx.text(T["no"], 28, "#FF4D6D", 6.0).move_to(C + v(3.6, -0.6)), t8 + 2.4, t_out=t9 - 0.2, z=6)
    # scene 9: about 350 million names - a wall of tiny tiles filling in
    for i in range(60):
        x, y = C[0] - 3.4 + 0.5 * (i % 15) + 0.0, C[1] + 1.5 - 0.5 * (i // 15)
        show(ctx, RoundedRectangle(corner_radius=0.06, width=0.4, height=0.34, stroke_width=0, fill_color="#7FD6FF", fill_opacity=0.9).move_to(v(x, y)), t9 + 0.3 + 0.05 * i, pop=0.1, z=5)
    show(ctx, ctx.text(T["m"], 52, "#FFFFFF", 8.0).move_to(C + v(0.5, -1.0)), t9 + 0.6, z=7)
    ctx.avatar.look_at(pts[2])
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
    ctx.until(t8)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
