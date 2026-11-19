"""Thumbnail for the stock-footage style: a Wikimedia Commons photo (same source and licence filter as
`render.py`'s clips: Public domain/CC0 only, no API key) as the background, with the headline, tag chip and
accent colour drawn in PIL - no Three.js engine here, since there is no 3D scene to render a frame from. Reuses
the director thumbnail module's text planning (`shorten`, `_accent_words`, `pick_tag`) so headlines read the
same way across every video style.

    python -m shorts.stockreel.thumbnail "city skyline at night" "Why Cities Never Really Sleep" --lang en --out t.jpg
"""
from __future__ import annotations

import argparse
import logging
import re
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ..director import stock, thumbnail as T
from . import aiframes

log = logging.getLogger(__name__)
SIZES = {"short": (720, 1280), "long": (1280, 720)}
FONT_DIR = Path(__file__).resolve().parents[1] / "explainer" / "fonts"
FONT_LATIN = FONT_DIR / "kalam-latin-700-normal.woff2"
FONT_DEVANAGARI = FONT_DIR / "kalam-devanagari-700-normal.woff2"


def _font_for(text: str) -> Path:
    """Fontsource ships Latin and Devanagari as separate subsetted files; pick the one that actually has the
    glyphs this text needs (mixing them, e.g. a Hindi headline with a Latin acronym, is a known limitation)."""
    return FONT_DEVANAGARI if any("\u0900" <= ch <= "\u097f" for ch in text) else FONT_LATIN


def _photo(query: str, out_dir: Path) -> Path | None:
    got = aiframes.generate_image(query, out_dir / "photo.jpg", 1280, 1280) or stock.fetch_broad(query, out_dir, "photo")
    return got["path"] if got else None


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(query: str, headline: str, tag: str, accent: str, out_jpg: Path, kind: str = "long") -> Path:
    w, h = SIZES[kind]
    land = w > h
    with tempfile.TemporaryDirectory() as td:
        photo = _photo(query, Path(td))
        if photo:
            img = ImageOps.fit(Image.open(photo).convert("RGB"), (w, h), Image.LANCZOS)
        else:   # no match: a plain dark gradient keeps the thumbnail complete rather than blank
            img = Image.new("RGB", (w, h), (18, 20, 30))
            grad = Image.new("L", (1, h), 0)
            for y in range(h):
                grad.putpixel((0, y), int(255 * (y / h) * 0.6))
            img = Image.composite(Image.new("RGB", (w, h), (40, 30, 70)), img, grad.resize((w, h)))
    draw = ImageDraw.Draw(img, "RGBA")
    scrim_h = int(h * 0.48)
    scrim = Image.new("L", (1, scrim_h), 0)
    for y in range(scrim_h):
        scrim.putpixel((0, y), int(235 * (y / scrim_h) ** 1.4))
    draw.bitmap((0, h - scrim_h), scrim.resize((w, scrim_h)), fill=(0, 0, 0, 255))
    full = Image.new("RGBA", img.size, (0, 0, 0, 0))
    full.paste((0, 0, 0, 255), (0, h - scrim_h, w, h), scrim.resize((w, scrim_h)))
    img = Image.alpha_composite(img.convert("RGBA"), full).convert("RGB")
    draw = ImageDraw.Draw(img)
    size = int(h * (0.085 if land else 0.07))
    font = ImageFont.truetype(str(_font_for(headline)), size)
    lines = _wrap(draw, headline.upper(), font, int(w * 0.86))
    ly = h - int(h * 0.1) - len(lines) * int(size * 1.18)
    for i, line in enumerate(lines):
        fill = _hex(accent) if i == len(lines) - 1 else (255, 255, 255)   # the last line (usually the payoff word) in the accent colour
        for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
            draw.text((int(w * 0.07) + dx, ly + dy), line, font=font, fill=(0, 0, 0))
        draw.text((int(w * 0.07), ly), line, font=font, fill=fill)
        ly += int(size * 1.18)
    if tag:
        tagfont = ImageFont.truetype(str(_font_for(tag)), int(size * 0.46))
        tw = draw.textlength(tag.upper(), font=tagfont)
        pad = int(size * 0.22)
        x0, y0 = int(w * 0.06), int(h * 0.06)
        draw.rounded_rectangle((x0, y0, x0 + tw + pad * 2, y0 + int(size * 0.46) + pad), radius=10, fill=_hex(accent))
        draw.text((x0 + pad, y0 + pad * 0.5), tag.upper(), font=tagfont, fill=(5, 7, 13))
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    for q in (92, 85, 75, 60):
        img.save(out_jpg, quality=q, optimize=True)
        if out_jpg.stat().st_size < 1_900_000:
            break
    log.info("Thumbnail %s (%d KB): %s", out_jpg.name, out_jpg.stat().st_size // 1024, headline)
    return out_jpg


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def for_script(script, niche: str, lang: str, out_jpg: Path, short: bool, query: str | None = None) -> Path:
    text = getattr(script, "thumbnail_text", "") or getattr(script, "hook_text", "") or script.title
    headline = T.shorten(text)
    accent = T.M.DEFAULTS["brandSystem"]["defaultPalette"].get("accent", "#FFCC33")
    tag = T.pick_tag(script.title, niche, getattr(script, "thumbnail_tag", None), lang)
    # the headline is drawn separately, on top - the image query is the subject it's about, not the caption
    # text itself (an image model asked for "YOU'D STILL BE FLYING EAST" tries to paint those actual words)
    q = query or re.sub(r"[?!.,'\"]", "", script.title)
    return render(q, headline, tag, accent, out_jpg, "short" if short else "long")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("title")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--out", default="thumbnail.jpg")
    ap.add_argument("--short", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    headline = T.shorten(a.title)
    render(a.query, headline, T.pick_tag(a.title, "", None, a.lang), "#FFCC33", Path(a.out), "short" if a.short else "long")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
