"""Vox look - shot 2 (scenes 3-4): crossing the horizon feels like nothing; seen from outside the clock slows, the light reddens and the figure fades without crossing."""
from __future__ import annotations

from ._kit import *
from .scene_001 import hole


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=7)
        H = b.C + v(0, 0.3)
        b.live(lambda a: hole(H, 1.2, ctx.elapsed(), a), b.t0 + 0.1, z=4)
        b.live(lambda a: Circle(radius=1.9, stroke_color=YEL, stroke_width=5, stroke_opacity=0.9 * a, fill_opacity=0).move_to(H), b.t0 + 0.4, z=5)
        b.text(vox.L(ctx, "THE HORIZON", "होराइज़न"), 26, v(0, 2.5), INK, 3.0, t=b.t0 + 0.5)
        fig = figure(0.55, coat=BLUE)
        fig.move_to(b.C + v(-3.0, -1.2))
        b.mover(fig, lambda: b.C + v(-3.0 + 3.4 * ease(level(ctx, b.t0 + 0.8, 3.2)), -1.2 + 0.9 * ease(level(ctx, b.t0 + 0.8, 3.2))), z=6)
        b.tape(vox.L(ctx, "YOU FEEL NOTHING", "कुछ महसूस नहीं"), v(0, -2.4), GREEN, 4.6, 28, 2.0, t=b.t0 + 2.0)
        b.tape(vox.L(ctx, "NOT A WALL", "दीवार नहीं"), v(2.0, 1.9), BLUE, 3.0, 26, -3.0, t=b.t0 + 3.2)

    def beat1(b):
        b.card(seed=9, rot=0.5)
        # outside clock: its hand slows down; the figure's colour goes red and it fades just short of the edge
        def clock(a):
            k = level(ctx, b.t0 + 0.5, 4.0)
            ang = 6.0 * (1 - math.exp(-3.0 * k)) / 3.0 * 2.0
            c = b.C + v(-1.6, 1.1)
            return VGroup(Circle(radius=0.8, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color=CREAM, fill_opacity=a).move_to(c),
                          Line(c, c + v(0.65 * math.sin(ang), 0.65 * math.cos(ang)), color=RED, stroke_width=6, stroke_opacity=a))
        b.live(clock, b.t0 + 0.3, z=5)
        b.text(vox.L(ctx, "THEIR CLOCK: SLOWS", "उनकी घड़ी: धीमी"), 22, v(-1.6, 2.2), INK, 3.0, t=b.t0 + 0.6)
        b.live(lambda a: hole(b.C + v(1.6, -0.2), 0.8, ctx.elapsed(), a), b.t0 + 0.2, z=4)

        def seen(a):
            f = ease(level(ctx, b.t0 + 0.8, 3.6))
            col = "#FFFFFF" if f < 0.3 else (ORANGE if f < 0.6 else RED)
            return Circle(radius=0.25 * (1 - 0.4 * f), stroke_color=INK, stroke_width=3, stroke_opacity=a * (1 - 0.8 * f), fill_color=col, fill_opacity=a * (1 - 0.9 * f)).move_to(b.C + v(0.0 + 0.55 * f, -0.2 + 0.0 * f))
        b.live(seen, b.t0 + 0.8, z=6)
        b.tape(vox.L(ctx, "TURNS RED", "लाल पड़ते हैं"), v(-1.2, -1.4), RED, 3.2, 28, -3.0, t=b.t0 + 1.8)
        b.tape(vox.L(ctx, "NEVER CROSSES", "कभी पार नहीं"), v(1.0, -2.4), BLUE, 3.8, 28, 2.0, t=b.t0 + 2.8)
    beat0(B[0])
    beat1(B[1])
