"""Vox look - shot 3 (scenes 11-15): the case layers, 3,400 g impact, crush and fire, the beacon quiz and its battery."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    n = 5
    B = [Beat(ctx, i, n) for i in range(n)]
    # ---- 11: layers of steel and titanium wrap the memory
    def beat_0(b):
        b.card(10.2, 4.7, seed=23, rot=-0.4)
        for k, (nm, col) in enumerate((("MEMORY", GREEN), ("STEEL / TITANIUM", "#8895A8"))):
            pass
        mem = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.9, stroke_color=INK, stroke_width=5, fill_color=GREEN, fill_opacity=1).move_to(b.C + v(-2.4, 0.2))
        b.put(mem, b.t0 + 0.2, z=7, pop=0.3)
        for k, col in enumerate(("#B7C0CD", "#8895A8", "#5F6E84")):
            r = RoundedRectangle(corner_radius=0.15, width=1.5 + 0.7 * k + 0.4, height=1.5 + 0.7 * k + 0.4, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1).move_to(b.C + v(-2.4, 0.2))
            r.set_z_index(6 - k)
            b.put(r, b.t0 + 0.6 + 0.5 * (2 - k), z=6 - k, pop=0.35)
        b.text("THE MEMORY", 28, v(-2.4, -1.7), INK, 3.0, t=b.t0 + 0.4)
        b.text("THICK STEEL", 40, v(2.6, 1.0), INK, 4.2, t=b.at(0) + 0.4)
        b.text("OR TITANIUM", 40, v(2.6, 0.2), BLUE, 4.2, t=b.at(0) + 1.0)
        b.tape("BUILT FOR THE WORST MOMENT", v(2.4, -1.2), RED, 5.0, 24, -2.0, t=b.at(0) + 1.6)
        # ---- 12: 3,400 g slam
    beat_0(B[0])
    def beat_1(b):
        b.card(10.4, 4.7, seed=25, rot=0.4)
        wall = Rectangle(width=0.5, height=3.6, stroke_color=INK, stroke_width=5, fill_color="#8895A8", fill_opacity=1).move_to(b.C + v(1.4, 0.0))
        b.put(wall, b.t0 + 0.2, z=4, pop=0.1)
        t_hit = b.t0 + 2.4
        b.mover(recorder(1.2).move_to(b.C + v(-4.4, 0.0)), lambda: b.C + v(-4.4 + 4.1 * ease(level(ctx, b.t0 + 0.8, 1.6)) + (0.14 * math.sin(ctx.elapsed() * 60) * (1 - level(ctx, t_hit, 0.5)) if t_hit < ctx.elapsed() < t_hit + 0.5 else 0.0), 0.0))
        for k in range(4):
            b.put(Line(b.C + v(-4.6, 0.7 - 0.45 * k), b.C + v(-3.5 - 0.3 * k, 0.7 - 0.45 * k), color="#B7AE9C", stroke_width=5), b.t0 + 1.0, z=3, pop=0)
        gcount = b.live(lambda a: ctx.text(f"{int(3400 * ease(level(ctx, b.t0 + 0.8, 2.2))):,} g", 70, RED, 4.2).move_to(b.C + v(3.7, 1.1)).set_opacity(a), b.t0 + 0.6, z=7)
        b.text("A FEW MILLISECONDS", 24, v(3.7, 0.2), INK, 2.9, t=b.at(0) + 0.6)
        b.tape("VIOLENT STOP", v(3.7, -0.9), RED, 3.0, 28, 2.0, t=b.at(1) - 0.2 if False else t_hit)
        # ---- 13: crush + fire
    beat_1(B[1])
    def beat_2(b):
        b.card(10.4, 4.7, seed=27, rot=-0.5)
        box = recorder(1.3).move_to(b.C + v(-2.4, -0.6))
        b.put(box, b.t0 + 0.2, z=6, pop=0.3)

        def press(a):
            f = ease(level(ctx, b.t0 + 0.6, 1.4))
            y = 2.0 - 1.9 * f
            pr = Rectangle(width=2.2, height=0.5, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#5F6E84", fill_opacity=a).move_to(b.C + v(-2.4, y))
            rod = Rectangle(width=0.4, height=1.6, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#8895A8", fill_opacity=a).move_to(b.C + v(-2.4, y + 1.0))
            return VGroup(rod, pr)
        b.live(press, b.t0 + 0.2, z=7)
        b.text("5,000 lb", 46, v(-2.4, -1.9), RED, 3.0, t=b.at(0) + 0.2)
        b.live(lambda a: VGroup(*[flame(1.0, k, ctx.elapsed()).move_to(b.C + v(1.6 + 0.8 * k, -1.2)).set_opacity(a) for k in range(5)]), b.at(0) + 0.9, z=5)
        b.put(recorder(1.1).move_to(b.C + v(3.2, -0.5)), b.t0 + 0.3, z=6, pop=0.3)
        b.text("1,100 C", 46, v(3.2, 1.6), ORANGE, 3.0, t=b.at(0) + 1.2)
        # ---- 14: quiz
    beat_2(B[2])
    def beat_3(b):
        b.card(10.0, 4.6, seed=29, rot=0.4)
        b.text("WHAT HELPS FIND IT?", 40, v(0, 1.8), INK, 8.0, t=b.t0 + 0.2)
        opts = (("A FLASHING LIGHT", BLUE), ("AN UNDERWATER BEACON", GREEN), ("A PARACHUTE", PINK))
        for k, (s, col) in enumerate(opts):
            y = 0.6 - 1.05 * k
            b.tape(s, v(-1.2, y), col, 5.2, 28, 0.0, t=b.t0 + 0.5 + 0.35 * k)
        t_a = b.t1 - 1.6 if b.t1 else b.t0 + 6

        def tick(a):
            f = level(ctx, t_a, 0.35)
            g = VGroup(Line(b.C + v(2.3, -0.5), b.C + v(2.6, -0.8), color=GREEN, stroke_width=14, stroke_opacity=a * (1 if f > 0 else 0)),
                       Line(b.C + v(2.6, -0.8), b.C + v(3.3, 0.1), color=GREEN, stroke_width=14, stroke_opacity=a * (1 if f > 0 else 0)))
            return g
        b.live(tick, t_a, z=9)
        # ---- 15: the beacon and its clock
    beat_3(B[3])
    def beat_4(b):
        b.card(10.4, 4.7, seed=31, rot=-0.4)
        b.live(lambda a: sea(b.C, 9.8, -0.2, 2.2, ctx.elapsed(), a * 0.8), b.t0 + 0.1, z=3)
        rec = recorder(1.2).move_to(b.C + v(-3.3, -1.5))
        b.put(rec, b.t0 + 0.3, z=6, pop=0.3)
        ring_pings(ctx, b.C + v(-2.4, -1.5), b.t0 + 0.8, b.t1, 1.4, 1.5, YEL)
        b.text("PING", 40, v(-3.3, -0.4), RED, 2.0, t=b.t0 + 1.0)
        b.text("BATTERY CLOCK", 28, v(2.6, 1.9), INK, 4.5, t=b.t0 + 0.4)

        def bat(a):
            f = level(ctx, b.t0 + 0.8, max(3.0, (b.t1 or b.t0 + 8) - b.t0 - 2.0))
            shell = Rectangle(width=4.6, height=0.9, stroke_color=INK, stroke_width=5, fill_opacity=0, stroke_opacity=a).move_to(b.C + v(2.6, 0.7))
            w = max(0.02, 4.4 * (1 - 0.92 * f))
            fill = Rectangle(width=w, height=0.7, stroke_width=0, fill_color=GREEN if f < 0.7 else RED, fill_opacity=a).move_to(b.C + v(0.4 + w / 2, 0.7))
            return VGroup(fill, shell)
        b.live(bat, b.t0 + 0.4, z=5)
        b.tape("30 DAYS", v(2.6, -0.7), RED, 2.6, 30, -2.0, t=b.at(0) + 0.8)
        b.tape("-> 90 DAYS", v(2.6, -1.8), GREEN, 3.2, 30, 2.0, t=b.t0 + 3.5)

    beat_4(B[4])