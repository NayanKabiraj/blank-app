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

from . import build, manifest as M, stock

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
# a short tag chip (top corner) is part of the lettering: "WHAT IF?" for hypotheticals, otherwise the subject of the channel's niche
NICHE_TAG = {"How Tech Works": "TECH", "AI Explained": "AI", "Science Explained": "SCIENCE", "Space & Universe": "SPACE", "Human Body": "YOUR BODY",
             "Brain & Psychology": "YOUR BRAIN", "Money Explained": "MONEY", "Earth & Nature": "EARTH", "How It's Made": "HOW IT'S MADE",
             "Engineering Marvels": "ENGINEERING", "India Explained": "INDIA", "History of Ideas": "HISTORY", "Technology": "TECH"}
WHAT_IF = re.compile(r"^\s*(what\s+(if|happens|would)|अगर|क्या\s+हो\s+अगर)", re.I)
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


def pick_tag(title: str, niche: str, given: str | None, lang: str = "en") -> str:
    if given is not None:
        return given[:14]
    if WHAT_IF.search(title or ""):
        return "अगर?" if lang == "hi" else "WHAT IF?"
    return NICHE_TAG.get(niche, "")


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
            "palette": m["brandSystem"]["defaultPalette"], "seed": m["randomization"]["globalSeed"], "concept": t.get("concept", ""),
            "title": M.localize(m, lang).get("publishingMetadata", {}).get("title", ""),
            "tag": pick_tag(M.localize(m, lang).get("publishingMetadata", {}).get("title", ""), m["creativeBrief"].get("niche", ""), loc.get("thumbnailTag", t.get("tag")) if lang != "en" or "tag" in t else None, lang)}


def spec_from_script(script, niche: str, lang: str) -> dict:
    """Whiteboard plans: `thumbnail_text` if Claude wrote one, else the hook text, else the first words of the title."""
    text = getattr(script, "thumbnail_text", "") or getattr(script, "hook_text", "") or script.title
    scene_type, env = NICHE_LOOK.get(niche, ("object-assembly", "abstract-dark"))
    if scene_type not in HERO_SCENES:
        scene_type = "object-assembly"
    headline = shorten(text)
    return {"headline": headline, "lang": lang, "sceneType": scene_type, "environment": env, "objects": None,
            "accentWords": _accent_words(headline, None, lang), "palette": M.DEFAULTS["brandSystem"]["defaultPalette"],
            "seed": sum(map(ord, script.title)) % 100000, "concept": "",
            "title": script.title, "tag": pick_tag(script.title, niche, getattr(script, "thumbnail_tag", None), lang)}


SUBJECTS = [("moon", re.compile(r"\b(moon|lunar|supermoon|eclipse)\b|चाँद|चांद|चंद्र", re.I)), ("sun", re.compile(r"\b(sun|solar|star)\b|सूरज|सूर्य", re.I)),
            ("earth", re.compile(r"\b(earth|planet|gravity|ocean|tides?|world|globe)\b|पृथ्वी|धरती", re.I))]
BRIGHT = {"moon": "thumb-grape", "sun": "thumb-ocean", "earth": "thumb-sunset"}
BRIGHT_BY_SEED = ["thumb-sunset", "thumb-ocean", "thumb-grape", "thumb-lime"]
VARIANTS = ("hero", "duo", "giant")


def pick_subject(spec: dict) -> str | None:
    text = " ".join([spec.get("title", ""), spec.get("headline", ""), spec.get("concept", "")])
    for kind, rx in SUBJECTS:
        if rx.search(text):
            return kind
    return None


def _subject_objects(spec: dict, kind: str, land: bool) -> tuple[list[dict], list[dict]]:
    """(objects, stickers) of the three variants. hero: one big body + friendly face; duo: two bodies + a "=?" burst; giant: one huge body, no face."""
    v, accent = spec.get("variant") or "hero", spec["palette"].get("accent", "#FFCC33")
    q = "?" in spec["headline"] or spec.get("tag") in ("WHAT IF?", "अगर?")
    mood = spec.get("mood") or ("surprised" if q else "happy")
    def body(x, y, sc, t=None):
        return {"id": f"b{x}", "type": t or kind, "position": {"x": x, "y": y, "z": 0}, "scale": sc, "spin": 0.1}
    if v == "duo":
        objs = [body(-2.9, 1.0, 0.62), body(2.4, 1.0, 0.9)] if land else [body(-1.5, 2.2, 0.8), body(1.4, 0.2, 1.1)]
        st = [{"type": "burst", "nx": 0.0, "ny": 0.28 if land else 0.1, "size": 0.34, "color": accent, "text": "?!"}]
        return objs, st
    if v == "giant":
        objs = [body(1.9, 0.9, 1.05)] if land else [body(0.0, 1.6, 1.5)]
        return objs, [{"type": "arrow", "nx": -0.5 if land else -0.55, "ny": 0.2 if land else 0.25, "size": 0.3, "color": accent}] if q else []
    objs = [body(2.4, 0.9, 0.85)] if land else [body(0.0, 1.8, 1.25)]
    st = [{"type": "face", "mood": mood, "nx": -0.6 if land else -0.72, "ny": 0.1 if land else 0.56, "size": 0.3 if land else 0.26, "look": 0.7, "tilt": -6}]
    return objs, st


