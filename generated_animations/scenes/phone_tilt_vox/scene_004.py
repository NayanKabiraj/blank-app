"""Vox look - shot 4 (scenes 7-8): the screen ignores wobbles and flips only after a real turn; closing: the phone knows up even in the dark."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.card(seed=15)
        t_turn = b.t0 + 3.2

        def pos_angle():
            wob = math.radians(8) * math.sin((ctx.elapsed() - b.t0) * 9.0) * (1 - level(ctx, t_turn - 0.2, 0.2))
            turn = math.radians(90) * ease(level(ctx, t_turn, 0.9))
            return wob + turn
        b.live(lambda a: phone(1.3).rotate(pos_angle()).move_to(b.C + v(-1.5, 0.4)).set_opacity(a), b.t0 + 0.2, z=5)

        def screen_arrow(a):                                      # the picture inside the screen only flips after the turn has lasted a moment
            flipped = level(ctx, t_turn + 0.6, 0.2)
            ang = math.radians(90) * flipped
            c = b.C + v(-1.5, 0.4) + v(0.0, 0.0)
            return Polygon(c + v(0, 0.35), c + v(-0.2, -0.1), c + v(0.2, -0.1), stroke_width=0, fill_color=RED, fill_opacity=a).rotate(-ang if flipped > 0.5 else 0, about_point=c)
        b.live(screen_arrow, b.t0 + 0.4, z=7)
        # a timer bar: "wait..." fills before the flip
        b.live(lambda a: VGroup(Rectangle(width=2.4, height=0.4, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_opacity=0).move_to(b.C + v(2.0, 0.8)),
                                Rectangle(width=max(0.02, 2.4 * level(ctx, t_turn, 0.8)), height=0.3, stroke_width=0, fill_color=ORANGE, fill_opacity=a).move_to(b.C + v(0.8 + max(0.02, 2.4 * level(ctx, t_turn, 0.8)) / 2, 0.8))), b.t0 + 0.6, z=6)
        b.text(vox.L(ctx, "WAIT...", "रुको..."), 30, v(2.0, 1.5), INK, 2.4, t=b.t0 + 0.6)
        b.tape(vox.L(ctx, "WOBBLE: IGNORED", "हिलावट: अनदेखी"), v(1.6, -1.0), BLUE, 3.8, 26, 2.0, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "REAL TURN: FLIP", "असली मोड़: पलटो"), v(1.0, -2.3), GREEN, 4.0, 26, -2.0, t=t_turn)

    def beat1(b):
        b.card(seed=17, rot=0.5)
        b.put(Rectangle(width=7.0, height=5.4, stroke_width=0, fill_color="#1B2238", fill_opacity=1).move_to(b.C + v(0, 0.1)), b.t0 + 0.1, z=3, pop=0)
        for k in range(8):
            b.put(Circle(radius=0.05, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).move_to(b.C + v(-3.0 + k * 0.85, 2.3 + 0.2 * math.sin(k * 2))), b.t0 + 0.2, z=4, pop=0)
        b.put(phone(1.6, on=False).move_to(b.C + v(0, 0.0)), b.t0 + 0.4, z=5, pop=0.3)
        b.live(lambda a: VGroup(Line(b.C + v(0, 0.5), b.C + v(0, 2.0 + 0.15 * math.sin(ctx.elapsed() * 3)), color=YEL, stroke_width=8, stroke_opacity=a),
                                Polygon(b.C + v(0, 2.45), b.C + v(-0.3, 1.9), b.C + v(0.3, 1.9), stroke_width=0, fill_color=YEL, fill_opacity=a)), b.t0 + 0.8, z=6)
        b.text(vox.L(ctx, "UP", "ऊपर"), 40, v(0.9, 1.5), YEL, 1.6, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "EVEN IN THE DARK", "अँधेरे में भी"), v(0, -2.0), BLUE, 4.4, 28, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "PART 3: YOU CHOOSE", "भाग 3: आप बताइए"), v(0, -2.8), RED, 4.6, 26, 2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
