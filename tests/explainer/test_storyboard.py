import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.storyboard_engine.scene_planner import PlannedLine, build_scenes
from explainer.storyboard_engine.storyboard_generator import build_storyboard, write_storyboard, load_storyboard
from explainer.storyboard_engine import visual_planner


def test_visual_planner_gives_every_template_a_camera_and_elements():
    for template in ("hook", "explainer_diagram", "comparison", "timeline", "takeaway"):
        camera = visual_planner.default_camera(template)
        elements = visual_planner.default_elements(template, "Headline")
        assert camera.movement
        assert len(elements) >= 1


def test_build_scenes_produces_valid_contiguous_scenes():
    lines = [
        PlannedLine("s1", 0, 4, "Hook line.", template="hook"),
        PlannedLine("s2", 4, 8, "Explainer line.", template="explainer_diagram"),
        PlannedLine("s3", 8, 12, "Takeaway line.", template="takeaway"),
    ]
    scenes = build_scenes(lines)
    sb = build_storyboard("t", "en", "cinematic", scenes)
    assert sb.total_duration == 12.0
    assert len(sb.scenes) == 3


def test_write_and_load_storyboard_roundtrip(tmp_path):
    lines = [PlannedLine("s1", 0, 4, "A.", template="hook"),
             PlannedLine("s2", 4, 8, "B.", template="explainer_diagram"),
             PlannedLine("s3", 8, 12, "C.", template="takeaway")]
    sb = build_storyboard("roundtrip_topic", "en", "whiteboard", build_scenes(lines))
    write_storyboard(sb, root=tmp_path)
    loaded = load_storyboard("roundtrip_topic", "en", root=tmp_path)
    assert loaded.visual_style == "whiteboard"
    assert [s.scene_id for s in loaded.scenes] == ["s1", "s2", "s3"]
