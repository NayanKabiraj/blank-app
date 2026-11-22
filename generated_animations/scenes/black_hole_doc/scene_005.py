"""Shot 5 (chapter 5, scenes 21-25): the singularity, inside the horizon, how a black hole is born, the swallow-everything myth, what telescopes see."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, Dot, Line, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, lighting, orbital
from generated_animations.timed import level, show, window

T = {"q": "?", "sing": "singularity: infinite density?", "in": "inside: every path leads inward", "breaks": "theory breaks down here", "star": "massive star", "core": "core collapses", "bh": "black hole",
     "far": "far away: pulls like a star", "safe": "planets can orbit safely", "shadow": "dark shadow", "ring": "bright ring: hot gas + bent light"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t22, t23, t24, t25 = (ctx.t_of(i) for i in (1, 2, 3, 4))
    BC = C + np.array([1.9, 0.2, 0.0])
    # ---- scenes 21-22: the center - and every path inside leads inward
    ctx.add(blackhole.black_hole(BC, 1.9, tl, alpha=window(ctx, 0.1, t23 - 0.2), disk=False), z=2)
    show(ctx, ctx.text(T["q"], 160, "#FFD166", 3.0).move_to(BC), 0.8, t_out=t22, z=6)
    for k in range(10):
        a = 2 * math.pi * k / 10
        d = np.array([math.cos(a), math.sin(a), 0.0])
        show(ctx, Arrow(BC + d * 1.75, BC + d * 0.35, buff=0, color="#FF4D6D", stroke_width=5, max_tip_length_to_length_ratio=0.35), t22 + 0.3 + 0.12 * k, t_out=t23 - 0.2, pop=0, z=6)
    show(ctx, Dot(BC, radius=0.12, color="#FFFFFF"), t22 + 1.6, t_out=t23 - 0.2, z=7)
    show(ctx, ctx.text(T["in"], 34, "#FF8FA3", 8.0).move_to(C + np.array([1.9, 2.6, 0.0])), t22 + 0.4, t_out=t23 - 0.2, z=7)
    show(ctx, ctx.text(T["sing"], 30, "#F5F7FA", 7.0).move_to(C + np.array([1.9, -2.5, 0.0])), ctx.tt(1, 1), t_out=t23 - 0.2, z=7)
    show(ctx, ctx.text(T["breaks"], 30, "#FFD166", 7.0).move_to(C + np.array([-2.2, 0.2, 0.0])), ctx.tt(1, 2), t_out=t23 - 0.2, z=7)
    # ---- scene 22: how a black hole is born - a massive star runs out of fuel and its core collapses
    SC = C + np.array([1.9, 0.2, 0.0])
    t_c = t23 + 2.4
    rad = lambda: max(0.06, 1.7 * (1 - level(ctx, t_c, 2.0)) ** 2.5 + 0.06 * math.sin(tl.t * 5) * (1 - level(ctx, t_c, 1.0)))
    star = always_redraw(lambda: VGroup(Circle(radius=rad() * 1.35, stroke_width=0, fill_color="#FF7B00", fill_opacity=0.3 * window(ctx, t23 + 0.2, t24 - 0.2)()).move_to(SC),
                                         Circle(radius=rad(), stroke_color="#FFE08A", stroke_width=3, fill_color="#000000" if level(ctx, t_c + 1.8, 0.3) > 0.5 else "#FF9F1C",
                                                fill_opacity=window(ctx, t23 + 0.2, t24 - 0.2)(), stroke_opacity=window(ctx, t23 + 0.2, t24 - 0.2)()).move_to(SC),
                                         Circle(radius=0.2 + 3.2 * level(ctx, t_c + 1.9, 1.2), stroke_color="#FFFFFF", stroke_width=6, stroke_opacity=(1 - level(ctx, t_c + 1.9, 1.2)) * (1.0 if tl.t - ctx.start > t_c + 1.9 else 0.0) * window(ctx, t23, t24 - 0.2)(), fill_opacity=0).move_to(SC)))
    star._dynamic = True
    ctx.add(star, z=3)
    show(ctx, ctx.text(T["star"], 32, "#FFC857", 5.0).move_to(C + np.array([-2.7, 2.2, 0.0])), t23 + 0.4, t_out=t_c)
    show(ctx, ctx.text(T["core"], 32, "#FF8FA3", 5.0).move_to(C + np.array([-2.7, 2.2, 0.0])), t_c, t_out=t24 - 0.2)
    show(ctx, ctx.text(T["bh"], 36, "#F5F7FA", 5.0).move_to(C + np.array([1.9, -2.3, 0.0])), t_c + 2.0, t_out=t24 - 0.2)
    # ---- scene 23: far away it pulls like a star of the same mass - planets orbit safely
    ctx.add(blackhole.black_hole(BC, 0.5, tl, alpha=window(ctx, t24, t25 - 0.2), disk=True), z=3)
    for k, (r, w, col) in enumerate(((1.4, 1.2, "#2EC5FF"), (2.2, 0.8, "#4CD97B"), (3.0, 0.55, "#F4C95D"))):
        pl = always_redraw(lambda r=r, w=w, col=col, k=k: Dot(BC + r * np.array([math.cos(w * tl.t + k * 2.0), math.sin(w * tl.t + k * 2.0) * 0.85, 0.0]), radius=0.14,
                                                              color=col, fill_opacity=window(ctx, t24 + 0.3 + 0.3 * k, t25 - 0.2)()))
        pl._dynamic = True
        ctx.add(pl, z=4)
        show(ctx, Circle(radius=r, stroke_color="#3C4F7A", stroke_width=2).stretch(0.85, 1).move_to(BC), t24 + 0.3, t_out=t25 - 0.2, pop=0)
    show(ctx, ctx.text(T["far"], 34, "#FFD166", 8.0).move_to(C + np.array([1.9, 2.6, 0.0])), t24 + 0.6, t_out=t25 - 0.2)
    show(ctx, ctx.text(T["safe"], 30, "#4CD97B", 7.0).move_to(C + np.array([1.9, -2.5, 0.0])), ctx.tt(3, 1), t_out=t25 - 0.2)
    # ---- scene 24: what telescopes see - a dark shadow inside a bright ring
    ctx.add(blackhole.starfield(C, W, H, 50, BC, 1.1, warp=lambda: 0.7, alpha=window(ctx, t25, None)), z=1)
    ctx.add(blackhole.black_hole(BC, 1.1, tl, alpha=window(ctx, t25, None), disk=True), z=3)
    show(ctx, Arrow(C + np.array([-2.7, 1.6, 0.0]), BC + np.array([-0.4, 0.2, 0.0]), buff=0, color="#F5F7FA", stroke_width=5), t25 + 0.6, z=6)
    show(ctx, ctx.text(T["shadow"], 32, "#F5F7FA", 4.0).move_to(C + np.array([-2.8, 2.1, 0.0])), t25 + 0.6, z=6)
    show(ctx, Arrow(C + np.array([6.0, -1.9, 0.0]), BC + np.array([1.2, -0.4, 0.0]), buff=0, color="#FFC857", stroke_width=5), t25 + 1.6, z=6)
    show(ctx, ctx.text(T["ring"], 28, "#FFC857", 6.5).move_to(C + np.array([5.2, -2.4, 0.0])), t25 + 1.6, z=6)
    ctx.avatar.look_at(lambda: BC)
    ctx.play(gestures.point_at(ctx.avatar, lambda: BC, 0.5), expressions.set_expression(ctx.avatar, "thinking", 0.4), run_time=0.6)
    ctx.until(t23)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t_c)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
    ctx.until(t25)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), gestures.point_at(ctx.avatar, lambda: BC, 0.5), run_time=0.6)
