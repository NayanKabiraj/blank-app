import json
from pathlib import Path

from shorts import channel_trends, plan, strategy


def _plan():
    return plan.Plan.model_validate_json(Path("shorts/sample_plan.json").read_text())


def test_sources_line_is_added_once():
    d = strategy.with_sources("A video. #Shorts", "x https://a.org/one , https://b.org/two. https://en.wikipedia.org/wiki/X https://c.org/3 https://d.org/4")
    assert d.count("Sources:") == 1 and "a.org/one" in d and "wikipedia" not in d and "d.org/4" not in d
    assert strategy.with_sources(d, "https://z.org") == d


def test_seo_problems_flag_long_title_and_many_tags():
    p = _plan()
    s = p.english.model_copy(update={"title": "x" * 70, "tags": ["a"] * 10, "description": "no tags here"})
    probs = plan._seo_problems("english", s)
    assert len(probs) == 3


def test_research_markers_required():
    p = _plan()
    probs = plan._strategy_problems(p)
    assert any("Claims:" in x for x in probs) and any("Channel check:" in x for x in probs) and any("Gap:" in x for x in probs)


def test_digest_joins_history_and_hedges_small_samples():
    data = {"available": True, "generated": "t", "videos": [
        {"id": "a", "title": "A", "views": 100, "likes": 1, "comments": 0}, {"id": "b", "title": "B", "views": 10, "likes": 0, "comments": 0},
        {"id": "c", "title": "C", "views": 50, "likes": 0, "comments": 0}, {"id": "d", "title": "D", "views": 5, "likes": 0, "comments": 0}],
        "analytics": [{"video": "a", "averageViewPercentage": 80}, {"video": "b", "averageViewPercentage": 30}]}
    hist = [{"niche": "Space", "topic": "t1", "videos": {"en": {"video_id": "a"}}}, {"niche": "Space", "topic": "t2", "videos": {"en": {"video_id": "b"}}},
            {"niche": "Body", "topic": "t3", "videos": {"en": {"video_id": "c"}}}, {"niche": "Body", "topic": "t4", "videos": {"en": {"video_id": "d"}}}]
    d = channel_trends.digest(data, hist, [])
    assert d["niches"]["Space"]["views_per_video"] == 55.0 and d["niches"]["Body"]["videos"] == 2
    assert any("hints, not proof" in s for s in d["signals"]) and any("Best niche" in s for s in d["signals"])
    assert channel_trends.digest({"available": False, "reason": "r"}, [], []) == {"available": False, "reason": "r"}
