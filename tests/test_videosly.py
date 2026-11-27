import datetime as dt

from shorts import videosly as vs


def test_request_is_a_prompt_only_with_the_horror_skill():
    r = vs.request("A guard in an empty tower notices the lift stops on a floor with no button", dt.date(2026, 11, 28))
    assert r["skill"] == "horror-story" and r["duration"] == "medium" and r["aspectRatio"] == "9:16" and r["prompt"].startswith("A horror story.")
    assert not {"script", "composition", "content", "title", "description"} & set(r)
    assert r["idempotencyKey"] == vs.request("A guard in an empty tower notices the lift stops on a floor with no button", dt.date(2026, 11, 28))["idempotencyKey"]


def test_topic_rules():
    assert vs.topic_problems("A guard finds blood in the lift", past=[])
    assert vs.topic_problems("A child hears a voice in the cellar of the old house", past=[])
    assert vs.topic_problems("A Google engineer sees a strange login at night in a quiet office", past=[])
    assert vs.topic_problems("short", past=[])
    ok = "A night-shift guard in an empty office tower notices the lift stops on a floor with no button"
    assert not vs.topic_problems(ok, past=[])
    assert vs.topic_problems(ok, past=["A night shift guard in an empty office tower notices the lift stops on a floor that has no button"])


def test_meta_rules_and_post_args():
    meta = {"title": "The Lift Stopped on Floor 13 (A Fictional Story)", "description": "A fictional AI-made horror story: a night guard and a lift that keeps stopping on a floor that does not exist. Listen to the end. #Shorts #HorrorStory #Fiction",
            "tags": ["horror story", "short horror story", "scary story", "creepy story", "lift horror", "fictional story"], "duration_seconds": 58}
    assert vs.meta_problems(meta) == []
    assert vs.meta_problems({**meta, "duration_seconds": 80}) == [] and vs.meta_problems({**meta, "tags": ["a"]}) and vs.meta_problems({**meta, "title": "x" * 70})
    a = vs.post_args(meta, "vid1", "ch1")
    assert a["aiGenerated"] is True and a["privacy"] in ("private", "public", "unlisted") and a["videoId"] == "vid1" and a["title"] == meta["title"]


def test_history_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(vs, "HISTORY", tmp_path / "h.json")
    assert vs.recent_topics() == []
    vs.record({"topic": "t one two three four five six seven", "videoId": "x"})
    assert vs.recent_topics() == ["t one two three four five six seven"] and "t one" in vs.brief_line()
