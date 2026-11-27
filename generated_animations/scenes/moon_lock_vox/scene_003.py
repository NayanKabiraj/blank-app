"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): Earth's pull stretches a bulge in the Moon and acts as a brake until the spin matches the orbit."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#241B4A", seed=21)
        b.put(Circle(radius=1.5, stroke_color=INK, stroke_width=4, fill_color="#2E86D6", fill_opacity=1).move_to(b.C + v(-2.7, 0.0)), b.t0 + 0.2, z=5)

        def bulgemoon(a):
            k = b.lv(b.t0 + 1.0, 1.4)
            return VGroup(Ellipse(width=2.2 + 1.3 * k, height=2.2 - 0.3 * k, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#C9CCD6", fill_opacity=a).move_to(b.C + v(2.6 - 0.35 * k, 0.0)))
        b.live(bulgemoon, b.t0 + 0.2, z=6)

        def pull(a):
            t = ctx.elapsed() - b.t0
            return VGroup(*[Line(b.C + v(0.5 + 0.12 * math.sin(t * 5 + i), -0.6 + 0.6 * i), b.C + v(-0.9, -0.6 + 0.6 * i), color=ORANGE, stroke_width=8, stroke_opacity=a * (0.5 + 0.5 * math.sin(t * 4 + i) ** 2)) for i in range(3)])
        b.live(pull, b.t0 + 0.8, z=7)
        b.text(vox.L(ctx, "EARTH'S PULL\nSTRETCHES THE MOON", "पृथ्वी का खिंचाव\nचाँद को खींचता है"), 54, v(0, 3.9), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "A TIDAL BULGE", "ज्वारीय उभार"), v(0, -3.9), ORANGE, 5.0, 36, -2.0, t=b.t0 + 2.0)

    def beat1(b):
        b.backdrop("#070D22", "#241B4A", seed=23)
        b.text(vox.L(ctx, "THE BRAKE", "ब्रेक"), 74, v(0, 4.1), W_, 6.0, t=b.t0 + 0.2)

        def bars(a):
            k = b.lv(b.t0 + 0.6, 2.6)
            spin = 4.6 * (1 - 0.78 * k)
            return VGroup(Rectangle(width=2.0, height=max(0.05, spin), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=RED, fill_opacity=a).move_to(b.C + v(-1.8, -3.2 + spin / 2)),
                          Rectangle(width=2.0, height=1.0, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(b.C + v(1.8, -3.2 + 0.5)))
        b.live(bars, b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "SPIN", "घूमाई"), 40, v(-1.8, -3.9), W_, 3.0, t=b.t0 + 0.6)
        b.text(vox.L(ctx, "ORBIT", "परिक्रमा"), 40, v(1.8, -3.9), W_, 3.0, t=b.t0 + 0.6)
        b.tape(vox.L(ctx, "MATCHED = LOCKED", "बराबर = बँधा हुआ"), v(0, 1.6), GREEN, 5.8, 38, -2.0, t=b.t0 + 3.0)
    beat0(B[0])
    beat1(B[1])
