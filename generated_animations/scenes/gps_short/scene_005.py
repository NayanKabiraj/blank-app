"""Shot 5 (scene 6): one distance is a circle; two narrow it down; three cross at one point - you."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Dot, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, lighting, particles
from generated_animations.timed import level, show

T = {"en": {"you": "You are here"}, "hi": {"you": "आप यहाँ हैं"}}
COLS = ["#7FD6FF", "#F4C95D", "#FF8FA3"]


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    sub = ctx.config["subs"][0]
    times = [t for _s, t, _e in ctx.sentences(sub["text"], sub["start"], sub["end"] - sub["start"])]
    times += [times[-1]] * (4 - len(times))
    me = C + np.array([0.2, 0.2, 0.0])
    sats = [C + np.array([-2.6, 3.0, 0.0]), C + np.array([2.8, 2.4, 0.0]), C + np.array([-0.4, -2.4, 0.0])]
    for k, S in enumerate(sats):
        show(ctx, diagrams.satellite(S, 0.55), 0.1 + 0.15 * k, z=4)
        r = float(np.linalg.norm(S - me))
        t_k = times[k]

        def circ(S=S, r=r, t_k=t_k, col=COLS[k]):
            f = level(ctx, t_k, 1.3)
            return Arc(radius=r, start_angle=math.pi / 2, angle=2 * math.pi * max(0.002, f), arc_center=S, stroke_color=col, stroke_width=5)
        c = always_redraw(circ)
        c._dynamic = True
        ctx.add(c, z=1)
    t_found = times[3] if len(times) > 3 else times[-1]
    show(ctx, lighting.glow(me, "#4CD97B", 0.75), t_found, pop=0.3, z=5)
    show(ctx, diagrams.location_dot(me, "#4CD97B", 0.18), t_found, pop=0.4, z=6)
    sp = particles.Sparkle(me, tl, "#FFD166", n=24, speed=1.8, life=1.0)
    ctx.add(sp, z=7)
    show(ctx, ctx.text(L["you"], 34, "#4CD97B").move_to(me + np.array([0.0, -0.95, 0.0])), t_found + 0.2)
    ctx.avatar.look_at(me)
    ctx.play(gestures.point_at(ctx.avatar, lambda: sats[min(2, int(max(0, (ctx.elapsed() - times[0]) // 1.8)))] if ctx.elapsed() < t_found else me, 0.5),
             expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t_found - 0.1)
    sp.restart()
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), run_time=0.4)
