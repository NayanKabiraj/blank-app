"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): ions travel through the battery's fluid to make power; in the cold the fluid thickens and they crawl."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def battery(C, a, cold):
    col = "#BFE4F7" if cold else "#F6D77E"
    return VGroup(RoundedRectangle(corner_radius=0.3, width=8.0, height=3.2, stroke_color=W_, stroke_width=5, stroke_opacity=a, fill_color=col, fill_opacity=a * 0.9).move_to(C),
                  Rectangle(width=0.9, height=3.2, stroke_width=0, fill_color="#2E86D6", fill_opacity=a).move_to(C + v(-3.55, 0)), Rectangle(width=0.9, height=3.2, stroke_width=0, fill_color="#E2423C", fill_opacity=a).move_to(C + v(3.55, 0)))


def ions(C, t, a, speed, n=9, cold=False):
    g = VGroup()
    for k in range(n):
        f = (t * speed + k / n) % 1.0
        wob = 0.12 * math.sin(t * (3 if not cold else 9) + k) if cold else 0.05 * math.sin(t * 3 + k)
        g.add(Circle(radius=0.17, stroke_color=INK, stroke_width=2, stroke_opacity=a, fill_color="#FFFFFF" if cold else "#2E86D6", fill_opacity=a).move_to(C + v(-2.7 + 5.4 * f, -1.0 + 0.5 * math.sin(k * 1.9) + wob)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B2A4A", "#4A7FA8", seed=11)
        C = b.C + v(0, -0.2)
        b.live(lambda a: battery(C, a, False), b.t0 + 0.2, z=4)
        b.live(lambda a: ions(C, ctx.elapsed() - b.t0, a, 0.55), b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "INSIDE THE BATTERY", "बैटरी के अंदर"), 62, v(0, 3.6), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "TINY PARTICLES TRAVEL = POWER", "छोटे कण चलते हैं = बिजली"), v(0, -3.0), BLUE, 7.2, 28, -2.0, t=b.t0 + 1.6)

    def beat1(b):
        b.backdrop("#0B2A4A", "#4A7FA8", seed=13)
        C = b.C + v(0, -0.2)
        b.live(lambda a: battery(C, a, True), b.t0 + 0.2, z=4)
        b.live(lambda a: ions(C, ctx.elapsed() - b.t0, a, 0.12, cold=True), b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "COLD THICKENS\nTHE FLUID", "ठंड से द्रव\nगाढ़ा हो जाता है"), 56, v(0, 3.7), W_, 7.6, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "SLOW PARTICLES", "धीमे कण"), v(0, -3.0), RED, 5.2, 36, 2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
