"""Topic discovery and de-duplication.

Important: this module does NOT call any LLM or search API itself. Per the spec's own
instruction ("do not assume Claude Code can execute inside GitHub Actions" / "use a configured
LLM or research provider only when credentials and access are available"), live research in
this repo is done interactively, the same way the existing shorts/ pipeline already works:
a Claude session researches a topic with real web search, then writes the result here as a
research record. This module's job is bookkeeping around that: list what's already been made,
flag duplicates/near-duplicates, and give the next topic_id to use.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[3]
RESEARCH_DIR = ROOT / "content" / "research"


def _slugify(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
    return slug[:60] or "topic"


def existing_topic_ids() -> List[str]:
    if not RESEARCH_DIR.exists():
        return []
    return sorted(p.stem for p in RESEARCH_DIR.glob("*.json"))


def existing_topics() -> List[str]:
    """The `topic` text of every saved research record (for duplicate checking)."""
    out = []
    for p in RESEARCH_DIR.glob("*.json") if RESEARCH_DIR.exists() else []:
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")).get("topic", ""))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def is_duplicate(topic: str, threshold: float = 0.6) -> Optional[str]:
    """A crude but dependency-free near-duplicate check: shared-word overlap against every
    saved topic. Returns the matching existing topic, or None. Good enough to catch
    "How does X work" asked twice; a real system would also check data/history.json-style
    cross-pipeline records before committing to a topic."""
    words = set(re.findall(r"[a-z0-9]+", topic.lower()))
    if not words:
        return None
    for existing in existing_topics():
        other = set(re.findall(r"[a-z0-9]+", existing.lower()))
        if not other:
            continue
        overlap = len(words & other) / min(len(words), len(other))
        if overlap >= threshold:
            return existing
    return None


def next_topic_id(topic: str) -> str:
    base = _slugify(topic)
    used = set(existing_topic_ids())
    if base not in used:
        return base
    i = 2
    while f"{base}_{i}" in used:
        i += 1
    return f"{base}_{i}"


def save_research_record(topic_id: str, record: dict) -> Path:
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    path = RESEARCH_DIR / f"{topic_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_research_record(topic_id: str) -> dict:
    return json.loads((RESEARCH_DIR / f"{topic_id}.json").read_text(encoding="utf-8"))
