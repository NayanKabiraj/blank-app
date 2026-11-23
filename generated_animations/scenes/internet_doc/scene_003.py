"""Shot 3 (chapter 3, scenes 11-15): a page is cut into packets that take different routes through routers and are rebuilt; the receiver reorders; a lost packet is asked for again."""
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


T = {"page": "web page", "pk": "packet", "rt": "routers", "dst": "your phone", "ask": "lost? ask again", "who": "the receiving device", "h": "piece of page + address + number"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t10, t11, t12, t13, t14 = ctx.t_of(0), ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    src, dst = C + v(-4.4, 0.4), C + v(5.0, 0.4)
    # scene 10-11: the page splits into 12 packets
    show(ctx, RoundedRectangle(corner_radius=0.12, width=1.3, height=1.7, stroke_color="#EAF6FF", stroke_width=4, fill_color="#10163A", fill_opacity=0.95).move_to(src), 0.3, t_out=t11 + 1.2, z=3)
    show(ctx, ctx.text(T["page"], 26, "#EAF6FF", 3.0).move_to(src + v(0, -1.3)), 0.4, t_out=t11 + 1.2, z=6)
    routers = [C + v(-1.6, 1.6), C + v(-0.4, 0.4), C + v(-1.6, -1.0), C + v(1.6, 1.6), C + v(1.2, 0.4), C + v(1.6, -1.0)]
    for r in routers:
        show(ctx, node(r, 0.32, "#FFD166"), t11 + 0.2, z=4)
    show(ctx, ctx.text(T["rt"], 26, "#FFD166", 3.0).move_to(C + v(0, 2.45)), t11 + 0.6, z=6)
    paths = [(0, 3), (1, 4), (2, 5)]
    show(ctx, ctx.text(T["dst"], 26, "#9BE59B", 3.0).move_to(dst + v(0, -1.3)), t11 + 0.4, z=6)
    show(ctx, RoundedRectangle(corner_radius=0.12, width=1.3, height=1.7, stroke_color="#9BE59B", stroke_width=4, fill_color="#10163A", fill_opacity=0.95).move_to(dst), t11 + 0.4, z=3)
    for i in range(12):
        a, b = paths[i % 3]
        t0 = t11 + 1.0 + 0.55 * i
        dur = 3.2
        def pos(i=i, a=a, b=b, t0=t0):
            f = level(ctx, t0, dur)
            pts = [src, routers[a], routers[b], dst]
            seg = min(2, int(f * 3))
            u = f * 3 - seg
            return pts[seg] + (pts[seg + 1] - pts[seg]) * u + v(0, 0.12 * math.sin(i))
        col = ("#7FD6FF", "#FFD166", "#FF8FA3")[i % 3]
        lost = (i == 7)
        d = always_redraw(lambda pos=pos, col=col, t0=t0, lost=lost: Rectangle(width=0.26, height=0.2, stroke_width=0, fill_color=("#FF4D6D" if lost and level(ctx, t0, 3.2) > 0.55 else col),
                                                                              fill_opacity=0.95 * window(ctx, t0 - 0.05, t14 - 0.2)() * (0.0 if (lost and level(ctx, t0, 3.2) > 0.62) else 1.0) * (1.0 if level(ctx, t0, 3.2) < 0.995 else 0.0)).move_to(pos()))
        d._dynamic = True
        ctx.add(d, z=6)
        # arrived packets stack up as the rebuilt page
        show(ctx, Rectangle(width=0.26, height=0.2, stroke_width=0, fill_color=col, fill_opacity=0.95).move_to(dst + v(-0.3 + 0.2 * (i % 4), 0.6 - 0.28 * (i // 4))), t0 + dur, pop=0.1, z=7)
    show(ctx, ctx.text(T["h"], 26, "#EAF6FF", 8.0).move_to(C + v(0.2, -2.2)), t11 + 0.8, t_out=t12 - 0.2, z=6)
    # scene 13: who rebuilds? highlight the receiving device
    glow = always_redraw(lambda: RoundedRectangle(corner_radius=0.2, width=1.7, height=2.1, stroke_color="#9BE59B", stroke_width=9, fill_opacity=0, stroke_opacity=level(ctx, ctx.tt(3, 2), 0.3) * window(ctx, 0.2, t14 - 0.2)() * (0.6 + 0.4 * math.sin(tl.t * 6))).move_to(dst))
    glow._dynamic = True
    ctx.add(glow, z=8)
    show(ctx, ctx.text(T["who"], 32, "#9BE59B", 8.0).move_to(C + v(2.5, -2.0)), ctx.tt(3, 2) + 0.2, t_out=t14 - 0.2, z=7)
    # scene 14: a lost packet is asked for again
    show(ctx, Arrow(dst + v(-0.8, -0.2), routers[4] + v(0.3, -0.1), buff=0, color="#FF4D6D", stroke_width=7), t14 + 0.6, z=7)
    show(ctx, ctx.text(T["ask"], 40, "#FF8FA3", 7.0).move_to(C + v(0.0, 1.9)), t14 + 0.4, z=7)
    again = always_redraw(lambda: Rectangle(width=0.26, height=0.2, stroke_width=0, fill_color="#FFD166", fill_opacity=0.95 * level(ctx, t14 + 1.4, 0.2) * (1 if level(ctx, t14 + 1.4, 3.0) < 0.995 else 0)).move_to(routers[4] + (dst - routers[4]) * level(ctx, t14 + 1.4, 3.0)))
    again._dynamic = True
    ctx.add(again, z=7)
    ctx.avatar.look_at(C + v(0, 0.4))
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t13)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.5)
