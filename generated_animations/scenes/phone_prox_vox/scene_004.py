"""Vox look - shot 4 (scenes 7-8): light hair reflects more light than dark hair and can fool the sensor; the closing question about what else the phone senses."""
from __future__ import annotations

from ._kit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        for side, hair, name, hi, hh in ((-1, "#E8D28A", "LIGHT HAIR", "हल्के बाल", 2.2), (1, "#2B2B35", "DARK HAIR", "काले बाल", 0.8)):
            x = side * 1.8
            hd = VGroup(Circle(radius=0.8, stroke_color=INK, stroke_width=4, fill_color="#F2C9A0", fill_opacity=1), Circle(radius=0.85, stroke_width=0, fill_color=hair, fill_opacity=1).shift(v(0, 0.35)).set_z_index(-1))
            b.put(vox.cutout(hd, 6.0).move_to(b.C + v(x, 0.9)), b.t0 + 0.2, z=4, pop=0.2)
            b.text(vox.L(ctx, name, hi), 26, v(x, 2.3), INK, 3.0, t=b.t0 + 0.4)
            b.live(lambda a, x=x, hh=hh: Rectangle(width=0.8, height=max(0.05, hh * ease(level(ctx, b.t0 + 1.0, 1.0))), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=RED, fill_opacity=a).move_to(b.C + v(x, -1.0 + max(0.05, hh * ease(level(ctx, b.t0 + 1.0, 1.0))) / 2)), b.t0 + 0.8, z=5)
        b.put(vox.tape(ctx, vox.L(ctx, "MORE LIGHT BACK = FOOLED!", "ज़्यादा रोशनी = धोखा!"), b.C + v(0, -2.4), RED, 5.2, 28, -2.0), b.t0 + 2.4, z=8, pop=0.3)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.put(phone(1.3).move_to(b.C + v(0, 0.2)), b.t0 + 0.1, z=4, pop=0.3)
        names = ((vox.L(ctx, "TILT", "झुकाव"), BLUE), (vox.L(ctx, "LIGHT", "रोशनी"), ORANGE), (vox.L(ctx, "SOUND", "आवाज़"), GREEN), (vox.L(ctx, "MOTION", "हलचल"), PINK))
        for k, (nm, col) in enumerate(names):
            an = k * math.pi / 2 + math.pi / 4
            pos = v(2.1 * math.cos(an), 0.2 + 1.9 * math.sin(an))
            b.tape(nm, pos, col, 2.2, 24, (-3 if k % 2 else 3), t=b.t0 + 0.6 + 0.4 * k)
        b.put(ctx.text("?", 110, RED, 1.2).move_to(b.C + v(0, 0.2)).set_opacity(1.0), b.t0 + 2.4, z=8, pop=0.3)
    beat0(B[0])
    beat1(B[1])
