"""Vox look - shot 4 (scenes 7-8): the back of the note, a fourth rule in my own handwriting; the closing question - leave, or wave back."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import mirror
from .scene_002 import person


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        note = vox.torn_card(4.4, 3.2, seed=43, rot=-2)
        note.move_to(b.C + v(0, 0.5))
        b.put(note, b.t0 + 0.3, z=3, pop=0.2)
        b.text(vox.L(ctx, "RULE 4", "नियम 4"), 50, v(0, 1.5), RED, 3.6, t=b.t0 + 1.0)
        b.text(vox.L(ctx, "never come back", "कभी वापस मत आना"), 44, v(0, 0.3), INK, 4.0, t=b.t0 + 1.8)
        b.put(Line(b.C + v(-1.9, -0.2), b.C + v(1.9, -0.2), color=RED, stroke_width=6), b.t0 + 2.6, z=6, pop=0)
        b.tape(vox.L(ctx, "MY OWN HANDWRITING", "मेरी ही लिखावट"), v(0, -1.6), BLUE, 4.6, 28, 2.0, t=b.t0 + 2.4)
        b.put(person(b.C + v(-2.4, -0.4), 0.0, 1.0).scale(0.9), b.t0 + 0.6, z=7, pop=0.2)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.live(lambda a: mirror(b.C + v(1.3, 0.3), a, 2.4, 3.4), b.t0 + 0.2, z=4)
        wave = lambda: 0.5 + 0.5 * math.sin(ctx.elapsed() * 5.0)
        b.live(lambda a: person(b.C + v(1.3, 0.7), wave(), a, coat="#6E8AD0"), b.t0 + 0.6, z=6)
        b.put(person(b.C + v(-2.0, 0.4), 0.0, 1.0), b.t0 + 0.4, z=6, pop=0.2)
        b.text(vox.L(ctx, "LEAVE OR WAVE BACK?", "निकलें या हाथ हिलाएँ?"), 34, v(0, 2.6), INK, 6.0, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "A FICTIONAL STORY", "एक काल्पनिक कहानी"), v(0, -2.5), BLUE, 4.6, 26, -2.0, t=b.t0 + 1.4)
    beat0(B[0])
    beat1(B[1])
