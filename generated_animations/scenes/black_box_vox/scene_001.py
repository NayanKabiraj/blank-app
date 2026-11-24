"""Vox look - shot 1 (scenes 1-5): a plane lost over the sea, the three-part promise, two recorders, 'is it black?', no record = mystery."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    n = 5
    B = [Beat(ctx, i, n) for i in range(n)]
    tm = lambda: ctx.elapsed()
    # ---- 1: a plane descends over the sea
    def beat_0(b):
        b.card(10.4, 4.8, seed=3)
        b.live(lambda a: sea(b.C, 9.6, -1.1, 1.2, tm(), a), z=3)
        dur_ = max(3.0, (b.t1 or 12) - b.t0 - 1.0)
        b.mover(plane(1.2).move_to(b.C + v(-4.4, 1.8)), lambda: b.C + v(-4.4 + 8.0 * ease(level(ctx, b.t0 + 0.3, dur_)), 1.8 - 2.5 * ease(level(ctx, b.t0 + 0.3, dur_)) ** 2))
        b.text("NO WITNESSES", 34, v(0, 2.0), RED, 4.0, t=b.t0 + 1.2)
        b.tape("ALMOST NOTHING TO GO ON", v(0, -1.9), BLUE, 5.4, 26, 1.5, t=b.at(2))
        # ---- 2: promise
    beat_0(B[0])
    def beat_1(b):
        b.card(10.2, 4.6, seed=5, rot=-0.6)
        b.put(recorder(1.6).move_to(b.C + v(0, 0.2)), b.t0 + 0.2, z=5, pop=0.3)
        for k, (s, col, p, r) in enumerate((("WHAT IS INSIDE", BLUE, v(-3.4, 1.6), -3.0), ("HOW IT SURVIVES", ORANGE, v(3.4, 1.2), 3.0), ("HOW IT WAS FOUND", GREEN, v(0, -1.7), -1.5))):
            b.tape(s, p, col, 4.0, 28, r, t=b.at(min(k, 1)) + 0.3 * k)
        # ---- 3: two recorders
    beat_1(B[1])
    def beat_2(b):
        b.card(10.4, 4.7, seed=7, rot=0.5)
        for side, name, col in ((-1, "FLIGHT DATA", BLUE), (1, "COCKPIT VOICE", PINK)):
            b.put(vox.torn_card(4.4, 3.2, seed=20 + side, rot=side * 1.5).move_to(b.C + v(side * 2.7, 0.0)), b.t0 + 0.3 + 0.3 * (side + 1) / 2, z=3, pop=0.15)
            b.text(name, 30, v(side * 2.7, 1.2), INK, 3.8, t=b.t0 + 0.5)
        ox = b.C + v(-4.5, -0.5)

        def trace(a):
            from manim import VMobject
            f = level(ctx, b.t0 + 0.8, 3.0)
            n_ = max(2, int(40 * f))
            pts = [ox + v(3.6 * k / 40, 0.6 * math.sin(k * 0.45) * (1 + 0.5 * math.sin(k * 0.11)) + 0.2) for k in range(n_)]
            return VMobject(stroke_color=BLUE, stroke_width=6, stroke_opacity=a).set_points_as_corners(pts)
        b.live(trace, b.t0 + 0.6, z=6)

        def bars(a):
            g = VGroup()
            for k in range(14):
                hh = 0.12 + 0.55 * abs(math.sin(ctx.elapsed() * 5 + k * 0.8)) * (0.5 + 0.5 * math.sin(k * 0.6 + 1))
                g.add(Rectangle(width=0.16, height=hh * 2, stroke_width=0, fill_color=PINK, fill_opacity=a).move_to(b.C + v(1.1 + 0.28 * k, -0.2)))
            return g
        b.live(bars, b.t0 + 0.8, z=6)
        b.tape("TOGETHER: THE STORY", v(0, -1.9), GREEN, 4.6, 26, 1.5, t=b.at(2))
        # ---- 4: is it black?
    beat_2(B[2])
    def beat_3(b):
        b.card(9.4, 4.6, seed=9, rot=0.4)

        def box(a):
            f = ease(level(ctx, b.at(1) - 0.6, 1.2))
            r = recorder(2.0, col=ORANGE if f > 0.5 else INK)
            r.move_to(b.C + v(-1.8, 0.1))
            r.set_opacity(a)
            return r
        b.live(box, b.t0 + 0.2, z=5)
        t = b.text("IS IT BLACK?", 44, v(2.3, 1.2), INK, 4.2, t=b.t0 + 0.3)
        b.text("USUALLY BRIGHT ORANGE", 28, v(2.3, 0.0), INK, 4.2, t=b.at(1))
        vox.marker(ctx, ctx.text("USUALLY BRIGHT ORANGE", 28, INK, 4.2).move_to(b.C + v(2.3, 0.0)), b.at(1) + 0.4, 0.9)
        b.tape("SO SEARCHERS CAN SPOT IT", v(0.6, -1.7), RED, 5.0, 26, -2.0, t=b.at(1) + 0.8)
        # ---- 5: no record, no answers
    beat_3(B[3])
    def beat_4(b):
        b.card(10.2, 4.6, seed=11, rot=-0.5)
        for k in range(7):
            pc = Polygon(v(0, 0), v(0.4, 0.1), v(0.3, -0.3), v(-0.2, -0.25), stroke_color=INK, stroke_width=3, fill_color=[CREAM, BLUE, RED][k % 3], fill_opacity=1)
            ang = k * 0.9
            pc.move_to(b.C + v(-3.8 + 1.25 * k, -0.9 + 0.5 * math.sin(ang)))
            pc.rotate(ang)
            b.put(pc, b.t0 + 0.3 + 0.15 * k, z=5, pop=0.3)
        for k, (x, y) in enumerate(((-2.8, 1.0), (0.2, 1.4), (2.8, 0.8))):
            b.text("?", 90, v(x, y), RED, 1.2, t=b.t0 + 0.8 + 0.6 * k)
        b.tape("NO RECORD, NO ANSWERS", v(0, -1.9), BLUE, 5.2, 28, -1.5, t=b.at(1))
        ctx.avatar.look_at(b.C + v(0, 0.3))
        ctx.until(b.t0 + 0.1)

    beat_4(B[4])