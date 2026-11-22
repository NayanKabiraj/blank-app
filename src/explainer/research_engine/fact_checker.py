"""A lightweight style check on a research summary: does it actually separate FACT from
INFERENCE/speculation the way section 7 of the spec asks, rather than asserting everything as
settled truth? This cannot verify a claim is *true* (nothing offline can); it only checks the
summary is HONEST about what kind of claim each statement is.
"""
from __future__ import annotations

import re

LABELS = ("FACT", "OBSERVATION", "INFERENCE", "RECOMMENDATION", "VERIFIED", "PARTIALLY VERIFIED",
          "UNVERIFIED", "FICTIONAL ASSUMPTION", "NOT PUBLICLY VERIFIABLE")

# phrasing that asserts certainty without hedging - a smell that a claim may be stated as fact
# without having been checked
_OVERCONFIDENT = re.compile(r"\b(always|never|proves|guarantees|definitely|undeniably)\b", re.I)


def check_summary(summary: str) -> list[str]:
    problems: list[str] = []
    if not any(label in summary for label in LABELS):
        problems.append(
            "research summary uses none of the required status labels "
            f"({', '.join(LABELS)}) - every claim should be tagged"
        )
    hits = _OVERCONFIDENT.findall(summary)
    if hits:
        problems.append(f"overconfident wording found ({', '.join(sorted(set(hits)))}); hedge or cite a source instead")
    if len(summary.split()) < 15:
        problems.append("research summary is too short to support a 45-60s script")
    return problems
