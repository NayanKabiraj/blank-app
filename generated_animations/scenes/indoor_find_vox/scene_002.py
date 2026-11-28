"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): a Wi-Fi map from router signal strengths; Bluetooth beacons say 'near', cell towers say 'roughly'."""
from __future__ import annotations

from manim import Arc

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def router(C, a):
    return VGroup(RoundedRectangle(corner_radius=0.1, width=1.0, height=0.36, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#F2F2F2", fill_opacity=a).move_to(C),
                  Line(C + v(-0.3, 0.18), C + v(-0.4, 0.6), color=INK, stroke_width=4, stroke_opacity=a), Line(C + v(0.3, 0.18), C + v(0.4, 0.6), color=INK, stroke_width=4, stroke_opacity=a))


def arcs(C, t, a, col=ORANGE, n=3):
    g = VGroup()
    for k in range(n):
        ph = ((t * 0.8) + k / n) % 1.0
        g.add(Arc(radius=0.4 + 1.8 * ph, start_angle=0.6, angle=1.9, arc_center=C + v(0, 0.2), stroke_color=col, stroke_width=7, stroke_opacity=a * (1 - ph)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=11)
        pos = [v(-2.8, 1.8), v(2.8, 2.2), v(-2.4, -1.6), v(2.6, -1.4)]
        for p in pos:
            b.live(lambda a, p=p: router(b.C + p, a), b.t0 + 0.3, z=6)
            b.live(lambda a, p=p: arcs(b.C + p, ctx.elapsed() - b.t0, a), b.t0 + 0.4, z=5)
        b.put(Circle(radius=0.36, stroke_color=W_, stroke_width=4, fill_color="#2E86D6", fill_opacity=1).move_to(b.C + v(0, 0.2)), b.t0 + 0.4, z=8)
        for p in pos:
            b.live(lambda a, p=p: Line(b.C + v(0, 0.2), b.C + p, color="#FFFFFF", stroke_width=3, stroke_opacity=a * (0.3 + 0.3 * math.sin(ctx.elapsed() * 5) ** 2)), b.t0 + 0.8, z=4)
        b.text(vox.L(ctx, "CLUE 1: WI-FI", "सुराग़ 1: वाई-फ़ाई"), 62, v(0, 4.1), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "SIGNAL STRENGTH = A MAP", "सिग्नल की ताक़त = नक्शा"), v(0, -4.1), ORANGE, 7.2, 30, -2.0, t=b.t0 + 2.0)

    def beat1(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=13)
        b.text(vox.L(ctx, "CLUE 2", "सुराग़ 2"), 66, v(0, 4.2), W_, 6.0, t=b.t0 + 0.2)
        for sx, en, hi, col in ((-2.3, "BEACON: NEAR", "बीकन: पास", BLUE), (2.3, "TOWER: ROUGHLY", "टावर: मोटा अंदाज़ा", ORANGE)):
            C = b.C + v(sx, 0.6)
            if sx < 0:
                b.live(lambda a, C=C: VGroup(Circle(radius=0.26, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#5E9A5A", fill_opacity=a).move_to(C), arcs(C, ctx.elapsed() - b.t0, a, "#5E9A5A", 3)), b.t0 + 0.3, z=6)
            else:
                b.live(lambda a, C=C: VGroup(Polygon(C + v(-0.5, -1.0), C + v(0.5, -1.0), C + v(0, 1.2), stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#C9CCD6", fill_opacity=a), arcs(C + v(0, 1.0), ctx.elapsed() - b.t0, a, ORANGE, 3)), b.t0 + 0.3, z=6)
            b.tape(vox.L(ctx, en, hi), v(sx, -2.0), col, 3.9, 28, -2.0 if sx < 0 else 2.0, t=b.t0 + 1.0)
        b.put(Circle(radius=0.32, stroke_color=W_, stroke_width=4, fill_color="#2E86D6", fill_opacity=1).move_to(b.C + v(0, -3.6)), b.t0 + 0.6, z=8)
    beat0(B[0])
    beat1(B[1])
