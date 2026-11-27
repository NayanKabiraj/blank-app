"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): between tall buildings the direct signal is blocked and an echo arrives on a longer path; the error grows from ~5 m to ~100 m."""
from __future__ import annotations

from generated_animations.scenes.gps_echo_vox.art import satellite
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def tower(C, w, h, a, seed=0):
    g = VGroup(Rectangle(width=w, height=h, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#46506B", fill_opacity=a).move_to(C))
    for r in range(int(h / 0.7)):
        for cc in range(int(w / 0.6)):
            lit = (r * 3 + cc * 5 + seed) % 4 == 0
            g.add(Rectangle(width=0.28, height=0.34, stroke_width=0, fill_color="#F2D36B" if lit else "#2B3350", fill_opacity=a).move_to(C + v(-w / 2 + 0.4 + cc * 0.6, h / 2 - 0.5 - r * 0.7)))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B1A33", "#233B66", seed=21)
        S, P = b.C + v(-2.4, 2.3), b.C + v(1.8, -2.9)
        b.live(lambda a: satellite(S, 0.9, a), b.t0 + 0.2, z=6)
        b.put(tower(b.C + v(-0.3, -0.6), 1.9, 4.4, 1.0), b.t0 + 0.2, z=4)
        b.put(tower(b.C + v(3.9, -0.6), 1.6, 4.4, 1.0, 1), b.t0 + 0.2, z=4)
        b.put(RoundedRectangle(corner_radius=0.15, width=1.0, height=1.6, stroke_color=W_, stroke_width=4, fill_color="#171A26", fill_opacity=1).move_to(P), b.t0 + 0.3, z=6)
        b.put(Line(S + v(0.3, -0.4), b.C + v(-1.25, 1.2), color=RED, stroke_width=8), b.t0 + 0.6, z=5, pop=0)                 # direct signal, blocked
        b.text("X", 72, v(-1.5, 1.3), RED, 1.5, t=b.t0 + 1.0, z=8)
        bounce = b.C + v(3.1, 1.0)
        b.put(Line(S + v(0.3, -0.4), bounce, color=ORANGE, stroke_width=8), b.t0 + 1.4, z=5, pop=0)
        b.put(Line(bounce, P + v(0, 0.8), color=ORANGE, stroke_width=8), b.t0 + 1.8, z=5, pop=0)
        b.text(vox.L(ctx, "BLOCKED!\nONLY AN ECHO ARRIVES", "रुका हुआ सिग्नल!\nसिर्फ़ गूँज पहुँची"), 50, v(0, 4.1), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "ECHO = LONGER PATH", "गूँज = लंबा रास्ता"), v(0, -4.2), ORANGE, 6.0, 32, -2.0, t=b.t0 + 2.4)

    def beat1(b):
        b.backdrop("#0B1A33", "#233B66", seed=23)
        b.text(vox.L(ctx, "THE ERROR GROWS", "ग़लती बढ़ती है"), 64, v(0, 4.0), W_, 7.5, t=b.t0 + 0.2)

        def bars(a):
            f1, f2 = b.lv(b.t0 + 0.6, 0.8), b.lv(b.t0 + 1.6, 1.4)
            return VGroup(Rectangle(width=1.8, height=max(0.05, 0.4 * f1), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color="#5E9A5A", fill_opacity=a).move_to(b.C + v(-1.8, -3.0 + 0.2 * f1)),
                          Rectangle(width=1.8, height=max(0.05, 4.6 * f2), stroke_color=INK, stroke_width=3, stroke_opacity=a, fill_color=RED, fill_opacity=a).move_to(b.C + v(1.8, -3.0 + 2.3 * f2)))
        b.live(bars, b.t0 + 0.4, z=6)
        b.text(vox.L(ctx, "OPEN SKY\n~5 m", "खुला आसमान\n~5 मी"), 40, v(-1.8, -1.9), W_, 3.4, t=b.t0 + 1.0)
        b.text(vox.L(ctx, "CITY\n~100 m", "शहर\n~100 मी"), 40, v(1.8, 2.6), W_, 3.4, t=b.t0 + 2.2)
    beat0(B[0])
    beat1(B[1])
