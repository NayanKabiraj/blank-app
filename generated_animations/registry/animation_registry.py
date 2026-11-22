"""Which topics have approved, version-controlled animation code.

`approved.json` maps topic_id -> {reviewer, approved_at, files: {name: sha256}}. Mode B rendering refuses a
topic that is not listed, or whose scene files changed after approval (so unreviewed edits never ship).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENES = HERE.parent / "scenes"
APPROVED = HERE / "approved.json"


def _load() -> dict:
    return json.loads(APPROVED.read_text()) if APPROVED.exists() else {}


def topic_dir(topic_id: str) -> Path:
    return SCENES / topic_id


def list_topics() -> list[str]:
    return sorted(p.name for p in SCENES.iterdir() if (p / "animation_config.json").exists())


def load_config(topic_id: str) -> dict:
    return json.loads((topic_dir(topic_id) / "animation_config.json").read_text(encoding="utf-8"))


def fingerprint(topic_id: str) -> dict[str, str]:
    d = topic_dir(topic_id)
    files = sorted(d.glob("scene_*.py")) + [d / "animation_config.json"]
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


def approve(topic_id: str, reviewer: str) -> dict:
    data = _load()
    data[topic_id] = {"reviewer": reviewer, "approved_at": time.strftime("%Y-%m-%d"),
                      "files": fingerprint(topic_id)}
    APPROVED.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data[topic_id]


def check_approved(topic_id: str) -> tuple[bool, str]:
    rec = _load().get(topic_id)
    if not rec:
        return False, f"'{topic_id}' is not approved (run: python -m generated_animations approve {topic_id} --reviewer NAME)"
    if rec["files"] != fingerprint(topic_id):
        return False, f"'{topic_id}' changed since it was approved - re-review and approve again"
    return True, f"approved by {rec['reviewer']} on {rec['approved_at']}"


def scene_modules(topic_id: str):
    """Import the topic's scene modules in config order (call only after the safety scan has passed)."""
    import importlib
    cfg = load_config(topic_id)
    return [importlib.import_module(f"generated_animations.scenes.{topic_id}.{s['module']}") for s in cfg["scenes"]]
