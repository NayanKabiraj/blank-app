"""Cinematic typography: locates a clean sans-serif for each language (Noto Sans / Noto Sans Devanagari,
installed system-wide by the workflow's `fonts-noto-core`/`fonts-noto-ui-core` packages - see
`.github/workflows/daily-shorts.yml`), falling back to the repo's bundled Kalam fonts so the engine still
runs somewhere those apt packages aren't installed (a local smoke test, for instance). Caches everything
so a 55-second render never re-resolves or re-opens the same font file per frame.
"""
from __future__ import annotations

import functools
import logging
import shutil
import subprocess
from pathlib import Path

from PIL import ImageFont

log = logging.getLogger(__name__)

_FALLBACK_DIR = Path(__file__).resolve().parents[1] / "explainer" / "fonts"
_FALLBACK = {
    "en": {False: _FALLBACK_DIR / "kalam-latin-400-normal.woff2", True: _FALLBACK_DIR / "kalam-latin-700-normal.woff2"},
    "hi": {False: _FALLBACK_DIR / "kalam-devanagari-400-normal.woff2", True: _FALLBACK_DIR / "kalam-devanagari-700-normal.woff2"},
}
_FC_NAMES = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}


@functools.lru_cache(maxsize=4)
def _font_file(lang: str, bold: bool) -> Path:
    """The TTF/OTF path for `lang`'s clean sans-serif, via fontconfig; the bundled woff2 if that fails.

    Fontconfig always returns *some* substitute, even one that cannot shape the requested script (e.g.
    a Latin-only font standing in for "Noto Sans Devanagari" on a box that never installed it) - for
    Hindi, trust the match only when fontconfig actually named a Devanagari family; otherwise prefer the
    bundled Kalam Devanagari font, which we know can render it.
    """
    name = _FC_NAMES.get(lang, "Noto Sans") + (":bold" if bold else "")
    if shutil.which("fc-match"):
        try:
            out = subprocess.run(["fc-match", "-f", "%{family}\t%{file}", name], capture_output=True, text=True, timeout=5)
            family, _, file_str = out.stdout.strip().partition("\t")
            path = Path(file_str)
            ok_script = lang != "hi" or "devanagari" in family.lower()
            if out.returncode == 0 and path.is_file() and ok_script:
                return path
        except (subprocess.SubprocessError, OSError) as e:
            log.warning("fc-match failed for %r: %s", name, e)
    log.warning("%s not found for lang=%s, falling back to the bundled Kalam font", name, lang)
    return _FALLBACK.get(lang, _FALLBACK["en"])[bold]


@functools.lru_cache(maxsize=64)
def font(lang: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = _font_file(lang, bold)
    try:
        return ImageFont.truetype(str(path), size)
    except OSError as e:
        log.warning("Could not load %s (%s), falling back to Kalam: %s", path, lang, e)
        return ImageFont.truetype(str(_FALLBACK.get(lang, _FALLBACK["en"])[bold]), size)


def wrap(draw, text: str, f: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word-wrap (character-wrap for scripts with no spaces, e.g. a single very long word)."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def fit_size(draw, text: str, lang: str, max_w: int, max_h: int, start: int, min_size: int = 28,
             bold: bool = True, line_spacing: float = 1.18) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """The largest font size (stepping down from `start`) whose wrapped lines fit inside max_w x max_h."""
    size = start
    while size > min_size:
        f = font(lang, size, bold)
        lines = wrap(draw, text, f, max_w)
        line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * line_spacing
        if line_h * len(lines) <= max_h and all(draw.textlength(ln, font=f) <= max_w for ln in lines):
            return f, lines
        size -= 2
    f = font(lang, min_size, bold)
    return f, wrap(draw, text, f, max_w)
