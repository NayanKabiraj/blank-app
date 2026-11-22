"""Shot 7 (chapter 5, scenes 24-26): the biggest tide on Earth - the Bay of Fundy rises about 16 m, the coast shape matters."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Polygon, Rectangle, VGroup, VMobject, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import icons, orbital
from generated_animations.timed import level, show, window

T = {"en": {"bay": "Bay of Fundy, Canada", "m": "16 m", "fl": "about 5 floors", "wide": "wide mouth", "narrow": "narrow and shallow", "grow": "the tide grows"},
     "hi": {"bay": "बे ऑफ़ फ़ंडी, कनाडा", "m": "16 मीटर", "fl": "लगभग 5 मंज़िल", "wide": "चौड़ा मुहाना", "narrow": "तंग और उथली", "grow": "ज्वार बढ़ता है"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t24, t25 = ctx.t_of(1), ctx.t_of(2)
    # scene 24: where is it? (a globe with a pulsing pin)
    G = C + np.array([0.6, 0.2, 0.0])
    show(ctx, icons.icon("globe", 3.4).move_to(G), 0.2, t_out=t24 - 0.2, pop=0.3)
    pin = np.array([G[0] - 0.9, G[1] + 0.85, 0.0])
    ring = always_redraw(lambda: orbital.Circle(radius=0.12 + 0.5 * ((tl.t * 0.8) % 1.0), stroke_color="#FF4D6D", stroke_width=4, stroke_opacity=(1 - (tl.t * 0.8) % 1.0) * window(ctx, 0.5, t24 - 0.2)()).move_to(pin))
    ring._dynamic = True
    ctx.add(ring, z=5)
    show(ctx, orbital.Dot(pin, radius=0.16, color="#FF4D6D"), 0.5, t_out=t24 - 0.2, z=6)
    show(ctx, ctx.text(L["bay"], 38, "#FFD166", 6.0).move_to(G + np.array([2.6, -1.0, 0.0])), 0.8, t_out=t24 - 0.2)

    # scene 25: sixteen metres - low tide to high tide next to a five-storey building
    y0 = C[1] - 2.0
    bl = np.array([C[0] - 5.4 + 1.9, y0, 0.0])
    show(ctx, orbital.building(np.array([C[0] - 3.4, y0, 0.0]), 5, 0.5, 1.4), t24 + 0.2, t_out=t25 - 0.2, z=4)
    wl = lambda: y0 + 1.25 + 1.25 * math.sin(2 * math.pi * (tl.t - t24) / 8.0 - math.pi / 2)
    x_l = C[0] - 1.6
    sea = always_redraw(lambda: Rectangle(width=W / 2 + 4.2, height=max(0.05, wl() - (y0 - 0.1)), stroke_width=0, fill_color="#1F6FB5",
                                          fill_opacity=0.88 * window(ctx, t24, t25 - 0.2)()).move_to((x_l + (W / 2 + 4.2) / 2 - 0.0, (wl() + y0 - 0.1) / 2, 0)))
    sea._dynamic = True
    ctx.add(sea, z=2)
    bt = always_redraw(lambda: orbital.boat(np.array([C[0] + 3.0, wl() + 0.12 + 0.05 * math.sin(tl.t * 2.3), 0.0]), 1.3).set_opacity(window(ctx, t24, t25 - 0.2)()))
    bt._dynamic = True
    ctx.add(bt, z=3)
    show(ctx, Arrow(np.array([C[0] - 1.9, y0, 0.0]), np.array([C[0] - 1.9, y0 + 2.5, 0.0]), buff=0, color="#FFD166", stroke_width=6, max_tip_length_to_length_ratio=0.12), t24 + 1.5, t_out=t25 - 0.2, z=6)
    show(ctx, ctx.text(L["m"], 64, "#FFD166", 3.0).move_to((C[0] - 0.4, y0 + 3.0, 0)), t24 + 1.6, t_out=t25 - 0.2, z=6)
    show(ctx, ctx.text(L["fl"], 28, "#F5F7FA", 3.5, "NORMAL").move_to((C[0] - 3.0, y0 + 2.9, 0)), t24 + 2.0, t_out=t25 - 0.2, z=6)

    # scene 26: why there? a funnel-shaped bay squeezes the tide higher
    x_a, x_b = C[0] - 3.2, C[0] + 5.6
    fun = Polygon((x_a, C[1] + 1.9, 0), (x_b, C[1] + 0.45, 0), (x_b, C[1] - 0.45, 0), (x_a, C[1] - 1.9, 0), stroke_color="#7FD6FF", stroke_width=4, fill_color="#14507E", fill_opacity=0.8)
    show(ctx, fun, t25 + 0.2, pop=0)
    N = 110

    def wave():
        pts = []
        for i in range(N):
            f = i / (N - 1)
            x = x_a + (x_b - x_a) * f
            amp = 0.12 + 0.62 * f ** 1.6
            pts.append(np.array([x, C[1] + amp * math.sin(9.0 * f - 2 * math.pi * (tl.t - t25) / 2.4), 0.0]))
        m = VMobject(stroke_color="#F5F7FA", stroke_width=6, stroke_opacity=window(ctx, t25 + 0.4, None)(), fill_opacity=0)
        m.set_points_as_corners(pts)
        return m
    w = always_redraw(wave)
    w._dynamic = True
    ctx.add(w, z=5)
    show(ctx, ctx.text(L["wide"], 28, "#9AA8C7", 3.0, "NORMAL").move_to((x_a + 1.2, C[1] + 2.35, 0)), t25 + 0.6)
    show(ctx, ctx.text(L["narrow"], 28, "#FF8FA3", 4.0).move_to((x_b - 1.6, C[1] + 1.45, 0)), t25 + 1.2)
    show(ctx, ctx.text(L["grow"], 32, "#FFD166", 4.0).move_to((C[0] + 1.2, C[1] - 2.35, 0)), t25 + 1.8)
    ctx.avatar.look_at(None)
    ctx.play(gestures.point_at(ctx.avatar, lambda: G + np.array([-0.9, 0.85, 0.0]), 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t24 + 1.4)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t25 + 0.5)
    ctx.play(gestures.point_at(ctx.avatar, lambda: np.array([x_b - 1.0, C[1] + 0.5, 0.0]), 0.5), run_time=0.5)
