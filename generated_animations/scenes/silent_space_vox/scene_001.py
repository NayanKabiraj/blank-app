"""Vox look, FULL-SCREEN art - shot 1 (scenes 1-2): a cartoon astronaut claps on a purple planet under the stars (burst + sound arcs), then the same clap in space is silent; the episode promise as tape labels."""
from __future__ import annotations

from manim import Arc

from generated_animations.shared.cartoon import astro
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def ground(b, y=-4.6):
    b.put(Ellipse(width=15.0, height=4.4, stroke_color="#2A1E4F", stroke_width=5, fill_color="#6B4C9A", fill_opacity=1).move_to(b.C + v(0, y)), b.t0 + 0.05, z=3, pop=0)
    for x, w in ((-2.6, 0.9), (2.2, 1.3), (0.2, 0.6)):
        b.put(Ellipse(width=w, height=w * 0.35, stroke_width=0, fill_color="#55397F", fill_opacity=1).move_to(b.C + v(x, y + 1.35 - 0.2 * w)), b.t0 + 0.05, z=3, pop=0)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0E1A3A", "#3B2A66", seed=3)
        ground(b)
        S = b.C + v(0, -0.5)

        def pose(a):
            t = ctx.elapsed() - b.t0
            k = 0.5 + 0.5 * math.cos(t * 2 * math.pi / 0.8)
            hl, hr = (-0.2 - 0.75 * k, 0.1 - 0.45 * k), (0.2 + 0.75 * k, 0.1 - 0.45 * k)
            return astro(S, 2.3, hl=hl, hr=hr, mouth=0.5 if t > 2.5 else 0.0, look=(0, 0.3), blink=0.1 if (t % 2.6) < 0.12 else 1.0, a=a)
        b.live(pose, b.t0 + 0.1, z=6)

        def arcs(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for i in range(3):
                ph = ((t / 0.8) + i * 0.33) % 1.0
                on = 1.0 if t < 2.5 else 0.0
                for st in (0.3, math.pi - 1.2):
                    g.add(Arc(radius=1.2 + 3.0 * ph, start_angle=st, angle=0.9, arc_center=S + v(0, 0.3), stroke_color=ORANGE, stroke_width=10, stroke_opacity=a * on * (1 - ph)))
            return g
        b.live(arcs, b.t0 + 0.1, z=5)
        b.text(vox.L(ctx, "CLAP!", "ताली!"), 120, v(0, 3.9), W_, 6.0, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "IN SPACE: SILENCE", "अंतरिक्ष में: सन्नाटा"), v(0, -3.6), RED, 6.6, 38, -2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.backdrop("#0E1A3A", "#3B2A66", seed=5)
        ground(b)
        b.live(lambda a: astro(b.C + v(-2.0, -1.3), 1.75, hr=(1.0, 0.7 + 0.14 * math.sin(ctx.elapsed() * 6)), look=(1, 0), mouth=0.3, a=a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("WHY SPACE IS SILENT", "अंतरिक्ष चुप क्यों है", BLUE, v(1.3, 3.2), -2.5), ("HOW ASTRONAUTS TALK", "यात्री बात कैसे करते हैं", ORANGE, v(1.3, 1.3), 2.5), ("PART 2: THE MOON", "भाग 2: चाँद", RED, v(1.3, -0.6), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 5.4, 30, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
