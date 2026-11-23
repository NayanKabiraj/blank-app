"""Animation packs: the scene-specific animation code Claude writes for ONE video (generated_animations/scenes/<pack>/).

A pack is a folder with `shots.json` - {"shots": [{"module": "scene_001", "scenes": [0, 1]}, ...]} - and one
Python module per shot exposing `animate(ctx)`. A shot covers one or more consecutive narration scenes of the plan
(index into the plan's scenes), draws the topic's own animation for them (orbits, signals, rising water ...) on the
scene clock, and the renderer adds the captions and the presenter. Plan scenes a pack does not cover fall back to
the generic graphic kinds (kinds.py), which the plan validator reports as a problem."""
from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path

from .authoring import safety

SCENES = Path(__file__).resolve().parent / "scenes"


@dataclass
class Shot:
    module: object
    scenes: list


def load(pack_id: str) -> list[Shot]:
    d = SCENES / pack_id
    problems = safety.scan_dir(d)
    if problems:
        raise SystemExit("animation pack failed the safety scan:\n  " + "\n  ".join(problems))
    spec = json.loads((d / "shots.json").read_text(encoding="utf-8"))["shots"]
    return [Shot(importlib.import_module(f"generated_animations.scenes.{pack_id}.{s['module']}"), list(s["scenes"])) for s in spec]


def look(pack_id: str) -> str:
    """The pack's look: "vox" (paper cut-out explainer style, shared/vox.py) or "classic" (the dark space theme). shots.json: {"look": "vox", ...}"""
    f = SCENES / pack_id / "shots.json"
    return (json.loads(f.read_text(encoding="utf-8")).get("look") or "classic") if f.exists() else "classic"


def covered(pack_id: str) -> set[int]:
    d = SCENES / pack_id / "shots.json"
    if not d.exists():
        return set()
    return {i for s in json.loads(d.read_text(encoding="utf-8"))["shots"] for i in s["scenes"]}
