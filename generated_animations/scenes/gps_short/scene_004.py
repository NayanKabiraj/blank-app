"""Shot 4 (scene 5): a stopwatch times one signal - about 0.067 s from space, quicker than an eye blink."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Dot, Ellipse, Line, Rectangle, VGroup, always_redraw

from generated_animations.avatar import expressions, gestures
from generated_animations.shared import diagrams
from generated_animations.timed import level, show

T = {"en": {"unit": "s", "cap": "straight overhead (computed)", "blink": "an eye blink is slower"},
     "hi": {"unit": "सेकंड", "cap": "ठीक ऊपर से (गणना)", "blink": "पलक झपकना इससे धीमा है"}}


def animate(ctx):
    L = T[ctx.lang]
    C, W, H = ctx.stage
    tl = ctx.timeline
    t0 = ctx.config.get("pad_before", 0.3) + 0.4
    # stopwatch on the left, readout counting up while the signal flies
    sw_c = C + np.array([-2.0, 0.6, 0.0])
    face = Circle(radius=1.5, stroke_color="#2EC5FF", stroke_width=8, fill_color="#0E1A3A", fill_opacity=1).move_to(sw_c)
    ticks = VGroup(*[Line(sw_c + 1.28 * np.array([math.cos(a), math.sin(a), 0]), sw_c + 1.42 * np.array([math.cos(a), math.sin(a), 0]),
                          color="#9AA8C7", stroke_width=4) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)])
    top = Rectangle(width=0.5, height=0.25, stroke_width=0, fill_color="#2EC5FF", fill_opacity=1).move_to(sw_c + np.array([0, 1.78, 0]))
    hand = always_redraw(lambda: Line(sw_c, sw_c + 1.2 * np.array([math.sin(2 * math.pi * min(1.0, level(ctx, t0, 1.4))),
                                                                    math.cos(2 * math.pi * min(1.0, level(ctx, t0, 1.4))), 0]),
                                      color="#FF4D6D", stroke_width=7))
    hand._dynamic = True
    show(ctx, face, 0.1, pop=0.2)
    show(ctx, ticks, 0.2, pop=0)
    show(ctx, top, 0.2, pop=0)
    ctx.add(hand, z=4)
    steps = 24
    frames = VGroup(*[ctx.text(f"{0.067 * k / steps:.3f} {L['unit']}", 56, "#FFD166", W * 0.5).move_to(sw_c + np.array([0, -2.5, 0])) for k in range(steps + 1)])

    def readout(m):
        p = level(ctx, t0, 1.4)
        idx = int((1 - (1 - p) ** 3) * steps)
        fade = 1.0 - (0 if ctx.is_last else max(0.0, min(1.0, (ctx.elapsed() - (ctx.duration - 0.2)) / 0.2)))
        for k, f in enumerate(m):
            for s in f.get_family():
                s.set_fill(opacity=(1.0 if k == idx and ctx.elapsed() > 0.2 else 0.0) * fade, family=False)
    readout(frames)
    frames.add_updater(readout)
    ctx.scene.add(frames)
    ctx.objects.append(frames)
    show(ctx, ctx.text(L["cap"], 26, "#9AA8C7", W * 0.5, "NORMAL").move_to(sw_c + np.array([0, -3.2, 0])), 0.8)
    # the signal crosses from the satellite (top right) to a phone (right), in the same 1.4 s
    S = C + np.array([2.4, 3.6, 0.0])
    P = C + np.array([2.4, -0.4, 0.0])
    show(ctx, diagrams.satellite(S, 0.6), 0.2)
    show(ctx, diagrams.phone(P, 0.7), 0.2)
    pk = always_redraw(lambda: Dot(S + np.array([0, -0.4, 0]) + (P - S + np.array([0, 1.3, 0])) * min(1.0, level(ctx, t0, 1.4)),
                                   radius=0.15, color="#F4C95D", fill_opacity=1.0 if level(ctx, t0, 1.4) < 1 else 0.0))
    pk._dynamic = True
    ctx.add(pk, z=5)
    # an eye blinks afterwards: slower than the signal
    eye_c = C + np.array([2.4, 1.6, 0.0])
    white = Ellipse(width=1.2, height=0.7, stroke_color="#FFFFFF", stroke_width=3, fill_color="#FFFFFF", fill_opacity=1).move_to(eye_c)
    pupil = Dot(eye_c, radius=0.2, color="#1A1A1A")
    show(ctx, VGroup(white, pupil), t0 + 1.8, pop=0.2)
    def lid_rect():
        p = level(ctx, t0 + 2.6, 0.5)
        h = 0.01 + (0.75 * math.sin(math.pi * p) if p < 1 else 0.0)
        return Rectangle(width=1.3, height=h, stroke_width=0, fill_color="#0B1020", fill_opacity=1).move_to(eye_c + np.array([0, 0.37 - h / 2, 0]))
    lid = always_redraw(lid_rect)
    lid._dynamic = True
    ctx.add(lid, z=6)
    show(ctx, ctx.text(L["blink"], 24, "#9AA8C7", W * 0.4, "NORMAL").move_to(eye_c + np.array([0, -0.8, 0])), t0 + 2.0)
    ctx.avatar.look_at(lambda: sw_c)
    ctx.play(gestures.present(ctx.avatar, 0.5), expressions.set_expression(ctx.avatar, "surprised", 0.4), run_time=0.6)
