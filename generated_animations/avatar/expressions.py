"""Facial expressions: target values for the avatar's face trackers, tweened by `set_expression`."""
from __future__ import annotations

from manim import AnimationGroup

from ..shared.motion import smooth

# brow_raise: eyebrows up (+) / down (-);  brow_tilt: inner ends up (+, worried/curious) / down (-, determined)
# smile: mouth curvature (+ smile, - frown);  eye_open: 1 normal, >1 wide, <1 squint;  mouth_o: resting open "o"
EXPRESSIONS = {
    "neutral":   dict(brow_raise=0.0,  brow_tilt=0.0,  smile=0.35, eye_open=1.0,  mouth_o=0.0),
    "happy":     dict(brow_raise=0.1,  brow_tilt=0.0,  smile=1.0,  eye_open=0.85, mouth_o=0.0),
    "surprised": dict(brow_raise=0.9,  brow_tilt=0.2,  smile=0.0,  eye_open=1.35, mouth_o=0.45),
    "curious":   dict(brow_raise=0.45, brow_tilt=0.5,  smile=0.2,  eye_open=1.1,  mouth_o=0.0),
    "thinking":  dict(brow_raise=0.2,  brow_tilt=-0.3, smile=0.0,  eye_open=0.9,  mouth_o=0.0),
    "excited":   dict(brow_raise=0.6,  brow_tilt=0.0,  smile=1.2,  eye_open=1.25, mouth_o=0.25),
}


def set_expression(avatar, name: str, run_time: float = 0.35):
    """Animation that eases the face into expression `name` (use inside scene.play / alongside other plays)."""
    target = EXPRESSIONS[name]
    return AnimationGroup(*[avatar.expr[k].animate.set_value(v) for k, v in target.items()],
                          rate_func=smooth, run_time=run_time)
