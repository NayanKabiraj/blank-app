import datetime as dt
import json
from pathlib import Path

from shorts import lineart
from shorts.lineart import build, run
from shorts.plan import Plan

PLAN = Path(__file__).resolve().parents[1] / "strategy" / "prepared" / "2026-11-29-ash-lane-lineart.json"


def test_prepared_plan_is_valid_and_scene_exists():
    plan = Plan.model_validate_json(PLAN.read_text(encoding="utf-8"))
    assert run.problems(plan, ["en", "hi"]) == []
    assert build.scene_exists("ash_lane") and not build.scene_exists("nope")


def test_plan_problems_flag_missing_scene_and_long_title():
    d = json.loads(PLAN.read_text(encoding="utf-8"))
    d["english"]["animation_pack"] = "missing_scene"
    d["english"]["title"] = "x" * 70
    probs = run.problems(Plan.model_validate(d), ["en"])
    assert any("animation_pack" in p for p in probs) and any("title" in p for p in probs)


def test_url_carries_the_narration_timing():
    u = build.url_for("ash_lane", [0.7, 4.2], [3.1, 2.0], 40.0)
    assert "/scenes/ash_lane/?debug&capture" in u and "cues=0.700,4.200" in u and "total=40.000" in u


def test_brief_line_days():
    assert "TODAY" in lineart.brief_line(dt.date(2026, 12, 1))      # Tuesday
    assert "TODAY" in lineart.brief_line(dt.date(2026, 12, 3))      # Thursday
    assert "not today" in lineart.brief_line(dt.date(2026, 12, 2))  # Wednesday


def test_library_files_are_not_git_ignored():
    """A root .gitignore rule once hid lineart/lib/ and the runner could not resolve the imports."""
    import subprocess
    root = Path(__file__).resolve().parents[1]
    files = [f"lineart/lib/{n}.ts" for n in ("ink", "gait", "motion", "daynight")]
    assert all((root / f).exists() for f in files)
    r = subprocess.run(["git", "check-ignore", *files], cwd=root, capture_output=True, text=True)
    assert r.returncode == 1 and not r.stdout.strip(), f"git-ignored: {r.stdout}"
