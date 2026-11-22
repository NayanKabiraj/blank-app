"""Shot 3 (scene 4): the same signal from a near and a far satellite - the late one is the far one."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Dot, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, lighting
from generated_animations.timed import show

T = {"en": {"near": "near: short delay", "far": "far: long delay", "n": "not to scale"},
     "hi": {"near": "पास: कम देरी", "far": "दूर: ज़्यादा देरी", "n": "पैमाना असली नहीं"}}
PERIOD = 3.4


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    P = C + np.array([0.0, -2.5, 0.0])
    phone = diagrams.phone(P, 0.8)
    show(ctx, phone, 0.1, z=2)
    sats = [(C + np.array([-2.5, 0.4, 0.0]), 1.0, "#7FD6FF", L["near"]), (C + np.array([2.2, 4.0, 0.0]), 2.3, "#FF8FA3", L["far"])]
    for S, travel, col, name in sats:
        sat = diagrams.satellite(S, 0.55)
        show(ctx, sat, 0.2, z=3)
        start, end = S + np.array([0, -0.4, 0]), P + np.array([0, 0.9, 0])

        def packet(s=start, e=end, tr=travel, col=col):
            p = ((tl.t - 0.4) % PERIOD)
            f = min(1.0, p / tr)
            vis = 1.0 if p < tr + 0.25 else 0.0
            pos = s + (e - s) * f
            g = VGroup(Dot(pos, radius=0.13, color=col, fill_opacity=vis), Dot(pos, radius=0.26, color=col, fill_opacity=0.25 * vis))
            return g
        pk = always_redraw(packet)
        pk._dynamic = True
        ctx.add(pk, z=5)
        tcen = S + np.array([-0.0, 0.95, 0.0])

        def timer(S=S, tr=travel, col=col, tcen=tcen):
            p = ((tl.t - 0.4) % PERIOD)
            f = min(1.0, p / tr)
            return VGroup(Circle(radius=0.3, stroke_color="#FFFFFF", stroke_opacity=0.35, stroke_width=3).move_to(tcen),
                          Arc(radius=0.3, start_angle=math.pi / 2, angle=-2 * math.pi * max(0.001, f), arc_center=tcen,
                              stroke_color=col, stroke_width=7))
        tm = always_redraw(timer)
        tm._dynamic = True
        ctx.add(tm, z=4)
        show(ctx, ctx.text(name, 28, col).move_to(S + np.array([0.0, -0.95, 0.0])), 0.6)
    show(ctx, ctx.text(L["n"], 24, "#9AA8C7", weight="NORMAL").move_to(C + np.array([0.0, -3.5, 0.0])), 1.0)
    ctx.avatar.look_at(phone)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(ctx.t_of(0) + 2.0)
    ctx.avatar.look_at(lambda: C + np.array([2.2, 4.0, 0.0]))
    ctx.play(gestures.point_at(ctx.avatar, lambda: C + np.array([2.2, 4.0, 0.0]), 0.5), run_time=0.5)
