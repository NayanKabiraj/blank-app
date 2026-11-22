"""python -m generated_animations <command>
  list                          topics with animation code and approval state
  scan <topic>                  static safety scan of the scene modules
  preview <topic> [--out DIR]   MODE A: low-res render + frame extraction + automated checks + contact sheet
  approve <topic> --reviewer X  record the reviewed code hashes (Mode B will only render approved topics)
  render <topic> [--out DIR]    MODE B: full render of an approved topic with narration + music
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="generated_animations")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for name in ("scan", "preview", "approve", "render"):
        p = sub.add_parser(name)
        p.add_argument("topic")
        p.add_argument("--out", default="output_generated")
        p.add_argument("--voice", default="auto", help="auto (use the topic config), piper, flite, edge:<name> or piper:<name>")
        p.add_argument("--reviewer", default="")
        p.add_argument("--no-approval", action="store_true", help="Mode A only: render unapproved code")
    a = ap.parse_args(argv)

    from .authoring import safety
    from .registry import animation_registry as reg
    if a.cmd == "list":
        for t in reg.list_topics():
            print(t, "-", reg.check_approved(t)[1])
        return 0
    if a.cmd == "scan":
        problems = safety.scan_dir(reg.topic_dir(a.topic))
        print("\n".join(problems) or "safety scan passed")
        return 1 if problems else 0
    if a.cmd == "approve":
        if not a.reviewer:
            raise SystemExit("--reviewer is required: code is approved only after a human review")
        problems = safety.scan_dir(reg.topic_dir(a.topic))
        if problems:
            raise SystemExit("\n".join(problems))
        print(json.dumps(reg.approve(a.topic, a.reviewer), indent=2))
        return 0
    from . import pipeline
    out = Path(a.out)
    if a.cmd == "preview":
        info = pipeline.render_topic(a.topic, out / "preview", preview=True, voice=a.voice, require_approved=False)
        from .authoring.inspect_frames import inspect_video
        rep = inspect_video(Path(info["picture"]), out / "preview" / "frames")
        (out / "preview" / "inspection.json").write_text(json.dumps(rep, indent=2))
        print(json.dumps({"overruns": info["scenes"], "problems": rep["problems"], "contact_sheet": rep["contact_sheet"]}, indent=2))
        return 0
    info = pipeline.render_topic(a.topic, out, voice=a.voice, require_approved=not a.no_approval)
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
