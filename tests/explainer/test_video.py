import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.quality_engine import video_quality


def _ffmpeg_available() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


@pytest.fixture
def tiny_video(tmp_path):
    if not _ffmpeg_available():
        pytest.skip("ffmpeg not available")
    out = tmp_path / "tiny.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", "color=c=blue:s=1080x1920:d=2:r=24",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out),
    ], check=True)
    return out


def test_check_video_passes_matching_spec(tiny_video):
    result = video_quality.check_video(tiny_video, expect_width=1080, expect_height=1920,
                                       expect_fps=24, min_duration=1.0, max_duration=5.0)
    assert result["ok"], result["errors"]
    assert result["has_audio"] is True


def test_check_video_flags_wrong_resolution(tiny_video):
    result = video_quality.check_video(tiny_video, expect_width=1920, expect_height=1080,
                                       expect_fps=24, min_duration=1.0, max_duration=5.0)
    assert not result["ok"]
    assert any("resolution" in e for e in result["errors"])


def test_check_video_flags_missing_file(tmp_path):
    result = video_quality.check_video(tmp_path / "nope.mp4", expect_width=1080, expect_height=1920,
                                       expect_fps=24, min_duration=1.0, max_duration=5.0)
    assert not result["ok"]


def test_check_not_black_flags_a_blue_frame_as_not_black(tiny_video):
    # A solid blue frame has non-trivial luma, so it should NOT be flagged as "black"
    assert video_quality.check_not_black(tiny_video, sample_times=[0.5]) == []
