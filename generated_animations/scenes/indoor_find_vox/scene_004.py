"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): indoors it is signals and sensors, not satellites; the closing question."""
from __future__ import annotations

from manim import Arc

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0F2A44", "#1F5C7A", seed=31)
        C = b.C + v(0, 0.2)

        def pulse(a):
            t = ctx.elapsed() - b.t0
            g = VGroup(Circle(radius=0.55, stroke_color=W_, stroke_width=5, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(C))
            for k in range(3):
                ph = ((t * 0.7) + k / 3) % 1.0
                g.add(Circle(radius=0.6 + 2.8 * ph, stroke_color="#8EC9F0", stroke_width=6, stroke_opacity=a * (1 - ph), fill_opacity=0).move_to(C))
            return g
        b.live(pulse, b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "SIGNALS\n+ SENSORS", "सिग्नल\n+ सेंसर"), 76, v(0, 3.9), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "NOT SATELLITES", "सैटेलाइट नहीं"), v(0, -3.8), RED, 5.6, 38, -2.0, t=b.t0 + 1.8)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.text(vox.L(ctx, "WHICH CLUE\nSURPRISED YOU?", "कौन-सा सुराग़\nअजीब लगा?"), 62, v(0, 3.9), W_, 7.8, t=b.t0 + 0.3)
        for k, (en, hi, col, p, r) in enumerate((("WI-FI", "वाई-फ़ाई", BLUE, v(-2.4, 1.4), -3.0), ("BEACONS", "बीकन", GREEN, v(2.4, 1.4), 3.0), ("TOWERS", "टावर", ORANGE, v(-2.4, -0.4), 2.0), ("BAROMETER", "बैरोमीटर", RED, v(2.4, -0.4), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.0, 30, r, t=b.t0 + 0.8 + 0.4 * k)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.0), RED, 5.4, 36, -1.5, t=b.t0 + 2.6)
    beat0(B[0])
    beat1(B[1])
