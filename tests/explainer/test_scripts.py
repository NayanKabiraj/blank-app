import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.script_engine import duration_controller, english_generator, hindi_generator, script_generator


def test_check_duration_flags_too_short_and_too_long():
    assert duration_controller.check_duration(50, "en").ok is False   # ~18.5s, too short
    assert duration_controller.check_duration(170, "en").ok is False  # ~63s, too long
    assert duration_controller.check_duration(140, "en").ok is True


def test_beat_for_second_matches_the_six_beat_table():
    assert duration_controller.beat_for_second(2) == "hook"
    assert duration_controller.beat_for_second(20) == "concept"
    assert duration_controller.beat_for_second(58) == "ending"


def test_hindi_generator_rejects_non_devanagari_lines(tmp_path):
    lines = [script_generator.ScriptLine("s1", 0, 4, "This is English, not Hindi.", "x")]
    with pytest.raises(ValueError):
        hindi_generator.write("t", "Topic", lines, root=tmp_path)


def test_hindi_generator_accepts_devanagari_and_writes_file(tmp_path):
    lines = [script_generator.ScriptLine("s1", 0, 4, "यह हिंदी में है।", "x")]
    path = hindi_generator.write("t", "Topic", lines, root=tmp_path)
    assert path.exists()
    assert "यह हिंदी में है" in path.read_text(encoding="utf-8")


def test_english_generator_writes_a_timing_table(tmp_path):
    lines = [script_generator.ScriptLine("s1", 0, 4, "A hook line here now.", "visual one")]
    path = english_generator.write("t", "Topic", lines, root=tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "s1" in text and "visual one" in text and "Word count" in text
