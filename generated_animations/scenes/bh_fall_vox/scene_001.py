"""Vox look - shot 1 (scenes 1-2): a figure falls toward a black hole while the outside view shows it freezing and reddening; the three-part promise."""
from __future__ import annotations

from ._kit import *


def hole(C, r=1.0, tm=0.0, alpha=1.0):
    ring = Ellipse(width=3.6 * r, height=1.1 * r, stroke_color=ORANGE, stroke_width=10, stroke_opacity=alpha, fill_opacity=0).move_to(C).rotate(0.25 + 0.03 * math.sin(tm))
    core = Circle(radius=r, stroke_color=INK, stroke_width=5, stroke_opacity=alpha, fill_color="#0C0C12", fill_opacity=alpha).move_to(C)
    return VGroup(core, ring)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        H = b.C + v(-0.9, 0.2)
        b.live(lambda a: hole(H, 1.0, ctx.elapsed(), a), b.t0 + 0.1, z=4)
        fig = figure(0.55, coat=BLUE)
        fig.move_to(b.C + v(-2.6, 2.4))
        b.mover(fig, lambda: b.C + v(-2.6 + 1.6 * ease(level(ctx, b.t0 + 0.6, 3.0)) , 2.4 - 2.0 * ease(level(ctx, b.t0 + 0.6, 3.0))), z=6)
        # the outside view: a small screen where the same figure slows, reddens and fades before the edge
        b.put(vox.torn_card(2.4, 2.0, seed=21, rot=2).move_to(b.C + v(2.3, -1.7)), b.t0 + 0.4, z=3, pop=0.2)
        b.text(vox.L(ctx, "WHAT THEY SEE", "वे क्या देखते हैं"), 22, v(2.3, -0.95), INK, 2.2, t=b.t0 + 0.6)

        def seen(a):
            f = ease(level(ctx, b.t0 + 0.8, 3.4))
            col = "#FFFFFF" if f < 0.3 else (ORANGE if f < 0.6 else RED)
            return Circle(radius=0.22 * (1 - 0.5 * f), stroke_color=INK, stroke_width=3, stroke_opacity=a * (1 - 0.7 * f), fill_color=col, fill_opacity=a * (1 - 0.8 * f)).move_to(b.C + v(1.2 + 0.9 * f, -1.8))
        b.live(seen, b.t0 + 0.8, z=6)
        b.tape(vox.L(ctx, "FROZEN?", "जमे हुए?"), v(2.2, -2.5), RED, 2.8, 28, -3.0, t=b.t0 + 3.2)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.live(lambda a: hole(b.C + v(0, 0.6), 0.8, ctx.elapsed(), a), b.t0 + 0.1, z=4)
        for k, (en, hi, col, p, r) in enumerate((("WHAT YOU FEEL", "आपको क्या लगेगा", BLUE, v(-1.2, 2.3), -3.0), ("WHAT THEY SEE", "बाहर क्या दिखेगा", ORANGE, v(1.2, -0.9), 3.0), ("HOW LONG YOU LAST", "कितना टिकेंगे", RED, v(-0.9, -2.1), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.2, 28, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
