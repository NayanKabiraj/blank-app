"""Vox look - shot 3 (scenes 5-6): inside, every path leads inward (even light bends back); a small black hole stretches the figure, a giant one is gentle."""
from __future__ import annotations

from ._kit import *
from .scene_001 import hole


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        H = b.C + v(0, 0.1)
        b.live(lambda a: Circle(radius=0.7, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#0C0C12", fill_opacity=a).move_to(H), b.t0 + 0.1, z=4)

        def arrows(a):                                          # every direction points inward; the arrows keep pulsing toward the centre
            g = VGroup()
            for k in range(8):
                an = k * math.pi / 4
                f = (ctx.elapsed() * 0.8 + k / 8.0) % 1.0
                r0, r1 = 2.7 - 1.7 * f, 2.2 - 1.7 * f
                g.add(Line(H + v(r0 * math.cos(an), r0 * math.sin(an) * 0.9), H + v(max(0.8, r1) * math.cos(an), max(0.8, r1) * math.sin(an) * 0.9), color=RED, stroke_width=6, stroke_opacity=a * (1 - 0.6 * f)))
            return g
        b.live(arrows, b.t0 + 0.5, z=5)
        b.tape(vox.L(ctx, "EVERY PATH LEADS IN", "हर रास्ता अंदर"), v(0, 2.5), RED, 5.0, 30, -2.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "LIGHT CAN'T TURN BACK", "रोशनी भी नहीं लौटती"), v(0, -2.5), BLUE, 5.2, 26, 2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        for side, name, hi, big in ((-1, "SMALL HOLE", "छोटा", False), (1, "GIANT HOLE", "विशाल", True)):
            x = side * 1.8
            r = 0.55 if not big else 1.3
            b.live(lambda a, x=x, r=r: Circle(radius=r, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#0C0C12", fill_opacity=a).move_to(b.C + v(x, 0.3)), b.t0 + 0.2, z=4)
            b.text(vox.L(ctx, name, hi), 24, v(x, 2.4), INK, 2.8, t=b.t0 + 0.4)
            fig = figure(0.5, coat=BLUE)
            fig.move_to(b.C + v(x, 1.7))

            def pos(x=x, big=big):
                f = ease(level(ctx, b.t0 + 1.0, 2.6))
                return b.C + v(x, 1.7 - 1.1 * f - (0.0 if big else 0.0))
            b.mover(fig, pos, z=6)
        # the small hole stretches the figure into a noodle: a thin tall ellipse grows beside it
        b.live(lambda a: Ellipse(width=max(0.05, 0.4 - 0.25 * level(ctx, b.t0 + 2.0, 1.5)), height=0.5 + 1.8 * level(ctx, b.t0 + 2.0, 1.5), stroke_color=INK, stroke_width=3, stroke_opacity=a * level(ctx, b.t0 + 2.0, 0.3), fill_color=BLUE, fill_opacity=a * level(ctx, b.t0 + 2.0, 0.3)).move_to(b.C + v(-1.8, 1.1)), b.t0 + 2.0, z=7)
        b.tape(vox.L(ctx, "TORN APART EARLY", "पहले ही चीर देता है"), v(-1.5, -1.6), RED, 3.8, 24, -2.0, t=b.t0 + 3.0)
        b.tape(vox.L(ctx, "GENTLE", "नरम"), v(1.8, -1.6), GREEN, 2.4, 28, 2.0, t=b.t0 + 3.6)
    beat0(B[0])
    beat1(B[1])
