"""Shot 8 (chapter 5, scenes 27-30): tide tables, the three answers, no Moon (the Sun alone), and the close."""
from __future__ import annotations

import math

import numpy as np
from manim import Cross, Line, Polygon, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import icons, orbital
from generated_animations.timed import level, show, window

T = {"en": {"table": "tide table", "hl": ["high", "low"], "a": ["two bulges", "50 min later", "Fundy: coast shape"], "sun": "Sun only", "small": "much smaller tides",
            "close": "One Moon, two bulges", "moon": "Moon"},
     "hi": {"table": "ज्वार तालिका", "hl": ["ज्वार", "भाटा"], "a": ["दो उभार", "50 मिनट देरी", "फ़ंडी: तट का आकार"], "sun": "सिर्फ़ सूरज", "small": "बहुत छोटे ज्वार",
            "close": "एक चाँद, दो उभार", "moon": "चाँद"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t27, t28, t29 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3)

    # scene 27: a tide table - two highs and two lows a day, every day
    show(ctx, ctx.text(L["table"], 40, "#FFD166", 5.0).move_to(C + np.array([0.0, 2.35, 0.0])), 0.3, t_out=t27 - 0.2)
    for d in range(5):
        for r, ev in enumerate(("hl0", "lo0", "hl1", "lo1")):
            high = ev.startswith("hl")
            x = C[0] - 3.6 + d * 1.8
            y = C[1] + 1.2 - r * 0.85
            cell = RoundedRectangle(corner_radius=0.15, width=1.5, height=0.66, stroke_color="#3C4F7A", stroke_width=2, fill_color="#16213E", fill_opacity=1).move_to((x, y, 0))
            tri = Polygon((x - 0.28, y - 0.17, 0), (x + 0.28, y - 0.17, 0), (x, y + 0.2, 0) if high else (x, y + 0.2, 0), stroke_width=0, fill_color="#FFD166" if high else "#2EC5FF", fill_opacity=1)
            if not high:
                tri.rotate(math.pi)
            show(ctx, VGroup(cell, tri), 0.6 + 0.12 * (d * 4 + r), t_out=t27 - 0.2, pop=0.3)

    # scene 28: the three answers light up one by one
    ts = [ctx.tt(1, 1), ctx.tt(1, 3), ctx.tt(1, 5)]
    for k, (txt, col) in enumerate(zip(L["a"], ("#2EC5FF", "#F4C95D", "#FF8FA3"))):
        x = C[0] + (k - 1) * 3.6
        card = RoundedRectangle(corner_radius=0.3, width=3.2, height=3.2, stroke_color=col, stroke_width=4, fill_color="#16213E", fill_opacity=1).move_to((x, C[1] + 0.1, 0))
        show(ctx, card, t27 + 0.3 + 0.25 * k, pop=0.2, t_out=t28 - 0.2)
        if k == 0:
            ctx.add(orbital.ocean_earth(np.array([x, C[1] + 0.6, 0.0]), 0.75, bulge=lambda: math.pi, amp=lambda: 0.4, rot=lambda: 0.5 * tl.t, alpha=window(ctx, ts[k], t28 - 0.2)), z=5)
        elif k == 1:
            show(ctx, icons.icon("clock", 1.4).move_to((x, C[1] + 0.6, 0)), ts[k], t_out=t28 - 0.2, z=5)
        else:
            fun = Polygon((x - 1.1, C[1] + 1.3, 0), (x + 1.1, C[1] + 0.75, 0), (x + 1.1, C[1] + 0.45, 0), (x - 1.1, C[1] - 0.1, 0), stroke_color="#7FD6FF", fill_color="#14507E", fill_opacity=0.9)
            show(ctx, fun, ts[k], t_out=t28 - 0.2, z=5)
        show(ctx, ctx.text(txt, 26, col, 3.0).move_to((x, C[1] - 0.95, 0)), ts[k] + 0.2, t_out=t28 - 0.2, z=6)

    # scene 29: no Moon - only the Sun's small tide
    E = C + np.array([0.6, 0.1, 0.0])
    ctx.add(orbital.ocean_earth(E, 1.25, bulge=lambda: 0.0, amp=lambda: 0.1, rot=lambda: 0.3 * tl.t, alpha=window(ctx, t28, t29 - 0.2)), z=3)
    show(ctx, orbital.sun(E + np.array([4.6, 0.0, 0.0]), 0.5), t28, t_out=t29 - 0.2, pop=0.3)
    mo = orbital.moon(E + np.array([-3.4, 0.0, 0.0]), 0.5)
    show(ctx, mo, t28, t_out=t29 - 0.2)
    show(ctx, Cross(mo, stroke_color="#FF4D6D", stroke_width=10).scale(1.2), t28 + 0.8, t_out=t29 - 0.2, z=6)
    show(ctx, ctx.text(L["sun"], 30, "#FFE08A", 4.0).move_to(E + np.array([4.6, -1.1, 0.0])), t28 + 0.3, t_out=t29 - 0.2)
    show(ctx, ctx.text(L["small"], 36, "#7FD6FF", 6.0).move_to(E + np.array([0.0, 2.0, 0.0])), t28 + 1.2, t_out=t29 - 0.2)

    # scene 30: one Moon, two bulges, a spinning Earth
    phi = lambda: 0.9 * (ctx.elapsed() - t29)
    ctx.add(orbital.ocean_earth(E, 1.2, bulge=phi, amp=lambda: 0.36 * level(ctx, t29, 0.8), rot=lambda: 0.6 * tl.t, alpha=window(ctx, t29, None)), z=3)
    mm = always_redraw(lambda: orbital.moon(E + 2.2 * np.array([math.cos(phi()), math.sin(phi()), 0.0]), 0.3).set_opacity(window(ctx, t29, None)()))
    mm._dynamic = True
    ctx.add(mm, z=4)
    show(ctx, ctx.text(L["close"], 46, "#FFD166", 8.0).move_to(E + np.array([0.0, -2.3, 0.0])), t29 + 0.4)
    ctx.avatar.look_at(None)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "happy", 0.4), run_time=0.6)
    ctx.until(t28)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.3), run_time=0.4)
    ctx.until(t29)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), gestures.wave(ctx.avatar, 0.4), run_time=0.5)
