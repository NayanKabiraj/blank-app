"""Shot 5 (scene 6): myth - the Moon does not hold us down; Earth's gravity does."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Cross, VGroup

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, orbital
from generated_animations.timed import level, show, window

T = {"myth": "Moon holds us down?", "truth": "Earth's gravity does", "moon": "Moon: tiny pull", "earth": "Earth: strong pull"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    E = C + np.array([0.0, -2.6, 0.0])
    R = 2.7
    t_truth = ctx.tt(0, 2) - 0.1
    ctx.add(orbital.ocean_earth(E, R, bulge=lambda: math.pi / 2, amp=lambda: 0.06, rot=lambda: 0.1 * tl.t, alpha=window(ctx, 0.1, None)), z=2)
    top = E + np.array([0.0, R * 0.85, 0.0])
    person = blackhole.astronaut(top + np.array([0.0, 0.62, 0.0]), 1.0, 1.0, 0.0, "#FFD166")
    show(ctx, person, 0.3, pop=0.2, z=4)
    mp = C + np.array([2.3, 3.7, 0.0])
    show(ctx, orbital.moon(mp, 0.5), 0.3, z=3)
    show(ctx, ctx.text(T["moon"], 26, "#E6E6E6", 3.5, "NORMAL").move_to(mp + np.array([0.0, -0.85, 0.0])), 0.6)
    arr_m = Arrow(top + np.array([0.7, 1.4, 0.0]), top + np.array([1.2, 1.85, 0.0]), buff=0, color="#E6E6E6", stroke_width=4)
    show(ctx, arr_m, ctx.tt(0, 0) + 0.5, z=4)
    # myth first (crossed out) then the truth: a strong arrow down into the Earth
    show(ctx, ctx.text(T["myth"], 38, "#FF4D6D", 7.0).move_to(C + np.array([-0.8, 4.35, 0.0])), 0.5, t_out=t_truth, z=6)
    show(ctx, Cross(ctx.text(T["myth"], 38, "#FF4D6D", 7.0).move_to(C + np.array([-0.8, 4.35, 0.0])), stroke_color="#FF4D6D", stroke_width=8), ctx.tt(0, 1) + 0.3, t_out=t_truth, z=7)
    show(ctx, Arrow(top + np.array([0.0, 0.9, 0.0]), top + np.array([0.0, -1.5, 0.0]), buff=0, color="#4CD97B", stroke_width=14), t_truth, z=5)
    show(ctx, ctx.text(T["truth"], 42, "#4CD97B", 7.0).move_to(C + np.array([-0.8, 4.35, 0.0])), t_truth + 0.2, z=6)
    show(ctx, ctx.text(T["earth"], 26, "#4CD97B", 4.0, "NORMAL").move_to(top + np.array([-2.2, 0.6, 0.0])), t_truth + 0.5, z=6)
    ctx.avatar.look_at(lambda: top)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t_truth)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), gestures.point_at(ctx.avatar, lambda: top, 0.5), run_time=0.6)
