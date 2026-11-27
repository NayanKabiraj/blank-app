"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): GPS is timing (a signal travels from a satellite to a phone); four satellites fix a place."""
from __future__ import annotations

from generated_animations.scenes.gps_echo_vox.art import satellite
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def pulses(A, Bp, t, a, n=3, col=ORANGE):
    g = VGroup()
    for i in range(n):
        f = ((t * 0.55) + i / n) % 1.0
        P = A * (1 - f) + Bp * f
        g.add(Circle(radius=0.12 + 0.22 * f, stroke_width=0, fill_color=col, fill_opacity=a * (1 - 0.6 * f)).move_to(P))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B1A33", "#2A4A78", seed=11)
        S, P = b.C + v(0, 2.0), b.C + v(0, -2.6)
        b.live(lambda a: satellite(S, 1.4, a), b.t0 + 0.2, z=6)
        b.put(RoundedRectangle(corner_radius=0.2, width=1.5, height=2.4, stroke_color=W_, stroke_width=4, fill_color="#171A26", fill_opacity=1).move_to(P), b.t0 + 0.3, z=6)
        b.live(lambda a: pulses(S + v(0, -0.6), P + v(0, 1.0), ctx.elapsed() - b.t0, a), b.t0 + 0.5, z=5)
        b.text(vox.L(ctx, "GPS = TIMING", "GPS = समय"), 80, v(0, 4.0), W_, 7.5, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "HOW LONG DID IT TAKE?", "कितनी देर लगी?"), v(0, -0.2), ORANGE, 6.2, 34, -2.0, t=b.t0 + 1.6)

    def beat1(b):
        b.backdrop("#0B1A33", "#2A4A78", seed=13)
        P = b.C + v(0, -1.2)
        sats = [v(-3.1, 3.4), v(3.1, 3.4), v(-3.5, 0.8), v(3.5, 0.8)]
        for i, sp in enumerate(sats):
            b.live(lambda a, sp=sp: satellite(b.C + sp, 0.7, a), b.t0 + 0.2 + 0.25 * i, z=6)
            b.live(lambda a, sp=sp: pulses(b.C + sp, P, ctx.elapsed() - b.t0, a, 2), b.t0 + 0.6, z=5)
        b.put(RoundedRectangle(corner_radius=0.2, width=1.3, height=2.1, stroke_color=W_, stroke_width=4, fill_color="#171A26", fill_opacity=1).move_to(P), b.t0 + 0.3, z=6)
        b.put(Circle(radius=0.22, stroke_color=W_, stroke_width=3, fill_color="#2E86D6", fill_opacity=1).move_to(P + v(0, 0.2)), b.t0 + 0.4, z=7)
        b.text(vox.L(ctx, "4 SATELLITES =\nYOUR PLACE", "4 सैटेलाइट =\nआपकी जगह"), 64, v(0, -3.2), W_, 7.5, t=b.t0 + 0.4)
        b.tape(vox.L(ctx, "IN A CITY?", "शहर में?"), v(0, 4.3), RED, 4.0, 40, 2.0, t=b.t0 + 2.0)
    beat0(B[0])
    beat1(B[1])
