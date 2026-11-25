"""Vox look - shot 4 (scenes 7-8): Sagittarius A* and a timer counting to roughly a minute; the closing question about your last minute."""
from __future__ import annotations

from ._kit import *
from .scene_001 import hole


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        b.live(lambda a: hole(b.C + v(0, 1.3), 1.0, ctx.elapsed(), a), b.t0 + 0.1, z=4)
        b.text("SAGITTARIUS A*", 28, v(0, 2.7), INK, 4.2, t=b.t0 + 0.4)
        # a ring timer fills to ~60 s
        def timer(a):
            f = ease(level(ctx, b.t0 + 0.8, 3.5))
            c = b.C + v(0, -1.1)
            ring = Circle(radius=0.9, stroke_color="#B7AE9C", stroke_width=8, stroke_opacity=a, fill_opacity=0).move_to(c)
            arc = Line(c + v(0, 0.9), c + v(0.9 * math.sin(2 * math.pi * f), 0.9 * math.cos(2 * math.pi * f)), color=RED, stroke_width=8, stroke_opacity=a)
            return VGroup(ring, arc)
        b.live(timer, b.t0 + 0.6, z=5)
        b.live(lambda a: ctx.text(f"{int(60 * ease(level(ctx, b.t0 + 0.8, 3.5)))} s", 52, RED, 2.0).move_to(b.C + v(0, -1.1)).set_opacity(a), b.t0 + 0.8, z=6)
        b.tape(vox.L(ctx, "ROUGHLY A MINUTE", "करीब एक मिनट"), v(0, -2.5), RED, 4.4, 30, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.live(lambda a: hole(b.C + v(0, 0.2), 1.1, ctx.elapsed(), a), b.t0 + 0.1, z=4)
        b.text(vox.L(ctx, "YOUR LAST MINUTE?", "आपका आख़िरी मिनट?"), 40, v(0, 2.4), INK, 6.0, t=b.t0 + 0.3)
        b.live(lambda a: Circle(radius=1.6 + 0.6 * ((ctx.elapsed() * 0.6) % 1.0), stroke_color=ORANGE, stroke_width=4, stroke_opacity=0.5 * a * (1 - ((ctx.elapsed() * 0.6) % 1.0)), fill_opacity=0).move_to(b.C + v(0, 0.2)), b.t0 + 0.6, z=3)
        b.tape(vox.L(ctx, "NO WAY TO TELL ANYONE", "किसी को बता नहीं सकते"), v(0, -2.3), BLUE, 5.2, 26, 2.0, t=b.t0 + 1.0)
    beat0(B[0])
    beat1(B[1])
