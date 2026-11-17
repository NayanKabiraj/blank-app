"""Thumbnails, designed like the video: one focal subject, one to four huge words, strong contrast, readable at phone size.

The same Three.js engine that renders the videos draws a single frame (shorts/director/still.cjs): an environment, a
focal 3D subject and the headline. A thumbnail spec is small:

    {"headline": "ZAPPED BY AIR?", "sceneType": "network-nodes", "environment": "data-network",
     "objects": [...optional...], "accentWords": {"AIR": "#FFCC33"}}

Claude writes it as `thumbnail` in a director manifest (and `thumbnail_text` in a whiteboard plan); anything missing is
derived from the video. The title explains the premise, the thumbnail shows the consequence: do not repeat the title.
The result is a JPEG under 2 MB (YouTube's limit), 1280x720 for long videos and 720x1280 for Shorts.

    python -m shorts.director.thumbnail --manifest-file m.json --lang en --out thumb.jpg
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path

from . import build, manifest as M

log = logging.getLogger(__name__)
DIR = Path(__file__).resolve().parent
SIZES = {"short": (720, 1280), "long": (1280, 720)}
# what the scene looks like per channel niche when a whiteboard plan gives no direction (kind of subject + room)
NICHE_LOOK = {
    "How Tech Works": ("diagram-3d", "dark-tech"), "AI Explained": ("network-nodes", "data-network"),
    "Science Explained": ("object-assembly", "holographic-room"), "Space & Universe": ("particle-world", "particle-space"),
    "Human Body": ("network-nodes", "abstract-dark"), "Brain & Psychology": ("network-nodes", "abstract-dark"),
    "Money Explained": ("wave-field", "wave-space"), "Earth & Nature": ("particle-world", "wave-space"),
    "How It's Made": ("object-assembly", "dark-tech"), "Engineering Marvels": ("geometry-swarm", "holographic-room"),
    "India Explained": ("kinetic-typography", "abstract-dark"), "History of Ideas": ("timeline-3d", "digital-city"),
}
ACCENTS = ["#FFCC33", "#00D9FF", "#FF3B6B"]
HERO_SCENES = {"object-assembly", "geometry-swarm", "network-nodes", "diagram-3d", "wave-field", "timeline-3d"}   # scenes with one clear focal subject


def shorten(text: str, max_words: int = 4, max_chars: int = 22) -> str:
    """A thumbnail headline is one to four words, a few characters per word."""
    ws = M.words(text.replace("\n", " "))
    out: list[str] = []
    for w in ws:
        if len(out) >= max_words or len(" ".join(out + [w])) > max_chars:
            break
        out.append(w)
    return " ".join(out) or (ws[0][:max_chars] if ws else "")


def _accent_words(headline: str, given: dict | None, lang: str) -> dict:
    if given:
        return given
    ws = headline.split()
    if not ws:
        return {}
    pick = ws[-1] if len(ws) > 1 else ws[0]      # the last word is usually the consequence
    return {re.sub(r"[?!.,]", "", pick): ACCENTS[0]}


def spec_from_manifest(m: dict, lang: str) -> dict:
    """The thumbnail spec of a (completed) director manifest for one language."""
    t = copy.deepcopy(m.get("thumbnail") or {})
    first = m["scenes"][0]
    loc = (m.get("localizations") or {}).get(lang, {})
    headline = loc.get("thumbnailText") or (t.get("headline") if lang == "en" or not t.get("headline_localized") else None) or t.get("headline")
    if lang != "en" and not loc.get("thumbnailText"):
        headline = None   # an English headline would not be read in a Hindi video: fall back to the localized hook text
    if not headline:
        hook = M.localize(m, lang)["scenes"][0]
        headline = (hook["textElements"][0]["text"] if hook.get("textElements") else M.localize(m, lang).get("publishingMetadata", {}).get("title", ""))
    headline = shorten(headline)
    hero = first["sceneType"] if first["sceneType"] in HERO_SCENES else "object-assembly"
    return {"headline": headline, "lang": lang, "sceneType": t.get("sceneType") or hero,
            "environment": t.get("environment") or first["environment"]["preset"], "objects": t.get("objects") or (first.get("objects") if hero == first["sceneType"] else None),
            "accentWords": _accent_words(headline, (loc.get("thumbnailAccent") or t.get("accentWords")), lang),
            "palette": m["brandSystem"]["defaultPalette"], "seed": m["randomization"]["globalSeed"], "concept": t.get("concept", "")}


def spec_from_script(script, niche: str, lang: str) -> dict:
    """Whiteboard plans: `thumbnail_text` if Claude wrote one, else the hook text, else the first words of the title."""
    text = getattr(script, "thumbnail_text", "") or getattr(script, "hook_text", "") or script.title
    scene_type, env = NICHE_LOOK.get(niche, ("object-assembly", "abstract-dark"))
    if scene_type not in HERO_SCENES:
        scene_type = "object-assembly"
    headline = shorten(text)
    return {"headline": headline, "lang": lang, "sceneType": scene_type, "environment": env, "objects": None,
            "accentWords": _accent_words(headline, None, lang), "palette": M.DEFAULTS["brandSystem"]["defaultPalette"],
            "seed": sum(map(ord, script.title)) % 100000, "concept": ""}


def _engine_cfg(spec: dict, w: int, h: int, still_path: Path) -> dict:
    land = w > h
    scene = {"sceneType": spec["sceneType"], "storyPhase": "hook", "narration": {"text": "thumbnail", "startSeconds": 0.1, "endSeconds": 3.5},
             "environment": {"preset": spec["environment"], "fogDensity": 0.05, "backgroundMotion": "drift"},
             "camera": {"preset": "dolly-out", "speed": 0.3, "fov": 46}, "energy": 0.9, "durationSeconds": 4.0,
             "textElements": [{"id": "headline", "text": spec["headline"], "animation": "kinetic-sentence",
                               "position": {"x": 0, "y": -3.3 if land else -2.6, "z": 0},
                               "style": {"scale": 1.0 if land else 1.1, "accentWords": spec["accentWords"]}}]}
    if spec.get("objects"):
        scene["objects"] = spec["objects"]
    m = {"creativeBrief": {"format": "documentary" if land else "short", "targetDurationSeconds": 4,
                           "resolution": {"width": w, "height": h}, "framesPerSecond": 30},
         "randomization": {"globalSeed": spec["seed"]}, "scenes": [scene],
         "renderSettings": {"safeArea": {"topPercent": 4, "bottomPercent": 4, "leftPercent": 4, "rightPercent": 4},
                            "postProcessing": {"glitch": {"enabled": False}, "filmGrain": {"strength": 0.0}, "bloom": {"strength": 0.5}}},
         "brandSystem": {"defaultPalette": spec["palette"], "typography": {"preferredHeadlineFontSizePixels": 96}}}
    m = M.complete(m)
    sc = m["scenes"][0]
    sc["startSeconds"], sc["endSeconds"], sc["durationSeconds"] = 0.0, 4.0, 4.0
    for te in sc["textElements"]:
        te["startSeconds"], te["durationSeconds"] = 0.0, 4.0     # scene-local, visible for the whole frame time
    sc["transitionOut"] = {"type": "fade-through-black", "durationSeconds": 0.1}
    cfg = build.engine_cfg(m, spec["lang"], 4.0, [], {"env": [0.0] * 150, "beats": [], "major": []})
    cfg.update({"renderScale": 1.0, "msaa": 4, "workers": 1, "stills": [{"t": 2.0, "path": str(still_path)}]})
    cfg["manifest"]["captions"] = {"enabled": False}
    return cfg


def render(spec: dict, out_jpg: Path, kind: str = "long") -> Path | None:
    """Draw the thumbnail to `out_jpg` (JPEG, under 2 MB). Returns the path, or None if the engine is not installed/fails."""
    w, h = SIZES[kind]
    out_jpg = Path(out_jpg)
    if not (DIR / "node_modules").exists():
        log.warning("Thumbnail skipped: shorts/director has no node_modules (npm ci)")
        return None
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "thumb.png"
        cfg_path = Path(td) / "cfg.json"
        cfg_path.write_text(json.dumps(_engine_cfg(spec, w, h, png), ensure_ascii=False), encoding="utf-8")
        try:
            subprocess.run(["node", str(DIR / "still.cjs"), str(cfg_path)], check=True, cwd=DIR, timeout=300)
        except (subprocess.SubprocessError, OSError) as e:
            log.warning("Thumbnail render failed: %s", e)
            return None
        out_jpg.parent.mkdir(parents=True, exist_ok=True)
        for q in (2, 4, 7, 12):     # smaller and smaller until it is under YouTube's 2 MB limit
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png), "-q:v", str(q), str(out_jpg)], check=True)
            if out_jpg.stat().st_size < 1_900_000:
                break
    log.info("Thumbnail %s (%d KB): %s", out_jpg.name, out_jpg.stat().st_size // 1024, spec["headline"])
    return out_jpg


def for_manifest(m: dict, lang: str, out_jpg: Path) -> Path | None:
    return render(spec_from_manifest(m, lang), out_jpg, "long" if M.is_documentary(m) else "short")


def for_script(script, niche: str, lang: str, out_jpg: Path, short: bool) -> Path | None:
    return render(spec_from_script(script, niche, lang), out_jpg, "short" if short else "long")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-file", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--out", default="thumbnail.jpg")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    m = M.complete(M.load(a.manifest_file))
    p = for_manifest(m, a.lang, Path(a.out))
    return 0 if p else 1


if __name__ == "__main__":
    raise SystemExit(main())
