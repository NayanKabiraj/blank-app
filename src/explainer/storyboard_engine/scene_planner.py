"""Builds Scene objects from authored script lines plus a per-line template/headline choice.
A thin layer: the creative call (which beat gets which template) is made by whoever authors
the topic; this module just assembles the schema object with sensible visual defaults filled
in via visual_planner, and keeps scene start/end times contiguous.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..schemas.storyboard_schema import Scene, SceneTemplate
from . import visual_planner as vp


@dataclass
class PlannedLine:
    scene_id: str
    start: float
    end: float
    narration: str
    template: SceneTemplate = "explainer_diagram"
    headline: str = ""
    focus_on: Optional[str] = None
    sound_effect: Optional[str] = None


def build_scene(line: PlannedLine) -> Scene:
    headline = line.headline or line.narration.split(".")[0][:40]
    return Scene(
        scene_id=line.scene_id,
        start=line.start,
        end=line.end,
        template=line.template,
        narration=line.narration,
        subtitle_text=line.narration,
        elements=vp.default_elements(line.template, headline),
        camera=vp.default_camera(line.template, line.focus_on),
        transition_out=vp.default_transition(line.template),
        sound_effect=line.sound_effect,
    )


def build_scenes(lines: List[PlannedLine]) -> List[Scene]:
    return [build_scene(l) for l in lines]
