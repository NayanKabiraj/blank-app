"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): the blue dot on a phone map jumps to the wrong street although the phone never moves; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def mapphone(C, s, dot, a, tm=0.0):
    g = VGroup(RoundedRectangle(corner_radius=0.4 * s, width=3.5 * s, height=6.2 * s, stroke_color=W_, stroke_width=4, stroke_opacity=a, fill_color="#171A26", fill_opacity=a).move_to(C),
               RoundedRectangle(corner_radius=0.25 * s, width=3.1 * s, height=5.7 * s, stroke_width=0, fill_color="#E9EEF2", fill_opacity=a).move_to(C))
    for (x0, y0, x1, y1) in ((-0.8, -2.7, -0.8, 2.7), (0.9, -2.7, 0.9, 2.7), (-1.5, 0.3, 1.5, 0.3), (-1.5, -1.3, 1.5, -1.3)):
        g.add(Line(C + v(x0 * s, y0 * s), C + v(x1 * s, y1 * s), color="#C3CBD6", stroke_width=14 * s, stroke_opacity=a))
    g.add(Circle(radius=(0.34 + 0.08 * math.sin(tm * 5)) * s, stroke_width=0, fill_color="#2E86D6", fill_opacity=0.25 * a).move_to(C + v(dot[0] * s, dot[1] * s)))
    g.add(Circle(radius=0.2 * s, stroke_color=W_, stroke_width=4, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(C + v(dot[0] * s, dot[1] * s)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=3)

        def dotpos():
            t = ctx.elapsed() - b.t0
            return (-0.8, 0.9) if int(t / 0.9) % 2 == 0 else (0.9, -0.5)
        b.live(lambda a: mapphone(b.C + v(0, -1.0), 1.0, dotpos(), a, ctx.elapsed()), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "THE BLUE DOT\nJUMPS", "नीला डॉट\nकूद जाता है"), 70, v(0, 3.7), W_, 7.5, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "YOU NEVER MOVED", "आप हिले ही नहीं"), v(0, -3.9), RED, 6.0, 38, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=5)
        b.live(lambda a: mapphone(b.C + v(-2.3, -0.3), 0.75, (-0.8, 0.9) if int((ctx.elapsed() - b.t0) / 0.9) % 2 == 0 else (0.9, -0.5), a, ctx.elapsed()), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("HOW BUILDINGS FOOL GPS", "इमारतें GPS को कैसे चकमा देती हैं", BLUE, v(1.5, 2.6), -2.5), ("ECHOES", "गूँज", ORANGE, v(1.5, 0.8), 2.5), ("PART 2 OF GPS", "GPS का भाग 2", RED, v(1.5, -1.0), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.0, 28, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
