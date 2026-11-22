"""Shot 6 (scene 7): quiz - the tides and the night change right away, the tilt takes ages."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Line, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import icons, orbital
from generated_animations.timed import level, show, window

T = {"opts": ["The tilt", "Tides and night", "The seasons"], "right": "right away", "ages": "takes ages", "q": "What changes first?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_a = ctx.tt(0, 1)
    show(ctx, ctx.text(T["q"], 46, "#FFD166", 7.5).move_to(C + np.array([0.0, 4.55, 0.0])), 0.2)
    xs = [-2.7, 0.0, 2.7]
    for k, txt in enumerate(T["opts"]):
        pill = RoundedRectangle(corner_radius=0.3, width=2.55, height=1.0, stroke_color="#3C4F7A", stroke_width=3, fill_color="#16213E", fill_opacity=1).move_to(C + np.array([xs[k], 3.5, 0.0]))
        label = ctx.text(txt, 26, "#F5F7FA", 2.3).move_to(pill)
        grp = VGroup(pill, label)
        if k == 1:
            def lit(_m, pill=pill):
                from manim import ManimColor, interpolate_color
                pill.set_fill(interpolate_color(ManimColor("#16213E"), ManimColor("#2E9E5B"), level(ctx, t_a, 0.5)), opacity=pill.get_fill_opacity(), family=False)
            grp.add_updater(lit)
        show(ctx, grp, 0.4 + 0.15 * k, z=5)
    # three little scenes: a wave (tides), a dark moonless sky (night), an hourglass-like slow tilt
    wave_c = C + np.array([-2.7, 0.7, 0.0])
    from generated_animations.shared.orbital import curve
    ctx.add(curve(wave_c + np.array([-1.0, 0.0, 0.0]), 2.0, 0.6, lambda u: math.sin(2 * math.pi * (u * 2 - 0.5 * tl.t)), lambda: 1.0, "#2EC5FF", 7, alpha=window(ctx, ctx.tt(0, 1) - 3.0, None)), z=4)
    show(ctx, ctx.text("tides", 28, "#2EC5FF", 2.5).move_to(wave_c + np.array([0.0, -1.2, 0.0])), ctx.tt(0, 1) - 2.8)
    sky_c = C + np.array([0.0, 0.7, 0.0])
    rng = np.random.default_rng(3)
    from manim import Dot
    stars = VGroup(*[Dot(sky_c + np.array([rng.uniform(-1.1, 1.1), rng.uniform(-0.8, 0.8), 0.0]), radius=0.04, color="#F5F7FA") for _ in range(22)])
    show(ctx, Circle(radius=1.2, stroke_color="#4A5A80", stroke_width=3, fill_color="#02030B", fill_opacity=1).move_to(sky_c), ctx.tt(0, 1) - 2.6, z=3)
    show(ctx, stars, ctx.tt(0, 1) - 2.4, z=4)
    show(ctx, ctx.text("night", 28, "#F5F7FA", 2.5).move_to(sky_c + np.array([0.0, -1.7, 0.0])), ctx.tt(0, 1) - 2.4)
    tl_c = C + np.array([2.7, 0.7, 0.0])
    ang = lambda: math.radians(23.4) + 0.12 * level(ctx, ctx.tt(0, 2), 8.0)
    tilt = always_redraw(lambda: VGroup(Circle(radius=0.9, stroke_color="#7FD6FF", stroke_width=3, fill_color="#14507E", fill_opacity=0.95).move_to(tl_c),
                                        Line(tl_c - 1.35 * np.array([math.sin(ang()), math.cos(ang()), 0]), tl_c + 1.35 * np.array([math.sin(ang()), math.cos(ang()), 0]), color="#FF8FA3", stroke_width=6)))
    tilt._dynamic = True
    ctx.add(tilt, z=4)
    show(ctx, ctx.text(T["ages"], 28, "#FF8FA3", 2.8).move_to(tl_c + np.array([0.0, -1.7, 0.0])), ctx.tt(0, 2) - 0.2)
    ctx.avatar.look_at(None)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(t_a)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
