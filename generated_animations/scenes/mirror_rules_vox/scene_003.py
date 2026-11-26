"""Vox look - shot 3 (scenes 5-6): rule three (it moves first: leave); the reflection raises its hand before me, then I run for the door while it stays, smiling."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import mirror
from .scene_002 import person, pose


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=11)
        b.live(lambda a: mirror(b.C + v(1.4, 0.2), a), b.t0 + 0.1, z=4)
        b.live(lambda a: person(b.C + v(-1.6, 0.6), pose(ctx.elapsed() - b.t0 + 1.0), a), b.t0 + 0.2, z=6)             # the reflection LEADS me by a second
        b.live(lambda a: person(b.C + v(1.4, 0.6), pose(ctx.elapsed() - b.t0 + 2.0), a, coat="#6E8AD0"), b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "ME", "मैं"), 26, v(-1.6, -1.6), INK, 1.6, t=b.t0 + 0.5)
        b.text(vox.L(ctx, "FIRST!", "पहले!"), 32, v(3.0, 0.3), RED, 1.4, t=b.t0 + 2.2)
        b.tape(vox.L(ctx, "RULE 3: IT MOVES FIRST", "नियम 3: वह पहले हिले"), v(0, 2.8), RED, 5.4, 26, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "LEAVE", "निकल जाओ"), v(0, -2.5), BLUE, 3.0, 34, 2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        b.live(lambda a: mirror(b.C + v(-1.5, 0.2), a), b.t0 + 0.1, z=4)
        # the reflection stays in the mirror, smiling; I run to the door on the right
        b.put(person(b.C + v(-1.5, 0.6), 0.0, 1.0, coat="#6E8AD0"), b.t0 + 0.3, z=6, pop=0.2)
        b.put(vox.cutout(Polygon(v(-0.18, -0.02), v(-0.05, -0.12), v(0.05, -0.12), v(0.18, -0.02), stroke_width=0, fill_color=INK, fill_opacity=1), 0.0).move_to(b.C + v(-1.5, 0.05)), b.t0 + 0.9, z=8, pop=0.1)
        door = Rectangle(width=1.1, height=2.4, stroke_color=INK, stroke_width=5, fill_color="#B07A4A", fill_opacity=1).move_to(b.C + v(2.7, 0.2))
        b.put(door, b.t0 + 0.2, z=3, pop=0.2)
        me = person(b.C + v(0.3, 0.6), 0.0, 1.0)
        b.mover(me, lambda: b.C + v(0.3 + 2.0 * ease(level(ctx, b.t0 + 0.8, 1.6)), 0.6), z=7)
        b.tape(vox.L(ctx, "I RAN FOR THE DOOR", "मैं दरवाज़े की ओर भागा"), v(0.4, 2.6), RED, 5.4, 26, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "IT STAYED. SMILING.", "वह रुकी। मुस्कुराती।"), v(-0.4, -2.5), BLUE, 5.0, 26, 2.0, t=b.t0 + 2.4)
    beat0(B[0])
    beat1(B[1])
