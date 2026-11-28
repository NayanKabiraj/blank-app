"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): a sudden stop is nearly impossible, the real spin only slows a tiny bit; the closing question."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#10224A", "#2B4C7E", seed=31)
        b.text(vox.L(ctx, "COULD IT HAPPEN?", "क्या ऐसा होगा?"), 62, v(0, 4.1), W_, 7.6, t=b.t0 + 0.2)

        def bars(a):
            f1, f2 = b.lv(b.t0 + 0.6, 0.9), b.lv(b.t0 + 1.6, 2.0)
            return VGroup(Rectangle(width=2.4, height=max(0.05, 5.0), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#7A2A2A", fill_opacity=a * 0.5).move_to(b.C + v(-1.9, -2.4 + 2.5)),
                          Rectangle(width=2.4, height=max(0.05, 0.25 * f2 + 0.05), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=GREEN, fill_opacity=a).move_to(b.C + v(1.9, -2.4 + (0.25 * f2 + 0.05) / 2)))
        b.live(bars, b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "SUDDEN\nSTOP", "अचानक\nरुकना"), 40, v(-1.9, 0.6), W_, 3.4, t=b.t0 + 0.8)
        b.text(vox.L(ctx, "TINY\nSLOWING", "ज़रा-सी\nधीमी"), 40, v(1.9, -1.2), W_, 3.4, t=b.t0 + 1.8)
        b.tape(vox.L(ctx, "NEARLY IMPOSSIBLE", "लगभग नामुमकिन"), v(-1.9, 2.6), RED, 4.6, 34, -3.0, t=b.t0 + 1.2)
        b.tape(vox.L(ctx, "WHAT REALLY HAPPENS", "असल में यह होता है"), v(1.9, -3.8), GREEN, 5.0, 28, 2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.live(lambda a: astro(b.C + v(0, -0.6), 1.9, hl=(-0.95, -0.6 + 0.25 * math.sin(ctx.elapsed() * 3)), hr=(0.95, -0.6 - 0.25 * math.sin(ctx.elapsed() * 3)), mouth=0.4, blink=0.1 if (ctx.elapsed() % 2.4) < 0.12 else 1.0, a=a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "SUNNY HALF OR\nDARK HALF?", "धूप वाला या\nअँधेरे वाला?"), 60, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "SUNNY HALF", "धूप वाला"), v(-2.6, 2.2), ORANGE, 3.8, 34, -3.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "DARK HALF", "अँधेरे वाला"), v(2.6, 2.2), BLUE, 3.8, 34, 3.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.4, 36, -1.5, t=b.t0 + 1.9)
    beat0(B[0])
    beat1(B[1])
