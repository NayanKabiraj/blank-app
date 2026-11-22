"""Assembles a validated Storyboard (schema) from planned scenes, writes the JSON file the
animation engine reads, and a human-readable Markdown companion (spec section 9: "Generate
storyboard JSON and a human-readable storyboard document")."""
from __future__ import annotations

from pathlib import Path
from typing import List

from ..schemas.storyboard_schema import Scene, Storyboard

ROOT = Path(__file__).resolve().parents[3]


def build_storyboard(topic_id: str, language: str, visual_style: str, scenes: List[Scene]) -> Storyboard:
    total_duration = max(s.end for s in scenes)
    return Storyboard(topic_id=topic_id, language=language, visual_style=visual_style,
                      total_duration=total_duration, scenes=scenes)


def _markdown(storyboard: Storyboard) -> str:
    out = [f"# Storyboard: {storyboard.topic_id} ({storyboard.language}, {storyboard.visual_style})", ""]
    for s in storyboard.scenes:
        out.append(f"## {s.scene_id} - {s.start:.1f}s to {s.end:.1f}s - {s.template}")
        out.append(f"- Narration: {s.narration}")
        out.append(f"- Camera: {s.camera.movement}" + (f" (focus: {s.camera.focus_on})" if s.camera.focus_on else ""))
        out.append(f"- Elements: " + ", ".join(f"{e.type}:{e.name} ({e.animation})" for e in s.elements))
        out.append(f"- Transition out: {s.transition_out}")
        if s.sound_effect:
            out.append(f"- SFX: {s.sound_effect}")
        out.append("")
    return "\n".join(out)


def write_storyboard(storyboard: Storyboard, root: Path = ROOT) -> tuple[Path, Path]:
    out_dir = root / "content" / "storyboards" / storyboard.topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{storyboard.language}.json"
    md_path = out_dir / f"{storyboard.language}.md"
    json_path.write_text(storyboard.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(_markdown(storyboard), encoding="utf-8")
    return json_path, md_path


def load_storyboard(topic_id: str, language: str, root: Path = ROOT) -> Storyboard:
    path = root / "content" / "storyboards" / topic_id / f"{language}.json"
    return Storyboard.model_validate_json(path.read_text(encoding="utf-8"))
