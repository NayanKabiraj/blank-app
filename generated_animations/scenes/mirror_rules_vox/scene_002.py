"""Vox look - shot 2 (scenes 3-4): rule one (the reflection is a second late, ignore it) and rule two (on time: say good morning); the reflection copies me with a delay, then in step."""
from __future__ import annotations

from generated_animations.shared.packkit import *
from .scene_001 import mirror


def pose(t, who="me"):
    """Hand height 0..1 of a wave cycle at time t."""
    return 0.5 + 0.5 * math.sin(t * 2.4)


def person(C, hand, a, coat=BLUE, face_right=True):
    body = RoundedRectangle(corner_radius=0.22, width=0.7, height=1.0, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=coat, fill_opacity=a).move_to(C + v(0, -0.55))
    head = Circle(radius=0.28, stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#F2C9A0", fill_opacity=a).move_to(C + v(0, 0.15))
    arm = Line(C + v(0.3, -0.3), C + v(0.55, -0.3 + 0.9 * hand), color=INK, stroke_width=6, stroke_opacity=a)
    return VGroup(body, head, arm)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def scene(b, lag, t0_label):
        b.live(lambda a: mirror(b.C + v(1.4, 0.2), a), b.t0 + 0.1, z=4)
        b.live(lambda a: person(b.C + v(-1.6, 0.6), pose(ctx.elapsed() - b.t0), a), b.t0 + 0.2, z=6)
        b.live(lambda a: person(b.C + v(1.4, 0.6), pose(ctx.elapsed() - b.t0 - lag), a * level(ctx, b.t0 + 0.6, 0.4), coat="#6E8AD0"), b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "ME", "मैं"), 26, v(-1.6, -1.6), INK, 1.6, t=b.t0 + 0.5)
        b.text(vox.L(ctx, "REFLECTION", "परछाईं"), 24, v(1.4, -1.6), INK, 2.6, t=b.t0 + 0.5)

    def beat0(b):
        b.card(seed=7)
        scene(b, 1.0, 0)
        b.tape(vox.L(ctx, "RULE 1: A SECOND LATE", "नियम 1: एक सेकंड देर"), v(0, 2.5), RED, 5.4, 26, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "IGNORE IT", "अनदेखा करो"), v(0, -2.5), BLUE, 3.4, 30, 2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.card(seed=9, rot=0.5)
        scene(b, 0.0, 0)
        b.put(vox.tape(ctx, vox.L(ctx, "\"GOOD MORNING\"", "\"सुप्रभात\""), b.C + v(-0.1, 1.9), GREEN, 3.8, 26, -2.0), b.t0 + 1.0, z=8, pop=0.3)
        b.tape(vox.L(ctx, "RULE 2: ON TIME", "नियम 2: समय पर"), v(0, 2.7), RED, 4.4, 26, 2.0, t=b.t0 + 0.6)
        b.tape(vox.L(ctx, "SAY GOOD MORNING", "सुप्रभात कहो"), v(0, -2.5), BLUE, 4.4, 28, -2.0, t=b.t0 + 2.4)
    beat0(B[0])
    beat1(B[1])
