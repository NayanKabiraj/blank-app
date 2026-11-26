"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): radio waves (a kind of light) cross the empty gap between two astronauts; inside the suit voice -> air -> mic -> radio."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *


def wave(C, t, a, x0=-1.7, x1=1.7, amp=0.7):
    pts = []
    for k in range(41):
        x = x0 + (x1 - x0) * k / 40
        env = math.sin(math.pi * k / 40) ** 0.6
        pts.append(C + v(x, amp * env * math.sin(7.0 * x - 9.0 * t)))
    return VGroup(*[Line(p, q, color=ORANGE, stroke_width=10, stroke_opacity=a) for p, q in zip(pts[:-1], pts[1:])])


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    W_ = "#FFFFFF"

    def beat0(b):
        b.backdrop("#070D22", "#241B4A", seed=21)
        b.live(lambda a: astro(b.C + v(-3.0, -0.9), 1.25, hr=(0.95, 0.35), look=(1, 0), mouth=0.4, a=a), b.t0 + 0.1, z=6)
        b.live(lambda a: astro(b.C + v(3.0, -0.9), 1.25, hl=(-0.95, 0.35), look=(-1, 0), mouth=0.2, a=a), b.t0 + 0.2, z=6)
        b.live(lambda a: wave(b.C + v(0, 0.0), ctx.elapsed() - b.t0, a), b.t0 + 0.6, z=5)
        b.text(vox.L(ctx, "RADIO", "रेडियो"), 120, v(0, 3.6), W_, 6.0, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "A KIND OF LIGHT:\nIT CROSSES EMPTY SPACE", "एक तरह की रोशनी:\nख़ाली जगह में चलती है"), v(0, -3.5), ORANGE, 7.6, 30, -1.5, t=b.t0 + 2.0)

    def beat1(b):
        b.backdrop("#10224A", "#3B2A66", seed=23)
        nodes = [(vox.L(ctx, "VOICE", "आवाज़"), v(-2.3, 2.3), BLUE), (vox.L(ctx, "AIR", "हवा"), v(2.3, 2.3), GREEN), (vox.L(ctx, "MIC", "माइक"), v(2.3, 0.0), ORANGE), (vox.L(ctx, "RADIO", "रेडियो"), v(-2.3, 0.0), RED)]
        for i, (s, p, col) in enumerate(nodes):
            b.put(RoundedRectangle(corner_radius=0.25, width=3.2, height=1.3, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=0.97).move_to(b.C + p), b.t0 + 0.3 + 0.5 * i, z=5)
            b.text(s, 40, p, "#FFFFFF" if col != GREEN else INK, 2.8, t=b.t0 + 0.35 + 0.5 * i, z=7)
        path = [v(-2.3, 2.3), v(2.3, 2.3), v(2.3, 0.0), v(-2.3, 0.0)]

        def dots(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for k in range(6):
                ph = ((t * 0.5) + k / 6) % 1.0 * 3.0
                seg = min(2, int(ph)); f = ph - seg
                g.add(Circle(radius=0.16, stroke_width=0, fill_color=YEL, fill_opacity=a).move_to(b.C + path[seg] * (1 - f) + path[seg + 1] * f))
            return g
        b.live(dots, b.t0 + 1.2, z=8)
        b.live(lambda a: astro(b.C + v(0, -2.6), 0.85, mouth=0.4, a=a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "INSIDE THE SUIT", "सूट के अंदर"), 68, v(0, 4.0), W_, 7.5, t=b.t0 + 0.2)
    beat0(B[0])
    beat1(B[1])
