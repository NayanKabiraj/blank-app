"""Vox look - shot 3 (scenes 5-6): radio waves (a kind of light) cross the empty gap between two astronauts; inside the suit voice -> air -> mic -> radio."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *


def wave(C, t, a, x0=-1.4, x1=1.4, amp=0.45):
    pts = []
    for k in range(41):
        x = x0 + (x1 - x0) * k / 40
        env = math.sin(math.pi * k / 40) ** 0.6
        pts.append(C + v(x, amp * env * math.sin(7.0 * x - 9.0 * t)))
    g = VGroup()
    for p, q in zip(pts[:-1], pts[1:]):
        g.add(Line(p, q, color=ORANGE, stroke_width=7, stroke_opacity=a))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=21)
        for k in range(14):
            b.put(Circle(radius=0.035, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).move_to(b.C + v(-2.8 + (k * 1.31) % 5.6, -2.3 + (k * 1.9) % 4.6)), b.t0 + 0.1, z=3, pop=0)
        b.live(lambda a: astro(b.C + v(-2.3, -0.5), 0.7, hr=(0.95, 0.35), look=(1, 0), mouth=0.4, a=a), b.t0 + 0.1, z=6)
        b.live(lambda a: astro(b.C + v(2.3, -0.5), 0.7, hl=(-0.95, 0.35), look=(-1, 0), mouth=0.2, a=a), b.t0 + 0.2, z=6)
        b.live(lambda a: wave(b.C + v(0, 0.2), ctx.elapsed() - b.t0, a), b.t0 + 0.6, z=5)
        b.text(vox.L(ctx, "RADIO", "रेडियो"), 64, v(0, 2.2), INK, 4.0, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "A KIND OF LIGHT - IT CROSSES EMPTY SPACE", "एक तरह की रोशनी - ख़ाली जगह में चलती है"), v(0, -2.2), ORANGE, 5.6, 22, -1.5, t=b.t0 + 2.0)

    def beat1(b):
        b.card(seed=23, rot=-0.5)
        nodes = [(vox.L(ctx, "VOICE", "आवाज़"), v(-2.1, 1.3), BLUE), (vox.L(ctx, "AIR", "हवा"), v(2.1, 1.3), GREEN), (vox.L(ctx, "MIC", "माइक"), v(2.1, -0.3), ORANGE), (vox.L(ctx, "RADIO", "रेडियो"), v(-2.1, -0.3), RED)]
        for i, (s, p, col) in enumerate(nodes):
            b.put(RoundedRectangle(corner_radius=0.2, width=2.0, height=0.8, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=0.95).move_to(b.C + p), b.t0 + 0.3 + 0.5 * i, z=5)
            b.text(s, 30, p, "#FFFFFF" if col != GREEN else INK, 1.8, t=b.t0 + 0.35 + 0.5 * i, z=7)
        path = [v(-2.1, 1.3), v(2.1, 1.3), v(2.1, -0.3), v(-2.1, -0.3)]

        def dots(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for k in range(6):
                ph = ((t * 0.5) + k / 6) % 1.0 * 3.0
                seg = min(2, int(ph)); f = ph - seg
                p = path[seg] * (1 - f) + path[seg + 1] * f
                g.add(Circle(radius=0.11, stroke_width=0, fill_color=YEL, fill_opacity=a).move_to(b.C + p))
            return g
        b.live(dots, b.t0 + 1.2, z=8)
        b.live(lambda a: astro(b.C + v(0, -1.55), 0.45, mouth=0.4, a=a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "INSIDE THE SUIT", "सूट के अंदर"), 38, v(0, 2.45), INK, 4.5, t=b.t0 + 0.2)
    beat0(B[0])
    beat1(B[1])
