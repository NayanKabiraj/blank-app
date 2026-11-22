import importlib
import json

import pytest

from generated_animations import packs
from generated_animations.authoring import safety

PACKS = sorted(p.name for p in packs.SCENES.iterdir() if (p / "shots.json").exists())


def test_packs_exist():
    assert {"gps_short", "tides_doc"} <= set(PACKS)


@pytest.mark.parametrize("pack", PACKS)
def test_pack_shots_are_contiguous_and_safe(pack):
    d = packs.SCENES / pack
    spec = json.loads((d / "shots.json").read_text(encoding="utf-8"))["shots"]
    covered = [i for s in spec for i in s["scenes"]]
    assert covered == list(range(len(covered)))             # in order, no gaps, no overlaps
    assert safety.scan_dir(d) == []
    for s in spec:
        assert (d / f"{s['module']}.py").exists()
        assert "def animate(ctx)" in (d / f"{s['module']}.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("pack", PACKS)
def test_pack_modules_import(pack):
    pytest.importorskip("manim")
    for shot in packs.load(pack):
        assert callable(shot.module.animate)


def test_plan_validation_requires_full_coverage():
    from shorts.plan import LangScript, Plan, Scene, _animation_problems
    sc = [Scene(text=f"s{i}") for i in range(3)]
    mk = lambda pack: LangScript(title="t", description="d", tags=["a"], hook_text="h", scenes=sc, animation_pack=pack)  # noqa: E731
    plan = Plan.model_construct(english=mk(""), hindi=mk("gps_short"))
    problems = _animation_problems(plan)
    assert any("animation_pack is empty" in p for p in problems)
    assert any("no authored animation" in p for p in problems) or any("gps_short" in p for p in problems) is False
