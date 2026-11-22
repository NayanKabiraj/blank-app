import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.research_engine import fact_checker, topic_discovery
from explainer.research_engine.source_validator import validate_research
from explainer.research_engine.web_research import ManualResearchProvider
from explainer.schemas.production_manifest import Research, Source


def test_fact_checker_flags_missing_status_labels():
    problems = fact_checker.check_summary("This is definitely true and always works, no source needed.")
    assert any("required status labels" in p for p in problems)
    assert any("overconfident" in p for p in problems)


def test_fact_checker_passes_a_properly_hedged_summary():
    summary = "A fact about X, VERIFIED by a 2021 study. " * 3
    assert fact_checker.check_summary(summary) == []


def test_source_validator_flags_malformed_and_duplicate_urls():
    research = Research(
        summary="A fact, VERIFIED. " * 5,
        sources=[Source(title="A", url="https://a.example.com"),
                 Source(title="B", url="https://a.example.com")],
        verification_status="verified",
    )
    problems = validate_research(research)
    assert any("duplicate" in p for p in problems)


def test_manual_research_provider_rejects_non_http_urls():
    provider = ManualResearchProvider()
    try:
        provider.add("Bad", "ftp://example.com/x")
        assert False, "should have raised"
    except ValueError:
        pass


def test_is_duplicate_matches_high_word_overlap(tmp_path, monkeypatch):
    monkeypatch.setattr(topic_discovery, "RESEARCH_DIR", tmp_path)
    topic_discovery.save_research_record("x", {"topic": "Why do heart cells beat together in a dish"})
    assert topic_discovery.is_duplicate("Why do heart cells beat together in a dish") is not None
    assert topic_discovery.is_duplicate("How does a boomerang come back") is None


def test_next_topic_id_dedupes(tmp_path, monkeypatch):
    monkeypatch.setattr(topic_discovery, "RESEARCH_DIR", tmp_path)
    assert topic_discovery.next_topic_id("Why do cats purr?") == "why_do_cats_purr"
    topic_discovery.save_research_record("why_do_cats_purr", {"topic": "x"})
    assert topic_discovery.next_topic_id("Why do cats purr?") == "why_do_cats_purr_2"
