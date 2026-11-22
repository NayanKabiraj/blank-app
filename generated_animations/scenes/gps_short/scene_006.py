"""Shot 6 (scene 7): quiz - three satellites fix the position, a fourth fixes the phone's clock."""
from __future__ import annotations

import math

import numpy as np
from manim import Line, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, icons
from generated_animations.timed import level, show

T = {"en": {"pos": ["1", "2", "3"], "clock": "clock", "opts": ["2", "3", "4"], "q": "How many satellites?"},
     "hi": {"pos": ["1", "2", "3"], "clock": "घड़ी", "opts": ["2", "3", "4"], "q": "कितने सैटेलाइट?"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    sub = ctx.config["subs"][0]
    s_times = [t for _s, t, _e in ctx.sentences(sub["text"], sub["start"], sub["end"] - sub["start"])]
    t_q = s_times[0]
    t_a = s_times[1] if len(s_times) > 1 else s_times[0] + 2.0
    P = C + np.array([0.0, -0.3, 0.0])
    show(ctx, diagrams.phone(P, 0.85), 0.1, z=3)
    show(ctx, ctx.text(L["q"], 42, "#FFD166", W * 0.9).move_to(C + np.array([0.0, 5.0, 0.0])), 0.2)
    # options row
    for k, o in enumerate(L["opts"]):
        show(ctx, ctx.text(o, 48, "#F5F7FA", 1.2).move_to(C + np.array([(k - 1) * 2.0, 4.1, 0.0])), 0.4 + 0.15 * k)
    from manim import RoundedRectangle
    hi = RoundedRectangle(corner_radius=0.3, width=1.5, height=1.0, stroke_color="#4CD97B", stroke_width=6, fill_opacity=0).move_to(C + np.array([2.0, 4.1, 0.0]))
    show(ctx, hi, t_a, pop=0.3, z=6)
    # satellites light up one after another around the phone (3 for position, a fourth for the clock)
    offs = [(-2.9, 1.5), (2.9, 1.5), (-2.5, -1.6), (2.5, -1.6)]
    for k, (dx, dy) in enumerate(offs):
        S = P + np.array([dx, dy, 0.0])
        col = "#7FD6FF" if k < 3 else "#F4C95D"
        t_k = (t_q + 0.6 + 0.6 * k) if k < 3 else t_a
        show(ctx, diagrams.satellite(S, 0.6), t_k, pop=0.3, z=4)
        line = always_redraw(lambda S=S, col=col, t_k=t_k: Line(S, P, color=col, stroke_width=4, stroke_opacity=0.7 * level(ctx, t_k + 0.2, 0.4)))
        line._dynamic = True
        ctx.add(line, z=2)
        label = L["pos"][k] if k < 3 else L["clock"]
        show(ctx, ctx.text(label, 30, col, 2.0).move_to(S + np.array([0.0, -0.8, 0.0])), t_k + 0.2)
    show(ctx, icons.icon("clock", 0.9).move_to(P + np.array([2.5, -2.9, 0.0])), t_a + 0.3, pop=0.3, z=5)
    ctx.avatar.look_at(P)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t_a)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
