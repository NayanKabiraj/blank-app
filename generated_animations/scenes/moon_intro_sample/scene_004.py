"""Shot 4 (scene 5): the Moon's gravity helps hold Earth's tilt steady; without it the tilt could wander."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Line, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"with": "with the Moon", "without": "no Moon", "steady": "steady", "wander": "could wander (very slowly)", "seasons": "steady seasons"}


def tilted_earth(ctx, center, tilt_fn, alpha, label_col):
    c = np.asarray(center, float)

    def build():
        a = tilt_fn()
        d = np.array([math.sin(a), math.cos(a), 0.0])
        g = VGroup(Circle(radius=1.15, stroke_color="#7FD6FF", stroke_width=4, fill_color="#14507E", fill_opacity=0.95).move_to(c),
                   Line(c - d * 1.7, c + d * 1.7, color=label_col, stroke_width=7),
                   Line(c + np.array([-1.15, 0, 0]), c + np.array([1.15, 0, 0]), color="#9EE6B5", stroke_width=3, stroke_opacity=0.7))
        k = alpha()
        for s in g.get_family():
            s.set_fill(opacity=s.get_fill_opacity() * k, family=False)
            s.set_stroke(opacity=s.get_stroke_opacity() * k, family=False)
        return g
    m = always_redraw(build)
    m._dynamic = True
    return m


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1 = ctx.tt(0, 2) - 0.1                          # "Without it, the tilt could wander"
    L = np.array([C[0] - 2.1, C[1] + 0.6, 0.0])
    R_ = np.array([C[0] + 2.1, C[1] + 0.6, 0.0])
    base = math.radians(23.4)
    ctx.add(tilted_earth(ctx, L, lambda: base + 0.03 * math.sin(tl.t * 1.5), window(ctx, 0.2, None), "#FFD166"), z=3)
    ctx.add(tilted_earth(ctx, R_, lambda: base + level(ctx, t1, 6.0) * 0.55 * math.sin(tl.t * 0.9) + level(ctx, t1, 6.0) * 0.25 * math.sin(tl.t * 2.1), window(ctx, 0.2, None), "#FF8FA3"), z=3)
    show(ctx, orbital.moon(np.array([L[0] - 1.9, L[1] + 1.3, 0.0]), 0.32), 0.4, z=3)
    show(ctx, ctx.text(T["with"], 30, "#FFD166", 3.8).move_to(L + np.array([0.0, -2.0, 0.0])), 0.4)
    show(ctx, ctx.text(T["without"], 30, "#FF8FA3", 3.8).move_to(R_ + np.array([0.0, -2.0, 0.0])), 0.8)
    show(ctx, ctx.text(T["steady"], 28, "#9EE6B5", 3.0, "NORMAL").move_to(L + np.array([0.0, -2.55, 0.0])), ctx.tt(0, 1))
    show(ctx, ctx.text(T["wander"], 26, "#FF8FA3", 4.2, "NORMAL").move_to(R_ + np.array([0.0, -2.55, 0.0])), t1 + 0.4)
    ctx.avatar.look_at(lambda: L)
    ctx.play(gestures.point_at(ctx.avatar, lambda: L, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t1)
    ctx.play(gestures.point_at(ctx.avatar, lambda: R_, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
