"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): the ground stops but the air keeps moving; winds rush on and the ocean surges over the land."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#10224A", "#3A6AA0", seed=11)
        gy = -2.0
        b.put(Rectangle(width=9.4, height=2.2, stroke_color=INK, stroke_width=4, fill_color="#7A5A3A", fill_opacity=1).move_to(b.C + v(0, gy - 1.1)), b.t0 + 0.1, z=4, pop=0)

        def air(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for k in range(16):
                x = -4.4 + ((k * 1.7 + t * 3.0) % 9.0)
                g.add(Circle(radius=0.11, stroke_width=0, fill_color="#DFF3FF", fill_opacity=a * 0.9).move_to(b.C + v(x, 0.3 + 0.35 * (k % 5))))
                g.add(Line(b.C + v(x - 0.5, 0.3 + 0.35 * (k % 5)), b.C + v(x, 0.3 + 0.35 * (k % 5)), color="#DFF3FF", stroke_width=3, stroke_opacity=a * 0.5))
            return g
        b.live(air, b.t0 + 0.2, z=6)

        def house(a):
            t = ctx.elapsed() - b.t0
            x = -3.0 + (0.0 if t > 1.6 else 0.0)
            return VGroup(Rectangle(width=1.5, height=1.2, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#C9A27A", fill_opacity=a).move_to(b.C + v(x, gy + 0.6)),
                          Polygon(v(-0.95, 0), v(0.95, 0), v(0, 0.8), stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#B5483C", fill_opacity=a).move_to(b.C + v(x, gy + 1.6)))
        b.live(house, b.t0 + 0.1, z=5)
        b.text(vox.L(ctx, "THE GROUND STOPS.\nTHE AIR DOES NOT.", "ज़मीन रुकती है।\nहवा नहीं।"), 52, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "INERTIA", "जड़त्व"), v(0, -4.3), ORANGE, 4.0, 40, -2.0, t=b.t0 + 2.0)

    def beat1(b):
        b.backdrop("#10224A", "#3A6AA0", seed=13)
        b.put(Rectangle(width=9.4, height=2.4, stroke_color=INK, stroke_width=4, fill_color="#C9A27A", fill_opacity=1).move_to(b.C + v(0, -3.6)), b.t0 + 0.1, z=4, pop=0)

        def sea(a):
            k = b.lv(b.t0 + 0.8, 2.2)
            h = 0.4 + 3.0 * k
            pts = [b.C + v(-4.7 + 9.4 * i / 24 * (0.45 + 0.55 * k), -2.4 + h * (0.6 + 0.4 * math.sin(i * 0.7 + ctx.elapsed() * 4))) for i in range(25)]
            body = Polygon(*pts, b.C + v(-4.7 + 9.4 * (0.45 + 0.55 * k), -2.4), b.C + v(-4.7, -2.4), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a)
            return body
        b.live(sea, b.t0 + 0.3, z=5)

        def wind(a):
            t = ctx.elapsed() - b.t0
            return VGroup(*[Line(b.C + v(-4.4 + ((k * 2.1 + t * 7.0) % 9.4), 3.4 - 0.55 * k), b.C + v(-4.4 + ((k * 2.1 + t * 7.0) % 9.4) + 1.4, 3.4 - 0.55 * k), color="#FFFFFF", stroke_width=7, stroke_opacity=a * 0.85) for k in range(6)])
        b.live(wind, b.t0 + 0.4, z=7)
        b.tape(vox.L(ctx, "VIOLENT WINDS", "भयानक हवाएँ"), v(0, 4.4), RED, 5.0, 38, -2.0, t=b.t0 + 0.6)
        b.tape(vox.L(ctx, "OCEANS SURGE OVER LAND", "समुद्र ज़मीन पर चढ़ते हैं"), v(0, -4.4), BLUE, 7.2, 32, 2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
