"""Vox look - shot 5 (scenes 22-26): lessons become rules, the learning loop, 'is it perfect?', seventy years on a timeline, the closing question."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    n = 5
    B = [Beat(ctx, i, n) for i in range(n)]
    # ---- 22: lessons -> rules (stamps)
    def beat_0(b):
        b.card(10.2, 4.7, seed=47, rot=0.4)
        b.put(vox.torn_card(3.6, 3.8, seed=48, rot=-2).move_to(b.C + v(-3.1, 0.1)), b.t0 + 0.2, z=3, pop=0.2)
        b.text("REPORT", 30, v(-3.1, 1.5), INK, 3.0, t=b.t0 + 0.3)
        for k in range(5):
            b.put(Line(b.C + v(-4.4, 0.8 - 0.4 * k), b.C + v(-1.9 - 0.3 * (k % 2), 0.8 - 0.4 * k), color="#B7AE9C", stroke_width=5), b.t0 + 0.5 + 0.1 * k, z=4, pop=0)
        b.put(vox.doodle_arrow(b.C + v(-1.0, 0.2), b.C + v(0.0, 0.2), RED, 0.5, 8), b.t0 + 1.0, z=6)
        for k, (s, col) in enumerate((("NEW RULE", RED), ("NEW TRAINING", BLUE), ("DESIGN FIX", GREEN))):
            b.tape(s, v(2.6, 1.2 - 1.15 * k), col, 3.8, 30, 2.0 - 2.0 * k, t=b.at(0) + 0.5 * k)
        # ---- 23: the learning loop
    beat_0(B[0])
    def beat_1(b):
        b.card(9.8, 4.7, seed=49, rot=-0.4)
        cen = b.C + v(0, 0.0)
        nodes = (("RECORD", RED, v(-2.9, 0.0)), ("INVESTIGATE", BLUE, v(0.0, 1.5)), ("CHANGE", GREEN, v(2.9, 0.0)))
        for k, (s, col, p) in enumerate(nodes):
            b.tape(s, p, col, 3.4, 28, 0.0, t=b.t0 + 0.4 + 0.6 * k)
        b.put(Circle(radius=2.3, stroke_color="#B7AE9C", stroke_width=5, fill_opacity=0).move_to(cen + v(0, -0.5)), b.t0 + 0.3, z=3, pop=0.1)

        def orbit(a):
            an = 2.1 + 3.2 * 0.5 * ctx.elapsed() * -1
            p = cen + v(0, -0.5) + v(2.3 * math.cos(an), 2.3 * math.sin(an))
            return Circle(radius=0.2, stroke_color=INK, stroke_width=4, stroke_opacity=a * level(ctx, b.t0 + 1.4, 0.3), fill_color=ORANGE, fill_opacity=a * level(ctx, b.t0 + 1.4, 0.3)).move_to(p)
        b.live(orbit, b.t0 + 1.2, z=9)
        b.tape("RECORD AGAIN", v(0, -2.0), ORANGE, 3.8, 26, 1.0, t=b.at(0) + 1.5)
        # ---- 24: myth - always found?
    beat_1(B[1])
    def beat_2(b):
        b.card(10.2, 4.6, seed=51, rot=0.4)
        for side, s, col in ((-1, "ALWAYS FOUND", RED), (1, "SOMETIMES NEVER FOUND", GREEN)):
            b.put(vox.torn_card(4.4, 2.6, seed=52 + side, rot=side * 2).move_to(b.C + v(side * 2.6, 0.4)), b.t0 + 0.3, z=3, pop=0.2)
            t = b.text(s, 30, v(side * 2.6, 0.4), INK, 3.8, t=b.t0 + 0.6)
        b.put(Line(b.C + v(-4.4, 0.4), b.C + v(-0.8, 0.4), color=RED, stroke_width=10), b.at(0) + 0.3, z=7, pop=0)
        vox.marker(ctx, ctx.text("SOMETIMES NEVER FOUND", 30, INK, 3.8).move_to(b.C + v(2.6, 0.4)), b.at(0) + 0.8, 0.9)
        b.mover(plane(0.9).move_to(b.C + v(-3.6, -1.6)), lambda: b.C + v(-3.6 + 7.0 * ease(level(ctx, b.t0 + 0.8, 4.0)), -1.6 + 0.1 * math.sin(ctx.elapsed() * 2)))
        b.tape("BETTER TRACKING", v(0.0, -2.0), BLUE, 3.8, 26, -1.5, t=b.at(0) + 1.4)
        # ---- 25: seventy years
    beat_2(B[2])
    def beat_3(b):
        b.card(10.4, 4.6, seed=53, rot=-0.4)
        b.live(lambda a: ctx.text(f"{int(70 * ease(level(ctx, b.t0 + 0.3, 2.0)))}", 130, RED, 3.4).move_to(b.C + v(-3.3, 0.5)).set_opacity(a), b.t0 + 0.3, z=6)
        b.text("YEARS", 40, v(-3.3, -0.9), INK, 2.6, t=b.t0 + 1.0)
        b.put(Line(b.C + v(-0.4, -0.4), b.C + v(4.6, -0.4), color=INK, stroke_width=8), b.t0 + 0.6, z=4, pop=0)
        for k, (yr, x) in enumerate((("1953", -0.4), ("TODAY", 4.6))):
            b.put(Circle(radius=0.17, stroke_color=INK, stroke_width=4, fill_color=ORANGE, fill_opacity=1).move_to(b.C + v(x, -0.4)), b.t0 + 0.8, z=5, pop=0.3)
            b.text(yr, 28, v(x, -1.0), INK, 1.8, t=b.t0 + 0.9)
        b.mover(recorder(0.7).move_to(b.C + v(-0.4, 0.2)), lambda: b.C + v(-0.4 + 5.0 * ease(level(ctx, b.t0 + 1.0, 3.5)), 0.2), t_in=b.t0 + 0.8, z=7)
        b.tape("ONE IDEA", v(2.4, 1.6), BLUE, 3.0, 30, 2.0, t=b.at(0) + 0.6)
        # ---- 26: closing question
    beat_3(B[3])
    def beat_4(b):
        b.card(10.2, 4.6, seed=55, rot=0.4)
        b.text("WHICH SURPRISED YOU?", 44, v(0, 1.7), INK, 8.6, t=b.t0 + 0.3)
        for k, (s, col) in enumerate((("THE CRASH TEST", RED), ("THE BEACON", BLUE), ("THE TWO-YEAR SEARCH", GREEN))):
            b.tape(s, v(-3.2 + 3.2 * k, 0.1 - 0.4 * (k % 2)), col, 3.0, 24, -2.0 + 2.0 * k, t=b.at(0) + 0.3 + 0.5 * k)
        b.put(recorder(1.4).move_to(b.C + v(0, -1.5)), b.t0 + 0.8, z=5, pop=0.3)
        b.live(lambda a: Circle(radius=1.1 + 0.6 * ((ctx.elapsed() * 0.7) % 1.0), stroke_color=ORANGE, stroke_width=4, fill_opacity=0, stroke_opacity=0.6 * a * (1 - ((ctx.elapsed() * 0.7) % 1.0))).move_to(b.C + v(0, -1.5)), b.t0 + 1.0, z=3)

    beat_4(B[4])