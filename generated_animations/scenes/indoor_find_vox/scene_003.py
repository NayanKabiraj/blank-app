"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): a barometer needle drops as the person climbs floors; every clue blends into one blue dot."""
from __future__ import annotations

from manim import Arc

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=21)
        for i in range(3):
            b.put(Rectangle(width=3.4, height=1.5, stroke_color=INK, stroke_width=4, fill_color="#46506B" if i % 2 == 0 else "#515B78", fill_opacity=1).move_to(b.C + v(-2.4, -3.6 + 1.5 * (i + 0.5))), b.t0 + 0.1, z=4, pop=0)

        def climber(a):
            k = b.lv(b.t0 + 0.6, 2.6)
            y = -3.6 + 0.75 + 3.0 * k
            return VGroup(Circle(radius=0.3, stroke_color=W_, stroke_width=3, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(b.C + v(-2.4, y)))
        b.live(climber, b.t0 + 0.3, z=7)
        G = b.C + v(2.4, 0.2)

        def gauge(a):
            k = b.lv(b.t0 + 0.6, 2.6)
            ang = math.pi * (0.85 - 0.7 * k)
            return VGroup(Arc(radius=1.7, start_angle=0, angle=math.pi, arc_center=G, stroke_color=W_, stroke_width=8, stroke_opacity=a),
                          Line(G, G + v(1.5 * math.cos(ang), 1.5 * math.sin(ang)), color=RED, stroke_width=9, stroke_opacity=a), Circle(radius=0.16, stroke_width=0, fill_color=W_, fill_opacity=a).move_to(G))
        b.live(gauge, b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "CLUE 3: BAROMETER", "सुराग़ 3: बैरोमीटर"), 56, v(0, 4.1), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "HIGHER = LESS PRESSURE", "ऊपर = कम दबाव"), v(0, -4.4), ORANGE, 6.4, 32, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=23)
        D = b.C + v(0, -0.8)
        icons = [(v(-2.8, 3.0), "#2E86D6", vox.L(ctx, "WI-FI", "वाई-फ़ाई")), (v(2.8, 3.0), "#5E9A5A", vox.L(ctx, "BEACON", "बीकन")), (v(-2.8, 0.2), "#F08A3C", vox.L(ctx, "TOWER", "टावर")), (v(2.8, 0.2), "#E2423C", vox.L(ctx, "BAROMETER", "बैरोमीटर"))]
        for i, (p, col, s) in enumerate(icons):
            b.put(RoundedRectangle(corner_radius=0.25, width=2.5, height=0.95, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=0.97).move_to(b.C + p), b.t0 + 0.3 + 0.35 * i, z=5)
            b.text(s, 28, p, W_, 2.3, t=b.t0 + 0.35 + 0.35 * i, z=7)

        def converge(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for i, (p, col, s) in enumerate(icons):
                f = ((t * 0.6) + i * 0.25) % 1.0
                P = b.C + p * (1 - f) + D * f
                g.add(Circle(radius=0.14, stroke_width=0, fill_color=YEL, fill_opacity=a).move_to(P))
            return g
        b.live(converge, b.t0 + 1.4, z=8)
        b.put(Circle(radius=0.5, stroke_color=W_, stroke_width=5, fill_color="#2E86D6", fill_opacity=1).move_to(D), b.t0 + 1.2, z=9, pop=0.3)
        b.text(vox.L(ctx, "ONE BEST GUESS", "एक सबसे अच्छा अंदाज़ा"), 54, v(0, 4.3), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "THE BLUE DOT", "नीला डॉट"), v(0, -3.4), RED, 4.6, 40, -2.0, t=b.t0 + 2.4)
    beat0(B[0])
    beat1(B[1])
