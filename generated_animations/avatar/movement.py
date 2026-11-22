"""Avatar movement: hop, slide aside for a full-screen illustration, return."""
from __future__ import annotations

from manim import AnimationGroup

from ..shared.motion import ease_in_out_cubic, there_and_back


def move_to(avatar, x: float, y: float, scale: float | None = None, run_time: float = 0.8):
    anims = [avatar.x.animate.set_value(x), avatar.y.animate.set_value(y)]
    if scale is not None:
        anims.append(avatar.s.animate.set_value(scale))
    return AnimationGroup(*anims, rate_func=ease_in_out_cubic, run_time=run_time)


def move_aside(avatar, frame_w: float, frame_h: float, run_time: float = 0.7):
    """Shrink into the bottom corner so a full-screen illustration owns the frame."""
    return move_to(avatar, -frame_w * 0.34, -frame_h * 0.49, 0.6, run_time)


def hop(avatar, height: float = 0.5, run_time: float = 0.5):
    y0 = avatar.y.get_value()
    return avatar.y.animate(rate_func=there_and_back, run_time=run_time).set_value(y0 + height)


def turn_to_stage(avatar, amount: float = 1.0, run_time: float = 0.5):
    return avatar.facing.animate(run_time=run_time).set_value(amount)
