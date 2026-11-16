"""Director entry point: a manifest written by Claude -> dynamic Three.js videos (EN + HI) -> upload -> history.

    python -m shorts.director.run --manifest-file m.json                 # render + save (+ upload when secrets exist)
    python -m shorts.director.run --manifest-file m.json --dry-run       # render only
    python -m shorts.director.run --manifest-file m.json --validate-only # check the manifest, render nothing
    python -m shorts.director.run schema                                 # the registered presets the engine understands

The same manifest drives Shorts (1080x1920) and documentaries (1920x1080, `creativeBrief.format: "documentary"`).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
from pathlib import Path

from .. import config, upload
from . import build, manifest as M

log = logging.getLogger("shorts.director")


def _stamp(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}" if sec < 3600 else f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def schema() -> dict:
    return {"sceneTypes": M.SCENE_TYPES, "cameraPresets": M.CAMERA_PRESETS, "objectTypes": M.OBJECT_TYPES, "objectBehaviors": M.BEHAVIORS,
            "textAnimations": M.TEXT_ANIMATIONS, "transitions": M.TRANSITIONS, "environments": M.ENVIRONMENTS, "storyPhases": M.PHASES}


def check(path: str, langs: list[str]) -> tuple[dict, list[str], list[str]]:
    m = M.complete(M.load(path))
    errs, warns = M.validate(m)
    for lang in langs:
        try:
            M.localize(m, lang)
        except ValueError as e:
            errs.append(str(e))
    return m, errs, warns


def write_history(m: dict, results: dict, today: str) -> None:
    """Topic memory for the daily task (data/history.json or data/documentary_history.json) and, for Shorts, the manifest
    under data/plans/<date>.json (which upload_saved uses for titles and tags)."""
    config.DATA_DIR.mkdir(exist_ok=True)
    topic = m["creativeBrief"].get("topic", "")
    niche = m["creativeBrief"].get("niche", "Technology")
    if is_doc(m):
        hist_file = config.DATA_DIR / "documentary_history.json"
        hist = json.loads(hist_file.read_text()) if hist_file.exists() else []
        hist.append({"date": today, "niche": niche, "topic": topic, "minutes": round(m["scenes"][-1]["endSeconds"] / 60, 1), "engine": "director", "videos": results})
        hist_file.write_text(json.dumps(hist[-200:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": today, "niche": niche, "topic": topic, "mood": build.music_mood(m), "engine": "director", "videos": results})
        plans = config.DATA_DIR / "plans"
        plans.mkdir(exist_ok=True)
        (plans / f"{today}.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_doc(m: dict) -> bool:
    return M.is_documentary(m)


def history_from(folder: str) -> int:
    """`run history <dir>`: merge the result.json files the per-language jobs produced into one history entry."""
    root = Path(folder)
    found = sorted(root.rglob("result.json"))
    if not found:
        log.error("no result.json under %s", folder)
        return 1
    results, today = {}, None
    for f in found:
        r = json.loads(f.read_text(encoding="utf-8"))
        results.update(r["results"])
        today = r["date"]
    m = json.loads(sorted(root.rglob("manifest.json"))[0].read_text(encoding="utf-8"))
    write_history(m, results, today)
    log.info("History written for %s", sorted(results))
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "schema":
        print(json.dumps(schema(), indent=2))
        return 0
    if len(sys.argv) > 2 and sys.argv[1] == "history":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        return history_from(sys.argv[2])
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-file", required=True)
    ap.add_argument("--langs", default="en,hi")
    ap.add_argument("--dry-run", action="store_true", help="render but do not upload")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--keep-in-repo", action="store_true", help="documentaries: also copy the video into videos/<date>/")
    ap.add_argument("--no-history", action="store_true", help="the workflow writes the history once, after all languages")
    ap.add_argument("--out", default="output_director")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]

    m, errs, warns = check(args.manifest_file, langs)
    for w in warns:
        log.warning("Manifest check: %s", w)
    for e in errs:
        log.error("Manifest error: %s", e)
    if errs and m["validation"].get("onError", "fail") == "fail":
        log.error("The manifest has %d error(s); not rendering. Fix them and send it again.", len(errs))
        return 2
    if args.validate_only:
        log.info("Manifest OK: %d scenes, %.1fs planned, %d warning(s)", len(m["scenes"]), m["scenes"][-1]["endSeconds"], len(warns))
        return 0

    doc = M.is_documentary(m)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    today = dt.date.today().isoformat()
    results, failures = {}, []
    for lang in langs:
        try:
            ml = M.localize(m, lang)
            rep = build.build(ml, lang, out / f"work_{lang}", out / lang)
            script = M.script(ml)
            desc = script.description
            if doc and rep.get("chapters"):
                lines = "\n".join(f"{_stamp(t)} {title}" for title, t in rep["chapters"])
                desc = f"{desc}\n\nChapters:\n{lines}\n"
            final = out / f"{today}_{'documentary_' if doc else ''}{lang}.mp4"
            shutil.copy2(rep["files"]["video"], final)
            (out / f"{today}_{'documentary_' if doc else ''}{lang}_youtube.txt").write_text(
                f"TITLE:\n{script.title}{'' if doc else ' #Shorts'}\n\nDESCRIPTION:\n{desc}\n\nTAGS:\n{', '.join(script.tags)}\n", encoding="utf-8")
            entry = {"file": final.name, "seconds": rep["seconds"], "issues": rep["checks"]["issues"], "engine": "director"}
            if not doc or args.keep_in_repo:   # Shorts are small enough to keep in the repo; documentaries are only artifacts
                day = config.VIDEOS_DIR / today
                day.mkdir(parents=True, exist_ok=True)
                name = f"documentary_{lang}" if doc else lang
                shutil.copy2(final, day / f"{name}.mp4")
                shutil.copy2(out / f"{final.stem}_youtube.txt", day / f"{name}_youtube.txt")
                entry["saved_to"] = f"videos/{today}/{name}.mp4"
            if args.dry_run:
                log.info("Dry run: not uploading %s", final)
            elif not upload.can_upload(lang):
                log.warning("YouTube secrets missing for %s; skipping upload", lang)
            else:
                priv = M.privacy(ml, config.YT_PRIVACY)
                entry["video_id"] = upload.upload(final, script, lang, short=not doc, description=desc, privacy=priv)
                entry["privacy"] = priv
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so the other language can still be made
            log.exception("Failed to produce the %s video", lang)
            failures.append(lang)

    (out / "result.json").write_text(json.dumps({"date": today, "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    if not args.dry_run and results and not args.no_history:
        write_history(m, results, today)
    log.info("Done: %s", json.dumps(results, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
