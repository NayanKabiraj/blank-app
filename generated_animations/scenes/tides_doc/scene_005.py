"""Shot 5 (chapter 4, scenes 17-19): the Sun's pull is 178 times the Moon's, yet the Moon makes the bigger tide."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, DashedLine, Rectangle

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital, particles
from generated_animations.timed import level, show, window

T = {"en": {"sun": "Sun", "moon": "Moon", "pull": "pull on Earth", "tide": "size of the tide", "x": ["178 x", "1 x"], "two": ["more than 2 x", "1 x"]},
     "hi": {"sun": "सूरज", "moon": "चाँद", "pull": "धरती पर खिंचाव", "tide": "ज्वार का आकार", "x": ["178 गुना", "1 गुना"], "two": ["2 गुना से ज़्यादा", "1 गुना"]}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t17, t18 = ctx.t_of(1), ctx.t_of(2)
    top = C[1] + 1.55
    E = np.array([-0.2, top, 0.0])
    S = np.array([6.0, top, 0.0])
    ctx.add(orbital.ocean_earth(E, 0.8, bulge=lambda: 2.5 + 0.2 * math.sin(tl.t), amp=lambda: 0.2, rot=lambda: 0.3 * tl.t, alpha=window(ctx, 0.1, None)), z=3)
    show(ctx, orbital.sun(S, 0.6), 0.2, pop=0.3, z=2)
    show(ctx, ctx.text(L["sun"], 26, "#FFE08A", 2.0).move_to(S + np.array([0.0, -1.0, 0.0])), 0.5)
    mf = lambda: E + 1.5 * np.array([math.cos(2.5 + 0.2 * math.sin(tl.t)), math.sin(2.5 + 0.2 * math.sin(tl.t)), 0.0])
    from manim import always_redraw
    mm = always_redraw(lambda: orbital.moon(mf(), 0.26))
    mm._dynamic = True
    ctx.add(mm, z=4)
    ctx.add(particles.signal_packets(lambda: S + np.array([-0.7, 0, 0]), lambda: E + np.array([0.9, 0, 0]), tl, "#FFD166", n=5, period=1.8, size=0.09), z=1)
    ctx.add(particles.signal_packets(lambda: mf() + np.array([0.0, 0.0, 0]), lambda: E + np.array([0.0, 0.0, 0]), tl, "#E6E6E6", n=2, period=1.8, size=0.07), z=1)

    # scene 18: pull on Earth as bars - the Sun is 178 times the Moon
    y0 = C[1] - 1.0
    for k, (name, col, ratio) in enumerate((("sun", "#FFC93C", 1.0), ("moon", "#C9CCD3", 1 / 178))):
        yy = y0 - k * 0.95
        full = max(0.12, 6.0 * ratio)
        bar = always_redraw(lambda yy=yy, col=col, full=full, k=k: Rectangle(width=max(0.02, full * level(ctx, t17 + 0.4 + 0.5 * k, 1.0)), height=0.5, stroke_width=0, fill_color=col,
                                                                     fill_opacity=window(ctx, t17 + 0.3, t18 - 0.2)()).move_to((C[0] - 2.4 + max(0.02, full * level(ctx, t17 + 0.4 + 0.5 * k, 1.0)) / 2, yy, 0)))
        bar._dynamic = True
        ctx.add(bar, z=3)
        show(ctx, ctx.text(L[name], 26, col, 2.0).move_to((C[0] - 3.6, yy, 0)), t17 + 0.3, t_out=t18 - 0.2)
        show(ctx, ctx.text(L["x"][k], 30, col, 2.5).move_to((C[0] - 2.2 + full + 1.0 if k == 0 else C[0] - 1.2, yy, 0)), t17 + 1.4 + 0.5 * k, t_out=t18 - 0.2)
    show(ctx, ctx.text(L["pull"], 26, "#9AA8C7", 4.0, "NORMAL").move_to((C[0] - 0.6, y0 + 0.65, 0)), t17 + 0.3, t_out=t18 - 0.2)
    # scene 19: the tide the Moon makes is the bigger one
    for k, (name, col, rad) in enumerate((("moon", "#C9CCD3", 0.95), ("sun", "#FFC93C", 0.5))):
        x = C[0] - 1.8 + 3.6 * k
        d = Circle(radius=rad, stroke_color="#F5F7FA", stroke_width=3, fill_color=col, fill_opacity=0.9).move_to((x, y0 - 0.5, 0))
        show(ctx, d, t18 + 0.4 + 0.4 * k, pop=0.35)
        show(ctx, ctx.text(L["two"][k], 28, col, 3.0).move_to((x, y0 - 1.9, 0)), t18 + 0.6 + 0.4 * k)
    show(ctx, ctx.text(L["tide"], 26, "#9AA8C7", 4.0, "NORMAL").move_to((C[0], y0 + 0.65, 0)), t18 + 0.3)
    ctx.avatar.look_at(lambda: S)
    ctx.play(gestures.point_at(ctx.avatar, lambda: S, 0.5), expressions.set_expression(ctx.avatar, "excited", 0.4), run_time=0.6)
    ctx.until(t18)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), gestures.present(ctx.avatar, 0.5), run_time=0.6)
