"""Checks on research sources before they're trusted enough to script from: well-formed URLs,
no duplicates, a sane count, and (for 'verified'/'partially_verified' claims) that sources
actually exist. Mirrors the spirit of shorts/plan.py's validate(), applied to this schema.
"""
from __future__ import annotations

from urllib.parse import urlparse

from ..schemas.production_manifest import Research


def validate_research(research: Research, *, min_sources_if_verified: int = 1, max_sources: int = 12) -> list[str]:
    problems: list[str] = []
    seen_urls: set[str] = set()
    for s in research.sources:
        parsed = urlparse(s.url)
        if not parsed.scheme or not parsed.netloc:
            problems.append(f"source {s.title!r} has a malformed url: {s.url!r}")
        if s.url in seen_urls:
            problems.append(f"duplicate source url: {s.url!r}")
        seen_urls.add(s.url)
    if len(research.sources) > max_sources:
        problems.append(f"{len(research.sources)} sources, more than the {max_sources}-source cap")
    if research.verification_status in ("verified", "partially_verified") and len(research.sources) < min_sources_if_verified:
        problems.append(f"verification_status={research.verification_status!r} but only {len(research.sources)} source(s) listed")
    if research.verification_status == "unverified" and not research.uncertainties:
        problems.append("verification_status is 'unverified' but `uncertainties` does not say what's unconfirmed")
    if research.verification_status == "fictional_assumption" and "assumption" not in research.uncertainties.lower() and "fictional" not in research.uncertainties.lower():
        problems.append("verification_status is 'fictional_assumption' but `uncertainties` doesn't say so explicitly")
    return problems
