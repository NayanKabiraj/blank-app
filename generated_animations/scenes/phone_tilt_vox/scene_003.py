"""Vox look - shot 3 (scenes 5-6): the gyroscope is quick but drifts; the phone blends it with gravity so the answer is both fast and honest."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def curve(pts, col, a, w=6):
    from manim import VMobject
    return VMobject(stroke_color=col, stroke_width=w, stroke_opacity=a).set_points_as_corners(pts)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    X0, X1 = -2.8, 2.8

    def beat0(b):
        b.card(seed=11)
        # a spinning gyroscope wheel and a drift plot: the true angle (dashed) versus the gyroscope's (drifting) estimate
        def wheel(a):
            c = b.C + v(-1.8, 1.4)
            g = VGroup(Circle(radius=0.8, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color="#8895A8", fill_opacity=a).move_to(c))
            for k in range(4):
                an = ctx.elapsed() * 6 + k * math.pi / 2
                g.add(Line(c, c + v(0.75 * math.cos(an), 0.75 * math.sin(an)), color=CREAM, stroke_width=6, stroke_opacity=a))
            return g
        b.live(wheel, b.t0 + 0.2, z=5)
        b.text(vox.L(ctx, "GYROSCOPE", "जाइरोस्कोप"), 26, v(-1.8, 2.6), INK, 3.0, t=b.t0 + 0.4)
        n = lambda: max(2, int(40 * level(ctx, b.t0 + 0.6, 3.2)))
        b.live(lambda a: curve([b.C + v(X0 + (X1 - X0) * k / 40, -1.2 + 0.5 * math.sin(k * 0.35)) for k in range(41)], "#B7AE9C", a * 0.8, 4), b.t0 + 0.6, z=4)
        b.live(lambda a: curve([b.C + v(X0 + (X1 - X0) * k / 40, -1.2 + 0.5 * math.sin(k * 0.35) + 0.02 * k) for k in range(n())], RED, a), b.t0 + 0.6, z=6)
        b.tape(vox.L(ctx, "QUICK...", "फुर्तीला..."), v(1.8, 1.9), GREEN, 2.8, 30, 2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "...BUT IT DRIFTS", "...पर भटकता है"), v(0.4, -2.4), RED, 4.0, 28, -2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.card(seed=13, rot=-0.5)
        true = lambda k: 0.55 * math.sin(k * 0.35)
        N = lambda: max(2, int(40 * level(ctx, b.t0 + 0.5, 3.0)))
        b.live(lambda a: curve([b.C + v(X0 + (X1 - X0) * k / 40, 0.9 + true(k) + 0.3 * math.sin(k * 2.3)) for k in range(N())], BLUE, a * 0.9, 4), b.t0 + 0.5, z=5)      # gravity sensor: honest but jittery
        b.live(lambda a: curve([b.C + v(X0 + (X1 - X0) * k / 40, 0.2 + true(k) + 0.025 * k) for k in range(N())], ORANGE, a * 0.9, 4), b.t0 + 0.5, z=5)                 # gyroscope: smooth but drifting
        b.live(lambda a: curve([b.C + v(X0 + (X1 - X0) * k / 40, -1.0 + true(k)) for k in range(N())], GREEN, a, 9), b.t0 + 1.4, z=6)                                    # the blend
        b.text(vox.L(ctx, "GRAVITY: HONEST", "गुरुत्व: सच्चा"), 22, v(-1.6, 2.5), BLUE, 3.2, t=b.t0 + 0.8)
        b.text(vox.L(ctx, "GYRO: FAST", "जाइरो: तेज़"), 22, v(1.8, 2.5), ORANGE, 2.6, t=b.t0 + 1.0)
        b.tape(vox.L(ctx, "BLEND = FAST + HONEST", "मेल = तेज़ + सच्चा"), v(0, -2.4), GREEN, 5.0, 28, 2.0, t=b.t0 + 2.2)
    beat0(B[0])
    beat1(B[1])
