"""Shot 4 (chapter 3, scenes 11-16): the Earth spins through the two bulges; a live sea-level graph; 12 h 25 min; the 50-minute slip; quiz."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Line, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"en": {"turn": "Earth turns once a day", "hi": "high", "lo": "low", "gap": "12 h 25 min", "plus": "+50 min", "ex": "(exaggerated)",
            "d1": "today", "d2": "tomorrow", "moon": "Moon", "o": ["The same time", "Earlier", "About 50 minutes later"]},
     "hi": {"turn": "धरती दिन में एक बार घूमती है", "hi": "ज्वार", "lo": "भाटा", "gap": "12 घंटे 25 मिनट", "plus": "+50 मिनट", "ex": "(बढ़ा-चढ़ाकर)",
            "d1": "आज", "d2": "कल", "moon": "चाँद", "o": ["उसी समय", "पहले", "लगभग 50 मिनट बाद"]}}
M0 = 1.885


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t13, t14, t15 = ctx.t_of(3), ctx.t_of(4), ctx.t_of(5)
    E = np.array([-0.4, C[1] + 0.1, 0.0])
    R = 1.25
    ts, DAY = 0.8, 7.0
    rot = lambda: 2 * math.pi * max(0.0, ctx.elapsed() - ts) / DAY
    ctx.add(orbital.ocean_earth(E, R, bulge=lambda: math.pi - 0.05 * level(ctx, t13, 6.0), amp=lambda: 0.36, rot=rot, marker=M0, alpha=window(ctx, 0.1, None)), z=3)
    show(ctx, orbital.moon(np.array([-3.0, C[1] + 0.1, 0.0]), 0.34), 0.2, z=4)
    show(ctx, ctx.text(L["moon"], 24, "#E6E6E6", 2.0).move_to((-3.0, C[1] - 0.6, 0)), 0.4)
    show(ctx, ctx.text(L["turn"], 28, "#FFD166", 4.0).move_to(E + np.array([0.0, 1.95, 0.0])), 0.6)

    # live tide graph for the marker on the Earth: high when the marker passes either bulge
    o = np.array([2.3, C[1] - 0.1, 0.0])
    gw, gh = 4.9, 1.3
    fn = lambda u: math.cos(2 * (2 * math.pi * u + M0 - math.pi))
    show(ctx, orbital.axes(o, gw, gh), 0.3, pop=0)
    ctx.add(orbital.curve(o, gw, gh, fn, lambda: level(ctx, ts, DAY), "#2EC5FF", 8, alpha=window(ctx, 0.3, None)), z=4)
    show(ctx, ctx.text(L["d1"], 24, "#2EC5FF", 2.0).move_to(o + np.array([gw + 0.1, 0.9, 0.0])), 1.0)
    for u in (0.2, 0.7):
        show(ctx, ctx.text(L["hi"], 24, "#FFD166", 2.0).move_to(o + np.array([gw * u, gh + 0.4, 0.0])), ts + u * DAY, z=5)
    # 12 h 25 min between the two highs
    t12 = ctx.t_of(2)
    ya = o[1] + gh + 0.85
    show(ctx, Arrow(np.array([o[0] + gw * 0.2, ya, 0.0]), np.array([o[0] + gw * 0.7, ya, 0.0]), buff=0, color="#FFD166", stroke_width=5, max_tip_length_to_length_ratio=0.1), t12 + 0.3, t_out=t13 + 1.0, z=5)
    show(ctx, ctx.text(L["gap"], 34, "#FFD166", 4.0).move_to(np.array([o[0] + gw * 0.45, ya + 0.5, 0.0])), t12 + 0.5, t_out=t13 + 1.0, z=5)
    # tomorrow's curve is a little later: the Moon moved on
    fn2 = lambda u: fn(u - 0.06)
    ctx.add(orbital.curve(o, gw, gh, fn2, lambda: level(ctx, t13, 3.0), "#FF8FA3", 6, alpha=window(ctx, t13, None), dashed=True), z=4)
    show(ctx, ctx.text(L["d2"], 24, "#FF8FA3", 2.0).move_to(o + np.array([gw + 0.1, 0.4, 0.0])), t13 + 0.5)
    show(ctx, Arrow(o + np.array([gw * 0.2, gh + 0.15, 0.0]), o + np.array([gw * 0.26, gh + 0.15, 0.0]), buff=0, color="#FF8FA3", stroke_width=6, max_tip_length_to_length_ratio=0.8), t14 + 0.3, z=6)
    show(ctx, ctx.text(L["plus"], 44, "#FF8FA3", 3.0).move_to(o + np.array([gw * 0.5, -gh - 0.65, 0.0])), t14 + 0.4, z=6)
    show(ctx, ctx.text(L["ex"], 22, "#9AA8C7", 3.0, "NORMAL").move_to(o + np.array([gw * 0.5, -gh - 1.15, 0.0])), t14 + 0.6, z=6)
    # quiz
    t_rev = ctx.config["subs"][5]["end"] - 1.2
    for k, txt in enumerate(L["o"]):
        b = ctx.text(txt, 24, "#F5F7FA", 3.3)
        x = C[0] + (k - 1) * 3.7
        pill = RoundedRectangle(corner_radius=0.25, width=3.5, height=0.85, stroke_color="#3C4F7A", stroke_width=3, fill_color="#16213E", fill_opacity=1).move_to((x, C[1] - 2.0, 0))
        b.move_to(pill)
        grp = VGroup(pill, b)
        if k == 2:
            def lit(_m, pill=pill):
                from manim import ManimColor, interpolate_color
                pill.set_fill(interpolate_color(ManimColor("#16213E"), ManimColor("#2E9E5B"), level(ctx, t_rev, 0.4)), opacity=pill.get_fill_opacity(), family=False)
            grp.add_updater(lit)
        show(ctx, grp, t15 + 0.6 + 0.2 * k, z=7)
    ctx.avatar.look_at(lambda: E)
    ctx.play(gestures.point_at(ctx.avatar, lambda: E, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t12 + 0.3)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.6)
    ctx.until(t14)
    ctx.play(gestures.point_at(ctx.avatar, lambda: o + np.array([gw * 0.4, gh, 0.0]), 0.5), run_time=0.5)
    ctx.until(t_rev)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
