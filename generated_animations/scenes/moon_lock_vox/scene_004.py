"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): libration - a small wobble lets us peek around the edge; the closing question."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#1D2A55", seed=31)

        def wob(a):
            t = ctx.elapsed() - b.t0
            sway = 0.5 * math.sin(t * 1.6)
            g = VGroup(Circle(radius=2.6, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#C9CCD6", fill_opacity=a).move_to(b.C + v(0, 0.0)))
            for x, y, rr in ((-0.8, 0.9, 0.5), (0.7, 0.5, 0.35), (-0.2, -0.7, 0.6), (1.0, -0.9, 0.3), (-1.4, -0.3, 0.25)):
                g.add(Circle(radius=rr, stroke_width=0, fill_color="#9FA3B2", fill_opacity=a).move_to(b.C + v(x + 1.4 * sway, y)))
            g.add(Circle(radius=2.6, stroke_color="#FFD640", stroke_width=8, stroke_opacity=a * (0.35 + 0.65 * abs(math.sin(t * 1.6))), fill_opacity=0).move_to(b.C))
            return g
        b.live(wob, b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "A SMALL WOBBLE", "एक हल्की डगमगाहट"), 62, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "LIBRATION: PEEK AROUND THE EDGE", "लिब्रेशन: किनारे के पार झलक"), v(0, -3.9), ORANGE, 7.4, 28, -2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.live(lambda a: astro(b.C + v(0, -0.6), 1.9, hl=(-0.95, -0.6 + 0.25 * math.sin(ctx.elapsed() * 3)), hr=(0.95, -0.6 - 0.25 * math.sin(ctx.elapsed() * 3)), mouth=0.4, blink=0.1 if (ctx.elapsed() % 2.4) < 0.12 else 1.0, a=a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "WHICH SIDE\nWOULD YOU VISIT?", "आप कौन-सा हिस्सा\nदेखना चाहेंगे?"), 60, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "NEAR SIDE", "सामने वाला"), v(-2.6, 2.2), BLUE, 3.6, 36, -3.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "FAR SIDE", "पीछे वाला"), v(2.6, 2.2), ORANGE, 3.6, 36, 3.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.4, 36, -1.5, t=b.t0 + 1.9)
    beat0(B[0])
    beat1(B[1])
