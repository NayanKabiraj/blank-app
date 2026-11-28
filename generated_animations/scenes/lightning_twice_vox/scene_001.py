"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): a tower under a storm cloud is struck again and again; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def tower(C, a, h=5.0):
    return VGroup(Polygon(C + v(-0.7, 0), C + v(0.7, 0), C + v(0.45, h), C + v(-0.45, h), stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#5B6788", fill_opacity=a),
                  Line(C + v(0, h), C + v(0, h + 0.9), color=INK, stroke_width=6, stroke_opacity=a))


def bolt(top, bottom, a, seed=0):
    pts = [top]
    n = 6
    for i in range(1, n):
        f = i / n
        pts.append(top + (bottom - top) * f + v(0.35 * math.sin(seed * 3.1 + i * 2.3), 0))
    pts.append(bottom)
    g = VGroup()
    for p, q in zip(pts[:-1], pts[1:]):
        g.add(Line(p, q, color="#FFE45C", stroke_width=11, stroke_opacity=a), Line(p, q, color="#FFFFFF", stroke_width=4, stroke_opacity=a))
    return g


def cloud(C, a, w=7.0):
    g = VGroup()
    for k, (x, y, r) in enumerate(((-2.2, 0, 0.9), (-0.8, 0.5, 1.1), (0.8, 0.45, 1.2), (2.2, 0, 0.9), (0, -0.2, 1.2))):
        g.add(Circle(radius=r, stroke_width=0, fill_color="#3A4468", fill_opacity=a).move_to(C + v(x, y)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=3)
        b.put(Rectangle(width=9.4, height=1.4, stroke_width=0, fill_color="#1B2238", fill_opacity=1).move_to(b.C + v(0, -4.5)), b.t0 + 0.1, z=3, pop=0)
        b.live(lambda a: cloud(b.C + v(0, 2.8), a), b.t0 + 0.1, z=4)
        b.live(lambda a: tower(b.C + v(0, -3.8), a, 3.4), b.t0 + 0.2, z=5)

        def flash(a):
            t = (ctx.elapsed() - b.t0) % 1.4
            on = 1.0 if t < 0.3 else 0.0
            return bolt(b.C + v(0.1, 2.6), b.C + v(0, 2.2 - 0.0), a * on, int((ctx.elapsed() - b.t0) / 1.4)) if on else VGroup()
        b.live(lambda a: bolt(b.C + v(0.2, 2.0), b.C + v(0, 0.55), a * (1.0 if (ctx.elapsed() - b.t0) % 1.4 < 0.3 else 0.0), int((ctx.elapsed() - b.t0) / 1.4)), b.t0 + 0.8, z=7)
        b.text(vox.L(ctx, "NEVER STRIKES\nTWICE?", "कभी दो बार\nनहीं गिरती?"), 66, v(0, 4.6), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "EVERYONE SAYS IT", "सब यही कहते हैं"), v(0, -1.0), ORANGE, 6.0, 38, -2.0, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#0B0F1E", "#2B3555", seed=5)
        b.live(lambda a: tower(b.C + v(-2.4, -3.2), a, 4.0), b.t0 + 0.2, z=5)
        for k, (en, hi, col, p, r) in enumerate((("THE MYTH", "मिथक", RED, v(1.8, 3.0), -2.5), ("TALL TOWERS", "ऊँचे टॉवर", ORANGE, v(1.8, 1.2), 2.5), ("MYTH SERIES, PART 2", "मिथक सीरीज़, भाग 2", BLUE, v(1.8, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.0, 28, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
