"""Shot 2 (chapter 2, scenes 5-10): the long fall - how far away, a warped sky, one star seen twice, escaping from outside, small vs giant, the crossing."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, DashedLine, Line, Polygon, VGroup, VMobject, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, diagrams, icons, orbital, particles
from generated_animations.timed import level, show, window

T = {"ly": "about 1,500 light-years", "safe": "Earth: safe", "bh": "nearest known black hole", "light": "light needs ~1,500 years to arrive", "sky": "the sky warps into rings", "two": "the same star, twice",
     "eye": "you", "esc": "escape is possible", "zone": "point of no return", "small": "small black hole", "giant": "giant black hole", "hurts": "strong stretch", "gentle": "gentle", "feel": "you may feel nothing special",
     "crash": "a crash?"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t5, t6, t7, t8, t9 = (ctx.t_of(i) for i in (1, 2, 3, 4, 5))
    # ---- scene 5: a very long way off
    ex, bx = C[0] - 3.0, C[0] + 5.0
    y = C[1] + 0.2
    ctx.add(diagrams.earth(np.array([ex, y, 0.0]), 0.45, tl), z=3)
    show(ctx, ctx.text(T["safe"], 28, "#4CD97B", 3.0).move_to((ex, y - 0.9, 0)), 0.5, t_out=t5 - 0.2)
    ctx.add(blackhole.black_hole(np.array([bx, y, 0.0]), 0.55, tl, alpha=window(ctx, 0.2, t5 - 0.2)), z=3)
    show(ctx, ctx.text(T["bh"], 26, "#FFC857", 4.0).move_to((bx - 0.4, y - 1.0, 0)), 0.8, t_out=t5 - 0.2)
    show(ctx, DashedLine((ex + 0.7, y, 0), (bx - 1.0, y, 0), color="#7FD6FF", stroke_width=3, dash_length=0.2), 0.6, t_out=t5 - 0.2, pop=0)
    ctx.add(particles.signal_packets(lambda: np.array([bx - 1.0, y, 0.0]), lambda: np.array([ex + 0.7, y, 0.0]), tl, "#FFD166", n=4, period=4.0, size=0.09), z=4)
    show(ctx, ctx.text(T["ly"], 44, "#FFD166", 8.0).move_to((C[0] + 1.5, y + 1.3, 0)), 0.8, t_out=t5 - 0.2)
    show(ctx, ctx.text(T["light"], 26, "#9AA8C7", 8.0, "NORMAL").move_to((C[0] + 1.5, y - 1.5, 0)), 1.6, t_out=t5 - 0.2)
    # ---- scene 6: the warped sky as you fall (the black hole grows and the stars bend)
    BC = C + np.array([2.2, 0.2, 0.0])
    grow = lambda: 0.5 + 0.6 * level(ctx, t5 + 0.5, t6 - t5 - 1.0)
    ctx.add(blackhole.starfield(C, W, H, 80, BC, 1.0, warp=lambda: 0.4 + 1.6 * level(ctx, t5 + 0.5, t6 - t5 - 1.0), alpha=window(ctx, t5, t6 - 0.2)), z=1)
    ctx.add(blackhole.black_hole(BC, 1.0, tl, alpha=window(ctx, t5, t6 - 0.2)), z=3)
    show(ctx, ctx.text(T["sky"], 34, "#FFD166", 8.0).move_to(C + np.array([-0.4, 2.55, 0.0])), t5 + 1.0, t_out=t6 - 0.2)
    # ---- scene 7: one star, seen twice (light curves around both sides)
    sx = C + np.array([-3.0, 0.2, 0.0])
    ob = C + np.array([6.4, 0.2, 0.0])
    show(ctx, Circle(radius=0.7, stroke_color="#FFD27F", stroke_width=3, fill_color="#000000", fill_opacity=1).move_to(C + np.array([1.4, 0.2, 0.0])), t6, t_out=t7 - 0.2, z=3)
    mid = C + np.array([1.4, 0.2, 0.0])
    for sgn in (1, -1):
        pts = [sx + (ob - sx) * u + np.array([0.0, sgn * 1.7 * math.sin(math.pi * u), 0.0]) for u in np.linspace(0, 1, 40)]
        pm = VMobject(stroke_color="#FFD166", stroke_width=5, fill_opacity=0)
        pm.set_points_as_corners(pts)
        show(ctx, pm, t6 + 0.8, t_out=t7 - 0.2, pop=0, z=4)
    show(ctx, Circle(radius=0.14, stroke_width=0, fill_color="#F5F7FA", fill_opacity=1).move_to(sx), t6 + 0.2, t_out=t7 - 0.2, z=5)
    show(ctx, icons.icon("star", 0.5).move_to(mid + np.array([0.0, 1.0, 0.0])), t6 + 2.2, t_out=t7 - 0.2, z=5)
    show(ctx, icons.icon("star", 0.5).move_to(mid + np.array([0.0, -0.6, 0.0])), t6 + 2.2, t_out=t7 - 0.2, z=5)
    show(ctx, ctx.text(T["eye"], 26, "#7FD6FF", 2.0).move_to(ob + np.array([0.0, -0.7, 0.0])), t6 + 0.4, t_out=t7 - 0.2)
    show(ctx, ctx.text(T["two"], 34, "#FFD166", 7.0).move_to(C + np.array([0.8, 2.55, 0.0])), t6 + 2.0, t_out=t7 - 0.2)
    # ---- scene 8: escape is possible from outside the horizon
    hc = C + np.array([2.0, 0.2, 0.0])
    ctx.add(blackhole.black_hole(hc, 0.8, tl, alpha=window(ctx, t7, t8 - 0.2), disk=False), z=3)
    show(ctx, Circle(radius=2.1, stroke_color="#4CD97B", stroke_width=3, fill_opacity=0.0).move_to(hc), t7 + 0.4, t_out=t8 - 0.2, pop=0)
    show(ctx, Circle(radius=0.8, stroke_color="#FF4D6D", stroke_width=5, fill_opacity=0).move_to(hc), t7 + 0.4, t_out=t8 - 0.2, pop=0, z=5)
    rk = lambda: hc + np.array([-1.7 - 1.7 * level(ctx, t7 + 0.8, 4.0), 0.5 + 0.9 * level(ctx, t7 + 0.8, 4.0), 0.0])
    rocket = always_redraw(lambda: icons.icon("rocket", 0.7).rotate(2.2).move_to(rk()).set_opacity(window(ctx, t7 + 0.5, t8 - 0.2)()))
    rocket._dynamic = True
    ctx.add(rocket, z=6)
    show(ctx, ctx.text(T["esc"], 32, "#4CD97B", 6.0).move_to(hc + np.array([0.0, -2.6, 0.0])), t7 + 1.0, t_out=t8 - 0.2)
    show(ctx, ctx.text(T["zone"], 28, "#FF4D6D", 5.0).move_to(hc + np.array([0.0, 0.0, 0.0])), t7 + 1.4, t_out=t8 - 0.2, z=7)
    # ---- scene 9: small vs giant black hole and the gradient across a body
    for k, (R, x, name, col, arrow_len) in enumerate(((0.4, C[0] - 2.4, T["small"], "#FF4D6D", 1.2), (1.4, C[0] + 2.7, T["giant"], "#4CD97B", 0.25))):
        ctr = np.array([x, C[1] + 0.4, 0.0])
        ctx.add(blackhole.black_hole(ctr, R, tl, alpha=window(ctx, t8 + 0.3, t9 - 0.2), disk=False), z=3)
        show(ctx, ctx.text(name, 30, col, 4.5).move_to(ctr + np.array([0.0, -2.0, 0.0])), t8 + 0.6, t_out=t9 - 0.2)
        pos = ctr + np.array([R + 0.9 if k == 0 else R + 0.9, 0.0, 0.0])
        show(ctx, blackhole.astronaut(pos + np.array([0.0, 0.0, 0.0]), 0.8, 1.0, math.pi / 2), t8 + 1.0, t_out=t9 - 0.2, z=6)
        for sgn in (-1, 1):
            show(ctx, Arrow(pos + np.array([0.0, sgn * 0.3, 0.0]), pos + np.array([0.0, sgn * (0.3 + arrow_len), 0.0]), buff=0, color=col, stroke_width=6, max_tip_length_to_length_ratio=0.5), t8 + 1.8, t_out=t9 - 0.2, z=6)
        show(ctx, ctx.text(T["hurts"] if k == 0 else T["gentle"], 24, col, 3.5, "NORMAL").move_to(pos + np.array([0.0, 1.9, 0.0])), t8 + 2.0, t_out=t9 - 0.2)
    # ---- scene 10: crossing the horizon of a giant black hole - you may feel nothing
    gc = C + np.array([2.2, 0.2, 0.0])
    ctx.add(blackhole.black_hole(gc, 1.5, tl, alpha=window(ctx, t9, None), disk=False), z=3)
    show(ctx, Circle(radius=1.5, stroke_color="#FF4D6D", stroke_width=5, fill_opacity=0).move_to(gc), t9 + 0.3, pop=0, z=5)
    pa = lambda: gc + np.array([-3.4 + 3.4 * level(ctx, t9 + 0.5, 6.0), 0.8 - 0.8 * level(ctx, t9 + 0.5, 6.0), 0.0])
    fig = always_redraw(lambda: blackhole.astronaut(pa(), 0.8, 1.0, -0.9).set_opacity(window(ctx, t9 + 0.3, None)()))
    fig._dynamic = True
    ctx.add(fig, z=6)
    show(ctx, ctx.text(T["crash"], 40, "#FF4D6D", 3.0).move_to(C + np.array([-2.6, 2.4, 0.0])), t9 + 0.5, t_out=ctx.tt(5, 1), z=7)
    show(ctx, ctx.text(T["feel"], 34, "#4CD97B", 7.0).move_to(C + np.array([0.4, -2.45, 0.0])), ctx.tt(5, 1) + 0.3, z=7)
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "curious", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t6)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t8)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(ctx.tt(5, 1))
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
