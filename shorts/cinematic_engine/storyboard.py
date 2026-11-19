"""Turns a plan's scenes + the already-synthesized voice timeline into per-scene render instructions
(accent colour, particle seed, camera drift range). The *content* of each scene - its `graphic.kind`,
headline, items - comes entirely from the plan (shorts.plan.Graphic), exactly as the whiteboard explainer
uses it; this module only decides the cinematic *look* each scene gets, cycling through the brand palette
and nudging the camera differently scene to scene so a 6-9 scene Short doesn't feel static.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import effects


@dataclass
class RenderScene:
    index: int
    graphic: object  # shorts.plan.Graphic | None
    start: float
    duration: float
    accent: str
    seed: int
    zoom_to: float
    pan_px: float


def build(scenes, timeline, total: float) -> list[RenderScene]:
    """`timeline` is compose._voice_track's [(start, end, text), ...], one per scene; `total` is the
    whole Short's length. Mirrors `shorts.animate.render`'s own segment-boundary rule (a scene runs
    from its own start to the NEXT scene's start, and the last one runs to `total`) so cut points line
    up with the narration exactly the same way the whiteboard renderer does."""
    out = []
    for i, (start, end, _text) in enumerate(timeline):
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        seg_start = 0.0 if i == 0 else start
        g = scenes[i].graphic if i < len(scenes) else None
        out.append(RenderScene(
            index=i, graphic=g, start=seg_start, duration=max(0.6, seg_end - seg_start),
            accent=effects.accent_for(i), seed=i * 7 + 3,
            zoom_to=1.05 + 0.03 * (i % 3), pan_px=14.0 + 6.0 * (i % 2),
        ))
    return out
