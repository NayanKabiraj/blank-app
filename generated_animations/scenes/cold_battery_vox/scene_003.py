"""Vox look, FULL-SCREEN art - shot 3 (scenes 5-6): slow particles cannot deliver enough voltage when the phone asks for power; the phone shuts down although charge is left."""
from __future__ import annotations

from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B2A4A", "#4A7FA8", seed=21)
        b.text(vox.L(ctx, "VOLTAGE", "वोल्टेज"), 72, v(0, 4.1), W_, 6.5, t=b.t0 + 0.2)

        def gauge(a):
            k = b.lv(b.t0 + 0.8, 2.2)
            h = 6.0 * (1 - 0.6 * k)
            return VGroup(Rectangle(width=2.6, height=6.0, stroke_color=W_, stroke_width=4, stroke_opacity=a, fill_opacity=0).move_to(b.C + v(0, 0.2)),
                          Rectangle(width=2.6, height=max(0.05, h), stroke_width=0, fill_color="#E2423C" if k > 0.6 else "#5E9A5A", fill_opacity=a).move_to(b.C + v(0, -2.8 + h / 2)),
                          Line(b.C + v(-2.0, -0.6), b.C + v(2.0, -0.6), color="#FFD640", stroke_width=6, stroke_opacity=a))
        b.live(gauge, b.t0 + 0.3, z=6)
        b.text(vox.L(ctx, "PHONE\nNEEDS POWER", "फ़ोन को\nबिजली चाहिए"), 36, v(-3.0, 0.6), W_, 2.4, t=b.t0 + 0.8)
        b.tape(vox.L(ctx, "LIMIT", "सीमा"), v(3.0, -0.6), ORANGE, 2.4, 30, 2.0, t=b.t0 + 1.4)
        b.tape(vox.L(ctx, "NOT ENOUGH VOLTAGE", "वोल्टेज कम"), v(0, -4.0), RED, 6.0, 34, -2.0, t=b.t0 + 2.6)

    def beat1(b):
        b.backdrop("#0B2A4A", "#4A7FA8", seed=23)
        from generated_animations.scenes.cold_battery_vox.scene_001 import cold_phone
        b.live(lambda a: cold_phone(b.C + v(-1.4, -0.4), 0.95, 0.3, True, a), b.t0 + 0.2, z=6)
        b.put(RoundedRectangle(corner_radius=0.4, width=3.6, height=2.2, stroke_color=INK, stroke_width=4, fill_color="#FFFDF5", fill_opacity=1).move_to(b.C + v(2.4, 0.8)).rotate(0.06), b.t0 + 0.6, z=5, pop=0.2)
        b.text(vox.L(ctx, "30% LEFT\nINSIDE", "30% अंदर\nबाक़ी"), 48, v(2.4, 0.8), INK, 3.2, t=b.t0 + 0.9, z=7)
        b.text(vox.L(ctx, "SHUTS OFF TO STAY SAFE", "सुरक्षा के लिए बंद"), 46, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.text("?", 150, v(2.4, -2.1), "#FFD640", 2.0, t=b.t0 + 2.0, z=8)
        b.tape(vox.L(ctx, "IS THE CHARGE GONE?", "क्या चार्ज ख़त्म है?"), v(0, -4.0), RED, 6.0, 34, -2.0, t=b.t0 + 1.8)
    beat0(B[0])
    beat1(B[1])
