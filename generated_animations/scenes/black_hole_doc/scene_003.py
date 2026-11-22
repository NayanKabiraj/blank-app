"""Shot 3 (chapter 3, scenes 11-15): spaghettification - feet pulled harder than the head, small vs giant, NASA's 12.8 s, why giant holes are gentler."""
from __future__ import annotations

import math

import numpy as np
from manim import Arrow, Circle, Line, ManimColor, RoundedRectangle, VGroup, always_redraw, interpolate_color

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, icons
from generated_animations.timed import level, show, window

T = {"feet": "feet pulled harder", "head": "head pulled less", "str": "stretched head to toe", "sq": "squeezed sideways", "small": "A small one", "giant": "A giant one", "q": "Which stretches you first?",
     "hrs": "about 3 hours to the horizon", "tear": "after crossing", "sim": "NASA simulation of a camera", "b": "bigger hole", "h": "bigger horizon", "g": "gentler stretch"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t11, t12, t13, t14 = ctx.t_of(1), ctx.t_of(2), ctx.t_of(3), ctx.t_of(4)
    # ---- scenes 11-12: a body in a steep gravity gradient
    BC = C + np.array([-2.6, 0.2, 0.0])
    ctx.add(blackhole.black_hole(BC, 0.9, tl, alpha=window(ctx, 0.1, t12 - 0.2), disk=False), z=3)
    ap = lambda: np.array([C[0] + 0.3 - 1.2 * level(ctx, t11, 5.0), C[1] + 0.2, 0.0])
    st = lambda: 1.0 + 1.5 * level(ctx, t11 + 0.5, 5.0)
    fig = always_redraw(lambda: blackhole.astronaut(ap(), 1.1, st(), -math.pi / 2).set_opacity(window(ctx, 0.3, t12 - 0.2)()))
    fig._dynamic = True
    ctx.add(fig, z=5)
    # arrows at the feet (long) and the head (short), both toward the hole
    foot = lambda: ap() + np.array([-0.35 * st() - 0.1, 0.0, 0.0])
    head = lambda: ap() + np.array([0.35 * st() + 0.1, 0.0, 0.0])
    fa = always_redraw(lambda: Arrow(foot(), foot() + np.array([-1.5, 0.0, 0.0]), buff=0, color="#FF4D6D", stroke_width=9, stroke_opacity=window(ctx, t11 + 0.4, t12 - 0.2)()).set_fill(opacity=window(ctx, t11 + 0.4, t12 - 0.2)()))
    ha = always_redraw(lambda: Arrow(head(), head() + np.array([-0.6, 0.0, 0.0]), buff=0, color="#FFC857", stroke_width=9, stroke_opacity=window(ctx, t11 + 0.4, t12 - 0.2)()).set_fill(opacity=window(ctx, t11 + 0.4, t12 - 0.2)()))
    for a in (fa, ha):
        a._dynamic = True
        ctx.add(a, z=6)
    show(ctx, ctx.text(T["feet"], 28, "#FF4D6D", 4.0).move_to(C + np.array([-0.9, -1.5, 0.0])), ctx.tt(1, 0) + 0.4, t_out=t12 - 0.2)
    show(ctx, ctx.text(T["head"], 28, "#FFC857", 4.0).move_to(C + np.array([2.3, -1.2, 0.0])), ctx.tt(1, 0) + 1.2, t_out=t12 - 0.2)
    show(ctx, ctx.text(T["str"], 34, "#F5F7FA", 7.0).move_to(C + np.array([1.4, 2.2, 0.0])), ctx.tt(1, 1) + 0.2, t_out=t12 - 0.2)
    show(ctx, ctx.text(T["sq"], 30, "#7FD6FF", 6.0).move_to(C + np.array([1.4, 1.5, 0.0])), ctx.tt(1, 2) + 0.2, t_out=t12 - 0.2)
    # ---- scene 12: quiz - small vs giant
    show(ctx, ctx.text(T["q"], 40, "#FFD166", 9.0).move_to(C + np.array([0.0, 2.55, 0.0])), t12 + 0.2, t_out=t13 - 0.2)
    t_rev = ctx.config["subs"][2]["end"] - 1.0
    for k, (name, R, x, stv) in enumerate(((T["small"], 0.4, C[0] - 2.2, 2.6), (T["giant"], 1.5, C[0] + 2.9, 1.0))):
        ctr = np.array([x, C[1] - 0.2, 0.0])
        ctx.add(blackhole.black_hole(ctr, R, tl, alpha=window(ctx, t12 + 0.3, t13 - 0.2), disk=False), z=3)
        show(ctx, blackhole.astronaut(ctr + np.array([R + 1.2, 0.0, 0.0]), 0.9, stv, -math.pi / 2), t12 + 0.6, t_out=t13 - 0.2, z=5)
        pill = RoundedRectangle(corner_radius=0.25, width=3.0, height=0.8, stroke_color="#3C4F7A", stroke_width=3, fill_color="#16213E", fill_opacity=1).move_to(ctr + np.array([0.3, -2.0, 0.0]))
        lab = ctx.text(name, 28, "#F5F7FA", 2.8).move_to(pill)
        grp = VGroup(pill, lab)
        if k == 0:
            def lit(_m, pill=pill):
                pill.set_fill(interpolate_color(ManimColor("#16213E"), ManimColor("#2E9E5B"), level(ctx, t_rev, 0.4)), opacity=pill.get_fill_opacity(), family=False)
            grp.add_updater(lit)
        show(ctx, grp, t12 + 0.8 + 0.2 * k, t_out=t13 - 0.2, z=6)
    # ---- scene 13: NASA's camera - about three hours to the horizon, then 12.8 s
    HC = C + np.array([2.2, 0.2, 0.0])
    ctx.add(blackhole.black_hole(HC, 1.3, tl, alpha=window(ctx, t13, t14 - 0.2), disk=True), z=3)
    t_cross = t13 + 2.8
    cam = lambda: HC + np.array([-3.6 + 3.6 * level(ctx, t13 + 0.3, 2.5), 0.0, 0.0]) + np.array([1.7 * level(ctx, t_cross, 3.5), 0.0, 0.0])
    cs = lambda: 1.0 + 3.0 * level(ctx, t_cross + 0.5, 3.0)
    camfig = always_redraw(lambda: blackhole.astronaut(cam(), 0.8, cs(), -math.pi / 2, "#FFD166").set_opacity(window(ctx, t13 + 0.2, t14 - 0.2)() * (1 - 0.8 * level(ctx, t_cross + 3.2, 0.4))))
    camfig._dynamic = True
    ctx.add(camfig, z=6)
    steps = 26
    frames = VGroup(*[ctx.text(f"{12.8 * k / steps:.1f} s", 64, "#FFD166", 4.0).move_to(C + np.array([-2.4, -1.5, 0.0])) for k in range(steps + 1)])

    def readout(m):
        p = level(ctx, t_cross, 3.4)
        idx = int(p * steps)
        fade = window(ctx, t_cross, t14 - 0.2)()
        for k, f in enumerate(m):
            for s_ in f.get_family():
                s_.set_fill(opacity=(1.0 if k == idx else 0.0) * fade, family=False)
    readout(frames)
    frames.add_updater(readout)
    ctx.scene.add(frames)
    frames.set_z_index(7)
    ctx.objects.append(frames)
    show(ctx, ctx.text(T["hrs"], 30, "#9AA8C7", 5.5, "NORMAL").move_to(C + np.array([-2.4, 2.4, 0.0])), t13 + 0.4, t_out=t14 - 0.2)
    show(ctx, ctx.text(T["tear"], 28, "#FF8FA3", 5.0, "NORMAL").move_to(C + np.array([-2.4, -2.2, 0.0])), t_cross, t_out=t14 - 0.2)
    show(ctx, ctx.text(T["sim"], 24, "#9AA8C7", 6.0, "NORMAL").move_to(C + np.array([3.3, -2.3, 0.0])), t13 + 0.4, t_out=t14 - 0.2)
    # ---- scene 14: a bigger hole has a bigger horizon, so the stretch is gentler
    for k, (R, x, name, col, al) in enumerate(((0.35, C[0] - 3.0, T["b"], "#FF4D6D", 1.3), (0.8, C[0] + 0.2, T["h"], "#FFC857", 0.8), (1.5, C[0] + 3.5, T["g"], "#4CD97B", 0.3))):
        ctr = np.array([x, C[1] + 0.3, 0.0])
        ctx.add(blackhole.black_hole(ctr, R, tl, alpha=window(ctx, t14 + 0.3 + 0.6 * k, None), disk=False), z=3)
        show(ctx, ctx.text(name, 30, col, 3.4).move_to(ctr + np.array([0.0, -2.05, 0.0])), t14 + 0.6 + 0.6 * k)
        for sgn in (-1, 1):
            show(ctx, Arrow(ctr + np.array([0.0, sgn * (R + 0.2), 0.0]), ctr + np.array([0.0, sgn * (R + 0.2 + al), 0.0]), buff=0, color=col, stroke_width=7, max_tip_length_to_length_ratio=0.5), t14 + 0.9 + 0.6 * k, z=5)
    ctx.avatar.look_at(lambda: BC)
    ctx.play(gestures.point_at(ctx.avatar, lambda: BC, 0.5), expressions.set_expression(ctx.avatar, "surprised", 0.4), run_time=0.6)
    ctx.until(t12)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.4), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t_rev)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.3), run_time=0.4)
    ctx.until(t13 + 3.2)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
