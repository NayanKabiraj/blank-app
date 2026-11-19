"""Text reveal and highlight animations shared by every scene in `graphics.py`: a cinematic title that
rises and fades in word by word, and a keyword underline/glow sweep. Takes a progress fraction `p` in
[0, 1] (the caller maps scene-local time to it), not an absolute frame index, so every scene can run its
reveal at its own pace independent of the renderer's frame loop.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import effects, typography


def draw_title(canvas: Image.Image, text: str, lang: str, center: tuple[int, int], max_w: int, p: float,
               color: str = effects.PALETTE["white"], accent: str = effects.PALETTE["blue"],
               size: int = 96, bold: bool = True) -> None:
    """Each word rises up and fades in, left to right, finishing by p=0.6 so it can hold on screen."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    f, lines = typography.fit_size(draw, text, lang, max_w, max_w * 2, size, bold=bold)
    words = [w for ln in lines for w in [ln]]  # keep wrapped lines as units; per-word reveal within a line below
    line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * 1.25
    total_h = line_h * len(lines)
    y = center[1] - total_h / 2
    n_words = sum(len(ln.split()) for ln in lines)
    done = 0
    for ln in lines:
        ws = ln.split()
        line_w = draw.textlength(ln, font=f)
        x = center[0] - line_w / 2
        for w in ws:
            ww = draw.textlength(w + " ", font=f)
            reveal_at = done / max(1, n_words) * 0.6
            local = effects.ease_out_cubic((p - reveal_at) / 0.18) if p > reveal_at else 0.0
            if local > 0:
                rise = (1 - local) * 22
                alpha = int(255 * local)
                draw.text((x, y + rise), w, font=f, fill=(*_rgb(color), alpha))
            x += ww
            done += 1
        y += line_h
    if p > 0.65:
        bar_p = effects.ease_in_out((p - 0.65) / 0.25)
        bar_w = max_w * 0.22 * bar_p
        by = center[1] + total_h / 2 + 14
        draw.rounded_rectangle([center[0] - bar_w / 2, by, center[0] + bar_w / 2, by + 5], radius=3,
                                fill=(*_rgb(accent), 230))


def _rgb(hexcolor: str) -> tuple[int, int, int]:
    h = hexcolor.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def draw_caption(canvas: Image.Image, text: str, lang: str, center_x: int, y: int, max_w: int, p: float,
                 accent: str = effects.PALETTE["gold"], size: int = 46) -> None:
    """A smaller supporting line under the headline - fades/rises in slightly after the title."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    f, lines = typography.fit_size(draw, text, lang, max_w, max_w, size, min_size=24, bold=False)
    local = effects.ease_out_cubic(p)
    alpha = int(255 * local)
    rise = (1 - local) * 14
    line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * 1.3
    yy = y + rise
    for ln in lines:
        w = draw.textlength(ln, font=f)
        draw.text((center_x - w / 2, yy), ln, font=f, fill=(*_rgb(accent), alpha))
        yy += line_h


def pulse(p: float, speed: float = 2.4) -> float:
    """A gentle 0..1..0 breathing value for glow intensity, line widths, etc."""
    import math
    return 0.5 + 0.5 * math.sin(p * speed * 2 * math.pi)
