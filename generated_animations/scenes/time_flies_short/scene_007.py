"""Shot 7 (scene 8): the close - a calendar page whose days light up with new colours; the question pulses."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Arrow, Circle, DashedLine, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, Sector, VGroup,
                   always_redraw)

from generated_animations.avatar import expressions, gestures
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def chip(ctx, text, color, center, w=3.6, size=30):
    return VGroup(RoundedRectangle(corner_radius=0.26, width=w, height=0.78, stroke_color=color, stroke_width=5, fill_color="#0A1330", fill_opacity=0.92),
                  ctx.text(text, size, color, w - 0.4)).move_to(center)


def clock(c, r, angle, a=1.0, hand="#FFD166"):
    """A round clock face with one fast hand and one slow hand (angle in radians, clockwise from 12)."""
    g = VGroup(Circle(radius=r, stroke_color="#EAF6FF", stroke_width=6, fill_color="#10163A", fill_opacity=0.95 * a).move_to(c),
               *[Line(c + (0.86 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), c + (0.96 * r) * v(math.sin(k * math.pi / 6), math.cos(k * math.pi / 6)), color="#EAF6FF", stroke_width=3) for k in range(12)],
               Line(c, c + (0.78 * r) * v(math.sin(angle), math.cos(angle)), color=hand, stroke_width=7),
               Line(c, c + (0.5 * r) * v(math.sin(angle / 12), math.cos(angle / 12)), color="#FF8FA3", stroke_width=9),
               Circle(radius=0.07 * r, stroke_width=0, fill_color="#FFFFFF", fill_opacity=1).move_to(c))
    g.set_stroke(opacity=a)
    return g


T = {"q": "Try one new thing", "w": "this week"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    show(ctx, RoundedRectangle(corner_radius=0.3, width=5.6, height=4.4, stroke_color="#EAF6FF", stroke_width=6, fill_color="#10163A", fill_opacity=0.95).move_to(C + v(0, 0.6)), 0.2, pop=0.2, z=3)
    show(ctx, Rectangle(width=5.6, height=0.9, stroke_width=0, fill_color="#FF4D6D", fill_opacity=1).move_to(C + v(0, 2.55)), 0.3, pop=0.1, z=4)
    cols = ["#FF8FA3", "#FFD166", "#9BE59B", "#7FD6FF", "#C792EA", "#FF8A5B", "#7FD6FF"]
    for i in range(7):
        show(ctx, RoundedRectangle(corner_radius=0.12, width=0.62, height=0.62, stroke_width=0, fill_color=cols[i], fill_opacity=0.95).move_to(C + v(-2.0 + 0.67 * i, 1.0)), 0.6 + 0.35 * i, pop=0.2, z=5)
    sp = always_redraw(lambda: VGroup(*[Dot(radius=0.06, color="#FFFFFF").set_opacity(0.8 * (0.5 + 0.5 * math.sin(tl.t * 3 + i))).move_to(C + v(-2.0 + 0.67 * (i % 7), 1.0 + 0.5 * math.sin(tl.t + i))) for i in range(7)]))
    sp._dynamic = True
    ctx.add(sp, z=6)
    show(ctx, ctx.text(T["q"], 54, "#FFD166", 6.5).move_to(C + v(0, -2.4)), 0.8, z=7)
    show(ctx, ctx.text(T["w"], 40, "#EAF6FF", 5.0).move_to(C + v(0, -3.1)), 1.2, z=7)
    pulse = always_redraw(lambda: Circle(radius=1.0 + 0.6 * ((tl.t * 0.7) % 1.0), stroke_color="#FFD166", stroke_width=4, fill_opacity=0, stroke_opacity=0.5 * (1 - ((tl.t * 0.7) % 1.0)) * level(ctx, ctx.tt(0, 1), 0.5)).move_to(C + v(0, -2.6)))
    pulse._dynamic = True
    ctx.add(pulse, z=5)
    ctx.avatar.look_at(C + v(0, 0.6))
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
