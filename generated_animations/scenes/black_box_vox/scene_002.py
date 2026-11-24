"""Vox look - shot 2 (scenes 6-10): 1953 clipping, jets crash with no clues, the protective case, how recorders changed, tape vs chip."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    n = 5
    B = [Beat(ctx, i, n) for i in range(n)]
    # ---- 6: David Warren, 1953 (a clipping)
    def beat_0(b):
        b.card(10.4, 4.8, seed=13, rot=0.4)
        paper = vox.newspaper(ctx, "The Curious Loop Times", "Melbourne scientist builds flight recorder", "MELBOURNE - 1953", w=4.9, h=4.0, seed=17, rot=-3.0)
        paper.move_to(b.C + v(-2.2, 0.0))
        vox.arrive(ctx, paper, b.t0 + 0.2, t_out=b.t1, side="left", z=8)
        b.text("1953", 90, v(2.9, 0.9), RED, 3.4, t=b.t0 + 1.0)
        b.tape("DAVID WARREN", v(2.9, -0.4), BLUE, 3.8, 28, 2.0, t=b.at(0) + 0.8)
        b.tape("MELBOURNE LAB", v(2.9, -1.4), GREEN, 3.8, 26, -2.0, t=b.at(0) + 1.4)
        # ---- 7: jets crash, record the instruments
    beat_0(B[0])
    def beat_1(b):
        b.card(10.4, 4.7, seed=15, rot=-0.4)
        for k in range(3):
            t_s = b.t0 + 0.2 + 0.5 * k
            b.mover(plane(0.8).move_to(b.C + v(-5.2, 1.7 - 0.8 * k)), lambda k=k, t_s=t_s: b.C + v(-5.2 + 4.4 * ease(level(ctx, t_s, 4.0)), 1.7 - 0.8 * k))
        b.text("?", 110, v(-0.9, 0.0), RED, 1.4, t=b.t0 + 2.6)
        b.text("NO CLUES", 32, v(-1.9, -1.9), RED, 3.0, t=b.t0 + 2.2)

        def dial(a):
            d = Circle(radius=1.15, stroke_color=INK, stroke_width=6, stroke_opacity=a, fill_color=CREAM, fill_opacity=a).move_to(b.C + v(2.9, 0.4))
            ang = 0.9 * math.sin(ctx.elapsed() * 1.8) * level(ctx, b.t0 + 1.0, 0.5)
            nd = Line(b.C + v(2.9, 0.4), b.C + v(2.9 + 0.95 * math.sin(ang), 0.4 + 0.95 * math.cos(ang)), color=RED, stroke_width=7, stroke_opacity=a)
            return VGroup(d, nd)
        b.live(dial, b.t0 + 0.5, z=5)
        b.tape("RECORD THE INSTRUMENTS", v(2.9, -1.4), BLUE, 4.6, 26, -1.5, t=b.at(1))
        b.tape("THE PLANE TELLS ITS STORY", v(0.4, -2.0), GREEN, 5.0, 26, 1.0, t=b.at(1) + 1.2)
        # ---- 8: a protective box
    beat_1(B[1])
    def beat_2(b):
        b.card(9.8, 4.6, seed=17, rot=0.4)
        b.put(recorder(1.4).move_to(b.C + v(-2.0, 0.2)), b.t0 + 0.2, z=5, pop=0.3)
        for k in range(3):
            sh = RoundedRectangle(corner_radius=0.15, width=2.4 + 0.6 * k, height=1.7 + 0.5 * k, stroke_color=INK, stroke_width=5, fill_opacity=0, stroke_opacity=1).move_to(b.C + v(-2.0, 0.2))
            b.put(sh.set_stroke(["#6B7A8F", "#8895A8", "#A4AFC0"][k], width=7), b.at(0) + 0.3 + 0.35 * k, z=4, pop=0.3)
        b.text("PROTECTIVE CASE", 32, v(2.6, 1.3), INK, 4.0, t=b.at(0) + 0.3)
        b.tape("BUILT IN MELBOURNE", v(2.6, 0.1), BLUE, 4.2, 28, 2.0, t=b.at(0) + 0.9)
        b.tape("YEARS TO CONVINCE", v(2.6, -1.1), ORANGE, 4.2, 28, -2.0, t=b.at(1) - 1.0 if False else b.t0 + 3.0)
        # ---- 9: foil -> tape -> chip
    beat_2(B[2])
    def beat_3(b):
        b.card(10.4, 4.6, seed=19, rot=-0.4)
        for k, (nm, col) in enumerate((("METAL FOIL", "#9AA8B8"), ("TAPE", BLUE), ("MEMORY CHIP", GREEN))):
            x = -3.4 + 3.4 * k
            c = vox.torn_card(2.8, 2.6, seed=30 + k, rot=2 - 2 * k).move_to(b.C + v(x, 0.2))
            b.put(c, b.t0 + 0.3 + 0.9 * k, z=3, pop=0.2)
            b.text(nm, 26, v(x, 1.0), INK, 2.5, t=b.t0 + 0.5 + 0.9 * k)
            ic = [Rectangle(width=1.4, height=0.7, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1),
                  Circle(radius=0.5, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1),
                  RoundedRectangle(corner_radius=0.08, width=0.9, height=0.9, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1)][k]
            b.put(ic.move_to(b.C + v(x, -0.2)), b.t0 + 0.6 + 0.9 * k, z=6, pop=0.3)
            if k < 2:
                b.put(vox.doodle_arrow(b.C + v(x + 1.5, -0.9), b.C + v(x + 1.95, -0.9), RED, 0.5, 6), b.t0 + 1.2 + 0.9 * k, z=7)
        b.tape("NO MOVING PARTS", v(0.0, -1.9), RED, 4.4, 28, 1.5, t=b.at(1) + 0.4)
        # ---- 10: tape vs chip
    beat_3(B[3])
    def beat_4(b):
        b.card(10.0, 4.6, seed=21, rot=0.5)
        for side, nm in ((-1, "TAPE"), (1, "CHIP")):
            b.text(nm, 38, v(side * 2.6, 1.7), INK, 2.5, t=b.t0 + 0.3)

        def reel(a):
            g = VGroup()
            for s_ in (-1.0, 0.0):
                cx = b.C + v(-3.1 + 1.0 * (s_ + 1.0), 0.2)
                g.add(Circle(radius=0.55, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(cx))
                for k in range(3):
                    an = ctx.elapsed() * 6 + k * 2.09
                    g.add(Line(cx, cx + v(0.5 * math.cos(an), 0.5 * math.sin(an)), color="#FFFFFF", stroke_width=5, stroke_opacity=a))
            return g
        b.live(reel, b.t0 + 0.3, z=5)
        chip = RoundedRectangle(corner_radius=0.1, width=1.3, height=1.3, stroke_color=INK, stroke_width=5, fill_color=GREEN, fill_opacity=1).move_to(b.C + v(2.6, 0.2))
        b.put(chip, b.t0 + 0.5, z=5, pop=0.3)
        for k in range(4):
            for sd in (-1, 1):
                b.put(Line(b.C + v(2.6 + sd * 0.65, 0.5 - 0.27 * k), b.C + v(2.6 + sd * 0.9, 0.5 - 0.27 * k), color=INK, stroke_width=5), b.t0 + 0.7, z=5, pop=0)
        b.tape("SPINS - CAN BREAK", v(-2.6, -1.4), RED, 3.8, 26, 2.0, t=b.at(0) + 0.8)
        b.tape("STILL - SURVIVES", v(2.6, -1.4), GREEN, 3.8, 26, -2.0, t=b.at(0) + 1.4)

    beat_4(B[4])