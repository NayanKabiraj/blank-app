"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): the dot lands on the wrong street (fooled, not broken); the closing question."""
from __future__ import annotations

from generated_animations.scenes.gps_echo_vox.scene_001 import mapphone
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#10203A", "#2A4A78", seed=31)
        b.live(lambda a: mapphone(b.C + v(-1.0, -0.9), 0.95, (0.9, -0.5), a, ctx.elapsed()), b.t0 + 0.2, z=6)
        b.put(Circle(radius=0.2, stroke_color=W_, stroke_width=3, fill_opacity=0).move_to(b.C + v(-1.0 - 0.8 * 0.95, -0.9 + 0.9 * 0.95)), b.t0 + 0.9, z=7)
        b.tape(vox.L(ctx, "WHERE YOU ARE", "आप यहाँ हैं"), v(-2.9, 3.0), GREEN, 3.0, 26, -4.0, t=b.t0 + 0.9)
        b.tape(vox.L(ctx, "WHERE THE DOT SAYS", "डॉट यहाँ दिखाता है"), v(2.6, -2.6), RED, 3.6, 26, 4.0, t=b.t0 + 1.6)
        b.text(vox.L(ctx, "NOT BROKEN.\nFOOLED BY ECHOES.", "ख़राब नहीं,\nगूँज ने धोखा दिया।"), 52, v(0, 4.1), W_, 7.8, t=b.t0 + 0.3)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.live(lambda a: mapphone(b.C + v(0, -0.9), 0.92, (-0.8, 0.9) if int((ctx.elapsed() - b.t0) / 0.7) % 2 == 0 else (0.9, -0.5), a, ctx.elapsed()), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "WHERE DOES\nYOUR DOT JUMP?", "आपका डॉट\nकहाँ कूदता है?"), 66, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.4, 36, -1.5, t=b.t0 + 1.4)
    beat0(B[0])
    beat1(B[1])
