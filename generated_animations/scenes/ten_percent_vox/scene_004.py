"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): the real story (all of it has a job, different parts at different moments) and the next-myth question."""
from __future__ import annotations

from generated_animations.scenes.ten_percent_vox.art import brain
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"
COLS = [YEL, ORANGE, RED, PINK, BLUE, GREEN, "#9B6BD6", "#2EC4B6"]


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#1E0F3A", "#4A2368", seed=31)

        def lit(a):
            t = ctx.elapsed() - b.t0
            return brain(b.C + v(0, 0.0), 2.4, [COLS[i] if (int(t * 1.4) + i) % 8 < 5 else "#B8B3D4" for i in range(8)], a)
        b.live(lit, b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "THE REAL STORY", "असली बात"), 66, v(0, 4.1), W_, 7.5, t=b.t0 + 0.2)
        b.tape(vox.L(ctx, "DIFFERENT PARTS, DIFFERENT MOMENTS", "अलग पल, अलग हिस्से"), v(0, -3.2), BLUE, 7.6, 28, -2.0, t=b.t0 + 1.2)
        b.tape(vox.L(ctx, "ALL OF IT HAS A JOB", "हर हिस्से का काम है"), v(0, -4.4), GREEN, 6.4, 30, 2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#3A1B5E", "#6B3A8A", seed=33)
        b.text(vox.L(ctx, "NEXT MYTH?", "अगला मिथक?"), 80, v(0, 4.0), W_, 7.5, t=b.t0 + 0.2)
        for k, (en, hi, col, y, r) in enumerate((("GREAT WALL FROM SPACE?", "चीन की दीवार अंतरिक्ष से?", BLUE, 1.9, -2.0), ("LIGHTNING STRIKES TWICE?", "बिजली दोबारा गिरती है?", ORANGE, 0.1, 2.0), ("IS THE SUN YELLOW?", "क्या सूरज पीला है?", GREEN, -1.7, -2.0))):
            b.tape(vox.L(ctx, en, hi), v(0, y), col, 7.0, 28, r, t=b.t0 + 0.6 + 0.7 * k)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.4, 36, -1.5, t=b.t0 + 3.0)
    beat0(B[0])
    beat1(B[1])
