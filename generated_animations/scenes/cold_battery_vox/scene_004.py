"""Vox look, FULL-SCREEN art - shot 4 (scenes 7-8): warming the phone speeds the particles up and the charge returns; warm it before charging; the closing question."""
from __future__ import annotations

from generated_animations.scenes.cold_battery_vox.scene_001 import cold_phone, snow
from generated_animations.scenes.cold_battery_vox.scene_002 import battery, ions
from generated_animations.shared.packkit import *

W_ = "#FFFFFF"


def animate(ctx):
    B = [Beat(ctx, i, 2) for i in range(2)]

    def beat0(b):
        b.backdrop("#0B2A4A", "#6FA8CE", seed=31)
        C = b.C + v(0, -1.6)

        def warm(a):
            t = ctx.elapsed() - b.t0
            f = min(1.0, max(0.0, (t - 0.4) / 2.4))
            return VGroup(battery(C, a, f < 0.5), ions(C, t, a, 0.1 + 0.45 * f, cold=f < 0.5))
        b.live(warm, b.t0 + 0.2, z=5)
        b.live(lambda a: cold_phone(b.C + v(0, 2.3), 0.5, 0.3, (ctx.elapsed() - b.t0) < 2.6, a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "WARM IT UP", "इसे गर्म करें"), 64, v(0, 4.4), W_, 7.2, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "THE CHARGE COMES BACK", "चार्ज वापस आ जाता है"), v(0, -4.0), GREEN, 6.6, 32, -2.0, t=b.t0 + 2.2)
        b.tape(vox.L(ctx, "WARM IT BEFORE CHARGING", "चार्ज से पहले गर्म करें"), v(0, 0.35), ORANGE, 7.0, 28, 2.0, t=b.t0 + 3.0)

    def beat1(b):
        b.backdrop("#0B2A4A", "#6FA8CE", seed=33)
        b.live(lambda a: snow(b, a), b.t0 + 0.1, z=3)
        b.live(lambda a: cold_phone(b.C + v(0, -0.4), 0.95, 0.3, False, a), b.t0 + 0.2, z=6)
        b.text(vox.L(ctx, "WHERE DID YOUR\nPHONE DIE ON YOU?", "आपका फ़ोन कहाँ\nबंद हुआ?"), 58, v(0, 4.0), W_, 7.8, t=b.t0 + 0.3)
        b.tape(vox.L(ctx, "TELL ME BELOW", "नीचे बताइए"), v(0, -4.0), RED, 5.4, 36, -1.5, t=b.t0 + 1.4)
    beat0(B[0])
    beat1(B[1])
