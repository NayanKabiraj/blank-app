"""Fast, Manim-import-only tests: the layout/timing logic the animation engine runs before any
actual rendering happens. The real rendered proof (progressive SVG drawing, camera movement,
transitions, all together) is `python -m explainer.cli demo`, exercised in
docs/production-guide.md and recorded in the implementation report - a full Manim render takes
tens of seconds, too slow to be a unit test that runs on every change.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

manim = pytest.importorskip("manim")

from explainer.animation_engine import diagram_builder, sketch_renderer
from explainer.schemas.storyboard_schema import Scene, SceneElement


def test_palettes_exist_for_all_three_required_styles():
    assert set(sketch_renderer.PALETTES) == {"whiteboard", "colourful", "cinematic"}


def test_accent_for_cycles_through_palette():
    palette = sketch_renderer.PALETTES["cinematic"]
    colours = [sketch_renderer.accent_for(palette, i) for i in range(len(palette.accents) * 2)]
    assert colours[: len(palette.accents)] == colours[len(palette.accents):]


def test_style_scene_class_builds_a_distinct_class_per_style():
    whiteboard_cls = sketch_renderer.style_scene_class("whiteboard")
    cinematic_cls = sketch_renderer.style_scene_class("cinematic")
    assert whiteboard_cls is not cinematic_cls
    assert whiteboard_cls.__name__ == "WhiteboardScene"


def test_create_doodle_character_returns_a_four_part_figure():
    character = diagram_builder.create_doodle_character("pointing", "#FFFFFF")
    assert len(character.submobjects) == 4   # head, body, arm, legs


def test_reveal_time_scales_with_element_count():
    few = Scene(scene_id="s1", start=0, end=10, narration="x", subtitle_text="x",
               elements=[SceneElement(type="label", name="a", animation="fade_in")])
    many = Scene(scene_id="s2", start=0, end=10, narration="x", subtitle_text="x",
                elements=[SceneElement(type="label", name="a", animation="fade_in"),
                          SceneElement(type="arrow", name="b", animation="draw_from_start"),
                          SceneElement(type="svg_illustration", name="c", animation="progressive_stroke_draw")])
    assert diagram_builder.reveal_time(many) > diagram_builder.reveal_time(few)
