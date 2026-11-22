"""Scene visuals are AUTHORED, not hardcoded. The storyboard (written by the AI session that
prepares the topic) carries each scene's elements, positions, keyframed motion, camera move and
transition as data. This module only validates that a planned scene's visuals were provided and
supplies neutral fallbacks (no layout, no motion, no per-template styling) - it never decides
where anything goes or how it moves.
"""
from __future__ import annotations

from ..schemas.storyboard_schema import SceneCamera, SceneElement


def camera_or_static(camera: SceneCamera | None) -> SceneCamera:
    return camera or SceneCamera()


def elements_or_empty(elements: list[SceneElement] | None) -> list[SceneElement]:
    return list(elements or [])
