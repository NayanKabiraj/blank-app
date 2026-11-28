"""Line-art entry point: the SAME plan schema as the stock-footage and whiteboard Shorts (`shorts.plan.Plan`; `graphic` is ignored) with `animation_pack` = the id of the scene in
`lineart/scenes/<id>/` (each language). Same upload queue, thumbnail, history and closing line as the other styles.

    python -m shorts.lineart.run --plan-file plan.json              # render + upload
    python -m shorts.lineart.run --plan-file plan.json --dry-run    # render only
    python -m shorts.lineart.run --plan-file plan.json --validate-only
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
from pathlib import Path

from .. import config, pending, strategy, upload
from ..plan import Plan
from . import build, thumbnail as thumbs

log = logging.getLogger("shorts.lineart")


def problems(plan: Plan, langs: list[str] | None = None) -> list[str]:
    """Checks for a line-art story plan (the whiteboard validator's intro/'In this video' rules do not apply to a story)."""
    p = []
    langs = langs or ["en"]
    for lang in langs:
        s = plan.english if lang == "en" else plan.hindi
        if s is None:
            p.append(f"{lang}: missing script block")
            continue
        if not build.scene_exists(s.animation_pack):
            p.append(f"{lang}: animation_pack {s.animation_pack!r} is not a scene in lineart/scenes/ (needs index.html and a .ts module)")
        if not 6 <= len(s.scenes) <= 12:
            p.append(f"{lang}: 6-12 scenes (got {len(s.scenes)})")
        words = sum(len(sc.text.split()) for sc in s.scenes)
        if not (55 <= words <= 125 if lang == "en" else 45 <= words <= 120):
            p.append(f"{lang}: narration is {words} words (target 60-110 English, 50-100 Hindi; the closing line is added automatically)")
        if len(s.title) > 65:
            p.append(f"{lang}: title over 65 characters")
        if not 5 <= len(s.tags) <= 8:
            p.append(f"{lang}: 5-8 tags")
        if plan.niche.lower().startswith("line-art stor") and not any(k in (s.title + s.description).lower() for k in ("story", "tale", "fiction", "कहानी", "काल्पनिक")):
            p.append(f"{lang}: label an invented story as a story or fiction in the title or description")
        if not s.thumbnail_text and not s.hook_text:
            p.append(f"{lang}: thumbnail_text or hook_text needed")
    return p


def run_short(plan: Plan, langs: list[str], out: Path, dry_run: bool) -> dict:
    scripts = {"en": plan.english, "hi": plan.hindi}
    today = dt.date.today().isoformat()
    results, failures = {}, []
    if not dry_run and upload.can_upload("en"):
        log.info("Queue: %s", pending.flush(langs))
    for lang in langs:
        try:
            script = scripts[lang]
            video, frame = build.build_short(script, lang, plan.mood, out / f"work_{lang}", script.animation_pack)
            final = out / f"{today}_{lang}.mp4"
            shutil.move(video, final)
            thumb = thumbs.for_script(script, frame, out / f"{today}_{lang}.jpg")
            desc = strategy.up_next(script.description, script.next_video, lang)
            (out / f"{today}_{lang}_youtube.txt").write_text(
                f"TITLE:\n{script.title} #Shorts\n\nDESCRIPTION:\n{desc}\n\nTAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n", encoding="utf-8")
            entry = {"file": final.name, "engine": "lineart"}
            day = config.VIDEOS_DIR / today
            day.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final, day / f"lineart_{lang}.mp4")
            shutil.copy2(out / f"{today}_{lang}_youtube.txt", day / f"lineart_{lang}_youtube.txt")
            shutil.copy2(thumb, day / f"lineart_{lang}_thumbnail.jpg")
            entry["saved_to"] = f"videos/{today}/lineart_{lang}.mp4"
            if dry_run:
                log.info("Dry run: not uploading %s", final)
            else:
                entry.update(pending.publish(final, script, lang, description=desc, topic=plan.topic, thumbnail=thumb))
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so the other language can still be made
            log.exception("Failed to produce the %s line-art Short", lang)
            failures.append(lang)
    if not dry_run and results:
        config.DATA_DIR.mkdir(exist_ok=True)
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": today, "niche": plan.niche, "topic": plan.topic, "mood": plan.mood, "cluster": plan.cluster, "follow_ups": plan.follow_ups,
                     "next_video": plan.english.next_video, "gate_score": plan.gate_score, "engine": "lineart", "videos": results})
        plans_dir = config.DATA_DIR / "plans"
        plans_dir.mkdir(exist_ok=True)
        (plans_dir / f"{today}.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"results": results, "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-file", required=True)
    ap.add_argument("--langs", default=config.LANGS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--out", default="output_lineart")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    raw = Path(args.plan_file).read_text(encoding="utf-8")
    plan = Plan.model_validate_json(raw)
    probs = problems(plan, langs)
    for x in probs:
        log.warning("Plan check: %s", x)
    if args.validate_only:
        log.info("Plan OK: %s | %d problem(s)", plan.topic, len(probs))
        return 1 if probs else 0
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "plan.json").write_text(raw, encoding="utf-8")
    r = run_short(plan, langs, out, args.dry_run)
    (out / "result.json").write_text(json.dumps(r["results"], ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("Done: %s", json.dumps(r["results"], ensure_ascii=False))
    return 1 if r["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
