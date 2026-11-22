"""Picks the camera movement, transition and default element set for a scene template (spec
section 9/11): hook, explainer_diagram, comparison, timeline, takeaway. These are defaults a
scene_planner starts from, not hard rules - a caller can always override camera/elements/
transition per scene.
"""
from __future__ import annotations

from ..schemas.storyboard_schema import CameraMovement, SceneCamera, SceneElement, Transition

TEMPLATE_CAMERA: dict[str, CameraMovement] = {
    "hook": "slow_zoom_in",
    "explainer_diagram": "static",
    "comparison": "pan_left",
    "timeline": "pan_right",
    "takeaway": "slow_zoom_in",
}

TEMPLATE_TRANSITION: dict[str, Transition] = {
    "hook": "sketch_reveal",
    "explainer_diagram": "crossfade",
    "comparison": "line_draw",
    "timeline": "crossfade",
    "takeaway": "zoom",
}


def default_camera(template: str, focus_on: str | None = None) -> SceneCamera:
    return SceneCamera(movement=TEMPLATE_CAMERA.get(template, "static"), focus_on=focus_on)


def default_transition(template: str) -> str:
    return TEMPLATE_TRANSITION.get(template, "crossfade")


def default_elements(template: str, headline: str) -> list[SceneElement]:
    if template == "hook":
        return [SceneElement(type="svg_illustration", name="hook_subject", animation="progressive_stroke_draw"),
                SceneElement(type="label", name="headline", text=headline, animation="pop_in")]
    if template == "comparison":
        return [SceneElement(type="diagram", name="side_a", animation="progressive_stroke_draw"),
                SceneElement(type="diagram", name="side_b", animation="progressive_stroke_draw"),
                SceneElement(type="arrow", name="vs_arrow", animation="draw_from_start")]
    if template == "timeline":
        return [SceneElement(type="diagram", name="timeline_track", animation="progressive_stroke_draw"),
                SceneElement(type="arrow", name="progress_arrow", animation="draw_from_start")]
    if template == "takeaway":
        return [SceneElement(type="label", name="takeaway_text", text=headline, animation="pop_in"),
                SceneElement(type="highlight", name="emphasis", animation="fade_in")]
    return [SceneElement(type="svg_illustration", name="main_diagram", animation="progressive_stroke_draw"),
            SceneElement(type="arrow", name="pointer", animation="draw_from_start"),
            SceneElement(type="label", name="caption", text=headline, animation="fade_in")]
