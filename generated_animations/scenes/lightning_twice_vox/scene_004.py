"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): the truth - lightning can strike the same place twice, and does; the closing question."""
from __future__ import annotations

from generated_animations.scenes.lightning_twice_vox.scene_001 import bolt, cloud, tower
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=31)
        b.live(lambda a: cloud(b.C + v(0, 2.8), a), b.t0 + 0.1, z=4)
        b.live(lambda a: tower(b.C + v(0, -3.8), a, 3.4), b.t0 + 0.2, z=5)
        b.live(lambda a: VGroup(bolt(b.C + v(-0.3, 2.0), b.C + v(-0.2, 0.55), a, 1), bolt(b.C + v(0.4, 2.0), b.C + v(0.2, 0.55), a, 5)), b.t0 + 0.6, z=7)
        b.text(vox.L(ctx, "THE TRUTH", "सच"), 80, v(0, 4.6), W_, 6.0, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "IT CAN STRIKE TWICE", "दो बार गिर सकती है"), v(0, -1.0), GREEN, 6.4, 38, -2.0, t=b.t0 + 1.4)
        b.put(VGroup(Line(v(-0.35, 0.0), v(-0.08, -0.32), color=GREEN, stroke_width=18), Line(v(-0.08, -0.32), v(0.45, 0.4), color=GREEN, stroke_width=18)).move_to(b.C + v(-3.3, -1.0)), b.t0 + 2.0, z=8)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.text(vox.L(ctx, "NEXT MYTH?", "अगला मिथक?"), 80, v(0, 4.0), W_, 7.5, t=b.t0 + 0.2)
        for k, (en, hi, col, y, r) in enumerate((("GREAT WALL FROM SPACE?", "चीन की दीवार अंतरिक्ष से?", BLUE, 1.9, -2.0), ("IS THE SUN YELLOW?", "क्या सूरज पीला है?", ORANGE, 0.1, 2.0), ("BULLS HATE RED?", "साँड़ को लाल रंग से चिढ़?", GREEN, -1.7, -2.0))):
            b.tape(vox.L(ctx, en, hi), v(0, y), col, 7.0, 28, r, t=b.t0 + 0.6 + 0.7 * k)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.4, 36, -1.5, t=b.t0 + 3.0)
    beat0(B[0])
    beat1(B[1])
