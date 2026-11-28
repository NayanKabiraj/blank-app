"""Thumbnail for a line-art Short: a frame from the video (the moment the story pays off) with the headline in big outlined type. No network, no stock photo."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..stockreel import thumbnail as base


def for_script(script, frame: Path, out_jpg: Path) -> Path:
    text = (getattr(script, "thumbnail_text", "") or getattr(script, "hook_text", "") or script.title).upper()
    img = Image.open(frame).convert("RGB").resize((1080, 1920))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(base._font_for(text)), 150)
    lines = base._wrap(d, text, font, 960)[:3]
    y = 150
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((1080 - w) / 2, y), ln, font=font, fill=(255, 214, 90), stroke_width=9, stroke_fill=(20, 18, 30))
        y += 170
    for q in (92, 85, 75, 60):
        img.save(out_jpg, quality=q, optimize=True)
        if out_jpg.stat().st_size < 1_900_000:
            break
    return out_jpg
