"""Whiteboard style: white/cream paper, black ink, monochrome marker look (spec section 4A).
Just the shared SketchRenderScene with the 'whiteboard' palette - see sketch_renderer.py for
the actual drawing/camera/transition logic every style shares."""
from __future__ import annotations

from .sketch_renderer import style_scene_class

WhiteboardScene = style_scene_class("whiteboard")
