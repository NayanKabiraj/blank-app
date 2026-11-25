"""Vox look - shot 2 (scenes 3-4): the infrared LED flashes invisible light; it bounces off the cheek into the sensor and the bounce meter fills."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=7)
        ph = phone(1.5).move_to(b.C + v(-1.8, 0.0))
        b.put(ph, b.t0 + 0.1, z=4, pop=0.2)
        led = Circle(radius=0.14, stroke_color=INK, stroke_width=3, fill_color=PINK, fill_opacity=1).move_to(b.C + v(-1.5, 1.05))
        b.put(led, b.t0 + 0.5, z=7, pop=0.4)
        # flashing, invisible (dashed, pale pink) rays fan out from the LED, pulsing several times
        def rays(a):
            f = max(0.0, math.sin(ctx.elapsed() * 7.0))
            g = VGroup()
            for k in range(5):
                an = math.radians(10 + 22 * k)
                g.add(Line(b.C + v(-1.35, 1.05), b.C + v(-1.35 + 3.8 * math.cos(an), 1.05 + 3.0 * math.sin(an)), color=PINK, stroke_width=4, stroke_opacity=a * f * 0.9))
            return g
        b.live(rays, b.t0 + 0.8, z=5)
        b.tape(vox.L(ctx, "INFRARED LED", "इन्फ्रारेड LED"), v(1.3, 2.1), PINK, 3.6, 30, 2.0, t=b.t0 + 0.7)
        b.tape(vox.L(ctx, "YOU CAN'T SEE IT", "आँखों को नहीं दिखती"), v(1.0, -2.2), BLUE, 4.6, 26, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.card(seed=9, rot=0.6)
        ph = phone(1.3).move_to(b.C + v(-2.0, 0.0))
        b.put(ph, b.t0 + 0.1, z=4, pop=0.2)
        cheek = vox.cutout(Circle(radius=1.05, stroke_color=INK, stroke_width=4, fill_color="#F2C9A0", fill_opacity=1), 6.0).move_to(b.C + v(1.7, 0.2))
        b.put(cheek, b.t0 + 0.2, z=4, pop=0.2)

        def light(a):                                         # a pulse travels out to the cheek and a stronger one comes back to the sensor
            f = (ctx.elapsed() * 0.9) % 1.0
            out = b.C + v(-1.5 + 2.3 * min(1.0, f * 2.0), 0.7)
            back = b.C + v(0.8 - 2.3 * max(0.0, f * 2.0 - 1.0), 0.7)
            g = VGroup(Circle(radius=0.11, stroke_width=0, fill_color=PINK, fill_opacity=a * (1.0 if f < 0.5 else 0.0)).move_to(out),
                       Circle(radius=0.17, stroke_width=0, fill_color=RED, fill_opacity=a * (1.0 if f >= 0.5 else 0.0)).move_to(back))
            return g
        b.live(light, b.t0 + 0.6, z=7)
        b.live(lambda a: Line(b.C + v(-1.5, 0.7), b.C + v(0.8, 0.7), color=PINK, stroke_width=3, stroke_opacity=0.5 * a), b.t0 + 0.4, z=5)
        # the bounce meter fills while the pulse returns
        def meter(a):
            w = 3.2 * ease(level(ctx, b.t0 + 1.2, 2.5))
            return VGroup(Rectangle(width=3.2, height=0.45, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_opacity=0).move_to(b.C + v(0, -1.9)),
                          Rectangle(width=max(0.02, w), height=0.33, stroke_width=0, fill_color=RED, fill_opacity=a).move_to(b.C + v(-1.6 + max(0.02, w) / 2, -1.9)))
        b.live(meter, b.t0 + 1.0, z=6)
        b.text(vox.L(ctx, "STRONG BOUNCE = VERY CLOSE", "तेज़ टक्कर = बहुत पास"), 26, v(0, -2.6), INK, 5.8, t=b.t0 + 1.4)
    beat0(B[0])
    beat1(B[1])
