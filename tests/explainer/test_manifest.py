import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.schemas.production_manifest import ProductionManifest, load_manifest


def test_bundled_sample_manifest_loads_and_validates():
    """The actual committed sample_topic_001.json this repo ships (spec: 'Add a sample topic
    and sample manifest')."""
    root = Path(__file__).resolve().parents[2]
    path = root / "content" / "manifests" / "sample_topic_001.json"
    if not path.exists():
        import pytest
        pytest.skip("sample_topic_001.json not present in this checkout")
    manifest = load_manifest(path)
    assert manifest.topic_id == "sample_topic_001"
    assert manifest.publishing.enabled is False


def test_manifest_script_and_storyboard_path_helpers(tmp_path):
    manifest = ProductionManifest.model_validate({
        "topic_id": "x", "topic": "X",
        "research": {"summary": "A fact, VERIFIED. " * 5,
                     "sources": [{"title": "A", "url": "https://example.com"}],
                     "verification_status": "verified"},
        "production": {"duration_seconds": 50, "languages": ["en"], "formats": ["vertical"]},
        "scripts": {"en": "content/scripts/x/en_script.md"},
        "storyboards": {"en": "content/storyboards/x/en.json"},
    })
    assert manifest.script_path("en", tmp_path) == tmp_path / "content/scripts/x/en_script.md"
    assert manifest.storyboard_path("en", tmp_path) == tmp_path / "content/storyboards/x/en.json"
