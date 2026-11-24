"""Vox look - shot 4 (scenes 16-21): flight 447 route, the rough sea floor, the submarine at 3,900 m, data download, the 2012 report clipping, 30 -> 90 days."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    n = 6
    B = [Beat(ctx, i, n) for i in range(n)]
    # ---- 16: Rio -> Paris, the plane vanishes mid-ocean
    def beat_0(b):
        b.card(10.4, 4.8, seed=33, rot=0.4)
        b.live(lambda a: sea(b.C, 9.6, 0.2, 2.6, ctx.elapsed(), a * 0.55), b.t0 + 0.1, z=3)
        b.text("RIO", 34, v(-4.1, 1.0), INK, 1.6, t=b.t0 + 0.3)
        b.text("PARIS", 34, v(4.0, 1.0), INK, 1.8, t=b.t0 + 0.3)
        arc = lambda f: v(-4.0 + 8.0 * f, 1.4 + 1.0 * math.sin(math.pi * f))
        b.mover(plane(0.8).move_to(b.C + arc(0)), lambda: b.C + arc(0.5 * ease(level(ctx, b.t0 + 0.5, 3.5))))
        b.live(lambda a: VGroup(*[Circle(radius=0.05, stroke_width=0, fill_color=INK, fill_opacity=a * level(ctx, b.t0 + 0.5 + k * 0.12, 0.1)).move_to(b.C + arc(k / 24)) for k in range(0, 13)]), b.t0 + 0.3, z=4)
        b.tape("JUNE 2009", v(0, -1.2), RED, 3.2, 30, -2.0, t=b.at(0) + 0.4)
        b.tape("FLIGHT 447", v(0, -2.0), BLUE, 3.2, 30, 2.0, t=b.at(0) + 0.9)
        # ---- 17: deep, rough sea floor + sonar
    beat_0(B[0])
    def beat_1(b):
        b.card(10.4, 4.7, seed=35, rot=-0.4)
        b.put(Rectangle(width=9.6, height=3.6, stroke_width=0, fill_color="#3F8FD8", fill_opacity=0.65).move_to(b.C + v(0, 0.0)), b.t0 + 0.2, z=3, pop=0)
        floor_pts = [(-4.8, -1.5), (-3.6, -1.0), (-2.4, -1.7), (-1.2, -0.7), (0.2, -1.6), (1.4, -0.9), (2.8, -1.7), (4.0, -1.0), (4.8, -1.4), (4.8, -1.8), (-4.8, -1.8)]
        b.put(Polygon(*[b.C + v(*p) for p in floor_pts], stroke_color=INK, stroke_width=4, fill_color="#7A6A55", fill_opacity=1), b.t0 + 0.4, z=4, pop=0)
        ship = b.mover(vox.cutout(Rectangle(width=1.4, height=0.35, stroke_color=INK, stroke_width=4, fill_color=RED, fill_opacity=1), 5).move_to(b.C + v(-3.5, 1.9)),
                       lambda: b.C + v(-3.5 + 6.5 * ease(level(ctx, b.t0 + 0.6, (b.t1 or b.t0 + 12) - b.t0 - 1.0)), 1.9 + 0.05 * math.sin(ctx.elapsed() * 3)))

        def sonar(a):
            sx = ship.get_center()
            f = (ctx.elapsed() * 0.5) % 1.0
            return VGroup(*[Line(sx + v(0, -0.2), sx + v(-1.6 + 1.6 * k, -3.4 * f - 0.3), color=YEL, stroke_width=3, stroke_opacity=a * (1 - f) * 0.8) for k in range(3)])
        b.live(sonar, b.t0 + 0.8, z=5)
        b.tape("HARD TO SEARCH", v(2.6, 0.9), RED, 4.0, 28, 2.0, t=b.at(0) + 0.4)
        b.tape("SLOW, COSTLY", v(2.6, 0.1), BLUE, 3.6, 28, -2.0, t=b.at(0) + 1.0)
        # ---- 18: May 2011 - a robot submarine at ~3,900 m
    beat_1(B[1])
    def beat_2(b):
        b.card(10.2, 4.7, seed=37, rot=0.4)
        b.put(Rectangle(width=9.4, height=4.0, stroke_width=0, fill_color="#2F6FB0", fill_opacity=0.7).move_to(b.C + v(0, -0.1)), b.t0 + 0.2, z=3, pop=0)
        b.put(Polygon(*[b.C + v(*p) for p in ((-4.7, -2.1), (-2.0, -1.8), (0.0, -2.1), (2.2, -1.7), (4.7, -2.1), (4.7, -2.3), (-4.7, -2.3))], stroke_color=INK, stroke_width=4, fill_color="#7A6A55", fill_opacity=1), b.t0 + 0.4, z=4, pop=0)
        sb = b.mover(sub(1.1).move_to(b.C + v(-1.8, 1.7)), lambda: b.C + v(-1.8, 1.7 - 3.2 * ease(level(ctx, b.t0 + 0.6, 3.0))), z=7)
        b.live(lambda a: Polygon(sb.get_center() + v(0.2, -0.2), sb.get_center() + v(1.8, -1.4), sb.get_center() + v(1.8, 0.2), stroke_width=0, fill_color=YEL, fill_opacity=0.28 * a * level(ctx, b.t0 + 1.0, 0.5)), b.t0 + 0.8, z=6)
        b.put(recorder(0.8).move_to(b.C + v(0.4, -1.95)), b.t0 + 3.6, z=7, pop=0.4)
        b.live(lambda a: ctx.text(f"{int(3900 * ease(level(ctx, b.t0 + 0.6, 3.0))):,} m", 64, "#FFFFFF", 3.4).move_to(b.C + v(2.9, 1.2)).set_opacity(a), b.t0 + 0.6, z=8)
        b.tape("MAY 2011", v(2.9, 0.0), RED, 3.0, 30, 2.0, t=b.at(0) + 0.5)
        # ---- 19: recovered -> lab -> data (flow)
    beat_2(B[2])
    def beat_3(b):
        b.card(10.4, 4.6, seed=39, rot=-0.4)
        xs = (-3.6, 0.0, 3.6)
        for k, (nm, col) in enumerate((("ROBOT SUB", YEL), ("RECOVERED", BLUE), ("DATA READ", GREEN))):
            c = vox.torn_card(2.8, 2.2, seed=40 + k, rot=2 - 2 * k).move_to(b.C + v(xs[k], 0.5))
            b.put(c, b.t0 + 0.3 + 0.8 * k, z=3, pop=0.2)
            b.text(nm, 28, v(xs[k], 1.2), INK, 2.5, t=b.t0 + 0.5 + 0.8 * k)
            if k == 0:
                b.put(sub(1.0).move_to(b.C + v(xs[k], 0.3)), b.t0 + 0.6, z=6, pop=0.3)
            if k == 1:
                b.put(recorder(0.9).move_to(b.C + v(xs[k], 0.3)), b.t0 + 1.4, z=6, pop=0.3)
            if k == 2:
                for j in range(5):
                    hh = [0.4, 0.8, 0.55, 1.0, 0.7][j]
                    b.put(Rectangle(width=0.28, height=hh, stroke_color=INK, stroke_width=3, fill_color=GREEN, fill_opacity=1).move_to(b.C + v(xs[k] - 0.6 + 0.3 * j, 0.0 + hh / 2 - 0.15)), b.t0 + 2.2 + 0.15 * j, z=6, pop=0.1)
            if k < 2:
                b.put(vox.doodle_arrow(b.C + v(xs[k] + 1.6, 0.5), b.C + v(xs[k] + 2.0, 0.5), RED, 0.5, 6), b.t0 + 1.0 + 0.8 * k, z=7)
        b.tape("COLD WATER HELPED", v(0, -1.7), BLUE, 4.6, 28, -1.5, t=b.at(1))
        # ---- 20: July 2012 report clipping
    beat_3(B[3])
    def beat_4(b):
        b.card(10.4, 4.8, seed=41, rot=0.4)
        paper = vox.newspaper(ctx, "The Curious Loop Times", "Investigators publish final report", "PARIS - JULY 2012", w=4.9, h=4.0, seed=43, rot=3.0)
        paper.move_to(b.C + v(-2.4, 0.0))
        vox.arrive(ctx, paper, b.t0 + 0.2, t_out=b.t1, side="right", z=8)
        b.tape("ICE CRYSTALS", v(3.0, 0.9), BLUE, 3.8, 30, 2.0, t=b.at(0) + 0.6)
        b.tape("CREW RESPONSE", v(3.0, -0.2), ORANGE, 3.8, 30, -2.0, t=b.at(0) + 1.4)
        b.tape("BEA REPORT", v(3.0, -1.3), GREEN, 3.4, 28, 1.5, t=b.at(0) + 2.2)
        # ---- 21: beacon 30 -> 90 days
    beat_4(B[4])
    def beat_5(b):
        b.card(9.8, 4.6, seed=45, rot=-0.4)
        for k, (nm, days, col) in enumerate((("BEFORE", 30, RED), ("AFTER", 90, GREEN))):
            y = 0.7 - 1.5 * k
            b.text(nm, 30, v(-3.8, y), INK, 2.0, t=b.t0 + 0.4 + 0.8 * k)
            wd = lambda days=days, k=k: max(0.05, 5.4 * days / 90.0 * ease(level(ctx, b.t0 + 0.8 + 0.8 * k, 1.3)))
            bar = always_redraw(lambda col=col, y=y, wd=wd: Rectangle(width=wd(), height=0.8, stroke_color=INK, stroke_width=4, stroke_opacity=window(ctx, b.t0 + 0.4, b.t1)(), fill_color=col, fill_opacity=window(ctx, b.t0 + 0.4, b.t1)()).move_to(b.C + v(-2.6 + wd() / 2, y)))
            bar._dynamic = True
            ctx.add(bar, z=5)
            b.text(f"{days} DAYS", 32, v(-2.6 + 5.4 * days / 90.0 + 0.9, y), INK, 1.8, t=b.t0 + 1.8 + 0.8 * k)
        b.tape("NEVER RACE A BATTERY", v(1.6, -2.0), BLUE, 4.8, 26, 1.5, t=b.at(0) + 1.0)

    beat_5(B[5])