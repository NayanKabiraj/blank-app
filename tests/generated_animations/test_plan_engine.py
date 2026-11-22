import pytest

from generated_animations import plan_render
from generated_animations.layout import LANDSCAPE, VERTICAL


def test_boundaries_cover_whole_video():
    tl = [(0.4, 3.0, "a"), (3.25, 6.0, "b"), (6.25, 9.0, "c")]
    e = plan_render.boundaries(tl, 11.0)
    assert e[0] == 0.0 and e[-1] == 11.0 and len(e) == 4
    assert all(b > a for a, b in zip(e, e[1:]))
    assert e[1] < tl[1][0]          # a scene starts a little before its narration


def test_layouts():
    assert not VERTICAL.landscape and LANDSCAPE.landscape
    assert VERTICAL.pixels == (1080, 1920) and LANDSCAPE.pixels == (1280, 720)


def test_every_plan_graphic_kind_has_a_renderer():
    pytest.importorskip("manim")
    from generated_animations import kinds
    from shorts.plan import KINDS
    assert set(KINDS) == set(kinds.KINDS)


def test_every_prop_has_an_icon():
    pytest.importorskip("manim")
    from generated_animations.shared import icons
    from shorts.plan import PROPS
    for p in PROPS:
        assert icons.icon(p, 1.0).width > 0


def test_engine_switch_defaults_to_generated(monkeypatch):
    from shorts import config
    assert config.ENGINE in ("generated", "whiteboard")
