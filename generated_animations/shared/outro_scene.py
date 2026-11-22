"""The closing scene every generated video ends with (appended by the pipeline, narration from shorts.outro):
the presenter waves while Like / Share / Subscribe buttons pop in one by one."""
from __future__ import annotations

import numpy as np
from manim import FadeIn, Indicate, RoundedRectangle, Text, VGroup

from ..avatar import expressions, gestures
from ..runtime import STAGE_Y
from . import particles, typography
from .motion import ease_out_back

LABELS = {"en": ("Like", "Share", "Subscribe"), "hi": ("लाइक", "शेयर", "सब्सक्राइब")}
COLORS = ("#FF4D6D", "#2EC5FF", "#FF2D2D")


def _button(label: str, color: str, lang: str) -> VGroup:
    t = Text(label, font_size=40, weight="BOLD", color="#FFFFFF", font="Noto Sans Devanagari" if lang == "hi" else "Noto Sans")
    box = RoundedRectangle(corner_radius=0.35, width=max(3.4, t.width + 0.9), height=1.1, stroke_width=0,
                           fill_color=color, fill_opacity=1)
    t.move_to(box)
    return VGroup(box, t)


def animate(ctx):
    lang = ctx.config.get("lang", "en")
    ctx.headline("Thanks for watching!" if lang == "en" else "धन्यवाद!", "#FFD166")
    buttons = VGroup(*[_button(l, c, lang) for l, c in zip(LABELS[lang], COLORS)]).arrange(np.array([0, -1, 0]), buff=0.45)
    buttons.move_to((0, STAGE_Y, 0))
    ctx.avatar.look_at(None)
    ctx.play(expressions.set_expression(ctx.avatar, "happy", 0.4), gestures.wave(ctx.avatar, 0.5), run_time=0.6)
    ctx.beat(0)
    for i, b in enumerate(buttons):
        if i == 1:
            ctx.beat(1)
        ctx.add(b, z=3)
        ctx.play(FadeIn(b, scale=0.6, rate_func=ease_out_back), run_time=0.5)
        ctx.play(Indicate(b, scale_factor=1.08), run_time=0.4)
    spark = particles.Sparkle(buttons[2].get_center(), ctx.timeline, "#FFD166", n=24, speed=2.0, life=1.0)
    ctx.add(spark, z=5)
    spark.restart()
    ctx.pad(reserve=0.5)
