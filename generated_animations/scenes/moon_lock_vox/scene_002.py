"""Vox look, FULL-SCREEN art - shot 2 (scenes 3-4): top view of the orbit - the Moon spins once per orbit, so its marker always faces Earth; compare with a Moon that does not spin."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def earth(C, r, a):
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#2E86D6", fill_opacity=a).move_to(C))
    g.add(Ellipse(width=r * 0.9, height=r * 0.6, stroke_width=0, fill_color="#5E9A5A", fill_opacity=a).move_to(C + v(-0.3 * r, 0.25 * r)), Ellipse(width=r * 0.6, height=r * 0.5, stroke_width=0, fill_color="#5E9A5A", fill_opacity=a).move_to(C + v(0.35 * r, -0.3 * r)))
    return g


def orbiter(C, R, ang, mode, a, r=0.42):
    """Moon at angle `ang` on an orbit of radius R around C; its red marker points to Earth (mode 'locked') or stays fixed up (mode 'fixed')."""
    P = C + v(R * math.cos(ang), R * math.sin(ang))
    g = VGroup(Circle(radius=r, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#C9CCD6", fill_opacity=a).move_to(P))
    d = v(-math.cos(ang), -math.sin(ang)) if mode == "locked" else v(0, 1)
    g.add(Circle(radius=r * 0.34, stroke_width=0, fill_color="#E2423C", fill_opacity=a).move_to(P + d * r * 0.72))
    g.add(Line(P, P + d * r * 0.72, color="#E2423C", stroke_width=5, stroke_opacity=a))
    return g


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#070D22", "#1D2A55", seed=11)
        C = b.C + v(0, -0.2)
        b.put(Circle(radius=3.1, stroke_color="#5A6AA0", stroke_width=3, fill_opacity=0), b.t0 + 0.1, z=3, pop=0)
        b.put(earth(C, 1.0, 1.0), b.t0 + 0.1, z=5)
        b.live(lambda a: orbiter(C, 3.1, (ctx.elapsed() - b.t0) * 0.9, "locked", a, 0.5), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "DOES THE MOON SPIN?", "क्या चाँद घूमता है?"), 56, v(0, 4.2), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "ONCE PER ORBIT", "एक चक्कर में एक घूमाई"), v(0, -4.2), ORANGE, 6.0, 34, -2.0, t=b.t0 + 2.0)

    def beat1(b):
        b.backdrop("#070D22", "#1D2A55", seed=13)
        for sx, mode, en, hi, col in ((-2.2, "fixed", "NO SPIN", "घूमाई नहीं", RED), (2.2, "locked", "REAL MOON", "असली चाँद", GREEN)):
            Cc = b.C + v(sx, 0.3)
            b.put(Circle(radius=1.5, stroke_color="#5A6AA0", stroke_width=3, fill_opacity=0).move_to(Cc), b.t0 + 0.2, z=3, pop=0)
            b.put(earth(Cc, 0.55, 1.0), b.t0 + 0.2, z=5)
            b.live(lambda a, Cc=Cc, mode=mode: orbiter(Cc, 1.5, (ctx.elapsed() - b.t0) * 0.9, mode, a, 0.3), b.t0 + 0.3, z=6)
            b.tape(vox.L(ctx, en, hi), v(sx, -2.4), col, 3.6, 30, -2.0 if sx < 0 else 2.0, t=b.t0 + 0.8)
        b.text(vox.L(ctx, "SAME SIDE FACES US", "एक ही तरफ़ हमारी ओर"), 52, v(0, 3.7), W_, 7.8, t=b.t0 + 0.4)
    beat0(B[0])
    beat1(B[1])
