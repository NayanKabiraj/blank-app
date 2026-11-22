# generated_animations - Claude-authored animation engine

Claude Code writes the Python scene modules; Python renders them. No external video-generation APIs.

```
shared/    camera, particles, typography, transitions, lighting, motion, diagrams   (reusable library)
avatar/    controller (Pip: blink, idle, lip-sync, gaze), gestures, expressions, movement
scenes/<topic_id>/scene_NNN.py + animation_config.json                                (per-topic code)
registry/  animation_registry.py + approved.json (code hashes recorded at human review)
authoring/ safety.py (AST scan), inspect_frames.py (frame extraction, checks, contact sheet)
```

**Mode A (Claude active):** write scenes -> `python -m generated_animations preview <topic>` -> read
`contact_sheet.png` + `inspection.json` -> fix -> repeat -> `approve <topic> --reviewer NAME` (after human review).
**Mode B (no Claude):** `python -m generated_animations render <topic>` renders only approved, unchanged code.
Run inside an env with manim, ffmpeg and the repo requirements. Automated frame checks do not replace
looking at the frames: every inspection reports `manual_review_needed`.
