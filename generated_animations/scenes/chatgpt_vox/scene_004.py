"""Vox look - shot 4 (scene 8): the close - a chat box with a blinking cursor and the question on a marker swipe."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import vox
from generated_animations.shared.vox import BLUE, CREAM, GREEN, INK, ORANGE, PINK, RED, YEL
from generated_animations.timed import level, show, window


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


T = {"a": "PREDICTING,", "b": "NOT KNOWING", "q": "WHAT WILL YOU ASK FIRST?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    show(ctx, vox.torn_card(5.6, 3.6, seed=44, rot=1.5).move_to(C + v(0, 1.4)), 0.2, pop=0.2, z=2)
    a = ctx.text(T["a"], 52, INK, 5.0).move_to(C + v(0, 2.3))
    b = ctx.text(T["b"], 60, RED, 5.0).move_to(C + v(0, 1.2))
    show(ctx, a, 0.4, z=5)
    show(ctx, b, 0.9, z=5)
    show(ctx, RoundedRectangle(corner_radius=0.25, width=5.0, height=0.9, stroke_color=INK, stroke_width=5, fill_color="#FFFFFF", fill_opacity=1).move_to(C + v(0, -0.7)), ctx.tt(0, 1), pop=0.2, z=4)
    q = ctx.text(T["q"], 34, INK, 4.6).move_to(C + v(-0.1, -0.7))
    show(ctx, q, ctx.tt(0, 1) + 0.3, z=5)
    vox.marker(ctx, q, ctx.tt(0, 1) + 0.6, 0.8)
    cur = always_redraw(lambda: Rectangle(width=0.07, height=0.55, stroke_width=0, fill_color=INK, fill_opacity=(1.0 if int(tl.t * 2.5) % 2 == 0 else 0.0) * level(ctx, ctx.tt(0, 1) + 1.2, 0.2)).move_to(C + v(2.25, -0.7)))
    cur._dynamic = True
    ctx.add(cur, z=6)
    pulse = always_redraw(lambda: Circle(radius=1.0 + 0.6 * ((tl.t * 0.7) % 1.0), stroke_color=RED, stroke_width=4, fill_opacity=0, stroke_opacity=0.5 * (1 - ((tl.t * 0.7) % 1.0)) * level(ctx, ctx.tt(0, 1) + 0.6, 0.5)).move_to(C + v(0, -0.7)))
    pulse._dynamic = True
    ctx.add(pulse, z=3)
    ctx.avatar.look_at(C + v(0, -0.7))
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