STOCK_QUERY = {"moon": "full moon lunar", "sun": "sun solar", "earth": "Earth from space"}


def stock_query(spec: dict, kind: str | None) -> str:
    return spec.get("stock_query") or STOCK_QUERY.get(kind or "") or re.sub(r"[?!.,]", "", spec.get("headline", ""))


def composite_photo(jpg_in: Path, photo: Path, out: Path, land: bool) -> None:
    """Paste the stock photo as a round, white-rimmed 'porthole' on the subject spot (where the 3D body would be), with a soft shadow."""
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
    base = Image.open(jpg_in).convert("RGB"); W, H = base.size
    d = int(H * 0.56) if land else int(W * 0.56)
    cx, cy = (int(W * 0.76), int(H * 0.34)) if land else (int(W * 0.56), int(H * 0.34))
    img = ImageOps.fit(Image.open(photo).convert("RGB"), (d, d), Image.LANCZOS)
    mask = Image.new("L", (d * 4, d * 4), 0); ImageDraw.Draw(mask).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255); mask = mask.resize((d, d), Image.LANCZOS)
    rim = max(8, d // 40)
    shadow = Image.new("L", (d + 2 * rim + 60, d + 2 * rim + 60), 0); ImageDraw.Draw(shadow).ellipse((30, 30, d + 2 * rim + 30, d + 2 * rim + 30), fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    base.paste((0, 0, 0), (cx - d // 2 - rim - 30 + 10, cy - d // 2 - rim - 30 + 14), shadow)
    ring = Image.new("L", (d + 2 * rim, d + 2 * rim), 0); ImageDraw.Draw(ring).ellipse((0, 0, d + 2 * rim - 1, d + 2 * rim - 1), fill=255)
    base.paste((255, 255, 255), (cx - d // 2 - rim, cy - d // 2 - rim), ring)
    base.paste(img, (cx - d // 2, cy - d // 2), mask)
    base.save(out, quality=92)


def stickers_for(spec: dict, land: bool) -> list[dict]:
    """Click-catching, friendly extras: a reaction face looking at the subject, a ring around the subject, a "?" badge. Faces and
    curiosity cues are what make people tap; `spec["stickers"] = False` turns them off, a list replaces them."""
    given = spec.get("stickers")
    if given is False:
        return []
    if isinstance(given, list):
        return given
    q = "?" in spec["headline"] or WHAT_IF.search(spec.get("title", "") or "") is not None or spec.get("tag") in ("WHAT IF?", "अगर?")
    mood = spec.get("mood") or ("surprised" if q else "happy")
    accent = spec["palette"].get("accent", "#FFCC33")
    if land:
        out = [{"type": "ring", "nx": -0.12, "ny": 0.2, "size": 0.66, "color": "#FF3B6B"},
               {"type": "face", "mood": mood, "nx": 0.72, "ny": 0.28, "size": 0.44, "look": -0.8, "tilt": 6}]
        if q:
            out.append({"type": "qmark", "nx": -0.84, "ny": 0.1, "size": 0.28, "color": accent, "tilt": -12})
    else:
        out = [{"type": "ring", "nx": 0.0, "ny": 0.16, "size": 0.62, "color": "#FF3B6B"},
               {"type": "face", "mood": mood, "nx": 0.52, "ny": 0.6, "size": 0.4, "look": -0.8, "tilt": 6}]
        if q:
            out.append({"type": "qmark", "nx": -0.5, "ny": 0.45, "size": 0.26, "color": accent, "tilt": -10})
    return out


def _engine_cfg(spec: dict, w: int, h: int, still_path: Path) -> dict:
    land = w > h
    scene = {"sceneType": spec["sceneType"], "storyPhase": "hook", "narration": {"text": "thumbnail", "startSeconds": 0.1, "endSeconds": 3.5},
             "environment": {"preset": spec["environment"], "fogDensity": 0.05, "backgroundMotion": "drift"},
             "camera": {"preset": "dolly-out", "speed": 0.3, "fov": 46}, "energy": 0.9, "durationSeconds": 4.0,
             "textElements": [{"id": "headline", "text": spec["headline"], "animation": "kinetic-sentence",
                               "position": {"x": 0, "y": -3.3 if land else -2.6, "z": 0},
                               "style": {"scale": 1.0 if land else 1.1, "accentWords": spec["accentWords"], "outline": True,
                                         "gradient": ["#FFFFFF", "#FFE9A6"], "tilt": -2.5}}]}
    if spec.get("tag"):
        scene["textElements"].append({"id": "tag", "text": spec["tag"], "animation": "kinetic-sentence", "position": {"x": -3.1 if land else -1.3, "y": 4.4 if land else 3.5, "z": 0},
                                      "style": {"scale": 0.42, "color": "#05070D", "chip": spec["palette"].get("accent", "#FFCC33"), "tilt": -4, "outline": False}})
    kind = None if spec.get("stickers") is False and spec.get("objects") else pick_subject(spec)
    if kind and not spec.get("objects") and spec.get("variant") != "classic":
        spec.setdefault("variant", "hero")
        scene["sceneType"], scene["environment"]["preset"] = "kinetic-typography", BRIGHT.get(kind, BRIGHT_BY_SEED[spec["seed"] % 4])
        scene["objects"], scene["stickers"] = _subject_objects(spec, kind, land)
        if spec.get("photo"):
            scene["objects"] = []     # the stock photo is composited over the spot afterwards
    else:
        if spec.get("objects"):
            scene["objects"] = spec["objects"]
        scene["stickers"] = stickers_for(spec, land)
    m = {"creativeBrief": {"format": "documentary" if land else "short", "targetDurationSeconds": 4,
                           "resolution": {"width": w, "height": h}, "framesPerSecond": 30},
         "randomization": {"globalSeed": spec["seed"]}, "scenes": [scene],
         "renderSettings": {"safeArea": {"topPercent": 4, "bottomPercent": 4, "leftPercent": 4, "rightPercent": 4},
                            "postProcessing": {"glitch": {"enabled": False}, "filmGrain": {"strength": 0.0}, "bloom": {"strength": 0.3},
                                            "look": {"saturation": 1.25, "gain": 1.0}}},   # brighter and more saturated than the video
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
        got = stock.fetch(stock_query(spec, pick_subject(spec)), Path(td), "stock") if spec.get("stock", True) and spec.get("variant", "hero") == "hero" and pick_subject(spec) else None
        if got:     # a relevant public-domain photo replaces the 3D body; on any failure the textured 3D body version stays
            png2 = Path(td) / "thumb_photo.png"
            try:
                cfg_path.write_text(json.dumps(_engine_cfg({**spec, "photo": True}, w, h, png2), ensure_ascii=False), encoding="utf-8")
                subprocess.run(["node", str(DIR / "still.cjs"), str(cfg_path)], check=True, cwd=DIR, timeout=300)
                composite_photo(png2, got["path"], Path(td) / "thumb_photo.jpg", w > h)
                png = Path(td) / "thumb_photo.jpg"
                log.info("Thumbnail photo credit: %s", got["credit"])
            except Exception as e:  # noqa: BLE001
                log.warning("Stock composite failed, keeping the 3D body: %s", e)
        from PIL import Image
        img = Image.open(png).convert("RGB")
        for q in (92, 85, 75, 60):     # smaller and smaller until it is under YouTube's 2 MB limit
            img.save(out_jpg, quality=q, optimize=True)
            if out_jpg.stat().st_size < 1_900_000:
                break
    log.info("Thumbnail %s (%d KB): %s", out_jpg.name, out_jpg.stat().st_size // 1024, spec["headline"])
    return out_jpg


def for_manifest(m: dict, lang: str, out_jpg: Path) -> Path | None:
    return render(spec_from_manifest(m, lang), out_jpg, "long" if M.is_documentary(m) else "short")


def for_script(script, niche: str, lang: str, out_jpg: Path, short: bool) -> Path | None:
    return render(spec_from_script(script, niche, lang), out_jpg, "short" if short else "long")


# headlines for queued videos: meta.json "thumbnail_text" wins, else a short hook from the topic
def refresh_queue(root: Path = Path("videos/unpublished")) -> int:
    """Redraw thumbnail.jpg of every queued video with the current design (run in CI, where the stock photo lookup has internet)."""
    n = 0
    for meta_path in sorted(root.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        title = meta.get("title", "")
        head = meta.get("thumbnail_text") or shorten(re.sub(r"\(.*?\)", "", title).strip() or meta.get("topic", ""))
        lang = meta.get("lang", "en")
        spec = {"headline": head, "lang": lang, "sceneType": "object-assembly", "environment": "abstract-dark", "objects": None,
                "accentWords": _accent_words(head, None, lang), "palette": M.DEFAULTS["brandSystem"]["defaultPalette"],
                "seed": sum(map(ord, title)) % 100000, "concept": meta.get("topic", ""), "title": title or meta.get("topic", ""),
                "tag": pick_tag(title, "Space & Universe", None, lang)}
        if render(spec, meta_path.parent / "thumbnail.jpg", "short" if meta.get("short") else "long"):
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-queue", action="store_true", help="redraw the thumbnails of videos waiting in videos/unpublished/")
    ap.add_argument("--manifest-file")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--out", default="thumbnail.jpg")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if a.refresh_queue:
        return 0 if refresh_queue() else 1
    if not a.manifest_file:
        ap.error("--manifest-file or --refresh-queue is required")
    m = M.complete(M.load(a.manifest_file))
    p = for_manifest(m, a.lang, Path(a.out))
    return 0 if p else 1


if __name__ == "__main__":
    raise SystemExit(main())
