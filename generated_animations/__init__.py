"""Claude-authored animation engine.

Claude Code writes Python scene modules (generated_animations/scenes/<topic_id>/scene_NNN.py) for each
topic; this package is the reusable library those modules are built from (shared/, avatar/), the registry
that records which topics are approved, and the authoring tools (safety scan, preview, frame checks).

MODE A (authoring, Claude active): write/iterate scene modules, run `python -m generated_animations preview`,
read the contact sheet, fix, then `approve`.
MODE B (automated): `python -m generated_animations render <topic_id>` runs only APPROVED, hash-matching
modules - no Claude session needed. No external video-generation APIs anywhere.
"""
ROOT_PACKAGE = "generated_animations"
