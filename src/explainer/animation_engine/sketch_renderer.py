"""The shared Manim scene every visual style renders through. A style is just a `Palette`
(background, ink/stroke colour, accent colours, whether a paper texture overlay is drawn) -
whiteboard_renderer.py, colourful_renderer.py and cinematic_renderer.py are each a one-line
subclass that picks a different palette, so the three required files exist (spec section 6)
without three separate animation implementations to maintain.

One continuous Manim Scene renders every storyboard scene in sequence (camera moves, element
reveals and the transition out of each scene all happen inside Manim's own timeline), so no
external video concatenation is needed - unlike shorts/cinematic_engine, which stitches
separately-encoded clips with FFmpeg's xfade, Manim does the whole video in one pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from manim import MovingCameraScene

from ..schemas.storyboard_schema import Storyboard


@dataclass(frozen=True)
class Palette:
    name: str
    background: str
    ink: str
    accents: List[str]
    paper_texture: bool = False


PALETTES: dict[str, Palette] = {
    "whiteboard": Palette("whiteboard", background="#FFFFF5", ink="#1A1A1A",
                          accents=["#1A1A1A"], paper_texture=True),
    "colourful": Palette("colourful", background="#FFFDF0", ink="#2B2B2B",
                         accents=["#E63946", "#2A9D8F", "#E9C46A", "#457B9D", "#8E44AD"], paper_texture=True),
    "cinematic": Palette("cinematic", background="#060912", ink="#F5F7FA",
                         accents=["#2EC5FF", "#5BFBEA", "#9B6BFF", "#F4C95D"], paper_texture=False),
}


def accent_for(palette: Palette, index: int) -> str:
    return palette.accents[index % len(palette.accents)]


class SketchRenderScene(MovingCameraScene):
    """Pass `storyboard`, `palette` and `lang` as constructor kwargs when instantiating this
    (or a style subclass) programmatically - see video_engine/ffmpeg_renderer.py for how
    rendering is actually invoked. The Manim CLI never instantiates this directly."""

    def __init__(self, storyboard: Storyboard, palette: Palette, lang: str = "en", **kwargs):
        self.storyboard = storyboard
        self.palette = palette
        self.lang = lang
        super().__init__(**kwargs)

    def construct(self) -> None:
        from . import diagram_builder, camera_controller, transition_engine

        self.camera.background_color = self.palette.background
        if self.palette.paper_texture:
            diagram_builder.add_paper_texture(self, self.palette)

        for index, scene in enumerate(self.storyboard.scenes):
            mobjects = diagram_builder.build_elements(scene, self.palette, self.lang)
            camera_controller.apply(self, scene.camera, mobjects)
            for mobj, elem in mobjects:
                diagram_builder.animate_in(self, mobj, elem)
            hold = (scene.end - scene.start) - diagram_builder.reveal_time(scene)
            if hold > 0:
                self.wait(hold)
            is_last = index == len(self.storyboard.scenes) - 1
            if not is_last:
                transition_engine.apply(self, scene.transition_out, mobjects)
            else:
                self.wait(0.3)


def style_scene_class(style: str):
    """whiteboard_renderer.py / colourful_renderer.py / cinematic_renderer.py each import this
    to build their one scene class - see those files for the actual per-style classes."""
    palette = PALETTES[style]

    class _StyleScene(SketchRenderScene):
        def __init__(self, storyboard: Storyboard, lang: str = "en", **kwargs):
            super().__init__(storyboard, palette, lang, **kwargs)

    _StyleScene.__name__ = f"{style.capitalize()}Scene"
    return _StyleScene
