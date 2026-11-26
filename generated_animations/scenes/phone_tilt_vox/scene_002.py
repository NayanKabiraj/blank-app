"""Vox look - shot 2 (scenes 3-4): a speck of silicon on springs leans when the chip tilts; the lean becomes a signal that says where gravity pulls."""
from __future__ import annotations

from generated_animations.shared.packkit import *


def spring(a, b_, n=7, amp=0.12):
    from manim import VMobject
    pts = [a + (b_ - a) * k / (n * 2) + (v(0, amp) if k % 2 else v(0, -amp)) * (0 < k < n * 2) for k in range(n * 2 + 1)]
    return VMobject(stroke_color=INK, stroke_width=4).set_points_as_corners(pts)


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]
    tilt = lambda t0: math.radians(26) * math.sin((ctx.elapsed() - t0) * 1.6) * level(ctx, t0 + 0.6, 0.6)

    def chip(b, a, scale=1.0):
        th = tilt(b.t0)
        c = b.C + v(-0.9, 0.3)
        frame = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.2, stroke_color=INK, stroke_width=5, stroke_opacity=a, fill_color=CREAM, fill_opacity=a).move_to(c).rotate(th, about_point=c)
        off = -0.55 * math.sin(th) * 2.0                        # the speck slides toward the lower side
        speck = Rectangle(width=0.7, height=0.7, stroke_color=INK, stroke_width=4, stroke_opacity=a, fill_color="#8895A8", fill_opacity=a).move_to(c + v(off, 0)).rotate(th, about_point=c)
        l = spring(c + v(-1.45, 0), c + v(off - 0.35, 0)).rotate(th, about_point=c).set_stroke(opacity=a)
        r = spring(c + v(off + 0.35, 0), c + v(1.45, 0)).rotate(th, about_point=c).set_stroke(opacity=a)
        return VGroup(frame, l, r, speck)

    def beat0(b):
        b.card(seed=7)
        b.live(lambda a: chip(b, a), b.t0 + 0.2, z=5)
        b.tape(vox.L(ctx, "A SPECK OF SILICON", "सिलिकॉन का कण"), v(1.0, 2.2), BLUE, 4.6, 28, 2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "ON TINY SPRINGS", "नन्हे स्प्रिंग पर"), v(-0.6, -2.0), ORANGE, 4.2, 28, -2.0, t=b.t0 + 1.6)
        b.live(lambda a: Line(b.C + v(2.6, 1.2), b.C + v(2.6, -0.4), color=RED, stroke_width=7, stroke_opacity=a * level(ctx, b.t0 + 1.2, 0.4)), b.t0 + 1.2, z=6)
        b.text(vox.L(ctx, "GRAVITY", "गुरुत्व"), 24, v(2.6, -0.9), RED, 2.2, t=b.t0 + 1.4)

    def beat1(b):
        b.card(seed=9, rot=0.5)
        b.live(lambda a: chip(b, a), b.t0 + 0.2, z=5)
        # the speck's sideways offset is drawn as a live signal trace
        def trace(a):
            from manim import VMobject
            pts = [b.C + v(-2.7 + 5.4 * k / 40, -2.0 + 0.55 * math.sin(math.radians(26)) * math.sin((ctx.elapsed() - 0.05 * (40 - k) - b.t0) * 1.6) * 2.0) for k in range(41)]
            return VMobject(stroke_color=RED, stroke_width=6, stroke_opacity=a).set_points_as_corners(pts)
        b.live(trace, b.t0 + 0.6, z=6)
        b.tape(vox.L(ctx, "LEAN = ELECTRICAL SIGNAL", "झुकाव = बिजली का संकेत"), v(0, 2.4), RED, 5.6, 26, -2.0, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "PHONE FINDS DOWN", "फ़ोन ढूँढता है नीचे"), v(1.4, -2.6), GREEN, 4.4, 26, 2.0, t=b.t0 + 2.4)
    beat0(B[0])
    beat1(B[1])
