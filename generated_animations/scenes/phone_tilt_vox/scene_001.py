"""Vox look - shot 1 (scenes 1-2): the phone turns sideways while an UP arrow stays put; the Phone series part-2 promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        ang = lambda: 90.0 * ease(level(ctx, b.t0 + 1.0, 1.6))
        b.live(lambda a: phone(1.4).rotate(math.radians(ang())).move_to(b.C + v(0, 0.3)).set_opacity(a), b.t0 + 0.2, z=5)
        b.live(lambda a: VGroup(Line(b.C + v(2.6, -1.0), b.C + v(2.6, 1.4), color=RED, stroke_width=8, stroke_opacity=a),
                                Polygon(b.C + v(2.6, 1.9), b.C + v(2.3, 1.3), b.C + v(2.9, 1.3), stroke_width=0, fill_color=RED, fill_opacity=a)), b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "UP", "ऊपर"), 44, v(2.6, -1.6), RED, 1.8, t=b.t0 + 0.5)
        b.put(ctx.text("?", 110, BLUE, 1.2).move_to(b.C + v(-2.4, 1.6)), b.t0 + 1.0, z=7, pop=0.3)
        b.tape(vox.L(ctx, "THE SCREEN FOLLOWS", "स्क्रीन घूम जाती है"), v(0, -2.4), BLUE, 5.2, 28, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.put(phone(1.3).move_to(b.C + v(0, 0.1)), b.t0 + 0.2, z=4, pop=0.3)
        for k, (en, hi, col, p, r) in enumerate((("PHONE SERIES #2", "फ़ोन सीरीज़ #2", RED, v(-0.8, 2.3), -3.0), ("ONE TINY SENSOR", "एक नन्हा सेंसर", BLUE, v(1.1, 0.5), 3.0), ("IT FEELS GRAVITY", "गुरुत्व महसूस करता है", ORANGE, v(-0.8, -1.9), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.2, 28, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
