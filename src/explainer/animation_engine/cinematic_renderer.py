"""Cinematic sketch style (the default - spec section 4C): deep navy/black background, glow-
friendly accent colours, dramatic camera moves. Just the shared SketchRenderScene with the
'cinematic' palette."""
from __future__ import annotations

from .sketch_renderer import style_scene_class

CinematicScene = style_scene_class("cinematic")

STYLE_SCENES = {
    "cinematic": CinematicScene,
}
