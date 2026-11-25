"""Vox look - shot 1 (scenes 1-2): the phone rises to an ear and its screen goes dark; the three-part promise as tape labels. English + Hindi via vox.L."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    ev = lambda: ctx.elapsed()

    def beat0(b):
        b.card(seed=3)
        # a head in profile with an ear; the phone swings up from the lower right to the ear
        head = vox.cutout(VGroup(Circle(radius=1.15, stroke_color=INK, stroke_width=4, fill_color="#F2C9A0", fill_opacity=1), Circle(radius=0.3, stroke_color=INK, stroke_width=3, fill_color="#E8B48A", fill_opacity=1).shift(v(0.95, 0.0))), 6.0)
        b.put(head.move_to(b.C + v(-0.6, 0.4)), b.t0 + 0.1, z=4, pop=0.2)
        t_arr = b.t0 + 2.6

        def pos():
            f = ease(level(ctx, b.t0 + 0.8, 1.8))
            return b.C + v(2.4 - 1.5 * f, -1.5 + 1.9 * f)
        ph = phone(0.9)
        ph.move_to(b.C + v(2.4, -1.5))
        b.mover(ph, pos, z=6)
        # the screen goes dark the moment the phone arrives
        dark = Rectangle(width=0.7, height=1.3, stroke_width=0, fill_color="#15151C", fill_opacity=1)
        b.mover(dark, lambda: pos() + v(0, -0.03), t_in=t_arr, z=7)
        b.put(ctx.text("?", 100, RED, 1.2).move_to(b.C + v(-0.6, 2.6)), t_arr + 0.2, z=7, pop=0.3)
        b.text(vox.L(ctx, "WHAT DID IT SEE?", "उसने क्या देखा?"), 36, v(0, -2.4), INK, 5.4, t=b.t0 + 0.4)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.put(phone(1.3).move_to(b.C + v(0, 0.1)), b.t0 + 0.2, z=4, pop=0.3)
        for k, (en, hi, col, p, r) in enumerate((("INVISIBLE LIGHT", "अदृश्य रोशनी", BLUE, v(-1.0, 2.0), -3.0), ("HOW IT MEASURES", "दूरी कैसे नापे", ORANGE, v(1.1, 0.5), 3.0), ("HAIR CAN FOOL IT", "बाल दें धोखा", RED, v(-0.8, -1.7), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.2, 30, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
