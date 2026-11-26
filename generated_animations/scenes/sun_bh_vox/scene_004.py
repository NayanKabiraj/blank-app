"""Vox look - shot 4 (scenes 7-8): the Sun is too light and ends as a white dwarf; closing: Earth circling in the dark and the question."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import sun


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        c = b.C + v(0, 0.8)
        k = lambda: ease(level(ctx, b.t0 + 1.2, 2.5))
        b.live(lambda a: Circle(radius=max(0.12, 1.1 * (1 - 0.88 * k())), stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color=YEL if k() < 0.5 else "#FFFFFF", fill_opacity=a).move_to(c), b.t0 + 0.2, z=4)
        b.text(vox.L(ctx, "THE SUN", "सूरज"), 28, v(0, 2.4), INK, 2.6, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "TOO LIGHT FOR A BLACK HOLE", "ब्लैक होल के लिए बहुत हल्का"), v(0, -1.0), RED, 5.8, 24, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "ENDS AS A WHITE DWARF", "अंत में सफ़ेद बौना"), v(0, -2.0), BLUE, 5.2, 26, 2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.put(Rectangle(width=7.0, height=5.4, stroke_width=0, fill_color="#1B2238", fill_opacity=1).move_to(b.C + v(0, 0.1)), b.t0 + 0.1, z=3, pop=0)
        S = b.C + v(0, 0.5)
        b.live(lambda a: sun(S, 0.5, 1.0, a, ctx.elapsed()), b.t0 + 0.2, z=4)
        b.live(lambda a: Circle(radius=0.2, stroke_color="#FFFFFF", stroke_width=3, stroke_opacity=a, fill_color=BLUE, fill_opacity=a).move_to(S + v(2.2 * math.cos(ctx.elapsed() * 0.9), 1.4 * math.sin(ctx.elapsed() * 0.9))), b.t0 + 0.4, z=5)
        b.text(vox.L(ctx, "SEE IT COMING?", "आते देखते?"), 40, v(0, 2.5), "#FFFFFF", 5.6, t=b.t0 + 0.5)
        b.tape(vox.L(ctx, "A DARK YEAR", "एक अँधेरा साल"), v(0, -2.3), RED, 3.8, 30, -2.0, t=b.t0 + 1.2)
    beat0(B[0])
    beat1(B[1])
