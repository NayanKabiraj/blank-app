import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.schemas.storyboard_schema import Scene, SceneCamera, SceneElement, Storyboard
from explainer.schemas.production_manifest import (AudioConfig, ProductionManifest, Production,
                                                    Publishing, Research, Source)


def make_scene(scene_id="s1", start=0.0, end=4.0, template="hook"):
    return Scene(scene_id=scene_id, start=start, end=end, template=template,
                narration="Test narration.", subtitle_text="Test narration.",
                elements=[SceneElement(type="label", name="x", text="X")],
                camera=SceneCamera(), transition_out="crossfade")


def test_storyboard_requires_at_least_three_scenes():
    with pytest.raises(ValueError):
        Storyboard(topic_id="t", language="en", visual_style="cinematic", total_duration=4.0,
                  scenes=[make_scene()])


def test_storyboard_rejects_overlapping_scenes():
    scenes = [make_scene("s1", 0, 4), make_scene("s2", 2, 8), make_scene("s3", 8, 12)]
    with pytest.raises(ValueError):
        Storyboard(topic_id="t", language="en", visual_style="cinematic", total_duration=12.0, scenes=scenes)


def test_storyboard_accepts_contiguous_scenes():
    scenes = [make_scene("s1", 0, 4), make_scene("s2", 4, 8), make_scene("s3", 8, 12)]
    sb = Storyboard(topic_id="t", language="en", visual_style="cinematic", total_duration=12.0, scenes=scenes)
    assert len(sb.scenes) == 3


def test_scene_end_must_be_after_start():
    with pytest.raises(ValueError):
        Scene(scene_id="s1", start=5.0, end=5.0, narration="x", subtitle_text="x")


def _manifest(languages=("en", "hi")):
    return ProductionManifest(
        topic_id="sample_topic_001", topic="Test topic",
        research=Research(summary="A fact, VERIFIED by a source. " * 3,
                          sources=[Source(title="A source", url="https://example.com/a")],
                          verification_status="verified"),
        production=Production(duration_seconds=50, languages=list(languages), formats=["vertical"]),
        scripts={l: f"content/scripts/sample_topic_001/{l}_script.md" for l in languages},
        storyboards={l: f"content/storyboards/sample_topic_001/{l}.json" for l in languages},
        audio=AudioConfig(), publishing=Publishing(),
    )


def test_manifest_requires_scripts_and_storyboards_for_every_language():
    with pytest.raises(ValueError):
        ProductionManifest.model_validate({
            **_manifest().model_dump(),
            "scripts": {"en": "x"}, "storyboards": {"en": "x"},
        })


def test_manifest_publishing_defaults_to_disabled():
    m = _manifest()
    assert m.publishing.enabled is False
    assert m.publishing.requires_approval is True


def test_research_verified_requires_sources():
    with pytest.raises(ValueError):
        Research(summary="A fact. " * 5, sources=[], verification_status="verified")
