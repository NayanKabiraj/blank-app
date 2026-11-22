"""Camera movement (spec section 10/11): zoom in/out, pan in four directions, focus on an
element, follow an element. Implemented on Manim's `MovingCameraScene` camera frame, which is
how Manim itself recommends camera moves - no custom camera math needed.
"""
from __future__ import annotations

from manim import DOWN, LEFT, RIGHT, UP, Mobject

from ..schemas.storyboard_schema import SceneCamera

PAN_DISTANCE = 1.2
ZOOM_IN_SCALE = 0.72
ZOOM_OUT_SCALE = 1.25


def apply(manim_scene, camera: SceneCamera, mobjects: list[tuple[Mobject, object]]) -> None:
    frame = manim_scene.camera.frame
    focus_mobj = None
    if camera.focus_on:
        for mobj, elem in mobjects:
            if elem.name == camera.focus_on:
                focus_mobj = mobj
                break

    if camera.movement == "static":
        return
    if camera.movement == "slow_zoom_in":
        target = frame.copy().scale(ZOOM_IN_SCALE)
        if focus_mobj is not None:
            target.move_to(focus_mobj)
        manim_scene.play(frame.animate.become(target), run_time=1.2)
    elif camera.movement == "slow_zoom_out":
        manim_scene.play(frame.animate.scale(ZOOM_OUT_SCALE), run_time=1.2)
    elif camera.movement == "pan_left":
        manim_scene.play(frame.animate.shift(LEFT * PAN_DISTANCE), run_time=1.0)
    elif camera.movement == "pan_right":
        manim_scene.play(frame.animate.shift(RIGHT * PAN_DISTANCE), run_time=1.0)
    elif camera.movement == "pan_up":
        manim_scene.play(frame.animate.shift(UP * PAN_DISTANCE), run_time=1.0)
    elif camera.movement == "pan_down":
        manim_scene.play(frame.animate.shift(DOWN * PAN_DISTANCE), run_time=1.0)
    elif camera.movement in ("focus", "follow") and focus_mobj is not None:
        manim_scene.play(frame.animate.move_to(focus_mobj).scale(ZOOM_IN_SCALE), run_time=1.0)


def reset(manim_scene) -> None:
    """Returns the camera frame to its default framing - called between storyboard scenes so
    one scene's zoom/pan doesn't carry into the next."""
    manim_scene.play(manim_scene.camera.frame.animate.set(width=manim_scene.camera.frame_width)
                     .move_to((0, 0, 0)), run_time=0.6)
