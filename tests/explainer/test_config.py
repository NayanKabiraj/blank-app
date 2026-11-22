import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.config.settings import ProductionConfig, load_config


def test_default_config_is_safe_by_default():
    cfg = load_config(Path("/nonexistent/production.yaml"))
    assert cfg.publishing.enabled is False
    assert cfg.topics_per_day == 1


def test_jobs_per_day_multiplies_correctly():
    cfg = ProductionConfig(topics_per_day=5, languages=["en", "hi"], formats=["vertical", "landscape"])
    assert cfg.jobs_per_day == 20


def test_loads_the_repo_production_yaml():
    cfg = load_config()   # the real src/explainer/config/production.yaml
    assert cfg.topics_per_day == 1   # the owner's decision (22 Nov 2026): keep current cadence
    assert cfg.publishing.enabled is False
