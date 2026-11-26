"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): the reframe (nothing carries it) and the closing question (hear it or see it)."""
from __future__ import annotations

from generated_animations.shared.cartoon import astro, ear, eye_icon
from generated_animations.shared.packkit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    W_ = "#FFFFFF"

    def beat0(b):
        b.backdrop("#10224A", "#2B4C7E", seed=31)
        b.text(vox.L(ctx, "QUIET BECAUSE...", "चुप इसलिए क्योंकि..."), 64, v(0, 3.9), W_, 7.5, t=b.t0 + 0.2)
        b.text(vox.L(ctx, "NOTHING HAPPENS", "कुछ होता नहीं"), 52, v(0.4, 1.7), "#9AA3BF", 7.0, t=b.t0 + 0.7)
        b.put(Line(b.C + v(-3.0, 1.7), b.C + v(3.4, 1.7), color=RED, stroke_width=10), b.t0 + 1.4, z=8, pop=0)
        b.put(VGroup(Line(v(-0.3, 0.3), v(0.3, -0.3), color=RED, stroke_width=16), Line(v(-0.3, -0.3), v(0.3, 0.3), color=RED, stroke_width=16)).move_to(b.C + v(-3.7, 1.7)), b.t0 + 1.4, z=8)
        b.tape(vox.L(ctx, "NOTHING CARRIES IT", "ले जाने वाला कुछ नहीं"), v(0.3, -0.2), GREEN, 6.6, 40, -1.5, t=b.t0 + 2.4)
        b.put(VGroup(Line(v(-0.35, 0.0), v(-0.08, -0.3), color=GREEN, stroke_width=16), Line(v(-0.08, -0.3), v(0.4, 0.35), color=GREEN, stroke_width=16)).move_to(b.C + v(-3.9, -0.2)), b.t0 + 2.9, z=8)
        b.live(lambda a: astro(b.C + v(0, -2.9), 0.7, look=(0, 0.2), mouth=0.2, a=a), b.t0 + 0.4, z=6)

    def beat1(b):
        b.backdrop("#1B2F5E", "#4B3A7A", seed=33)
        b.live(lambda a: astro(b.C + v(0, -0.6), 1.9, hl=(-0.95, -0.6 + 0.25 * math.sin(ctx.elapsed() * 3)), hr=(0.95, -0.6 - 0.25 * math.sin(ctx.elapsed() * 3)), mouth=0.4, blink=0.1 if (ctx.elapsed() % 2.4) < 0.12 else 1.0, a=a), b.t0 + 0.2, z=6)
        b.live(lambda a: ear(b.C + v(-3.0, 3.6), 1.5, W_, a), b.t0 + 0.8, z=6)
        b.live(lambda a: eye_icon(b.C + v(3.0, 3.6), 1.5, W_, a), b.t0 + 1.2, z=6)
        b.tape(vox.L(ctx, "HEAR IT", "सुनना"), v(-2.6, 2.0), BLUE, 3.6, 40, -3.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "SEE IT", "देखना"), v(2.6, 2.0), ORANGE, 3.6, 40, 3.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -3.9), RED, 5.6, 36, -1.5, t=b.t0 + 1.9)
    beat0(B[0])
    beat1(B[1])
