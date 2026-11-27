"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): the brain is 2% of body weight but burns ~20% of the energy; nobody pays that bill for an idle brain."""
from __future__ import annotations

from generated_animations.scenes.ten_percent_vox.art import brain
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#1E0F3A", "#4A2368", seed=21)
        b.text(vox.L(ctx, "THE BRAIN'S SHARE", "दिमाग़ का हिस्सा"), 62, v(0, 4.1), W_, 7.5, t=b.t0 + 0.2)

        def bars(a):
            f1, f2 = b.lv(b.t0 + 0.7, 0.8), b.lv(b.t0 + 1.8, 1.4)
            return VGroup(Rectangle(width=2.0, height=max(0.05, 0.4 * f1), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(b.C + v(-2.0, -3.2 + 0.2 * f1)),
                          Rectangle(width=2.0, height=max(0.05, 5.4 * f2), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=ORANGE, fill_opacity=a).move_to(b.C + v(2.0, -3.2 + 2.7 * f2)))
        b.live(bars, b.t0 + 0.5, z=6)
        b.text(vox.L(ctx, "2%\nOF YOUR WEIGHT", "2%\nवज़न का"), 40, v(-2.0, -1.9), W_, 3.8, t=b.t0 + 1.1)
        b.text(vox.L(ctx, "20%\nOF YOUR ENERGY", "20%\nऊर्जा का"), 40, v(2.0, 2.6), W_, 3.8, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#1E0F3A", "#4A2368", seed=23)
        b.live(lambda a: brain(b.C + v(-2.0, 0.6), 1.5, [None] * 8, a), b.t0 + 0.2, z=6)
        b.put(RoundedRectangle(corner_radius=0.2, width=3.6, height=4.4, stroke_color=INK, stroke_width=4, fill_color="#FFFDF5", fill_opacity=1).move_to(b.C + v(2.3, 0.4)).rotate(0.08), b.t0 + 0.5, z=5, pop=0.2)
        b.text(vox.L(ctx, "ENERGY\nBILL", "ऊर्जा\nबिल"), 44, v(2.3, 1.7), INK, 3.0, t=b.t0 + 0.7, z=7)
        b.text("20%", 90, v(2.3, 0.2), RED, 3.2, t=b.t0 + 1.0, z=7)
        b.text(vox.L(ctx, "FOR AN IDLE BRAIN?", "ख़ाली दिमाग़ के लिए?"), 26, v(2.3, -1.5), INK, 3.0, t=b.t0 + 1.4, z=7)
        b.tape(vox.L(ctx, "NOBODY PAYS FOR IDLE", "ख़ाली के लिए कोई नहीं भरता"), v(0, -3.9), RED, 6.8, 30, -2.0, t=b.t0 + 2.0)
    beat0(B[0])
    beat1(B[1])
