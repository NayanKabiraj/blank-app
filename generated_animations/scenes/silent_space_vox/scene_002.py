"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): sound is air wiggling (a pulse runs through a row of air dots to an ear); in space there are almost no dots, so the pulse dies."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro, ear
from generated_animations.shared.packkit import *

X0, X1 = -2.3, 2.4


def row(C, xs, t, a, amp_decay):
    g = VGroup()
    for x in xs:
        p = (t * 2.0) % 4.6 - 0.1
        d = (x - X0) - p
        env = math.exp(-(d * d) / 0.22)
        g.add(Circle(radius=0.14, stroke_color="#FFFFFF", stroke_width=2, stroke_opacity=a, fill_color="#8EC9F0", fill_opacity=a).move_to(C + v(x + 0.4 * env * amp_decay(x), 0.0)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    W_ = "#FFFFFF"

    def clap(b, t, s=1.0):
        k = 0.5 + 0.5 * math.cos(t * 4)
        return dict(hl=(-0.2 - 0.5 * k, 0.1), hr=(0.2 + 0.5 * k, 0.1))

    def beat0(b):
        b.backdrop("#10224A", "#2B4C7E", seed=11)
        xs = [X0 + 0.4 * k for k in range(12)]
        b.live(lambda a: row(b.C + v(0, -0.5), xs, ctx.elapsed() - b.t0, a, lambda x: 1.0), b.t0 + 0.2, z=5)
        b.live(lambda a: astro(b.C + v(-3.55, -0.7), 0.9, mouth=0.3, a=a, **clap(b, ctx.elapsed() - b.t0)), b.t0 + 0.1, z=6)
        b.live(lambda a: ear(b.C + v(3.7, -0.3), 1.2, W_, a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "SOUND =\nAIR WIGGLING", "आवाज़ =\nहवा का कंपन"), 64, v(0, 3.4), W_, 7.0, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "THE WIGGLE REACHES YOUR EAR", "कंपन कान तक पहुँचता है"), v(0, -3.5), BLUE, 7.4, 30, -1.5, t=b.t0 + 2.2)

    def beat1(b):
        b.backdrop("#070D22", "#1A1F3C", seed=13)
        far = [X0, -0.1, X1 - 0.2]
        b.live(lambda a: row(b.C + v(0, -0.5), far, ctx.elapsed() - b.t0, a, lambda x: math.exp(-max(0.0, x - X0) * 1.2)), b.t0 + 0.2, z=5)
        b.live(lambda a: astro(b.C + v(-3.55, -0.7), 0.9, hl=(-0.5, 0.1), hr=(0.5, 0.1), mouth=0.3, a=a), b.t0 + 0.1, z=6)
        b.live(lambda a: ear(b.C + v(3.7, -0.3), 1.2, W_, a), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "SPACE:\nALMOST EMPTY", "अंतरिक्ष:\nलगभग ख़ाली"), 64, v(0, 3.4), W_, 7.0, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "NO AIR = NO WIGGLE", "हवा नहीं = कंपन नहीं"), v(0, -3.5), RED, 6.4, 34, 2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
