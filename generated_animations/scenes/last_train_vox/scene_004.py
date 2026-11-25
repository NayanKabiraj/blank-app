"""Vox look - shot 4 (scenes 7-8): the clock stuck at 11:40 as the train leaves with the other man; the closing question about tonight's last train."""
from __future__ import annotations

from ._kit import *
from .scene_001 import carriage


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        c = b.C + v(-1.6, 1.3)
        b.put(Circle(radius=0.95, stroke_color=INK, stroke_width=5, fill_color=CREAM, fill_opacity=1).move_to(c), b.t0 + 0.2, z=4, pop=0.3)
        b.put(Line(c, c + v(0.0, 0.62), color=INK, stroke_width=6), b.t0 + 0.4, z=6, pop=0)               # 11:40, frozen
        b.put(Line(c, c + v(-0.5, 0.55) * 0.0 + v(0.28, -0.46), color=RED, stroke_width=5), b.t0 + 0.4, z=6, pop=0)
        b.text("11:40", 44, v(1.4, 1.3), INK, 2.6, t=b.t0 + 0.6)
        me = figure(0.9, coat=BLUE)
        b.put(me.move_to(b.C + v(-2.5, -1.2)), b.t0 + 0.8, z=6, pop=0.3)
        b.live(lambda a: carriage(b.C + v(0.4 + 3.0 * ease(level(ctx, b.t0 + 1.6, 3.0)), -1.0), ctx.elapsed(), a, flicker=False).scale(0.6).move_to(b.C + v(0.4 + 3.0 * ease(level(ctx, b.t0 + 1.6, 3.0)), -1.0)), b.t0 + 1.2, z=5)
        b.tape(vox.L(ctx, "EVERY NIGHT", "हर रात"), v(1.4, 2.5), RED, 3.0, 30, 2.0, t=b.t0 + 2.0)
        b.tape(vox.L(ctx, "SOMEONE GETS OFF", "कोई उतर जाता है"), v(0, -2.5), BLUE, 4.4, 28, -2.0, t=b.t0 + 3.0)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.live(lambda a: carriage(b.C + v(0, 0.3), ctx.elapsed(), a).scale(0.8), b.t0 + 0.2, z=4)
        b.text(vox.L(ctx, "WHO RIDES TONIGHT?", "आज रात कौन?"), 40, v(0, 2.4), INK, 6.0, t=b.t0 + 0.3)
        b.put(ctx.text("?", 110, RED, 1.2).move_to(b.C + v(0, 0.3)), b.t0 + 1.0, z=8, pop=0.3)
        b.tape(vox.L(ctx, "A FICTIONAL STORY", "एक काल्पनिक कहानी"), v(0, -2.4), BLUE, 4.6, 26, -2.0, t=b.t0 + 1.4)
    beat0(B[0])
    beat1(B[1])
