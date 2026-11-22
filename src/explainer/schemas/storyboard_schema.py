"""Storyboard schema: the scene-by-scene visual plan a script is turned into, and that the
animation engine renders frame by frame. One storyboard per language (English/Hindi narration
differ in length, so their scene timings differ too, even for the same topic).
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

VisualStyle = Literal["whiteboard", "colourful", "cinematic"]
CameraMovement = Literal["static", "slow_zoom_in", "slow_zoom_out", "pan_left", "pan_right",
                         "pan_up", "pan_down", "focus", "follow"]
Transition = Literal["cut", "crossfade", "sketch_reveal", "erase", "paper_wipe", "zoom", "line_draw"]
ElementType = Literal["svg_illustration", "arrow", "label", "highlight", "character", "diagram"]
ElementAnimation = Literal["progressive_stroke_draw", "draw_from_start", "fade_in", "pop_in", "slide_in"]
SceneTemplate = Literal["hook", "explainer_diagram", "comparison", "timeline", "takeaway"]


class SceneElement(BaseModel):
    """One visual layer inside a scene: an illustration, an arrow, a label, a highlight, a
    character pose, or a diagram built from the storyboard's own primitives (no external asset
    files required for the default shapes)."""
    type: ElementType
    name: str = Field(description="What this element shows, e.g. 'central_concept' or 'step_1'")
    animation: ElementAnimation = "fade_in"
    text: Optional[str] = Field(default=None, description="Label/caption text, if any (EN or HI).")
    color: Optional[str] = Field(default=None, description="Hex override; default comes from the style palette.")
    position: Optional[str] = Field(default=None, description="e.g. 'center', 'top', 'left', 'right'")


class SceneCamera(BaseModel):
    movement: CameraMovement = "static"
    focus_on: Optional[str] = Field(default=None, description="Element name to zoom/focus/follow, if applicable.")


class Scene(BaseModel):
    scene_id: str
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    template: SceneTemplate = "explainer_diagram"
    narration: str = Field(description="The spoken line(s) this scene covers (same text as the script).")
    subtitle_text: str = Field(description="What appears on screen; usually equal to narration.")
    background: str = Field(default="textured_paper", description="Background look, style-dependent.")
    elements: List[SceneElement] = Field(default_factory=list)
    camera: SceneCamera = Field(default_factory=SceneCamera)
    transition_out: Transition = "crossfade"
    sound_effect: Optional[str] = Field(default=None, description="Cue name, e.g. 'pop', 'whoosh' - optional.")

    @model_validator(mode="after")
    def _check_times(self) -> "Scene":
        if self.end <= self.start:
            raise ValueError(f"{self.scene_id}: end ({self.end}) must be after start ({self.start})")
        return self


class Storyboard(BaseModel):
    schema_version: str = "1.0"
    topic_id: str
    language: Literal["en", "hi"]
    visual_style: VisualStyle
    total_duration: float = Field(gt=0)
    scenes: List[Scene]

    @model_validator(mode="after")
    def _check_coverage(self) -> "Storyboard":
        if not self.scenes:
            raise ValueError("storyboard has no scenes")
        if len(self.scenes) < 3:
            raise ValueError(f"{len(self.scenes)} scenes: need at least 3-ish for a 45-60s video (spec wants 5-8)")
        ordered = sorted(self.scenes, key=lambda s: s.start)
        for a, b in zip(ordered, ordered[1:]):
            if b.start < a.end - 0.05:   # small overlap tolerance for crossfades
                raise ValueError(f"scenes overlap: {a.scene_id} ends {a.end}, {b.scene_id} starts {b.start}")
        last_end = ordered[-1].end
        if abs(last_end - self.total_duration) > 1.0:
            raise ValueError(f"last scene ends at {last_end}s but total_duration is {self.total_duration}s")
        return self
