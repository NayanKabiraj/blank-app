"""Shot 3 (chapter 2, scenes 7-10): pull by distance, myth vs truth, the lemon-shaped ocean, why the far side bulges."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Line

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"en": {"near": "near: strongest", "mid": "middle: less", "far": "far: weakest", "myth": "Myth: the Moon drags water to one side",
            "truth": "Truth: the difference in pull stretches the ocean", "b1": "bulge toward the Moon", "b2": "bulge away",
            "e": "Earth is pulled more", "w": "far water: pulled less", "lb": "left behind"},
     "hi": {"near": "पास: सबसे ज़्यादा", "mid": "बीच: कम", "far": "दूर: सबसे कम", "myth": "भ्रम: चाँद पानी को एक तरफ़ खींचता है",
            "truth": "सच: खिंचाव का अंतर समुद्र को तानता है", "b1": "चाँद की ओर उभार", "b2": "दूसरी ओर उभार",
            "e": "धरती ज़्यादा खिंचती है", "w": "दूर का पानी: कम खिंचता है", "lb": "पीछे छूट गया"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t7, t8, t9 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3)
    E = C + np.array([1.6, -0.2, 0.0])
    R = 1.3
    M = C + np.array([-3.0, -0.1, 0.0])
    t_truth, t_core = ctx.tt(1, 1), ctx.tt(3, 1)

    def amp():
        t = ctx.elapsed()
        if t < t7:
            return 0.1
        return 0.1 + 0.3 * level(ctx, t_truth, 1.0)

    def offset():
        return 0.5 * (1 - level(ctx, t_truth, 1.0)) if ctx.elapsed() >= t7 else 0.0
    ctx.add(orbital.ocean_earth(E, R, bulge=lambda: math.pi, amp=amp, offset=offset, rot=lambda: 0.2 * tl.t,
                                core=lambda: (-0.3 * R * level(ctx, t_core, 1.3), 0.0), alpha=window(ctx, 0.1, None)), z=3)
    show(ctx, orbital.moon(M, 0.5), 0.2, z=4)

    # scene 7: the pull is strongest on the near side
    t_a = ctx.tt(0, 1)
    for k, (key, length) in enumerate((("near", 1.9), ("mid", 1.3), ("far", 0.7))):
        x0 = [E[0] - R * 0.9, E[0], E[0] + R * 0.9][k]
        y = E[1] + R + 0.55 + 0.62 * (2 - k)
        start = np.array([x0, y, 0.0])
        col = ["#FF8FA3", "#F4C95D", "#7FD6FF"][k]
        show(ctx, Line(np.array([x0, E[1] + R * 0.8, 0.0]), start, color=col, stroke_width=2, stroke_opacity=0.6), t_a + 0.9 * k, t_out=t7 - 0.2, pop=0)
        show(ctx, Arrow(start, start + np.array([-length, 0.0, 0.0]), buff=0, color=col, stroke_width=8), t_a + 0.9 * k, t_out=t7 - 0.2, z=5)
        show(ctx, ctx.text(L[key], 24, col, 3.2).move_to(start + np.array([-length - 1.6, 0.0, 0.0])), t_a + 0.9 * k + 0.2, t_out=t7 - 0.2, z=5)
    # scene 8: myth then truth
    show(ctx, ctx.text(L["myth"], 30, "#FF4D6D", W * 0.95).move_to(C + np.array([0.0, 2.5, 0.0])), t7 + 0.2, t_out=t_truth - 0.1)
    show(ctx, Arrow(E + np.array([-1.0, 0.0, 0.0]), M + np.array([0.7, 0.0, 0.0]), buff=0, color="#FF4D6D", stroke_width=7), t7 + 0.6, t_out=t_truth - 0.1, z=5)
    show(ctx, ctx.text(L["truth"], 30, "#4CD97B", W * 0.95).move_to(C + np.array([0.0, 2.5, 0.0])), t_truth + 0.2, t_out=t8 - 0.2)
    # scene 9: a lemon shape - one bulge toward the Moon, one away
    show(ctx, ctx.text(L["b1"], 26, "#2EC5FF", 3.5).move_to(E + np.array([-2.1, 1.7, 0.0])), t8 + 0.4, t_out=t9 - 0.2)
    show(ctx, Arrow(E + np.array([-2.1, 1.35, 0.0]), E + np.array([-1.7, 0.2, 0.0]), buff=0, color="#2EC5FF", stroke_width=5), t8 + 0.7, t_out=t9 - 0.2)
    show(ctx, ctx.text(L["b2"], 26, "#2EC5FF", 3.5).move_to(E + np.array([2.1, 1.7, 0.0])), t8 + 1.4, t_out=t9 - 0.2)
    show(ctx, Arrow(E + np.array([2.1, 1.35, 0.0]), E + np.array([1.8, 0.2, 0.0]), buff=0, color="#2EC5FF", stroke_width=5), t8 + 1.7, t_out=t9 - 0.2)
    # scene 10: the Earth itself is pulled toward the Moon more than the far water
    show(ctx, Arrow(E + np.array([0.0, 0.0, 0.0]), E + np.array([-1.5, 0.0, 0.0]), buff=0, color="#FFD166", stroke_width=10), t_core, z=6)
    show(ctx, ctx.text(L["e"], 26, "#FFD166", 3.5).move_to(E + np.array([-0.4, 1.85, 0.0])), t_core, z=6)
    show(ctx, Arrow(E + np.array([1.9, 0.0, 0.0]), E + np.array([1.5, 0.0, 0.0]), buff=0, color="#7FD6FF", stroke_width=6), t_core + 0.4, z=6)
    show(ctx, ctx.text(L["w"], 24, "#7FD6FF", 3.5).move_to(E + np.array([2.2, -1.9, 0.0])), t_core + 0.4, z=6)
    show(ctx, ctx.text(L["lb"], 34, "#FF8FA3", 3.5).move_to(E + np.array([2.7, 0.9, 0.0])), ctx.tt(3, 2), z=6)
    ctx.avatar.look_at(lambda: E)
    ctx.play(gestures.point_at(ctx.avatar, lambda: E + np.array([-1.0, 0.0, 0.0]), 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t_truth)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t_core)
    ctx.play(gestures.present(ctx.avatar, 0.5), run_time=0.5)
