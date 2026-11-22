"""Shot 7 (scene 8): the takeaway - a stopwatch plus some geometry - and a question for the viewer."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Line, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, icons, lighting
from generated_animations.timed import show

T = {"en": {"plus": "+", "q": "Where do you use GPS most?"}, "hi": {"plus": "+", "q": "GPS सबसे ज़्यादा कहाँ चलाते हैं?"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    left, right = C + np.array([-2.5, 1.4, 0.0]), C + np.array([2.5, 1.4, 0.0])
    sw = icons.icon("clock", 2.6).move_to(left)
    geo = VGroup(*[Circle(radius=1.0, stroke_color=c, stroke_width=7).move_to(right + np.array([dx, dy, 0.0]))
                   for c, dx, dy in (("#7FD6FF", -0.55, -0.35), ("#F4C95D", 0.55, -0.35), ("#FF8FA3", 0.0, 0.6))])
    show(ctx, sw, 0.2, pop=0.3)
    show(ctx, geo, 0.5, pop=0.3)
    show(ctx, ctx.text(L["plus"], 64, "#F5F7FA", 1.0).move_to(C + np.array([0.0, 1.4, 0.0])), 0.8)
    # a swinging clock hand and slowly rotating circles keep the picture alive
    hand = always_redraw(lambda: Line(left, left + 0.85 * np.array([math.sin(tl.t * 2.0), math.cos(tl.t * 2.0), 0.0]), color="#FF4D6D", stroke_width=6))
    hand._dynamic = True
    ctx.add(hand, z=5)
    dot = diagrams.location_dot(right + np.array([0.0, -0.1, 0.0]), "#4CD97B", 0.16)
    show(ctx, lighting.glow(right + np.array([0.0, -0.1, 0.0]), "#4CD97B", 0.7), 1.0, z=4)
    show(ctx, dot, 1.0, z=6)
    show(ctx, ctx.text(L["q"], 40, "#FFD166", W * 0.95).move_to(C + np.array([0.0, -2.0, 0.0])), 2.0)
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
