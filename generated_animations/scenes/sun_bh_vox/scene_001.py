"""Vox look - shot 1 (scenes 1-2): the Sun turns black while Earth keeps orbiting for eight minutes; the Black Holes part-2 promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def sun(C, r, black, a, tm=0.0):
    """The Sun (yellow, rays) that turns into a black hole (dark disc with an orange ring); `black` goes 0 -> 1."""
    col = "#0C0C12" if black > 0.5 else YEL
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color=col, fill_opacity=a).move_to(C))
    if black < 0.5:
        for k in range(12):
            an = k * math.pi / 6 + tm * 0.5
            g.add(Line(C + v(1.15 * r * math.cos(an), 1.15 * r * math.sin(an)), C + v(1.45 * r * math.cos(an), 1.45 * r * math.sin(an)), color=ORANGE, stroke_width=5, stroke_opacity=a))
    else:
        g.add(Ellipse(width=3.2 * r, height=0.9 * r, stroke_color=ORANGE, stroke_width=8, stroke_opacity=a, fill_opacity=0).move_to(C).rotate(0.25))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        S = b.C + v(-0.8, 0.5)
        t_black = b.t0 + 3.0
        b.live(lambda a: sun(S, 0.8, level(ctx, t_black, 0.3), a, ctx.elapsed()), b.t0 + 0.2, z=4)
        earth = lambda: S + v(2.3 * math.cos(ctx.elapsed() * 0.9), 1.3 * math.sin(ctx.elapsed() * 0.9))
        b.live(lambda a: VGroup(Ellipse(width=4.6, height=2.6, stroke_color="#B7AE9C", stroke_width=3, stroke_opacity=0.7 * a, fill_opacity=0).move_to(S),
                                Circle(radius=0.22, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(earth())), b.t0 + 0.4, z=5)
        b.live(lambda a: ctx.text(f"0:{min(59, int(60 * ease(level(ctx, t_black, 3.5)))):02d}" if False else f"{int(8 * ease(level(ctx, t_black, 3.0)))}:{int(20 * ease(level(ctx, t_black, 3.0))):02d}", 46, RED, 2.6).move_to(b.C + v(2.1, 2.5)).set_opacity(a * level(ctx, t_black, 0.3)), t_black, z=7)
        b.tape(vox.L(ctx, "THE SUN TURNS BLACK", "सूरज काला हो गया"), v(-0.8, -2.3), RED, 4.6, 28, -2.0, t=t_black)
        b.tape(vox.L(ctx, "NOTHING CHANGES?", "कुछ नहीं बदलता?"), v(1.6, -1.1), BLUE, 3.8, 28, 2.0, t=b.t0 + 4.4)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.live(lambda a: sun(b.C + v(0, 0.3), 0.8, 1.0, a, ctx.elapsed()), b.t0 + 0.2, z=4)
        for k, (en, hi, col, p, r) in enumerate((("BLACK HOLES #2", "ब्लैक होल्स #2", RED, v(-0.7, 2.3), -3.0), ("WHAT EARTH FEELS", "धरती को क्या लगेगा", BLUE, v(1.1, 0.0), 3.0), ("AND WHEN", "और कब", ORANGE, v(-0.8, -2.1), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.2, 28, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
