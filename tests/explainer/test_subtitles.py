import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.schemas.storyboard_schema import Scene
from explainer.subtitle_engine import subtitle_formatter, subtitle_generator, subtitle_validator


def _scene(text, start=0.0, end=6.0):
    return Scene(scene_id="s1", start=start, end=end, narration=text, subtitle_text=text)


def test_cues_cover_the_full_scene_span():
    cues = subtitle_generator.cues_for_scene(_scene("one two three four five six seven eight"))
    assert cues[0].start == 0.0
    assert abs(cues[-1].end - 6.0) < 0.01


def test_validator_flags_overlong_cue():
    long_text = "word " * 20
    cues = [subtitle_generator.SubtitleCue(0, 2, long_text.strip())]
    problems = subtitle_validator.validate_cues(cues, "en")
    assert any("mobile-safe" in p for p in problems)


def test_validator_flags_hindi_cue_with_no_devanagari():
    cues = [subtitle_generator.SubtitleCue(0, 2, "this has no hindi in it")]
    problems = subtitle_validator.validate_cues(cues, "hi")
    assert any("Devanagari" in p for p in problems)


def test_validator_passes_correct_hindi_cue():
    cues = [subtitle_generator.SubtitleCue(0, 2, "यह सही है")]
    assert subtitle_validator.validate_cues(cues, "hi") == []


def test_srt_and_ass_write_files(tmp_path):
    cues = [subtitle_generator.SubtitleCue(0, 2, "Hello"), subtitle_generator.SubtitleCue(2, 4, "World")]
    srt = subtitle_formatter.write_srt(cues, tmp_path / "out.srt")
    ass = subtitle_formatter.write_ass(cues, tmp_path / "out.ass", "en")
    assert "Hello" in srt.read_text(encoding="utf-8")
    assert "Dialogue:" in ass.read_text(encoding="utf-8")
