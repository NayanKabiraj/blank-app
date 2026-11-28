"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): lightning takes the easiest path to the ground, and a tall tower is that path; it keeps no memory of where it has been."""
from __future__ import annotations

from generated_animations.scenes.lightning_twice_vox.scene_001 import bolt, cloud, tower
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=21)
        b.put(Rectangle(width=9.4, height=1.0, stroke_width=0, fill_color="#1B2238", fill_opacity=1).move_to(b.C + v(0, -4.5)), b.t0 + 0.1, z=3, pop=0)
        b.live(lambda a: cloud(b.C + v(0, 3.0), a), b.t0 + 0.1, z=4)
        b.live(lambda a: tower(b.C + v(2.0, -4.0), a, 4.6), b.t0 + 0.2, z=5)
        b.put(Line(b.C + v(-2.4, 2.1), b.C + v(-2.4, -4.0), color="#8E8AA6", stroke_width=4), b.t0 + 0.4, z=5, pop=0)
        b.text(vox.L(ctx, "LONG WAY", "लंबा रास्ता"), 32, v(-2.4, -0.6), "#8E8AA6", 2.4, t=b.t0 + 0.6)

        def path(a):
            f = b.lv(b.t0 + 1.4, 1.2)
            return bolt(b.C + v(1.9, 2.1), b.C + v(2.0, 2.1 - 5.6 * f), a * (1.0 if f > 0.02 else 0.0), 3)
        b.live(path, b.t0 + 0.8, z=7)
        b.text(vox.L(ctx, "THE EASIEST PATH", "सबसे आसान रास्ता"), 56, v(0, 4.6), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "SHORT WAY: THE TOWER", "छोटा रास्ता: टॉवर"), v(2.0, 0.8), ORANGE, 4.6, 26, -2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=23)
        b.live(lambda a: tower(b.C + v(0, -4.2), a, 4.2), b.t0 + 0.2, z=5)
        b.live(lambda a: bolt(b.C + v(0.1, 3.4), b.C + v(0, 0.2), a * (1.0 if (ctx.elapsed() - b.t0) % 0.8 < 0.22 else 0.0), int((ctx.elapsed() - b.t0) / 0.8)), b.t0 + 0.3, z=7)
        b.text(vox.L(ctx, "NO MEMORY", "कोई याददाश्त नहीं"), 64, v(0, 4.4), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "IT JUST TAKES THE EASY PATH", "बस आसान रास्ता लेती है"), v(0, -4.6), ORANGE, 7.6, 28, -2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
