"""Vox look - shot 1 (scenes 1-2): a note with three rules taped to a mirror; the tonight's-story promise as tape labels. Fiction."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def mirror(C, a=1.0, w=2.6, h=3.6):
    frame = RoundedRectangle(corner_radius=0.2, width=w, height=h, stroke_color="#B07A4A", stroke_width=10, stroke_opacity=a, fill_color="#DCEBF5", fill_opacity=a).move_to(C)
    shine = Line(C + v(-0.8 * w / 2, h / 2 - 0.5), C + v(-0.2 * w / 2, h / 2 - 1.3), color="#FFFFFF", stroke_width=6, stroke_opacity=a * 0.8)
    return VGroup(frame, shine)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=3)
        b.live(lambda a: mirror(b.C + v(-1.4, 0.2), a), b.t0 + 0.2, z=4)
        note = vox.torn_card(2.6, 3.0, seed=41, rot=3)
        note.move_to(b.C + v(1.6, 0.4))
        b.mover(note, lambda: b.C + v(1.6, 0.4 + 0.06 * math.sin(ctx.elapsed() * 2.0)), t_in=b.t0 + 0.8, z=6)
        for k, (en, hi) in enumerate((("1.", "१."), ("2.", "२."), ("3.", "३."))):
            b.text(vox.L(ctx, en, hi), 44, v(0.8, 1.3 - 0.85 * k), INK, 0.8, t=b.t0 + 1.2 + 0.5 * k)
            b.put(Line(b.C + v(1.2, 1.15 - 0.85 * k), b.C + v(2.6, 1.15 - 0.85 * k), color="#B7AE9C", stroke_width=5), b.t0 + 1.3 + 0.5 * k, z=7, pop=0)
        b.tape(vox.L(ctx, "A NOTE ON MY MIRROR", "आईने पर एक नोट"), v(-0.2, -2.2), RED, 4.8, 28, -2.0, t=b.t0 + 2.6)
        b.text(vox.L(ctx, "A FICTIONAL STORY", "एक काल्पनिक कहानी"), 22, v(0.2, -2.9), "#6B6B75", 4.0, t=b.t0 + 0.6)

    def beat1(b):
        b.card(seed=5, rot=-0.6)
        b.live(lambda a: mirror(b.C + v(0, 0.2), a, 2.2, 3.0), b.t0 + 0.2, z=4)
        for k, (en, hi, col, p, r) in enumerate((("THREE RULES", "तीन नियम", BLUE, v(-1.0, 2.3), -3.0), ("ONE MIRROR", "एक आईना", ORANGE, v(1.2, 0.3), 3.0), ("A REFLECTION THAT WON'T WAIT", "परछाईं जो रुकती नहीं", RED, v(-0.4, -2.2), -2.0))):
            b.tape(vox.L(ctx, en, hi), p, col, 4.4, 26, r, t=b.t0 + 0.6 + 0.9 * k)
    beat0(B[0])
    beat1(B[1])
