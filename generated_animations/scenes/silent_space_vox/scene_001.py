"""Vox look - shot 1 (scenes 1-2): a cartoon astronaut claps (burst + sound arcs), then the same clap in space is silent; the episode promise as tape labels."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro
from manim import Arc

from generated_animations.shared.packkit import *


def stars(C, a, tm, n=18):
    g = VGroup()
    for k in range(n):
        x, y = -3.0 + (k * 1.37) % 6.0, -2.4 + (k * 2.11) % 5.2
        g.add(Circle(radius=0.03 + 0.02 * ((k + int(tm * 2)) % 3 == 0), stroke_width=0, fill_color="#FFFFFF", fill_opacity=a * 0.8).move_to(C + v(x, y)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        S = b.C + v(0, -0.25)

        def pose(a):
            t = ctx.elapsed() - b.t0
            k = 0.5 + 0.5 * math.cos(t * 2 * math.pi / 0.8)                # 0 = hands together, 1 = apart
            hl, hr = (-0.2 - 0.7 * k, 0.1 - 0.4 * k), (0.2 + 0.7 * k, 0.1 - 0.4 * k)
            return astro(S, 1.25, hl=hl, hr=hr, mouth=0.5 if t > 2.5 else 0.0, look=(0, 0.3), blink=0.1 if (t % 2.6) < 0.12 else 1.0, a=a)
        b.live(pose, b.t0 + 0.1, z=6)

        def arcs(a):
            t = ctx.elapsed() - b.t0
            g = VGroup()
            for i in range(3):
                ph = ((t / 0.8) + i * 0.33) % 1.0
                on = 1.0 if t < 2.5 else 0.0
                g.add(Arc(radius=0.5 + 1.6 * ph, start_angle=0.35, angle=0.9, arc_center=S + v(0, 0.2), stroke_color=ORANGE, stroke_width=8, stroke_opacity=a * on * (1 - ph)))
                g.add(Arc(radius=0.5 + 1.6 * ph, start_angle=math.pi - 1.25, angle=0.9, arc_center=S + v(0, 0.2), stroke_color=ORANGE, stroke_width=8, stroke_opacity=a * on * (1 - ph)))
            return g
        b.live(arcs, b.t0 + 0.1, z=5)
        b.text(vox.L(ctx, "CLAP!", "ताली!"), 70, v(0, 2.3), INK, 3.5, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "IN SPACE: SILENCE", "अंतरिक्ष में: सन्नाटा"), v(0, -2.35), RED, 4.9, 30, -2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.live(lambda a: stars(b.C, a, ctx.elapsed()), b.t0 + 0.1, z=3)
        b.live(lambda a: astro(b.C + v(-1.5, -0.35), 0.8, hr=(1.0, 0.6 + 0.12 * math.sin(ctx.elapsed() * 6)), look=(1, 0), mouth=0.3, a=a), b.t0 + 0.2, z=6)
        for k, (en, hi, col, p, r) in enumerate((("WHY SPACE IS SILENT", "अंतरिक्ष चुप क्यों है", BLUE, v(0.7, 1.6), -2.5), ("HOW ASTRONAUTS TALK", "यात्री बात कैसे करते हैं", ORANGE, v(0.7, 0.3), 2.5), ("PART 2: THE MOON", "भाग 2: चाँद", RED, v(0.7, -1.2), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 3.9, 24, r, t=b.t0 + 0.7 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
