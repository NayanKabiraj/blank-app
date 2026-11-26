"""Vox look - shot 2 (scenes 3-4): light and gravity both need eight minutes to reach Earth; then the lights go out and Earth cools."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import sun


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=7)
        S, E = b.C + v(-2.3, 0.6), b.C + v(2.3, 0.6)
        b.live(lambda a: sun(S, 0.6, 1.0, a, ctx.elapsed()), b.t0 + 0.1, z=4)
        b.put(Circle(radius=0.3, stroke_color=INK, stroke_width=4, fill_color=BLUE, fill_opacity=1).move_to(E), b.t0 + 0.2, z=5, pop=0.3)
        b.put(Line(S + v(0.7, 0), E + v(-0.4, 0), color="#B7AE9C", stroke_width=3), b.t0 + 0.3, z=3, pop=0)
        f = lambda: ease(level(ctx, b.t0 + 1.0, 5.0))
        b.live(lambda a: VGroup(Circle(radius=0.16, stroke_width=0, fill_color=YEL, fill_opacity=a).move_to(S + v(0.9 + (E[0] - S[0] - 1.4) * f(), 0.18)),
                                Circle(radius=0.16, stroke_width=0, fill_color=RED, fill_opacity=a).move_to(S + v(0.9 + (E[0] - S[0] - 1.4) * f(), -0.18))), b.t0 + 0.8, z=6)
        b.live(lambda a: ctx.text(f"{int(8 * f())}:{int(20 * f()):02d}", 50, RED, 2.6).move_to(b.C + v(0, -0.7)).set_opacity(a), b.t0 + 1.0, z=7)
        b.tape(vox.L(ctx, "LIGHT: 8 MINUTES", "रोशनी: 8 मिनट"), v(-1.0, 2.2), YEL, 4.0, 28, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "GRAVITY: THE SAME", "गुरुत्व: उतना ही"), v(1.4, -1.9), RED, 4.4, 28, 2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.card(seed=9, rot=0.5)
        # the card's picture darkens: a navy sheet fades in; Earth cools (a snowflake dot ring appears)
        b.live(lambda a: Rectangle(width=7.0, height=5.4, stroke_width=0, fill_color="#1B2238", fill_opacity=a * 0.92 * ease(level(ctx, b.t0 + 0.4, 1.6))).move_to(b.C + v(0, 0.1)), b.t0 + 0.2, z=3)
        b.live(lambda a: sun(b.C + v(-2.0, 1.4), 0.55, 1.0, a, ctx.elapsed()), b.t0 + 0.3, z=5)
        b.live(lambda a: Circle(radius=0.8, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color=BLUE if level(ctx, b.t0 + 2.0, 1.5) < 0.5 else "#9FD8FF", fill_opacity=a).move_to(b.C + v(1.4, 0.2)), b.t0 + 0.4, z=5)
        b.live(lambda a: VGroup(*[Circle(radius=0.06, stroke_width=0, fill_color="#FFFFFF", fill_opacity=a * level(ctx, b.t0 + 2.0 + 0.1 * k, 0.3)).move_to(b.C + v(1.4 + 1.15 * math.cos(k * 0.9), 0.2 + 1.15 * math.sin(k * 0.9))) for k in range(7)]), b.t0 + 2.0, z=6)
        b.tape(vox.L(ctx, "LIGHTS OUT", "रोशनी बुझी"), v(-1.0, -1.2), RED, 3.2, 30, -3.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "EARTH COOLS", "धरती ठंडी"), v(1.4, -2.3), BLUE, 3.4, 30, 3.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
