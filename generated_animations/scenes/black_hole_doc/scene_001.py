"""Shot 1 (chapter 1, scenes 1-5: opening, intro roadmap, then the pull / squeeze / horizon): a dark circle with a glowing ring; a black hole pulls like any star of the same mass; squeezing the Sun to 6 km; the event horizon."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, Dot, DashedLine, Line, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, orbital
from generated_animations.timed import level, show, window

T = {"you": "you", "star": "a star", "bh": "a black hole", "same": "same mass, same orbit far away", "sun": "the Sun: a ball 6 km wide", "earth": "Earth: a marble",
     "hz": "event horizon", "esc": "escapes", "no": "no way back", "no2": "not even light", "intro": "In this video", "c1": "how it forms", "c2": "the fall", "c3": "time goes strange"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    ti = ctx.t_of(1)                     # scene 2 = the intro (a roadmap of what the video will show)
    t1, t2, t3 = ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    # ---- A: a dark circle with a glowing ring, and you drifting toward it
    BC = C + np.array([2.3, 0.2, 0.0])
    ctx.add(blackhole.starfield(C, W, H, 70, BC, 1.1, warp=lambda: 0.8, alpha=window(ctx, 0.1, t1 - 0.2)), z=1)
    ctx.add(blackhole.black_hole(BC, 1.1, tl, alpha=window(ctx, 0.2, t1 - 0.2)), z=3)
    ship = lambda: np.array([C[0] - 3.0 + 2.1 * level(ctx, 0.8, t1 - 1.4), C[1] - 1.7 + 1.0 * level(ctx, 0.8, t1 - 1.4), 0.0])
    me = always_redraw(lambda: blackhole.astronaut(ship(), 0.9, 1.0, -0.6).set_opacity(window(ctx, 0.5, t1 - 0.2)()))
    me._dynamic = True
    ctx.add(me, z=5)
    show(ctx, ctx.text(T["you"], 30, "#FFD166", 2.0).move_to(C + np.array([-3.0, -2.35, 0.0])), 0.9, t_out=t1 - 0.2)
    # ---- intro: three chips appear as the narrator names what the video will show
    from manim import RoundedRectangle
    show(ctx, ctx.text(T["intro"], 40, "#FFFFFF", 6.0).move_to(C + np.array([-2.6, 3.1, 0.0])), ti + 0.1, t_out=t1 - 0.3, z=7)
    for n, (key, col) in enumerate((("c1", "#7FD6FF"), ("c2", "#FFD166"), ("c3", "#9BE59B"))):
        box = RoundedRectangle(corner_radius=0.3, width=4.6, height=0.8, stroke_color=col, stroke_width=5, fill_color="#10163A", fill_opacity=0.92)
        chip = VGroup(box, ctx.text(f"{n + 1}  {T[key]}", 34, col, 4.2)).move_to(C + np.array([-2.6, 2.1 - 0.95 * n, 0.0]))
        show(ctx, chip, ti + 1.6 + 1.7 * n, t_out=t1 - 0.3, pop=0.25, z=7)
    # ---- B: far away a black hole pulls like a star of the same mass - the same planet orbit
    xs = (C[0] - 1.9, C[0] + 4.1)
    for k, x in enumerate(xs):
        ctr = np.array([x, C[1] + 0.3, 0.0])
        if k == 0:
            show(ctx, orbital.sun(ctr, 0.4), t1 + 0.2, t_out=t2 - 0.2, pop=0.2)
        else:
            ctx.add(blackhole.black_hole(ctr, 0.4, tl, alpha=window(ctx, t1 + 0.2, t2 - 0.2), disk=True), z=3)
        pl = always_redraw(lambda ctr=ctr: Dot(ctr + 1.7 * np.array([math.cos(1.1 * tl.t), math.sin(1.1 * tl.t), 0.0]), radius=0.15, color="#2EC5FF", fill_opacity=window(ctx, t1 + 0.3, t2 - 0.2)()))
        pl._dynamic = True
        ctx.add(pl, z=4)
        ring = Circle(radius=1.7, stroke_color="#3C4F7A", stroke_width=2).move_to(ctr)
        show(ctx, ring, t1 + 0.3, t_out=t2 - 0.2, pop=0)
        show(ctx, ctx.text(T["star"] if k == 0 else T["bh"], 28, "#F5F7FA", 3.5).move_to(ctr + np.array([0.0, -2.2, 0.0])), t1 + 0.5, t_out=t2 - 0.2)
    show(ctx, ctx.text(T["same"], 30, "#FFD166", 8.0).move_to(C + np.array([1.2, 2.6, 0.0])), t1 + 2.0, t_out=t2 - 0.2)
    # ---- C: squeeze the Sun into a ball about 6 km wide - it becomes a black hole
    sc = C + np.array([-0.2, 0.4, 0.0])
    t_sq = ctx.tt(3, 1)
    rad = lambda: max(0.05, 1.6 * (1 - level(ctx, t_sq, 3.2)) ** 3)
    sun = always_redraw(lambda: VGroup(Circle(radius=rad() * 1.15, stroke_width=0, fill_color="#FFB703", fill_opacity=0.25 * window(ctx, t2 + 0.2, t3 - 0.2)()).move_to(sc),
                                       Circle(radius=rad(), stroke_color="#FFE08A", stroke_width=3, fill_color="#000000" if level(ctx, t_sq + 2.6, 0.4) > 0.5 else "#FFC93C",
                                              fill_opacity=window(ctx, t2 + 0.2, t3 - 0.2)(), stroke_opacity=window(ctx, t2 + 0.2, t3 - 0.2)()).move_to(sc)))
    sun._dynamic = True
    ctx.add(sun, z=3)
    show(ctx, ctx.text(T["sun"], 32, "#FFC93C", 6.0).move_to(sc + np.array([0.0, 2.6, 0.0])), t2 + 0.4, t_out=t3 - 0.2)
    # once it is squeezed small enough it is a black hole: a pulsing ring marks the tiny dark ball
    halo = always_redraw(lambda: Circle(radius=0.35 + 0.08 * math.sin(tl.t * 4), stroke_color="#FFC857", stroke_width=6,
                                        stroke_opacity=level(ctx, t_sq + 3.0, 0.5) * window(ctx, t2 + 0.2, t3 - 0.2)(), fill_opacity=0).move_to(sc))
    halo._dynamic = True
    ctx.add(halo, z=5)
    show(ctx, ctx.text("a black hole", 36, "#F5F7FA", 4.0).move_to(sc + np.array([0.0, -1.0, 0.0])), t_sq + 3.2, t_out=t3 - 0.2, z=6)
    mb = Circle(radius=0.07, stroke_color="#7FD6FF", stroke_width=2, fill_color="#1F6FB5", fill_opacity=1).move_to(sc + np.array([4.0, -1.0, 0.0]))
    show(ctx, mb, ctx.tt(3, 2), t_out=t3 - 0.2, pop=0.4)
    show(ctx, ctx.text(T["earth"], 28, "#7FD6FF", 4.0).move_to(sc + np.array([4.0, -1.7, 0.0])), ctx.tt(3, 2) + 0.2, t_out=t3 - 0.2)
    # ---- D: the event horizon - rays outside escape, rays inside fall back
    HC = C + np.array([1.9, 0.2, 0.0])
    ctx.add(blackhole.black_hole(HC, 1.3, tl, alpha=window(ctx, t3, None), disk=False), z=3)
    hz = always_redraw(lambda: Circle(radius=1.3 + 0.06 * math.sin(tl.t * 3), stroke_color="#FF4D6D", stroke_width=6, stroke_opacity=window(ctx, t3 + 0.4, None)()).move_to(HC))
    hz._dynamic = True
    ctx.add(hz, z=5)
    for k, a in enumerate((0.5, 2.1, 3.7, 5.3)):
        d = np.array([math.cos(a), math.sin(a), 0.0])
        show(ctx, Arrow(HC + d * 1.9, HC + d * 3.0, buff=0, color="#F5F7FA", stroke_width=5), t3 + 0.9 + 0.15 * k, z=4)
        show(ctx, Arrow(HC + d * 1.0, HC + d * 0.35, buff=0, color="#FF4D6D", stroke_width=5, max_tip_length_to_length_ratio=0.5), t3 + 1.6 + 0.15 * k, z=6)
    show(ctx, ctx.text(T["hz"], 40, "#FF8FA3", 5.0).move_to(HC + np.array([0.0, 2.45, 0.0])), t3 + 0.6, z=7)
    show(ctx, ctx.text(T["esc"], 24, "#F5F7FA", 3.0, "NORMAL").move_to(HC + np.array([3.1, 0.9, 0.0])), t3 + 1.2, z=7)
    show(ctx, ctx.text(T["no"] + " - " + T["no2"], 28, "#FF4D6D", 7.0).move_to(HC + np.array([0.0, -2.25, 0.0])), ctx.tt(4, 2), z=7)
    ctx.avatar.look_at(lambda: BC)
    ctx.play(gestures.point_at(ctx.avatar, lambda: BC, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t2)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.6)
    ctx.until(t3)
    ctx.play(gestures.point_at(ctx.avatar, lambda: HC, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
