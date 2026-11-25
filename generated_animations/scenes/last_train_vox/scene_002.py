"""Vox look - shot 2 (scenes 3-4): the invented stop 'Moonlight Road' on a route map; the doors open on the narrator's own station, cracked bench and all."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=7)
        # a route line with stops; the announced stop appears as a gap that is not on the map
        b.put(Line(b.C + v(-3.0, 0.2), b.C + v(3.0, 0.2), color=INK, stroke_width=7), b.t0 + 0.2, z=4, pop=0)
        for k in range(5):
            b.put(Circle(radius=0.2, stroke_color=INK, stroke_width=4, fill_color=CREAM, fill_opacity=1).move_to(b.C + v(-3.0 + 1.5 * k, 0.2)), b.t0 + 0.3 + 0.2 * k, z=5, pop=0.4)
        b.put(ctx.text("?", 90, RED, 1.2).move_to(b.C + v(0.7, 1.4)), b.t0 + 1.6, z=7, pop=0.3)
        sign = vox.torn_card(5.0, 1.2, seed=31, rot=-2)
        sign.move_to(b.C + v(0, -1.6))
        b.mover(sign, lambda: b.C + v(0, -1.6 + 0.08 * math.sin(ctx.elapsed() * 3.0)), t_in=b.t0 + 1.0, z=6)
        b.text(vox.L(ctx, "MOONLIGHT ROAD", "मूनलाइट रोड"), 36, v(0, -1.6), INK, 4.6, t=b.t0 + 1.2)
        b.tape(vox.L(ctx, "NOT ON ANY MAP", "किसी नक़्शे में नहीं"), v(0, 2.4), RED, 4.6, 28, 2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.card(seed=9, rot=0.5)
        b.put(Rectangle(width=7.4, height=0.3, stroke_color=INK, stroke_width=3, fill_color="#8895A8", fill_opacity=1).move_to(b.C + v(0, -1.7)), b.t0 + 0.1, z=3, pop=0)   # platform edge
        # the doors slide open
        L_ = Rectangle(width=1.1, height=2.2, stroke_color=INK, stroke_width=4, fill_color="#3D4A66", fill_opacity=1)
        R_ = L_.copy()
        L_.move_to(b.C + v(-0.55, -0.4))
        R_.move_to(b.C + v(0.55, -0.4))
        b.mover(L_, lambda: b.C + v(-0.55 - 0.9 * ease(level(ctx, b.t0 + 0.6, 1.2)), -0.4), z=6)
        b.mover(R_, lambda: b.C + v(0.55 + 0.9 * ease(level(ctx, b.t0 + 0.6, 1.2)), -0.4), z=6)
        b.put(Rectangle(width=2.0, height=2.2, stroke_width=0, fill_color=YEL, fill_opacity=0.35).move_to(b.C + v(0, -0.4)), b.t0 + 0.5, z=5, pop=0)
        # bench with a crack, lamp
        bench = Rectangle(width=2.0, height=0.3, stroke_color=INK, stroke_width=4, fill_color="#B07A4A", fill_opacity=1).move_to(b.C + v(-2.3, -1.3))
        b.put(bench, b.t0 + 1.2, z=6, pop=0.3)
        b.put(Line(b.C + v(-2.4, -1.15), b.C + v(-2.25, -1.45), color=INK, stroke_width=4), b.t0 + 1.6, z=7, pop=0)
        b.put(Line(b.C + v(2.4, -1.5), b.C + v(2.4, 1.0), color=INK, stroke_width=5), b.t0 + 1.2, z=5, pop=0)
        b.put(Circle(radius=0.3, stroke_color=INK, stroke_width=4, fill_color=YEL, fill_opacity=1).move_to(b.C + v(2.4, 1.15)), b.t0 + 1.3, z=6, pop=0.3)
        b.tape(vox.L(ctx, "MY OWN STATION", "मेरा अपना स्टेशन"), v(0, 2.4), BLUE, 4.4, 28, -2.0, t=b.t0 + 1.8)
        b.tape(vox.L(ctx, "CRACKED BENCH", "टूटी बेंच"), v(-1.8, -2.4), ORANGE, 3.4, 26, 2.0, t=b.t0 + 2.6)
    beat0(B[0])
    beat1(B[1])
