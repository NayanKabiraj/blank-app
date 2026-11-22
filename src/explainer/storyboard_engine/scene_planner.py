"""Builds Scene objects from authored visuals. Each PlannedLine carries the AI-authored elements
(with positions and keyframes), camera move and transition; this module assembles them into the
validated schema without adding any layout or motion of its own."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..schemas.storyboard_schema import Scene, SceneCamera, SceneElement, SceneTemplate, Transition
from . import visual_planner as vp


@dataclass
class PlannedLine:
    scene_id: str
    start: float
    end: float
    narration: str
    elements: List[SceneElement] = field(default_factory=list)
    camera: Optional[SceneCamera] = None
    transition: Transition = "crossfade"
    template: SceneTemplate = "explainer_diagram"
    sound_effect: Optional[str] = None


def build_scene(line: PlannedLine) -> Scene:
    return Scene(
        scene_id=line.scene_id,
        start=line.start,
        end=line.end,
        template=line.template,
        narration=line.narration,
        subtitle_text=line.narration,
        elements=vp.elements_or_empty(line.elements),
        camera=vp.camera_or_static(line.camera),
        transition_out=line.transition,
        sound_effect=line.sound_effect,
    )


def build_scenes(lines: List[PlannedLine]) -> List[Scene]:
    return [build_scene(l) for l in lines]
