"""Shot 1 (chapter 1, scenes 1-4): the two-tide puzzle - a 24-hour sea-level graph, the Moon's one-sided pull, a harbour on the tide, the three questions this video answers."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Line, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import icons, orbital
from generated_animations.timed import level, show, window

T = {"en": {"gauge": "Sea level at one beach, 24 hours", "high": "high", "low": "low", "moon": "Moon", "q": "?",
            "c1": "Why two bulges?", "c2": "50 min later", "c3": "16 m tide", "hours": ["0", "6", "12", "18", "24 h"]},
     "hi": {"gauge": "एक समुद्र तट पर 24 घंटे का जलस्तर", "high": "ज्वार", "low": "भाटा", "moon": "चाँद", "q": "?",
            "c1": "दो उभार क्यों?", "c2": "50 मिनट देर", "c3": "16 मीटर ज्वार", "hours": ["0", "6", "12", "18", "24 घं"]}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t1, t2, t3 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3)

    # ---- A: the sea rises twice in a day
    o = C + np.array([-W / 2 + 0.9, 0.0, 0.0])
    w, h = W - 1.5, H * 0.34
    show(ctx, orbital.axes(o, w, h), 0.2, t_out=t1 - 0.2, pop=0)
    show(ctx, ctx.text(L["gauge"], 30, "#9AA8C7", W * 0.9).move_to(C + np.array([0.0, H * 0.46, 0.0])), 0.3, t_out=t1 - 0.2)
    for k, hr in enumerate(L["hours"]):
        show(ctx, ctx.text(hr, 22, "#9AA8C7", 1.5, "NORMAL").move_to(o + np.array([w * k / 4, -h - 0.35, 0.0])), 0.4, t_out=t1 - 0.2)
    fn = lambda u: math.cos(2 * math.pi * (u * 24 / 12.42 - 0.3))
    u_end = max(5.0, t1 - 1.2)
    ctx.add(orbital.curve(o, w, h, fn, lambda: level(ctx, 0.6, u_end - 0.6), "#2EC5FF", 8, alpha=window(ctx, 0.2, t1 - 0.2)), z=4)
    for k, (u, txt) in enumerate(((0.155, "high"), (0.413, "low"), (0.672, "high"), (0.93, "low"))):
        y = h * fn(u) + (0.45 if txt == "high" else -0.45)
        show(ctx, ctx.text(L[txt], 26, "#FFD166" if txt == "high" else "#7FD6FF", 2.0).move_to(o + np.array([w * u, y, 0.0])),
             0.6 + u * (u_end - 0.6), t_out=t1 - 0.2)

    # ---- B: the Moon pulls the sea up on its side ... and the far side bulges too
    E = C + np.array([1.4, 0.0, 0.0])
    t_far = ctx.tt(1, 3) if len(ctx.config["subs"][1]["text"]) > 0 else t1 + 6
    ctx.add(orbital.ocean_earth(E, 1.3, bulge=lambda: math.pi, amp=lambda: 0.34 * level(ctx, t1 + 0.4, 0.9),
                                offset=lambda: 0.42 * (1 - level(ctx, t_far, 1.0)), rot=lambda: 0.15 * tl.t,
                                alpha=window(ctx, t1, t2 - 0.2)), z=3)
    M = C + np.array([-3.0, 0.2, 0.0])
    show(ctx, orbital.moon(M, 0.45), t1, t_out=t2 - 0.2, z=4)
    show(ctx, ctx.text(L["moon"], 28, "#E6E6E6", 2.0).move_to(M + np.array([0.0, -0.85, 0.0])), t1 + 0.3, t_out=t2 - 0.2)
    show(ctx, Arrow(E + np.array([-1.5, 0.0, 0.0]), M + np.array([0.6, 0.0, 0.0]), buff=0, color="#FFD166", stroke_width=6), t1 + 0.6, t_out=t2 - 0.2, z=4)
    show(ctx, ctx.text(L["q"], 90, "#FF8FA3", 1.5).move_to(E + np.array([2.1, 0.0, 0.0])), t_far - 1.0, t_out=t_far + 0.2)
    show(ctx, Arrow(E + np.array([1.9, 0.0, 0.0]), E + np.array([2.6, 0.0, 0.0]), buff=0, color="#FF8FA3", stroke_width=6), t_far + 0.4, t_out=t2 - 0.2, z=4)

    # ---- C: a harbour that lives by the tide
    base = C[1] - 1.9
    wlev = lambda: base + 1.0 + 0.8 * math.sin(2 * math.pi * (tl.t - t2) / 6.0)
    sea = always_redraw(lambda: Rectangle(width=W - 0.4, height=max(0.05, wlev() - (C[1] - 2.3)), stroke_width=0, fill_color="#1F6FB5",
                                          fill_opacity=0.85 * window(ctx, t2, t3 - 0.2)()).move_to((C[0], (wlev() + C[1] - 2.3) / 2, 0)))
    sea._dynamic = True
    ctx.add(sea, z=2)
    bt = always_redraw(lambda: orbital.boat(np.array([C[0] - 1.0, wlev() + 0.15 + 0.06 * math.sin(tl.t * 2.2), 0.0]), 1.2).set_opacity(window(ctx, t2, t3 - 0.2)()))
    bt._dynamic = True
    ctx.add(bt, z=3)
    for dx in (3.2, 4.3, 5.3):
        house = VGroup(Rectangle(width=0.8, height=0.7, stroke_width=0, fill_color="#8D99AE", fill_opacity=1),
                       Polygon((-0.5, 0.35, 0), (0.5, 0.35, 0), (0, 0.85, 0), stroke_width=0, fill_color="#C0392B", fill_opacity=1)).move_to(C + np.array([dx, -0.95, 0.0]))
        show(ctx, house, t2 + 0.2, t_out=t3 - 0.2)
    show(ctx, ctx.text({"en": "boats, beaches, coasts", "hi": "नावें, तट, किनारे"}[ctx.lang], 34, "#FFD166", W * 0.9).move_to(C + np.array([0.0, 2.3, 0.0])), t2 + 0.4, t_out=t3 - 0.2)

    # ---- D: three questions this video answers
    for k, (txt, col) in enumerate(((L["c1"], "#2EC5FF"), (L["c2"], "#F4C95D"), (L["c3"], "#FF8FA3"))):
        x = C[0] + (k - 1) * 3.5
        card = RoundedRectangle(corner_radius=0.3, width=3.1, height=3.3, stroke_color=col, stroke_width=4, fill_color="#16213E", fill_opacity=1).move_to((x, C[1] + 0.2, 0))
        t_k = ctx.tt(3, 0) + 0.8 * k + 0.6
        show(ctx, card, t_k, pop=0.2)
        if k == 0:
            ctx.add(orbital.ocean_earth(np.array([x, C[1] + 0.7, 0.0]), 0.75, bulge=lambda: math.pi, amp=lambda: 0.4, rot=lambda: 0.4 * tl.t, alpha=window(ctx, t_k, None)), z=5)
        elif k == 1:
            show(ctx, icons.icon("clock", 1.4).move_to((x, C[1] + 0.7, 0)), t_k, z=5)
        else:
            show(ctx, orbital.building((x - 0.7, C[1] - 0.2), 4, 0.36, 1.2), t_k, z=5)
        show(ctx, ctx.text(txt, 28, col, 2.8).move_to((x, C[1] - 1.1, 0)), t_k + 0.2, z=6)
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t_far)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
