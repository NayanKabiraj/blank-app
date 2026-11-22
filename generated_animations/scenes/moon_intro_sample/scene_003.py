"""Shot 3 (scene 4): a moonlit night turns truly dark - the Moon fades, the landscape dims, the stars stay."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Polygon, Rectangle, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import lighting, orbital
from generated_animations.timed import level, show, window

T = {"fx": "25 - 150 x brighter", "cap": "full Moon vs a moonless sky"}


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t_off = ctx.tt(0, 2) - 0.1
    rng = np.random.default_rng(9)
    stars = [C + np.array([rng.uniform(-3.8, 3.8), rng.uniform(0.2, 4.9), 0.0]) for _ in range(70)]
    from manim import VGroup, Dot
    sky = VGroup(*[Dot(p, radius=float(rng.uniform(0.02, 0.05)), color="#F5F7FA") for p in stars])

    def twinkle(m):
        for k, d in enumerate(m):
            d.set_fill(opacity=0.5 + 0.4 * math.sin(tl.t * 2 + k) if True else 1, family=False)
    twinkle(sky)
    sky.add_updater(twinkle)
    show(ctx, sky, 0.1, pop=0, z=1, fade_out=True)
    mp = C + np.array([1.6, 3.2, 0.0])
    show(ctx, lighting.glow(mp, "#FFFFFF", 1.3, 6, 0.45), 0.3, t_out=t_off, z=2, pop=0)
    show(ctx, orbital.moon(mp, 0.75), 0.3, t_out=t_off, z=3)
    # ground and hills lit by the Moon, then fading to black as it goes
    hills = Polygon(C + np.array([-4.0, -2.0, 0.0]), C + np.array([-4.0, -0.6, 0.0]), C + np.array([-2.4, 0.4, 0.0]), C + np.array([-0.8, -0.5, 0.0]),
                    C + np.array([1.0, 0.6, 0.0]), C + np.array([2.8, -0.3, 0.0]), C + np.array([4.0, 0.3, 0.0]), C + np.array([4.0, -2.0, 0.0]), stroke_width=0, fill_color="#223A5E", fill_opacity=1)
    lit = always_redraw(lambda: hills.copy().set_fill("#4A6FA5" if True else "#000", opacity=0.9 * (1 - level(ctx, t_off, 1.4)) * window(ctx, 0.1, None)()))
    lit._dynamic = True
    show(ctx, hills, 0.1, pop=0, z=2)
    ctx.add(lit, z=2)
    tint = always_redraw(lambda: Rectangle(width=W + 1, height=H + 1, stroke_width=0, fill_color="#000010",
                                           fill_opacity=0.62 * level(ctx, t_off, 1.4) * window(ctx, 0.1, None)()).move_to(C))
    tint._dynamic = True
    ctx.add(tint, z=4)
    show(ctx, ctx.text(T["fx"], 54, "#FFD166", 7.0).move_to(C + np.array([0.0, -2.35, 0.0])), ctx.tt(0, 1), z=8)
    show(ctx, ctx.text(T["cap"], 26, "#9AA8C7", 7.0, "NORMAL").move_to(C + np.array([0.0, -3.0, 0.0])), ctx.tt(0, 1) + 0.3, z=8)
    ctx.avatar.look_at(lambda: mp)
    ctx.play(gestures.point_at(ctx.avatar, lambda: mp, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t_off)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), gestures.present(ctx.avatar, 0.5), run_time=0.6)
