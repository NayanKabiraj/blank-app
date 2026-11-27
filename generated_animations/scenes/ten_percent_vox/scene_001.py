"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): "you only use 10% of your brain" - a brain with one lobe lit and the rest idle; the episode promise as tape labels."""
from __future__ import annotations

from manim import Arc

from generated_animations.scenes.ten_percent_vox.art import brain
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#1E0F3A", "#5B2A6E", seed=3)
        b.live(lambda a: brain(b.C + v(0, -0.6), 2.5, [YEL] + [None] * 7, a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "YOU ONLY USE\n10% OF YOUR BRAIN", "आप दिमाग़ का\nसिर्फ़ 10% इस्तेमाल करते हैं"), 58, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "EVERYONE SAYS IT", "सब यही कहते हैं"), v(0, -4.0), ORANGE, 6.0, 38, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#1E0F3A", "#5B2A6E", seed=5)
        b.live(lambda a: brain(b.C + v(-2.3, -0.4), 1.2, [YEL] + [None] * 7, a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("THE 10% MYTH", "10% का मिथक", RED, v(1.6, 2.7), -2.5), ("BRAIN SCANS", "ब्रेन स्कैन", BLUE, v(1.6, 0.9), 2.5), ("THE ENERGY BILL", "ऊर्जा का बिल", ORANGE, v(1.6, -0.9), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.6, 32, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
