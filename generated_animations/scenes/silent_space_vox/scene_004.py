"""Vox look - shot 4 (scenes 7-8): the reframe (nothing carries it) and the closing question (hear it or see it)."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro, ear, eye_icon
from generated_animations.shared.packkit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=31)
        b.text(vox.L(ctx, "QUIET BECAUSE...", "चुप इसलिए क्योंकि..."), 40, v(0, 2.3), INK, 5.5, t=b.t0 + 0.2)
        left = b.text(vox.L(ctx, "NOTHING HAPPENS", "कुछ होता नहीं"), 34, v(0, 1.0), "#6B6B75", 5.0, t=b.t0 + 0.7)
        b.put(Line(b.C + v(-2.6, 1.0), b.C + v(2.6, 1.0), color=RED, stroke_width=8), b.t0 + 1.4, z=8, pop=0)
        b.put(VGroup(Line(v(-0.2, 0.2), v(0.2, -0.2), color=RED, stroke_width=12), Line(v(-0.2, -0.2), v(0.2, 0.2), color=RED, stroke_width=12)).move_to(b.C + v(-2.9, 1.0)), b.t0 + 1.4, z=8)
        right = b.text(vox.L(ctx, "NOTHING CARRIES IT", "उसे ले जाने वाला कुछ नहीं"), 36, v(0, -0.6), INK, 5.4, t=b.t0 + 2.4)
        vox.marker(ctx, right, t_in=b.t0 + 2.9)
        b.put(VGroup(Line(v(-0.25, 0.0), v(-0.05, -0.22), color=GREEN, stroke_width=12), Line(v(-0.05, -0.22), v(0.3, 0.25), color=GREEN, stroke_width=12)).move_to(b.C + v(-2.9, -0.6)), b.t0 + 2.9, z=8)
        b.live(lambda a: astro(b.C + v(0, -2.0), 0.4, look=(0, 0.2), mouth=0.2, a=a), b.t0 + 0.4, z=6)

    def beat1(b):
        b.card(seed=33, rot=0.6)
        b.live(lambda a: astro(b.C + v(0, 0.1), 1.0, hl=(-0.95, -0.6 + 0.2 * math.sin(ctx.elapsed() * 3)), hr=(0.95, -0.6 - 0.2 * math.sin(ctx.elapsed() * 3)), mouth=0.4, blink=0.1 if (ctx.elapsed() % 2.4) < 0.12 else 1.0, a=a), b.t0 + 0.2, z=6)
        b.live(lambda a: ear(b.C + v(-2.1, 1.7), 0.9, INK, a), b.t0 + 0.8, z=6)
        b.live(lambda a: eye_icon(b.C + v(2.1, 1.7), 0.9, INK, a), b.t0 + 1.2, z=6)
        b.tape(vox.L(ctx, "HEAR IT", "सुनना"), v(-2.0, 0.6), BLUE, 2.6, 28, -3.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "SEE IT", "देखना"), v(2.0, 0.6), ORANGE, 2.6, 28, 3.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -2.2), RED, 4.0, 28, -1.5, t=b.t0 + 1.9)
    beat0(B[0])
    beat1(B[1])
