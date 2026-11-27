"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): the Moon we always see, with a mysterious hidden other side; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"
CRATERS = [(-0.8, 0.9, 0.5), (0.7, 0.5, 0.35), (-0.2, -0.7, 0.6), (1.0, -0.9, 0.3), (-1.4, -0.3, 0.25), (0.2, 1.5, 0.22)]


def moon(C, r, a, craters=True):
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#C9CCD6", fill_opacity=a).move_to(C))
    for x, y, rr in CRATERS:
        g.add(Circle(radius=rr * r / 2.6, stroke_width=0, fill_color="#9FA3B2", fill_opacity=a if craters else 0).move_to(C + v(x * r / 2.6, y * r / 2.6)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#1D2A55", seed=3)
        b.live(lambda a: VGroup(Circle(radius=2.6, stroke_color="#5A6AA0", stroke_width=5, stroke_opacity=a * 0.7, fill_color="#10183A", fill_opacity=a * 0.9).move_to(b.C + v(1.4, 0.2))), b.t0 + 0.2, z=4)
        b.live(lambda a: moon(b.C + v(-0.6, -0.2), 2.6, a), b.t0 + 0.2, z=6)
        b.text("?", 170, v(2.3, 0.3), "#FFD640", 2.5, t=b.t0 + 2.4, z=7)
        b.text(vox.L(ctx, "THE MOON'S\nOTHER SIDE", "चाँद का\nदूसरा हिस्सा"), 66, v(0, 3.9), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "NEVER SEEN FROM EARTH", "पृथ्वी से कभी नहीं दिखा"), v(0, -3.9), RED, 6.8, 34, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#070D22", "#1D2A55", seed=5)
        b.live(lambda a: astro(b.C + v(-2.2, -1.0), 1.6, hr=(1.0, 0.7 + 0.14 * math.sin(ctx.elapsed() * 6)), look=(1, 0), mouth=0.3, a=a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("WHY ONE FACE", "एक ही चेहरा क्यों", BLUE, v(1.5, 3.0), -2.5), ("HOW EARTH LOCKED IT", "पृथ्वी ने कैसे बाँधा", ORANGE, v(1.5, 1.2), 2.5), ("PART 2: SPACE SERIES", "भाग 2: अंतरिक्ष सीरीज़", RED, v(1.5, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.2, 28, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
