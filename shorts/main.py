"""Daily entry point: research -> scripts -> render (EN + HI) -> upload -> log history.

    python -m shorts.main                 # full run
    python -m shorts.main --dry-run       # render only, no upload
    python -m shorts.main --plan-file p.json --dry-run   # skip research, reuse a plan
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
from pathlib import Path

from . import compose, config, upload
from .research import Plan, make_plan

log = logging.getLogger("shorts")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="render videos but do not upload")
    ap.add_argument("--langs", default="en,hi", help="comma-separated: en,hi")
    ap.add_argument("--niche", default="", help="force a niche instead of researching one")
    ap.add_argument("--plan-file", default="", help="use an existing plan JSON (skips Claude)")
    ap.add_argument("--out", default="output", help="output directory")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    plan = (Plan.model_validate_json(Path(args.plan_file).read_text())
            if args.plan_file else make_plan(args.niche))
    (out / "plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    scripts = {"en": plan.english, "hi": plan.hindi}
    results, failures = {}, []
    for lang in [l.strip() for l in args.langs.split(",") if l.strip()]:
        try:
            video = compose.build(scripts[lang], lang, plan.mood, out / f"work_{lang}")
            final = out / f"{dt.date.today().isoformat()}_{lang}.mp4"
            shutil.move(video, final)
            entry = {"file": final.name}
            if args.dry_run:
                log.info("Dry run: not uploading %s", final)
            elif not upload.can_upload(lang):
                log.warning("YouTube secrets missing for %s; skipping upload", lang)
            else:
                entry["video_id"] = upload.upload(final, scripts[lang], lang)
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so one language can still publish
            log.exception("Failed to produce the %s Short", lang)
            failures.append(lang)

    if not args.dry_run and any("video_id" in r for r in results.values()):
        config.DATA_DIR.mkdir(exist_ok=True)
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": dt.date.today().isoformat(), "niche": plan.niche,
                     "topic": plan.topic, "mood": plan.mood, "videos": results})
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    log.info("Done: %s", json.dumps(results, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
