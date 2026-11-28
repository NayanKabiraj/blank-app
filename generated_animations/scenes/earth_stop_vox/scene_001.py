"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): the spinning Earth with its equator speed; the episode promise as tape labels."""
from __future__ import annotations

from manim import Arc

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"
BLOBS = [(-0.8, 0.6, 0.9, 0.5), (0.6, 0.9, 0.7, 0.45), (0.3, -0.7, 0.9, 0.6), (-0.9, -0.5, 0.5, 0.4)]


def earth(C, r, a, spin=0.0):
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(C))
    for x, y, w, h in BLOBS:
        ang = math.atan2(y, x) + spin
        d = math.hypot(x, y)
        px, py = d * math.cos(ang), d * math.sin(ang)
        vis = 1.0 if px > -0.2 * 0 + -r * 0.9 else 0.0
        g.add(Ellipse(width=w * r / 2.2, height=h * r / 2.2, stroke_width=0, fill_color="#5E9A5A", fill_opacity=a * 0.95).move_to(C + v(px * r / 2.2, py * r / 2.2)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#1D2A55", seed=3)
        C = b.C + v(0, -0.2)
        b.live(lambda a: earth(C, 2.5, a, (ctx.elapsed() - b.t0) * 0.5), b.t0 + 0.2, z=5)
        b.live(lambda a: VGroup(*[Arc(radius=2.9 + 0.15 * k, start_angle=-0.35, angle=0.7, arc_center=C, stroke_color=ORANGE, stroke_width=9, stroke_opacity=a * (0.35 + 0.65 * ((ctx.elapsed() * 1.2 + k * 0.3) % 1.0))) for k in range(3)]), b.t0 + 0.6, z=6)
        b.text(vox.L(ctx, "THE GROUND\nIS MOVING", "ज़मीन चल रही है"), 64, v(0, 3.9), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "~1,600 KM/H AT THE EQUATOR", "भूमध्य रेखा पर ~1,600 किमी/घं"), v(0, -4.0), ORANGE, 7.4, 30, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#070D22", "#1D2A55", seed=5)
        b.live(lambda a: astro(b.C + v(-2.4, -1.0), 1.6, hr=(1.0, 0.7 + 0.14 * math.sin(ctx.elapsed() * 6)), look=(1, 0), mouth=0.3, a=a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("AIR AND OCEANS", "हवा और समुद्र", BLUE, v(1.5, 3.0), -2.5), ("DAYS", "दिन", ORANGE, v(1.5, 1.2), 2.5), ("SPACE SERIES, PART 3", "अंतरिक्ष सीरीज़, भाग 3", RED, v(1.5, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.2, 28, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
