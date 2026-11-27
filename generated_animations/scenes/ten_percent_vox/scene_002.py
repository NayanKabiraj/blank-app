"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): MYTH stamp; brain scans light up every region; the test: if 90% did nothing, damage there would change nothing."""
from __future__ import annotations

from generated_animations.scenes.ten_percent_vox.art import brain
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"
COLS = [YEL, ORANGE, RED, PINK, BLUE, GREEN, "#9B6BD6", "#2EC4B6"]


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#1E0F3A", "#4A2368", seed=11)

        def lit(a):
            t = ctx.elapsed() - b.t0
            return brain(b.C + v(0, -0.5), 2.4, [COLS[i] if t > 0.8 + 0.28 * i else None for i in range(8)], a)
        b.live(lit, b.t0 + 0.2, z=6)
        b.put(RoundedRectangle(corner_radius=0.2, width=5.2, height=1.6, stroke_color="#FF5A5A", stroke_width=10, fill_opacity=0).move_to(b.C + v(0, 3.9)).rotate(-0.1), b.t0 + 0.3, z=7, pop=0.3)
        b.text(vox.L(ctx, "FALSE", "ग़लत"), 96, v(0, 3.9), "#FF5A5A", 4.6, t=b.t0 + 0.35, z=8)
        b.tape(vox.L(ctx, "EVERY REGION SHOWS ACTIVITY", "हर हिस्से में हलचल"), v(0, -4.2), BLUE, 6.8, 30, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#1E0F3A", "#4A2368", seed=13)
        b.text(vox.L(ctx, "THE TEST", "जाँच"), 70, v(0, 4.1), W_, 6.0, t=b.t0 + 0.2)
        for i, (en, hi, col, y) in enumerate((("IDLE 90%", "90% ख़ाली", "#8E8AA6", 2.2), ("DAMAGE IT", "नुक़सान करो", RED, 0.2), ("NO CHANGE?", "कुछ नहीं बदला?", ORANGE, -1.8))):
            b.put(RoundedRectangle(corner_radius=0.3, width=6.0, height=1.4, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1).move_to(b.C + v(0, y)), b.t0 + 0.5 + 0.6 * i, z=5)
            b.text(vox.L(ctx, en, hi), 46, v(0, y), W_, 5.6, t=b.t0 + 0.55 + 0.6 * i, z=7)
            if i < 2:
                b.put(Polygon(v(-0.3, 0), v(0.3, 0), v(0, -0.45), stroke_width=0, fill_color=W_, fill_opacity=1).move_to(b.C + v(0, y - 1.0)), b.t0 + 0.9 + 0.6 * i, z=6)
        b.text("?", 150, v(2.8, -3.8), "#FFD640", 2.0, t=b.t0 + 2.2, z=8)
    beat0(B[0])
    beat1(B[1])
