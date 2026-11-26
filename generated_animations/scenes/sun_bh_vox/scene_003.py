"""Vox look - shot 3 (scenes 5-6): the orbit is unchanged because gravity depends on mass, not size; the Sun shrinks to three kilometres while the pull arrow stays the same."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import sun


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        for side, name, hi, black in ((-1, "WITH THE SUN", "सूरज के साथ", 0.0), (1, "WITH A BLACK HOLE", "ब्लैक होल के साथ", 1.0)):
            c = b.C + v(side * 1.7, 0.5)
            b.live(lambda a, c=c, black=black: sun(c, 0.5, black, a, ctx.elapsed()), b.t0 + 0.2, z=4)
            b.live(lambda a, c=c, side=side: VGroup(Ellipse(width=2.8, height=2.0, stroke_color="#B7AE9C", stroke_width=3, stroke_opacity=0.8 * a, fill_opacity=0).move_to(c),
                                                    Circle(radius=0.16, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(c + v(1.4 * math.cos(ctx.elapsed() * 1.1), 1.0 * math.sin(ctx.elapsed() * 1.1)))), b.t0 + 0.4, z=5)
            b.text(vox.L(ctx, name, hi), 22, v(side * 1.7, 2.3), INK, 3.2, t=b.t0 + 0.5)
        b.tape(vox.L(ctx, "SAME ORBIT", "वही कक्षा"), v(0, -2.2), GREEN, 3.6, 32, 2.0, t=b.t0 + 2.0)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        c = b.C + v(-1.6, 0.6)
        shrink = lambda: 1.0 - 0.94 * ease(level(ctx, b.t0 + 1.0, 2.4))
        b.live(lambda a: Circle(radius=max(0.05, 1.0 * shrink()), stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color=YEL if shrink() > 0.5 else "#0C0C12", fill_opacity=a).move_to(c), b.t0 + 0.2, z=4)
        E = b.C + v(2.3, 0.6)
        b.put(Circle(radius=0.28, stroke_color=INK, stroke_width=4, fill_color=BLUE, fill_opacity=1).move_to(E), b.t0 + 0.2, z=5, pop=0.3)
        b.live(lambda a: VGroup(Line(E + v(-0.4, 0), E + v(-1.7, 0), color=RED, stroke_width=9, stroke_opacity=a), Polygon(E + v(-2.0, 0), E + v(-1.6, 0.25), E + v(-1.6, -0.25), stroke_width=0, fill_color=RED, fill_opacity=a)), b.t0 + 0.6, z=6)
        b.text(vox.L(ctx, "PULL: THE SAME", "खिंचाव: वही"), 26, v(0.8, -0.8), RED, 3.6, t=b.t0 + 1.0)
        b.live(lambda a: ctx.text("3 km", 40, INK, 2.2).move_to(c + v(0, -1.4)).set_opacity(a * level(ctx, b.t0 + 2.6, 0.4)), b.t0 + 2.6, z=6)
        b.tape(vox.L(ctx, "MASS, NOT SIZE", "द्रव्यमान, आकार नहीं"), v(0.4, 2.4), BLUE, 4.6, 28, -2.0, t=b.t0 + 1.2)
    beat0(B[0])
    beat1(B[1])
