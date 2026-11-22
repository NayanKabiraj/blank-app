"""Scene-to-scene transitions (spec section 10): sketch reveal, erase, paper wipe, zoom, shape
transformation (line-draw), crossfade. Each clears the previous scene's mobjects and resets the
camera, so the next storyboard scene starts from a clean, centred frame.
"""
from __future__ import annotations

from manim import DOWN, FadeOut, LEFT, RIGHT, Mobject, UP

from . import camera_controller


def apply(manim_scene, transition: str, mobjects: list[tuple[Mobject, object]]) -> None:
    group = [m for m, _ in mobjects]
    if not group:
        camera_controller.reset(manim_scene)
        return

    if transition == "cut":
        manim_scene.remove(*group)
    elif transition == "erase":
        manim_scene.play(*[FadeOut(m, shift=UP * 0.3) for m in group], run_time=0.5)
    elif transition == "paper_wipe":
        manim_scene.play(*[FadeOut(m, shift=LEFT * 4) for m in group], run_time=0.6)
    elif transition == "zoom":
        manim_scene.play(*[FadeOut(m, scale=1.6) for m in group], run_time=0.6)
    elif transition == "line_draw":
        manim_scene.play(*[FadeOut(m, shift=RIGHT * 4) for m in group], run_time=0.6)
    elif transition == "sketch_reveal":
        manim_scene.play(*[FadeOut(m) for m in group], run_time=0.4)
    else:   # crossfade, default
        manim_scene.play(*[FadeOut(m) for m in group], run_time=0.5)

    camera_controller.reset(manim_scene)
