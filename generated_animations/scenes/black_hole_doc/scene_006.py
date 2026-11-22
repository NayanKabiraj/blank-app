"""Shot 6 (chapter 5, scenes 26-27): the whole fall in four beats, then the close over a spinning black hole."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, RoundedRectangle, VGroup

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, icons
from generated_animations.timed import level, show, window

T = {"c": ["Horizon: no return", "Stretch: tidal forces", "Time: slows for watchers", "Center: unknown"], "no": "No way back", "q": "?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t27 = ctx.t_of(1)
    cols = ("#FF4D6D", "#FFC857", "#7FD6FF", "#B084FF")
    for k, (txt, col) in enumerate(zip(T["c"], cols)):
        x = C[0] + (k - 1.5) * 2.7
        t_k = ctx.tt(0, k + 1)
        card = RoundedRectangle(corner_radius=0.3, width=2.5, height=3.6, stroke_color=col, stroke_width=4, fill_color="#16213E", fill_opacity=1).move_to((x, C[1] + 0.3, 0))
        show(ctx, card, 0.4 + 0.2 * k, t_out=t27 - 0.2, pop=0.2)
        ic = [Circle(radius=0.55, stroke_color="#FF4D6D", stroke_width=8, fill_color="#000000", fill_opacity=1), blackhole.astronaut((0, 0, 0), 0.9, 2.2, math.pi / 2),
              icons.icon("clock", 1.1), ctx.text("?", 90, "#B084FF", 1.5)][k]
        ic.move_to((x, C[1] + 0.9, 0))
        show(ctx, ic, t_k, t_out=t27 - 0.2, z=5)
        show(ctx, ctx.text(txt, 24, col, 2.3).move_to((x, C[1] - 0.6, 0)), t_k + 0.2, t_out=t27 - 0.2, z=6)
    # close
    BC = C + np.array([1.9, 0.5, 0.0])
    ctx.add(blackhole.starfield(C, W, H, 60, BC, 1.2, warp=lambda: 0.9, alpha=window(ctx, t27, None)), z=1)
    ctx.add(blackhole.black_hole(BC, 1.2, tl, alpha=window(ctx, t27, None)), z=3)
    show(ctx, ctx.text(T["no"], 56, "#FFD166", 8.0).move_to(C + np.array([1.9, -2.2, 0.0])), t27 + 0.6, z=6)
    show(ctx, ctx.text(T["q"], 90, "#B084FF", 2.0).move_to(BC), t27 + 1.6, z=6)
    ctx.avatar.look_at(None)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(t27)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
