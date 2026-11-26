"""Vox look - shot 2 (scenes 3-4): sound is air wiggling (a pulse runs through a row of air dots to an ear); in space there are almost no dots, so the pulse dies."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro, ear
from generated_animations.shared.packkit import *

X0, X1 = -1.7, 1.9


def row(C, xs, t, a, amp_decay):
    g = VGroup()
    for x in xs:
        p = (t * 1.5) % 3.2 - 0.1                                    # pulse front (distance from X0)
        d = (x - X0) - p
        env = math.exp(-(d * d) / 0.18)
        dx = 0.28 * env * amp_decay(x)
        g.add(Circle(radius=0.09, stroke_color=INK, stroke_width=2, stroke_opacity=a, fill_color="#8EC9F0", fill_opacity=a).move_to(C + v(x + dx, 0.0)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        xs = [X0 + 0.32 * k for k in range(12)]
        b.live(lambda a: row(b.C + v(0, -0.2), xs, ctx.elapsed() - b.t0, a, lambda x: 1.0), b.t0 + 0.2, z=5)
        b.live(lambda a: astro(b.C + v(-2.3, -0.4), 0.55, hl=(-0.2 - 0.5 * (0.5 + 0.5 * math.cos((ctx.elapsed() - b.t0) * 4)), 0.1), hr=(0.2 + 0.5 * (0.5 + 0.5 * math.cos((ctx.elapsed() - b.t0) * 4)), 0.1), mouth=0.3, a=a), b.t0 + 0.1, z=6)
        b.live(lambda a: ear(b.C + v(2.45, -0.15), 0.8, INK, a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "SOUND = AIR WIGGLING", "आवाज़ = हवा का कंपन"), 40, v(0, 2.2), INK, 5.5, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "THE WIGGLE REACHES YOUR EAR", "कंपन कान तक पहुँचता है"), v(0, -2.1), BLUE, 5.2, 26, -1.5, t=b.t0 + 2.2)

    def beat1(b):
        b.card(seed=13, rot=0.5)
        far = [X0, 0.0, X1 - 0.2]
        b.live(lambda a: row(b.C + v(0, -0.2), far, ctx.elapsed() - b.t0, a, lambda x: math.exp(-max(0.0, x - X0) * 1.2)), b.t0 + 0.2, z=5)
        b.live(lambda a: astro(b.C + v(-2.3, -0.4), 0.55, hl=(-0.5, 0.1), hr=(0.5, 0.1), mouth=0.3, a=a), b.t0 + 0.1, z=6)
        b.live(lambda a: ear(b.C + v(2.45, -0.15), 0.8, INK, a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "SPACE: ALMOST EMPTY", "अंतरिक्ष: लगभग ख़ाली"), 40, v(0, 2.2), INK, 5.5, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "NO AIR = NO WIGGLE", "हवा नहीं = कंपन नहीं"), v(0, -2.1), RED, 4.6, 28, 2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
