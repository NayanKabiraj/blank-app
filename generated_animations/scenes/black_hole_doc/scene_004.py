"""Shot 4 (chapter 4, scenes 16-20): time - two clocks, who sees what, gravity bends time (a warped grid), GPS clocks."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Line, ManimColor, RoundedRectangle, VGroup, VMobject, always_redraw, interpolate_color

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import blackhole, diagrams, icons, particles
from generated_animations.timed import level, show, window

T = {"their": "their clock", "your": "your clock", "slow": "slower and redder for them", "chat": ["Does time stop for me?", "No. It feels normal", "Then who sees it freeze?", "Anyone far away"],
     "bend": "gravity bends time", "high": "higher: faster", "low": "lower: slower", "gps": "GPS satellite clock", "fix": "corrected for gravity", "ph": "your phone"}


def clock(c, r, angle, col="#F5F7FA"):
    c = np.asarray(c, float)
    return VGroup(Circle(radius=r, stroke_color="#7FD6FF", stroke_width=4, fill_color=col, fill_opacity=1).move_to(c),
                  Line(c, c + 0.8 * r * np.array([math.sin(angle), math.cos(angle), 0.0]), color="#0B1020", stroke_width=6),
                  Line(c, c + 0.5 * r * np.array([math.sin(angle * 0.08), math.cos(angle * 0.08), 0.0]), color="#0B1020", stroke_width=6))


def animate(ctx):
    C, W, H = ctx.stage
    tl = ctx.timeline
    t17, t18, t19 = (ctx.t_of(i) for i in (2, 3, 4))      # chat, bending time, GPS
    # ---- scenes 16-17: two clocks, one near the hole and one far away
    BC = C + np.array([4.4, 0.2, 0.0])
    ctx.add(blackhole.black_hole(BC, 1.0, tl, alpha=window(ctx, 0.1, t18 - 0.2), disk=False), z=2)
    far = np.array([C[0] - 2.8, C[1] + 0.2, 0.0])
    ramp = 5.0
    lv = lambda: level(ctx, 1.0, ramp)
    # the falling clock slows: its hand angle integrates a rate that drops from 1 to 0.05
    def fall_angle():
        t = tl.t - ctx.start
        t0 = 1.0
        if t <= t0:
            return 1.2 * t
        l = min(1.0, (t - t0) / ramp)
        integral = ramp * (l - 0.475 * l * l) if (t - t0) < ramp else ramp * 0.525 + 0.05 * (t - t0 - ramp)
        return 1.2 * (t0 + integral)
    far_clock = always_redraw(lambda: clock(far, 0.8, 1.2 * (tl.t - ctx.start)).set_opacity(window(ctx, 0.2, t18 - 0.2)()))
    near = lambda: np.array([C[0] + 1.6 + 1.2 * lv(), C[1] + 0.2, 0.0])
    near_clock = always_redraw(lambda: clock(near(), 0.8, fall_angle(), "#" + "".join(f"{int(v):02X}" for v in (245 - 30 * lv() * 1.0, 247 - 190 * lv(), 250 - 200 * lv()))).set_opacity(window(ctx, 0.2, t18 - 0.2)()))
    for m in (far_clock, near_clock):
        m._dynamic = True
        ctx.add(m, z=4)
    beam = always_redraw(lambda: Line(near() + np.array([-0.9, 0.0, 0.0]), far + np.array([0.9, 0.0, 0.0]), stroke_width=4, stroke_opacity=0.8 * window(ctx, 0.5, t18 - 0.2)(),
                                      color=interpolate_color(ManimColor("#F5F7FA"), ManimColor("#FF4D6D"), lv())))
    beam._dynamic = True
    ctx.add(beam, z=3)
    show(ctx, ctx.text(T["their"], 30, "#F5F7FA", 3.8).move_to(far + np.array([0.0, -1.5, 0.0])), 0.5, t_out=t18 - 0.2)
    show(ctx, ctx.text(T["your"], 30, "#FF8FA3", 3.8).move_to(np.array([C[0] + 2.3, C[1] - 1.5, 0.0])), 0.5, t_out=t18 - 0.2)
    show(ctx, ctx.text(T["slow"], 28, "#FFD166", 6.5).move_to(C + np.array([0.2, 2.4, 0.0])), 2.2, t_out=t17)
    # scene 17: chat bubbles one at a time
    for k, txt in enumerate(T["chat"]):
        t_k = t17 + 0.3 if k == 0 else ctx.tt(2, k)
        t_n = ctx.tt(2, k + 1) if k < 3 else t18 - 0.2
        viewer = k % 2 == 0
        box = RoundedRectangle(corner_radius=0.3, width=4.6, height=0.95, stroke_color="#6D8FD6" if viewer else "#4CD97B", stroke_width=3, fill_color="#27427A" if viewer else "#1E6B4E", fill_opacity=1).move_to(C + np.array([0.4, 2.3, 0.0]))
        show(ctx, VGroup(box, ctx.text(txt, 28, "#F5F7FA", 4.2).move_to(box)), t_k, t_out=t_n, z=7)
    # ---- scene 18: gravity bends time - a sagging grid with a slow clock low down
    M = C + np.array([1.9, -0.2, 0.0])
    depth = lambda: 1.5 * level(ctx, t18 + 0.3, 2.5)
    N = 60
    for gy in np.linspace(-1.8, 2.2, 7):
        def hline(gy=gy):
            pts = []
            for u in np.linspace(-4.5, 4.5, N):
                sag = depth() * math.exp(-(u / 1.8) ** 2) * (1.0 - 0.18 * abs(gy - 0.2))
                pts.append(M + np.array([u, gy - 0.2 - sag * (1 if gy > -1.0 else 0.4), 0.0]))
            m = VMobject(stroke_color="#4A6FA5", stroke_width=3, stroke_opacity=0.9 * window(ctx, t18 + 0.2, t19 - 0.2)(), fill_opacity=0)
            m.set_points_as_corners(pts)
            return m
        g = always_redraw(hline)
        g._dynamic = True
        ctx.add(g, z=2)
    lo = always_redraw(lambda: clock(M + np.array([0.0, -1.0 - depth() * 0.7, 0.0]), 0.5, 0.6 * (tl.t - ctx.start)).set_opacity(window(ctx, t18 + 1.0, t19 - 0.2)()))
    hi = always_redraw(lambda: clock(M + np.array([3.0, 1.9, 0.0]), 0.5, 1.3 * (tl.t - ctx.start)).set_opacity(window(ctx, t18 + 1.0, t19 - 0.2)()))
    for m in (lo, hi):
        m._dynamic = True
        ctx.add(m, z=5)
    show(ctx, ctx.text(T["bend"], 42, "#FFD166", 8.0).move_to(C + np.array([0.2, 2.55, 0.0])), t18 + 0.4, t_out=t19 - 0.2)
    show(ctx, ctx.text(T["low"], 26, "#FF8FA3", 3.0, "NORMAL").move_to(M + np.array([0.0, -2.5, 0.0])), t18 + 1.6, t_out=t19 - 0.2)
    show(ctx, ctx.text(T["high"], 26, "#4CD97B", 3.0, "NORMAL").move_to(M + np.array([3.0, 1.2, 0.0])), t18 + 1.6, t_out=t19 - 0.2)
    # ---- scene 19: GPS satellite clocks are corrected
    E = C + np.array([1.2, -0.2, 0.0])
    class _Vis:
        def __init__(self, f):
            self.f = f

        def get_value(self):
            return max(0.001, self.f())
    ctx.add(diagrams.earth(E, 1.05, tl, grow=_Vis(window(ctx, t19, None))), z=2)
    sat = lambda: E + np.array([2.4 * math.cos(0.7 * tl.t), 1.9 * math.sin(0.7 * tl.t), 0.0])
    sm = always_redraw(lambda: diagrams.satellite(sat(), 0.5).set_opacity(window(ctx, t19, None)()))
    sm._dynamic = True
    ctx.add(sm, z=4)
    ctx.add(particles.pulse_rings(sat, tl, "#F4C95D", n=2, period=1.6, max_radius=1.0, width=2.4), z=1)
    show(ctx, ctx.text(T["gps"], 30, "#F4C95D", 5.0).move_to(C + np.array([-2.4, 2.4, 0.0])), t19 + 0.5)
    show(ctx, ctx.text(T["fix"], 32, "#4CD97B", 5.5).move_to(C + np.array([-2.2, -2.3, 0.0])), ctx.tt(3, 1))
    show(ctx, icons.icon("phone", 0.9).move_to(E + np.array([3.7, -1.2, 0.0])), t19 + 1.0)
    ctx.avatar.look_at(lambda: near())
    ctx.play(gestures.point_at(ctx.avatar, lambda: near(), 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.6)
    ctx.until(t17)
    ctx.play(expressions.set_expression(ctx.avatar, "thinking", 0.3), gestures.present(ctx.avatar, 0.5), run_time=0.6)
    ctx.until(t18)
    ctx.play(expressions.set_expression(ctx.avatar, "excited", 0.3), run_time=0.4)
    ctx.until(t19)
    ctx.play(gestures.point_at(ctx.avatar, sat, 0.5), run_time=0.5)
