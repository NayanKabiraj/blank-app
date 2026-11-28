"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): with no spin one sunrise takes about a year; half the planet in months of daylight, half in months of dark."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#241B4A", seed=21)
        sun = b.C + v(-3.0, 0.4)
        b.put(Circle(radius=1.0, stroke_color="#FFB300", stroke_width=5, fill_color="#FFD640", fill_opacity=1).move_to(sun), b.t0 + 0.2, z=5)
        E = b.C + v(1.2, 0.4)
        b.put(Circle(radius=1.6, stroke_color=INK, stroke_width=5, fill_color="#0B1F3A", fill_opacity=1).move_to(E), b.t0 + 0.2, z=5)
        b.put(Circle(radius=1.6, stroke_width=0, fill_color="#2E86D6", fill_opacity=0.0).move_to(E), b.t0 + 0.2, z=5, pop=0)

        def lit(a):
            return VGroup(Polygon(*[E + v(1.6 * math.cos(math.pi / 2 + math.pi * i / 20), 1.6 * math.sin(math.pi / 2 + math.pi * i / 20)) for i in range(21)], stroke_width=0, fill_color="#2E86D6", fill_opacity=a))
        b.live(lambda a: VGroup(Polygon(*[E + v(-1.6 * math.sin(math.pi * i / 20), 1.6 * math.cos(math.pi * i / 20)) for i in range(21)], stroke_width=0, fill_color="#2E86D6", fill_opacity=a)), b.t0 + 0.3, z=6)
        b.live(lambda a: Circle(radius=0.14, stroke_width=0, fill_color="#E2423C", fill_opacity=a).move_to(E + v(-1.2, 0.0)), b.t0 + 0.3, z=7)

        def count(a):
            t = ctx.elapsed() - b.t0
            return VGroup(*[Rectangle(width=0.05, height=0.7, stroke_width=0, fill_color="#FFD640", fill_opacity=a * (1 if k < int(min(1, t / 3.4) * 24) else 0.2)).move_to(b.C + v(-3.0 + 0.27 * k, -3.2)) for k in range(24)])
        b.live(count, b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "ONE SUNRISE =\nABOUT A YEAR", "एक सूर्योदय =\nलगभग एक साल"), 58, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "ONE DAY, ONE ORBIT", "एक दिन, एक परिक्रमा"), v(0, -4.3), ORANGE, 6.0, 32, -2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.backdrop("#070D22", "#241B4A", seed=23)
        C = b.C + v(0, 0.2)
        b.put(Polygon(*[C + v(2.6 * math.cos(math.pi / 2 + math.pi * i / 24), 2.6 * math.sin(math.pi / 2 + math.pi * i / 24)) for i in range(25)], stroke_color=INK, stroke_width=4, fill_color="#FFB300", fill_opacity=1), b.t0 + 0.2, z=5)
        b.put(Polygon(*[C + v(2.6 * math.cos(-math.pi / 2 + math.pi * i / 24), 2.6 * math.sin(-math.pi / 2 + math.pi * i / 24)) for i in range(25)], stroke_color=INK, stroke_width=4, fill_color="#10224A", fill_opacity=1), b.t0 + 0.2, z=5)
        b.tape(vox.L(ctx, "MONTHS OF DAYLIGHT", "महीनों की धूप"), v(-1.5, 1.4), RED, 4.6, 30, -3.0, t=b.t0 + 0.7)
        b.tape(vox.L(ctx, "MONTHS OF DARKNESS", "महीनों का अँधेरा"), v(1.5, -1.2), BLUE, 4.6, 30, 3.0, t=b.t0 + 1.5)
        b.text(vox.L(ctx, "TWO HALVES", "दो हिस्से"), 70, v(0, 4.2), W_, 6.0, t=b.t0 + 0.3)
    beat0(B[0])
    beat1(B[1])
