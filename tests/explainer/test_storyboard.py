import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.storyboard_engine.scene_planner import PlannedLine, build_scenes
from explainer.storyboard_engine.storyboard_generator import build_storyboard, write_storyboard, load_storyboard
from explainer.storyboard_engine import visual_planner
from explainer.schemas.storyboard_schema import SceneCamera, SceneElement


def test_visuals_are_taken_as_authored_not_defaulted():
    assert visual_planner.camera_or_static(None).movement == "static"
    cam = SceneCamera(movement="pan_left")
    assert visual_planner.camera_or_static(cam) is cam
    els = [SceneElement(type="label", name="x", text="x")]
    assert visual_planner.elements_or_empty(els) == els
    assert visual_planner.elements_or_empty(None) == []


def test_build_scenes_produces_valid_contiguous_scenes():
    lines = [
        PlannedLine("s1", 0, 4, "Hook line.", template="hook",
                    elements=[SceneElement(type="label", name="a", text="a")]),
        PlannedLine("s2", 4, 8, "Explainer line.", template="explainer_diagram",
                    elements=[SceneElement(type="label", name="b", text="b")]),
        PlannedLine("s3", 8, 12, "Takeaway line.", template="takeaway",
                    elements=[SceneElement(type="label", name="c", text="c")]),
    ]
    scenes = build_scenes(lines)
    sb = build_storyboard("t", "en", "cinematic", scenes)
    assert sb.total_duration == 12.0
    assert len(sb.scenes) == 3


def test_write_and_load_storyboard_roundtrip(tmp_path):
    el = [SceneElement(type="label", name="x", text="x")]
    lines = [PlannedLine("s1", 0, 4, "A.", template="hook", elements=el),
             PlannedLine("s2", 4, 8, "B.", template="explainer_diagram", elements=el),
             PlannedLine("s3", 8, 12, "C.", template="takeaway", elements=el)]
    sb = build_storyboard("roundtrip_topic", "en", "whiteboard", build_scenes(lines))
    write_storyboard(sb, root=tmp_path)
    loaded = load_storyboard("roundtrip_topic", "en", root=tmp_path)
    assert loaded.visual_style == "whiteboard"
    assert [s.scene_id for s in loaded.scenes] == ["s1", "s2", "s3"]
