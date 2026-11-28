"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): GPS signals are blocked at the roof of a building; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def building(b, a_floor=3, y0=-4.2, floor_h=1.7, w=5.6, xc=0.0):
    for i in range(a_floor):
        b.put(Rectangle(width=w, height=floor_h, stroke_color=INK, stroke_width=4, fill_color="#46506B" if i % 2 == 0 else "#515B78", fill_opacity=1).move_to(b.C + v(xc, y0 + floor_h * (i + 0.5))), b.t0 + 0.1, z=4, pop=0)
    b.put(Polygon(v(-w / 2 - 0.3, 0), v(w / 2 + 0.3, 0), v(w / 2, 0.45), v(-w / 2, 0.45), stroke_color=INK, stroke_width=4, fill_color="#2B3350", fill_opacity=1).move_to(b.C + v(xc, y0 + floor_h * a_floor + 0.22)), b.t0 + 0.1, z=4, pop=0)


def phone_dot(C, a, s=1.0):
    return VGroup(Circle(radius=0.32 * s, stroke_color=W_, stroke_width=3, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(C))


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=3)
        building(b)
        sat = b.C + v(2.8, 2.9)
        b.put(RoundedRectangle(corner_radius=0.12, width=0.9, height=0.6, stroke_color=INK, stroke_width=4, fill_color="#D9DDE6", fill_opacity=1).move_to(sat), b.t0 + 0.2, z=6)
        b.put(Rectangle(width=1.1, height=0.4, stroke_color=INK, stroke_width=3, fill_color="#3A66C4", fill_opacity=1).move_to(sat + v(-1.1, 0)), b.t0 + 0.2, z=6)
        b.put(Rectangle(width=1.1, height=0.4, stroke_color=INK, stroke_width=3, fill_color="#3A66C4", fill_opacity=1).move_to(sat + v(1.1, 0)), b.t0 + 0.2, z=6)

        def beam(a):
            t = (ctx.elapsed() - b.t0) % 1.2 / 1.2
            P = sat + v(-0.2, -0.5)
            Q = b.C + v(0.2, -0.45)
            return VGroup(Line(P, Q, color=ORANGE, stroke_width=6, stroke_opacity=a * 0.7), Circle(radius=0.14, stroke_width=0, fill_color=ORANGE, fill_opacity=a).move_to(P + (Q - P) * min(1.0, t * 1.1)))
        b.live(beam, b.t0 + 0.4, z=5)
        b.text("X", 110, v(0.2, -0.2), RED, 2.0, t=b.t0 + 1.2, z=8)
        b.live(lambda a: phone_dot(b.C + v(0, -3.1), a), b.t0 + 0.3, z=7)
        b.text(vox.L(ctx, "GPS CAN'T\nSEE INSIDE", "GPS अंदर\nनहीं देख पाता"), 64, v(0, 4.1), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "THE ROOF BLOCKS IT", "छत उसे रोकती है"), v(0, -4.5), RED, 6.0, 32, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=5)
        b.live(lambda a: astro(b.C + v(-2.4, -1.0), 1.5, hr=(1.0, 0.6 + 0.12 * math.sin(ctx.elapsed() * 6)), look=(1, 0), mouth=0.3, a=a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("WI-FI", "वाई-फ़ाई", BLUE, v(1.6, 3.0), -2.5), ("BEACONS AND TOWERS", "बीकन और टावर", ORANGE, v(1.6, 1.2), 2.5), ("PHONE SERIES, PART 4", "फ़ोन सीरीज़, भाग 4", RED, v(1.6, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.0, 28, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
