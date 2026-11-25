"""Vox look - shot 3 (scenes 5-6): a figure in my coat with my bag under the lamp; the swap - he steps in, I step out - and the calm voice thanks us."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        b.live(lambda a: Polygon(b.C + v(0.0, 2.4), b.C + v(-1.8, -1.9), b.C + v(1.8, -1.9), stroke_width=0, fill_color=YEL, fill_opacity=0.28 * a), b.t0 + 0.1, z=3)
        b.put(Circle(radius=0.3, stroke_color=INK, stroke_width=4, fill_color=YEL, fill_opacity=1).move_to(b.C + v(0, 2.55)), b.t0 + 0.2, z=5, pop=0.3)
        man = figure(1.1, coat=ORANGE)
        man.move_to(b.C + v(0, 0.2))
        b.put(man, b.t0 + 0.6, z=6, pop=0.3)
        bag = RoundedRectangle(corner_radius=0.1, width=0.7, height=0.55, stroke_color=INK, stroke_width=3, fill_color="#B07A4A", fill_opacity=1)
        b.mover(bag.move_to(b.C + v(0.9, -0.6)), lambda: b.C + v(0.9, -0.6 + 0.05 * math.sin(ctx.elapsed() * 2.4)), t_in=b.t0 + 0.9, z=7)
        b.put(Line(b.C + v(-0.2, 0.05), b.C + v(0.2, 0.05), color=INK, stroke_width=4), b.t0 + 1.2, z=8, pop=0)
        b.tape(vox.L(ctx, "MY COAT", "मेरा कोट"), v(-2.0, 1.2), RED, 2.8, 30, -3.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "MY BAG", "मेरा बैग"), v(2.0, -1.6), BLUE, 2.8, 30, 3.0, t=b.t0 + 2.0)
        b.text(vox.L(ctx, "HE SMILED...", "वह मुस्कुराया..."), 28, v(0, -2.5), INK, 4.0, t=b.t0 + 2.8)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        b.put(Rectangle(width=7.4, height=0.3, stroke_color=INK, stroke_width=3, fill_color="#8895A8", fill_opacity=1).move_to(b.C + v(0, -1.7)), b.t0 + 0.1, z=3, pop=0)
        b.put(Rectangle(width=2.0, height=2.6, stroke_color=INK, stroke_width=4, fill_color="#3D4A66", fill_opacity=1).move_to(b.C + v(-2.2, -0.3)), b.t0 + 0.1, z=3, pop=0)   # the train doorway
        me = figure(1.0, coat=BLUE)
        him = figure(1.0, coat=ORANGE)
        t_sw = b.t0 + 0.8
        me.move_to(b.C + v(-2.2, -0.3))
        him.move_to(b.C + v(2.2, -0.3))
        b.mover(me, lambda: b.C + v(-2.2 + 4.4 * ease(level(ctx, t_sw, 1.6)), -0.3), z=6)
        b.mover(him, lambda: b.C + v(2.2 - 4.4 * ease(level(ctx, t_sw, 1.6)), -0.3 + 0.05 * math.sin(ctx.elapsed() * 6)), z=6)
        b.live(lambda a: Line(b.C + v(-2.2, 0.9), b.C + v(-2.2, -1.6), color=INK, stroke_width=8, stroke_opacity=a * level(ctx, t_sw + 1.8, 0.3)), t_sw, z=8)
        b.tape(vox.L(ctx, "HE STEPS IN. I STEP OUT.", "वह चढ़ा। मैं उतरा।"), v(0, 2.4), RED, 5.4, 26, -2.0, t=b.t0 + 0.6)
        b.tape(vox.L(ctx, "\"THANK YOU FOR SWAPPING\"", "\"अदला-बदली का शुक्रिया\""), v(0, -2.5), BLUE, 5.8, 24, 2.0, t=t_sw + 2.0)
    beat0(B[0])
    beat1(B[1])
