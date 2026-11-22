"""Pluggable research-source interface.

No network calls happen here by default - this repo's actual research step is an interactive
Claude session doing real web search (as every video in shorts/ is researched today), which
then calls `record_source()`/`ManualResearchProvider` to shape what it found into the schema
the rest of the pipeline expects. A future automated provider (e.g. a search API) would
implement the same `ResearchProvider` protocol and could be swapped in without touching
anything downstream.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol


@dataclass
class SourceCandidate:
    title: str
    url: str
    published: Optional[str] = None
    note: str = ""   # what this source supports, for the human/session compiling research


class ResearchProvider(Protocol):
    def search(self, topic: str, max_sources: int = 5) -> List[SourceCandidate]:
        ...


@dataclass
class ManualResearchProvider:
    """Wraps sources a human/session already found (e.g. via real web search) into the
    pipeline's shape. This is the only provider implemented by default."""
    found: List[SourceCandidate] = field(default_factory=list)

    def add(self, title: str, url: str, published: Optional[str] = None, note: str = "") -> None:
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError(f"source url must be http(s): {url!r}")
        self.found.append(SourceCandidate(title=title, url=url, published=published, note=note))

    def search(self, topic: str, max_sources: int = 5) -> List[SourceCandidate]:
        return self.found[:max_sources]
