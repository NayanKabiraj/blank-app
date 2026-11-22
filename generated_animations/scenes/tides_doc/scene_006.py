"""Shot 6 (chapter 4, scenes 20-23): spring and neap tides - the Moon orbits through a month while the Sun, Earth and Moon line up and un-line."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Dot, Line, RoundedRectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import orbital
from generated_animations.timed import level, show, window

T = {"en": {"spring": "SPRING TIDE", "neap": "NEAP TIDE", "new": "new", "full": "full", "q": "quarter", "same": "same way = big", "side": "sideways = small",
            "chat": ["Spring tides in spring?", "No. Twice a month", "When exactly?", "New moon, full moon"], "sun": "Sun"},
     "hi": {"spring": "बड़ा ज्वार", "neap": "छोटा ज्वार", "new": "अमावस", "full": "पूर्णिमा", "q": "अर्ध चाँद", "same": "एक तरफ़ = बड़ा", "side": "बगल से = छोटा",
            "chat": ["क्या बड़े ज्वार रोज़ आते हैं?", "नहीं, महीने में दो बार", "कब?", "अमावस और पूर्णिमा पर"], "sun": "सूरज"}}
PERIOD = 8.0


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_rope, t_cycle, t_chat = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3)
    E = np.array([C[0] + 3.0, C[1] + 0.0, 0.0])
    R, ORB = 1.0, 1.85
    t0 = ctx.tt(0, 0) + 0.4
    phi = lambda: 2 * math.pi * max(0.0, ctx.elapsed() - t0) / PERIOD            # 0 = new moon (Moon between Earth and Sun)
    spring = lambda: math.cos(2 * phi())
    ctx.add(orbital.ocean_earth(E, R, bulge=phi, amp=lambda: 0.2 + 0.13 * spring(), rot=lambda: 0.4 * tl.t, alpha=window(ctx, 0.1, None)), z=3)
    show(ctx, orbital.sun(np.array([E[0] + 4.2, E[1], 0.0]), 0.42), 0.2, pop=0.3, z=2)
    show(ctx, ctx.text(L["sun"], 22, "#FFE08A", 1.5).move_to((E[0] + 4.2, E[1] - 0.85, 0)), 0.4)
    show(ctx, Circle(radius=ORB, stroke_color="#4A5A80", stroke_width=2, stroke_opacity=0.7).move_to(E), 0.3, pop=0)
    mm = always_redraw(lambda: orbital.moon(E + ORB * np.array([math.cos(phi()), math.sin(phi()), 0.0]), 0.26))
    mm._dynamic = True
    ctx.add(mm, z=4)
    # SPRING / NEAP labels follow the phase
    lab_s = ctx.text(L["spring"], 40, "#4CD97B", 5.0).move_to(E + np.array([0.0, 2.75, 0.0]))
    lab_n = ctx.text(L["neap"], 40, "#7FD6FF", 5.0).move_to(E + np.array([0.0, 2.75, 0.0]))
    for lab, sign in ((lab_s, 1), (lab_n, -1)):
        def upd(m, sign=sign):
            a = max(0.0, min(1.0, (sign * spring() - 0.35) / 0.4)) * (1.0 if ctx.elapsed() > t0 else 0.0) * (1.0 - max(0.0, min(1.0, (ctx.elapsed() - (ctx.duration - 0.2)) / 0.2)))
            for s in m.get_family():
                if hasattr(s, "set_fill"):
                    s.set_fill(opacity=a, family=False)
        upd(lab)
        lab.add_updater(upd)
        ctx.scene.add(lab)
        lab.set_z_index(6)
        ctx.objects.append(lab)
    # phase names around the orbit
    for ang, key in ((0.0, "new"), (math.pi / 2, "q"), (math.pi, "full"), (-math.pi / 2, "q")):
        p = E + (ORB + 0.55) * np.array([math.cos(ang), math.sin(ang), 0.0])
        show(ctx, ctx.text(L[key], 20, "#9AA8C7", 1.6, "NORMAL").move_to(p), t_cycle, z=5)

    # scene 21: two friends and a rope - same way = big, sideways = small
    bx, by = C[0] - 2.1, C[1] + 0.2
    def block():
        a = level(ctx, ctx.tt(1, 1), 1.5)
        b = level(ctx, ctx.tt(1, 3), 1.5) if len(ctx.config["subs"]) > 1 else 0.0
        return np.array([bx + 0.9 * a - 0.55 * b, by + 0.5 * b, 0.0])
    blk = always_redraw(lambda: VGroup(Circle(radius=0.01, fill_opacity=0, stroke_width=0), orbital.Rectangle(width=0.9, height=0.9, stroke_color="#F5F7FA", stroke_width=3, stroke_opacity=window(ctx, t_rope, t_cycle - 0.2)(), fill_color="#5B6B96", fill_opacity=window(ctx, t_rope, t_cycle - 0.2)()).move_to(block())))
    blk._dynamic = True
    ctx.add(blk, z=4)

    def person(x, y, col):
        return VGroup(Circle(radius=0.2, stroke_color=col, stroke_width=4, fill_opacity=0).move_to((x, y + 0.65, 0)), Line((x, y + 0.45, 0), (x, y - 0.35, 0), color=col, stroke_width=5),
                      Line((x, y - 0.35, 0), (x - 0.2, y - 0.85, 0), color=col, stroke_width=5), Line((x, y - 0.35, 0), (x + 0.2, y - 0.85, 0), color=col, stroke_width=5))
    pa, pb = person(bx + 2.2, by + 0.9, "#2EC5FF"), person(bx + 2.2, by - 0.6, "#F4C95D")
    for p in (pa, pb):
        show(ctx, p, t_rope + 0.2, t_out=t_cycle - 0.2, z=5)
    for yy, col in ((by + 0.75, "#2EC5FF"), (by - 0.4, "#F4C95D")):
        r = always_redraw(lambda yy=yy, col=col: Line((bx + 0.5, by + (yy - by) * 0.5, 0), (bx + 2.0, yy, 0), color=col, stroke_width=4, stroke_opacity=window(ctx, t_rope, t_cycle - 0.2)()))
        r._dynamic = True
        ctx.add(r, z=3)
    show(ctx, ctx.text(L["same"], 26, "#4CD97B", 3.4).move_to((bx + 0.6, by + 1.95, 0)), ctx.tt(1, 1), t_out=ctx.tt(1, 3))
    show(ctx, ctx.text(L["side"], 26, "#7FD6FF", 3.4).move_to((bx + 0.6, by + 1.95, 0)), ctx.tt(1, 3), t_out=t_cycle - 0.2)

    # scene 23: viewer chat
    for k, txt in enumerate(L["chat"]):
        viewer = k % 2 == 0
        b = ctx.text(txt, 24, "#F5F7FA", 3.4)
        box = RoundedRectangle(corner_radius=0.25, width=3.5, height=0.8, stroke_color="#6D8FD6" if viewer else "#4CD97B", stroke_width=3,
                               fill_color="#27427A" if viewer else "#1E6B4E", fill_opacity=1).move_to((C[0] - 2.0 + (0 if viewer else 0.4), C[1] + 1.6 - k * 1.0, 0))
        b.move_to(box)
        show(ctx, VGroup(box, b), ctx.tt(3, min(k, 3)) if k else t_chat + 0.3, t_out=None, pop=0.2, z=6)
    ctx.avatar.look_at(lambda: E)
    ctx.play(gestures.point_at(ctx.avatar, lambda: E + ORB * np.array([math.cos(phi()), math.sin(phi()), 0.0]), 0.5), expressions.set_expression(ctx.avatar, "excited", 0.4), run_time=0.6)
    ctx.until(t_rope)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.6)
