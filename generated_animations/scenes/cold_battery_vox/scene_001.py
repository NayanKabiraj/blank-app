"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): a phone at 30% in the snow that then dies; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def snow(b, a, n=26):
    t = ctx_t = b.ctx.elapsed()
    g = VGroup()
    for k in range(n):
        x = -4.2 + (k * 1.93) % 8.4
        y = 4.8 - ((t * (0.9 + 0.05 * (k % 5)) + k * 0.7) % 9.6)
        g.add(Circle(radius=0.06 + 0.03 * (k % 3), stroke_width=0, fill_color="#FFFFFF", fill_opacity=a * 0.9).move_to(b.C + v(x, y)))
    return g


def cold_phone(C, s, pct, dead, a):
    g = VGroup(RoundedRectangle(corner_radius=0.4 * s, width=3.4 * s, height=6.0 * s, stroke_color=W_, stroke_width=4, stroke_opacity=a, fill_color="#10131C", fill_opacity=a).move_to(C),
               RoundedRectangle(corner_radius=0.28 * s, width=3.0 * s, height=5.6 * s, stroke_width=0, fill_color="#0A0C12" if dead else "#DCEAF5", fill_opacity=a).move_to(C))
    g.add(RoundedRectangle(corner_radius=0.12 * s, width=1.3 * s, height=0.6 * s, stroke_color="#222222" if not dead else "#444A5C", stroke_width=4, stroke_opacity=a, fill_color="#0A0C12" if dead else "#FFFFFF", fill_opacity=a).move_to(C + v(0, 1.4 * s)))
    g.add(Rectangle(width=max(0.02, 1.1 * s * pct), height=0.44 * s, stroke_width=0, fill_color="#444A5C" if dead else "#E2423C", fill_opacity=a).move_to(C + v((-0.55 + 0.55 * pct) * s, 1.4 * s)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B2A4A", "#6FA8CE", seed=3)
        b.live(lambda a: snow(b, a), b.t0 + 0.1, z=3)
        b.live(lambda a: cold_phone(b.C + v(0, -1.0), 0.95, 0.3, (ctx.elapsed() - b.t0) > 2.6, a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "30% ... THEN DEAD", "30% ... फिर बंद"), 64, v(0, 3.9), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "IN THE COLD", "ठंड में"), v(0, -4.0), BLUE, 4.6, 40, -2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.backdrop("#0B2A4A", "#6FA8CE", seed=5)
        b.live(lambda a: snow(b, a), b.t0 + 0.1, z=3)
        b.live(lambda a: cold_phone(b.C + v(-2.3, -0.4), 0.7, 0.3, False, a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("WHY COLD KILLS BATTERIES", "ठंड बैटरी क्यों मारती है", BLUE, v(1.4, 3.0), -2.5), ("HOW TO BRING IT BACK", "इसे वापस कैसे लाएँ", ORANGE, v(1.4, 1.2), 2.5), ("PHONE SERIES, PART 3", "फ़ोन सीरीज़, भाग 3", RED, v(1.4, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.2, 26, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
