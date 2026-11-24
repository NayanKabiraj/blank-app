"""Videos that could not be uploaded (YouTube's daily upload limit, a network error...) wait in `videos/unpublished/`.

Every run first uploads what is waiting there, oldest first, and deletes each entry once it is on YouTube; only then are the
new videos uploaded. If the daily limit is hit again the run stops trying (the rest stays queued, new videos join the queue),
so nothing is lost and nothing is uploaded twice. Each entry is a folder with the video and a meta.json (title, description,
tags, language, privacy), so it does not depend on a plan or on the videos/<date>/ folders that shorts.cleanup removes.

    python -m shorts.pending list
    python -m shorts.pending flush [--langs en,hi]                    # upload what is waiting (the workflow's `upload` format)
    python -m shorts.pending enqueue-saved --date 2026-11-16          # queue a saved day's Shorts (videos/<date>/ + data/plans/<date>.json)
    python -m shorts.pending enqueue-file video.mp4 --lang en --kind documentary --youtube-txt x_youtube.txt --date 2026-11-16
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from . import config

log = logging.getLogger("shorts.pending")
QUEUE = config.VIDEOS_DIR / "unpublished"
MAX_MB = 90            # GitHub rejects files over 100 MB: a bigger video is re-encoded to fit
MAX_ATTEMPTS = 8
_state = {"quota": False, "auth": False, "scope": False}   # set once during a run: daily limit reached / authorization needed / scope problem


def is_quota_error(exc: BaseException) -> bool:
    return "uploadLimitExceeded" in str(exc) or "exceeded the number of videos" in str(exc)


def _on_error(e: BaseException, name: str) -> str:
    """Classify an upload error and react: only invalid_grant asks the owner to authorize again (see shorts.ytauth)."""
    from . import ytauth
    kind = ytauth.classify(e)
    if kind == "auth":
        _state["auth"] = True
        rec = ytauth.request_authorization("Refresh token expired or was revoked (invalid_grant)." if "invalid_grant" in str(e).lower() or "revoked" in str(e).lower()
                                           else (str(e) or "Google authorization is required.")[:160])
        ytauth.announce(rec)
        log.warning("Authorization needed: %s stays queued and uploads when the owner has authorized", name)
    elif kind == "quota":
        _state["quota"] = True
        log.warning("YouTube quota / daily upload limit reached: %s stays queued, nothing more is uploaded in this run (no new authorization needed)", name)
    elif kind == "scope":
        _state["scope"] = True
        log.error("The stored Google sign-in lacks a permission (insufficient scopes): a configuration problem; re-authorize ONCE with every box ticked (python -m shorts.ytauth url)")
    else:
        log.error("Upload of %s failed (%s): %s", name, kind, str(e)[:200])
    return kind


def _fit(video: Path, dest: Path) -> bool:
    """Copy the video into the queue, re-encoding it when it is too big for a git push."""
    if video.stat().st_size <= MAX_MB * 1e6:
        shutil.copy2(video, dest)
        return True
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True).stdout or 0)
    if dur <= 0:
        return False
    kbps = int((MAX_MB * 0.92 * 8e3) / dur) - 128
    if kbps < 300:
        log.error("%s is too long to fit %d MB; it stays a workflow artifact", video.name, MAX_MB)
        return False
    log.info("Re-encoding %s to about %d kbps so it fits in the repository", video.name, kbps)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-c:v", "libx264", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.4)}k",
                    "-bufsize", f"{kbps * 2}k", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(dest)], check=True)
    return dest.stat().st_size <= 99e6


def enqueue(video: Path, script, lang: str, short: bool, description: str | None, privacy: str | None,
            topic: str = "", date: str | None = None, error: str = "", thumbnail: Path | None = None,
            synthetic: bool | None = None) -> Path | None:
    date = date or dt.date.today().isoformat()
    name = f"{date}_{'short' if short else 'documentary'}_{lang}"
    folder = QUEUE / name
    folder.mkdir(parents=True, exist_ok=True)
    if not _fit(Path(video), folder / "video.mp4"):
        shutil.rmtree(folder, ignore_errors=True)
        return None
    if thumbnail and Path(thumbnail).exists():
        shutil.copy2(thumbnail, folder / "thumbnail.jpg")
    meta = {"lang": lang, "short": short, "date": date, "topic": topic, "title": script.title,
            "description": description if description is not None else script.description, "tags": list(script.tags),
            "privacy": privacy or config.YT_PRIVACY, "synthetic": synthetic, "attempts": 0,
            "queued_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "last_error": error[:300]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    log.warning("Queued %s for the next upload (%s)", name, error[:120] or "not uploaded")
    return folder


def pending(langs: list[str] | None = None) -> list[Path]:
    if not QUEUE.is_dir():
        return []
    out = []
    for f in sorted(QUEUE.iterdir()):
        if (f / "meta.json").exists() and (f / "video.mp4").exists():
            if langs is None or json.loads((f / "meta.json").read_text(encoding="utf-8"))["lang"] in langs:
                out.append(f)
    return out


def _remember(meta: dict, vid: str) -> None:
    """Add the video id to the history entry of the day it was made."""
    path = config.DATA_DIR / ("history.json" if meta["short"] else "documentary_history.json")
    if not path.exists():
        return
    hist = json.loads(path.read_text(encoding="utf-8"))
    for e in hist:
        if e.get("date") == meta["date"]:
            e.setdefault("videos", {}).setdefault(meta["lang"], {}).update({"video_id": vid, "queued": False})
    path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def flush(langs: list[str] | None = None) -> dict:
    """Upload everything waiting (oldest first) and delete each entry after it is up. Stops at the daily limit."""
    from . import upload
    done, left = [], 0
    for folder in pending(langs):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        if _state["quota"] or _state["auth"] or _state["scope"] or not upload.can_upload(meta["lang"]):
            left += 1
            continue
        script = SimpleNamespace(title=meta["title"], description=meta["description"], tags=meta["tags"])
        try:
            thumb = folder / "thumbnail.jpg"
            vid = upload.upload(folder / "video.mp4", script, meta["lang"], short=meta["short"], description=meta["description"],
                                privacy=meta["privacy"], thumbnail=thumb if thumb.exists() else None, synthetic=meta.get("synthetic"))
        except Exception as e:  # noqa: BLE001
            kind = _on_error(e, folder.name)
            if kind not in ("auth", "quota", "scope"):          # waiting for the owner / the limit is not a failed attempt
                meta["attempts"] += 1
            meta["last_error"] = str(e)[:300]
            (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
            left += 1
            continue
        _remember(meta, vid)
        shutil.rmtree(folder)
        done.append({"entry": folder.name, "video_id": vid})
        log.info("Uploaded queued %s as %s and removed it from the queue", folder.name, vid)
    if QUEUE.is_dir() and not any(QUEUE.iterdir()):
        QUEUE.rmdir()
    return {"uploaded": done, "left": left, "quota": _state["quota"], "auth_required": _state["auth"], "scope_problem": _state["scope"]}


def publish(video: Path, script, lang: str, short: bool = True, description: str | None = None, privacy: str | None = None,
            topic: str = "", date: str | None = None, thumbnail: Path | None = None, synthetic: bool | None = None) -> dict:
    """Upload a new video, or queue it when the limit was reached (or the upload fails). Returns the history fields."""
    from . import upload
    if not upload.can_upload(lang):
        log.warning("YouTube secrets missing for %s; skipping upload", lang)
        return {}
    err = ""
    if _state["quota"]:
        err = "daily upload limit already reached in this run"
    elif _state["auth"]:
        err = "Google authorization required (waiting for the owner)"
    elif _state["scope"]:
        err = "the stored Google sign-in lacks a permission (insufficient scopes)"
    else:
        try:
            return {"video_id": upload.upload(video, script, lang, short=short, description=description, privacy=privacy, thumbnail=thumbnail, synthetic=synthetic)}
        except Exception as e:  # noqa: BLE001
            err = str(e)
            log.error("Upload failed: %s", err[:300])
            _on_error(e, f"{date or ''} {lang} video")
    folder = enqueue(Path(video), script, lang, short, description, privacy, topic, date, err, thumbnail, synthetic)
    if _state["auth"]:                                    # list the new queue entry as part of the interrupted operation
        from . import ytauth
        ytauth.request_authorization("Refresh token expired or was revoked (invalid_grant).")
    return {"queued": f"videos/unpublished/{folder.name}" if folder else None, "error": err[:200]}


def _parse_txt(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = text.split("TITLE:\n", 1)[1].split("\n\nDESCRIPTION:", 1)[0].strip()
    desc = text.split("DESCRIPTION:\n", 1)[1].split("\nTAGS:\n", 1)[0].strip()
    tags = [t.strip() for t in text.split("TAGS:\n", 1)[1].split(",") if t.strip()]
    return {"title": title.replace(" #Shorts", ""), "description": desc, "tags": tags}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    f = sub.add_parser("flush")
    f.add_argument("--langs", default="")
    s = sub.add_parser("enqueue-saved")
    s.add_argument("--date", required=True)
    s.add_argument("--langs", default=config.LANGS)
    e = sub.add_parser("enqueue-file")
    e.add_argument("video")
    e.add_argument("--lang", required=True)
    e.add_argument("--kind", choices=["short", "documentary"], required=True)
    e.add_argument("--youtube-txt", required=True)
    e.add_argument("--date", required=True)
    e.add_argument("--topic", default="")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if a.cmd == "list":
        for p in pending():
            m = json.loads((p / "meta.json").read_text(encoding="utf-8"))
            print(f"{p.name}\t{m['title']}\t{p.joinpath('video.mp4').stat().st_size / 1e6:.0f} MB\tattempts {m['attempts']}\t{m['last_error'][:60]}")
        return 0
    if a.cmd == "flush":
        r = flush([x for x in a.langs.split(",") if x] or None)
        print(json.dumps(r))
        return 0 if not r["left"] else 1
    if a.cmd == "enqueue-saved":
        raw = (config.DATA_DIR / "plans" / f"{a.date}.json").read_text(encoding="utf-8")
        if '"schemaVersion"' in raw:
            from .director import manifest as dm
            m = dm.complete(json.loads(raw))
            scripts = {l: dm.script(dm.localize(m, l)) for l in a.langs.split(",")}
            topic = m["creativeBrief"].get("topic", "")
        else:
            from .plan import Plan
            p = Plan.model_validate_json(raw)
            scripts, topic = {"en": p.english, "hi": p.hindi}, p.topic
        for lang in a.langs.split(","):
            enqueue(config.VIDEOS_DIR / a.date / f"{lang}.mp4", scripts[lang], lang, True, None, None, topic, a.date, "queued by hand")
        return 0
    meta = _parse_txt(Path(a.youtube_txt))
    enqueue(Path(a.video), SimpleNamespace(**meta), a.lang, a.kind == "short", meta["description"], None, a.topic, a.date, "queued by hand")
    return 0


if __name__ == "__main__":
    sys.exit(main())
