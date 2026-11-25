"""Vox look - shot 3 (scenes 5-6): the bounce is compared with a preset number (screen on/off); why the screen goes dark: a cheek would press buttons."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        # a bar swings up and down past a threshold line; the screen below switches OFF above it
        def bar(a):
            lvl = 0.5 + 0.5 * math.sin(ctx.elapsed() * 1.6)
            h = 0.3 + 2.4 * lvl
            col = RED if lvl > 0.55 else GREEN
            return VGroup(Rectangle(width=0.9, height=h, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color=col, fill_opacity=a).move_to(b.C + v(-1.8, -1.0 + h / 2)),
                          Line(b.C + v(-2.9, 0.7), b.C + v(-0.6, 0.7), color=INK, stroke_width=5, stroke_opacity=a))
        b.live(bar, b.t0 + 0.2, z=5)
        b.text(vox.L(ctx, "PRESET NUMBER", "तय संख्या"), 26, v(-1.4, 2.7), INK, 3.2, t=b.t0 + 0.5)

        def scr(a):
            on = (0.5 + 0.5 * math.sin(ctx.elapsed() * 1.6)) <= 0.55
            return phone(1.2, on=on).move_to(b.C + v(1.7, 0.2)).set_opacity(a)
        b.live(scr, b.t0 + 0.4, z=5)
        b.text(vox.L(ctx, "ABOVE: SCREEN OFF", "ऊपर: स्क्रीन बंद"), 26, v(1.7, -1.6), RED, 3.4, t=b.t0 + 0.9)
        b.tape(vox.L(ctx, "BELOW: BACK ON", "नीचे: फिर चालू"), v(0, -2.4), GREEN, 4.2, 28, -2.0, t=b.t0 + 1.4)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        ph = phone(1.5).move_to(b.C + v(-0.2, 0.2))
        b.put(ph, b.t0 + 0.1, z=4, pop=0.2)
        hang = Circle(radius=0.28, stroke_color=INK, stroke_width=3, fill_color=RED, fill_opacity=1).move_to(b.C + v(-0.2, -0.45))
        b.put(hang, b.t0 + 0.5, z=6, pop=0.3)
        cheek = vox.cutout(Circle(radius=0.8, stroke_color=INK, stroke_width=4, fill_color="#F2C9A0", fill_opacity=1), 6.0)
        cheek.move_to(b.C + v(2.4, -1.2))
        b.mover(cheek, lambda: b.C + v(2.4 - 2.6 * ease(level(ctx, b.t0 + 1.0, 1.2)), -1.2 + 0.1 * math.sin(ctx.elapsed() * 5)), z=7)
        b.put(vox.tape(ctx, vox.L(ctx, "CALL ENDED!", "कॉल कट!"), b.C + v(-1.6, 1.7), RED, 3.2, 30, -4.0), b.t0 + 2.4, z=8, pop=0.3)
        b.text(vox.L(ctx, "SCREEN OFF = NO TAPS + SAVES BATTERY", "स्क्रीन बंद = टैप नहीं + बैटरी बचत"), 24, v(0, -2.5), INK, 6.2, t=b.t0 + 1.6)
    beat0(B[0])
    beat1(B[1])
