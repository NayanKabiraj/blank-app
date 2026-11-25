"""Vox look - shot 1 (scenes 1-2): the last train glides through the night announcing a stop; the tonight's-story promise as tape labels. Fiction."""
from __future__ import annotations

from ._kit import *


def carriage(C, tm=0.0, alpha=1.0, flicker=True):
    body = RoundedRectangle(corner_radius=0.25, width=4.6, height=1.7, stroke_color=INK, stroke_width=5, stroke_opacity=alpha, fill_color="#3D4A66", fill_opacity=alpha).move_to(C)
    g = VGroup(body)
    for k in range(4):
        lit = (math.sin(tm * 9 + k * 2.1) > -0.6) if flicker else True
        g.add(Rectangle(width=0.75, height=0.6, stroke_color=INK, stroke_width=3, stroke_opacity=alpha, fill_color=YEL if lit else "#4A4A55", fill_opacity=alpha).move_to(C + v(-1.65 + 1.1 * k, 0.25)))
    g.add(Line(C + v(-2.3, -0.55), C + v(2.3, -0.55), color=INK, stroke_width=4, stroke_opacity=alpha))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        b.put(Rectangle(width=7.4, height=3.0, stroke_width=0, fill_color="#1B2238", fill_opacity=1).move_to(b.C + v(0, 0.2)), b.t0 + 0.1, z=3, pop=0)
        for k in range(7):                                                  # a few stars
            b.put(Circle(radius=0.05, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).move_to(b.C + v(-3.0 + k * 1.0, 1.4 + 0.3 * math.sin(k * 2))), b.t0 + 0.2, z=4, pop=0)
        b.live(lambda a: VGroup(Line(b.C + v(-3.6, -1.1), b.C + v(3.6, -1.1), color="#B7AE9C", stroke_width=6, stroke_opacity=a),
                                *[Line(b.C + v(-3.6 + ((k * 0.8 - ctx.elapsed() * 2.0) % 7.2), -1.1), b.C + v(-3.6 + ((k * 0.8 - ctx.elapsed() * 2.0) % 7.2), -1.35), color="#B7AE9C", stroke_width=5, stroke_opacity=a) for k in range(9)]), b.t0 + 0.2, z=5)
        b.live(lambda a: carriage(b.C + v(0.2 * math.sin(ctx.elapsed() * 2.0), 0.0), ctx.elapsed(), a), b.t0 + 0.3, z=6)
        b.tape(vox.L(ctx, "\"NEXT STOP: YOUR STATION\"", "\"अगला स्टेशन: आपका\""), v(0, 2.3), RED, 5.6, 26, -2.0, t=b.t0 + 2.2)
        b.tape(vox.L(ctx, "TWICE", "दो बार"), v(2.3, -2.3), BLUE, 2.4, 32, 3.0, t=b.t0 + 3.2)
        b.text(vox.L(ctx, "A FICTIONAL STORY", "एक काल्पनिक कहानी"), 22, v(-1.8, -2.6), "#6B6B75", 3.6, t=b.t0 + 0.8)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.live(lambda a: carriage(b.C + v(0, 0.1), ctx.elapsed(), a, flicker=False).scale(0.7), b.t0 + 0.2, z=4)
        for k, (en, hi, col, p, r) in enumerate((("AN EMPTY CARRIAGE", "ख़ाली डिब्बा", BLUE, v(-0.8, 2.3), -3.0), ("A CALM VOICE", "एक शांत आवाज़", ORANGE, v(1.0, -1.1), 3.0), ("A STOP ON NO MAP", "नक़्शे में नहीं", RED, v(-0.6, -2.3), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.2, 28, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
