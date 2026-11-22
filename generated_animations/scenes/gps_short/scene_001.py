"""Shot 1 (scenes 1-2): a phone finds itself, yet sends no signal - the outgoing signal is crossed out."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Line, VGroup

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams, particles
from generated_animations.timed import show

T = {"en": {"where": "Where am I?", "none": "No signal sent"}, "hi": {"where": "मैं कहाँ हूँ?", "none": "कोई सिग्नल नहीं"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    phone = diagrams.phone(C + np.array([0.0, -0.4, 0.0]), 1.5)
    dot = diagrams.location_dot(phone.get_center() + np.array([0.0, 0.15, 0.0]), r=0.17)
    ctx.add(particles.pulse_rings(dot, tl, "#FF4D6D", n=3, period=1.8, max_radius=2.3), z=1)
    show(ctx, phone, 0.2, pop=0.25, z=2)
    show(ctx, dot, 0.3, z=3)
    show(ctx, ctx.text(L["where"], 48, "#FFD166").move_to(C + np.array([0.0, -2.75, 0.0])), 0.5)

    # scene 1: the phone does not call anyone - three outgoing signal arcs, crossed out in red
    t0 = ctx.t_of(0) + 1.3
    top = phone.get_top() + np.array([0.0, 0.2, 0.0])
    for k, r in enumerate((0.55, 0.95, 1.35)):
        show(ctx, Arc(radius=r, start_angle=math.pi / 2 - 0.75, angle=1.5, arc_center=top, stroke_color="#7FD6FF", stroke_width=7),
             t0 + 0.18 * k, pop=0)
    cross = VGroup(Line(top + np.array([-0.7, 0.2, 0]), top + np.array([0.7, 1.3, 0]), color="#FF4D6D", stroke_width=12),
                   Line(top + np.array([-0.7, 1.3, 0]), top + np.array([0.7, 0.2, 0]), color="#FF4D6D", stroke_width=12))
    show(ctx, cross, t0 + 0.8, pop=0.3)
    show(ctx, ctx.text(L["none"], 34, "#FF8FA3").move_to(top + np.array([0.0, 2.0, 0.0])), t0 + 1.0)

    # scene 2: question marks drift around the phone while the answer is worked out
    t1 = ctx.t_of(1)
    base = [phone.get_center() + np.array([3.0 * math.cos(a), 2.3 * math.sin(a), 0.0]) for a in (0.35, 1.1, 2.1, 2.9, 3.9, 5.4)]
    qs = VGroup(*[ctx.text("?", 56, "#FFD166").move_to(p) for p in base])

    def drift(m):
        t = tl.t
        for k, (q, p) in enumerate(zip(m, base)):
            q.move_to(p + np.array([0.18 * math.sin(t * 1.3 + k), 0.22 * math.cos(t * 1.1 + k * 1.7), 0.0]))
    drift(qs)
    qs.add_updater(drift)
    show(ctx, qs, t1 + 0.2, pop=0)

    ctx.avatar.look_at(phone)
    ctx.play(gestures.point_at(ctx.avatar, phone, 0.5), expressions.set_expression(ctx.avatar, "curious", 0.4), run_time=0.5)
    ctx.until(t1 + 0.3)
    ctx.play(expressions.set_expression(ctx.avatar, "surprised", 0.3), run_time=0.4)
