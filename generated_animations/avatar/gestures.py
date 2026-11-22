"""Arm gestures for the presenter. Each returns a Manim animation (or list) to hand to scene.play()."""
from __future__ import annotations

from manim import AnimationGroup

from ..shared.motion import smooth


def _to(avatar, weights: dict, run_time: float):
    return AnimationGroup(*[avatar.pose[k].animate.set_value(weights.get(k, 0.0)) for k in avatar.pose],
                          rate_func=smooth, run_time=run_time)


def point_at(avatar, target, run_time: float = 0.5):
    """Raise the arm and keep pointing at `target` (mobject / world point / callable), even as it moves."""
    avatar.set_point_target(target)
    return _to(avatar, {"point": 1.0}, run_time)


def wave(avatar, run_time: float = 0.4):
    return _to(avatar, {"wave": 1.0}, run_time)


def present(avatar, run_time: float = 0.5):
    """Open-hand 'here is the thing' presenting pose."""
    return _to(avatar, {"present": 1.0}, run_time)


def shrug(avatar, run_time: float = 0.4):
    return _to(avatar, {"shrug": 1.0}, run_time)


def rest(avatar, run_time: float = 0.5):
    return _to(avatar, {}, run_time)
