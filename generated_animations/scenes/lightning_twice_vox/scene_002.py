"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): a MYTH stamp and repeated strikes on a tower; about 25 strikes a year on a tall tower against almost none on open ground."""
from __future__ import annotations

from generated_animations.scenes.lightning_twice_vox.scene_001 import bolt, cloud, tower
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=11)
        b.live(lambda a: cloud(b.C + v(0, 2.8), a), b.t0 + 0.1, z=4)
        b.live(lambda a: tower(b.C + v(0, -3.9), a, 3.5), b.t0 + 0.2, z=5)
        b.live(lambda a: bolt(b.C + v(0.2, 2.0), b.C + v(0, 0.55), a * (1.0 if (ctx.elapsed() - b.t0) % 0.9 < 0.25 else 0.0), int((ctx.elapsed() - b.t0) / 0.9)), b.t0 + 0.3, z=7)
        b.put(RoundedRectangle(corner_radius=0.2, width=5.2, height=1.6, stroke_color="#FF5A5A", stroke_width=10, fill_opacity=0).move_to(b.C + v(0, 4.5)).rotate(-0.1), b.t0 + 0.3, z=8, pop=0.3)
        b.text(vox.L(ctx, "FALSE", "ग़लत"), 96, v(0, 4.5), "#FF5A5A", 4.6, t=b.t0 + 0.35, z=9)

        def count(a):
            n = 1 + int((ctx.elapsed() - b.t0) / 0.9)
            return VGroup(*[Circle(radius=0.2, stroke_width=0, fill_color="#FFE45C", fill_opacity=a).move_to(b.C + v(-3.4 + 0.55 * k, -4.7)) for k in range(min(n, 10))])
        b.live(count, b.t0 + 0.3, z=6)
        b.tape(vox.L(ctx, "AGAIN AND AGAIN", "बार-बार"), v(0, -1.0), ORANGE, 5.0, 38, 2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=13)
        b.text(vox.L(ctx, "STRIKES PER YEAR", "साल में बिजली"), 62, v(0, 4.2), W_, 7.8, t=b.t0 + 0.2)

        def bars(a):
            f = b.lv(b.t0 + 0.7, 2.0)
            h = 0.12 + 5.6 * f
            return VGroup(Rectangle(width=2.4, height=h, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#FFE45C", fill_opacity=a).move_to(b.C + v(-1.9, -3.4 + h / 2)),
                          Rectangle(width=2.4, height=0.22, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#8E8AA6", fill_opacity=a).move_to(b.C + v(1.9, -3.4 + 0.11)))
        b.live(bars, b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "TALL TOWER\n~25", "ऊँचा टॉवर\n~25"), 44, v(-1.9, 2.6), W_, 3.6, t=b.t0 + 2.4)
        b.text(vox.L(ctx, "OPEN FIELD\nA FEW", "खुला मैदान\nबहुत कम"), 40, v(1.9, -2.3), W_, 3.6, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "EMPIRE STATE BUILDING", "एम्पायर स्टेट बिल्डिंग"), v(0, -4.4), ORANGE, 6.8, 30, -2.0, t=b.t0 + 2.6)
    beat0(B[0])
    beat1(B[1])
