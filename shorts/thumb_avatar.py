"""Eye-catching thumbnails for the generated-animation videos: a big QUESTION about the topic, the presenter's face (the owner's avatar,
cut out, white outline, mouth open in surprise) and a topic picture on a bold gradient.

    for_script(script, niche, lang, out_jpg, short) -> Path     # 1280x720 (documentary) or 1080x1920 (Short)

The question is `script.thumbnail_question` (<= 8 words, ends with "?"); when a plan has none it is derived from the title/hook.
"""
from __future__ import annotations

import math
import random
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONTS = ["/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
PALETTES = [((10, 16, 60), (90, 40, 170), (255, 216, 77)), ((6, 30, 70), (0, 120, 190), (255, 120, 80)),
            ((40, 10, 60), (190, 40, 110), (255, 226, 90)), ((8, 40, 40), (20, 150, 120), (255, 190, 60))]
SUBJECTS = [("hole", re.compile(r"black hole", re.I)), ("moon", re.compile(r"\b(moon|lunar|eclipse)\b", re.I)),
            ("sun", re.compile(r"\b(sun|solar|star)\b", re.I)), ("earth", re.compile(r"\b(earth|gps|satellite|tides?|ocean|planet|gravity)\b", re.I))]


def _font(size: int):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def question_for(script) -> str:
    q = (getattr(script, "thumbnail_question", "") or "").strip()
    if q:
        return q if q.endswith("?") else q + "?"
    title = re.sub(r"#\w+", "", script.title).strip()
    if title.endswith("?"):
        return title
    base = (getattr(script, "thumbnail_text", "") or getattr(script, "hook_text", "") or title).strip(" ?!.")
    return base + "?"


def _wrap(draw, text: str, font, width: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def _background(w: int, h: int, pal, seed: int) -> Image.Image:
    c0, c1, _ = pal
    yy, xx = np.mgrid[0:h, 0:w]
    t = np.clip((xx / w * 0.6 + yy / h * 0.4), 0, 1)[..., None]
    arr = np.array(c0)[None, None] * (1 - t) + np.array(c1)[None, None] * t
    im = Image.fromarray(arr.astype("uint8")).convert("RGBA")
    rnd = random.Random(seed)
    d = ImageDraw.Draw(im)
    for _ in range(90):                                   # soft stars
        x, y, r = rnd.randrange(w), rnd.randrange(h), rnd.choice((1, 1, 2, 3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randrange(60, 180)))
    return im


def _glow(im: Image.Image, cx: float, cy: float, r: float, color, alpha: int = 140):
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45)))


def _subject(im: Image.Image, kind: str | None, cx: float, cy: float, r: float, accent):
    if not kind:
        return
    d = ImageDraw.Draw(im)
    _glow(im, cx, cy, r * 1.5, accent, 90)
    if kind == "moon":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(226, 228, 236, 255))
        for dx, dy, rr in ((-.3, -.25, .22), (.28, .1, .16), (-.1, .4, .12), (.35, -.4, .09)):
            d.ellipse((cx + dx * r - rr * r, cy + dy * r - rr * r, cx + dx * r + rr * r, cy + dy * r + rr * r), fill=(176, 180, 196, 255))
    elif kind == "earth":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 120, 220, 255))
        for dx, dy, rx, ry in ((-.3, -.2, .3, .22), (.3, .25, .28, .2), (.1, -.55, .2, .1)):
            d.ellipse((cx + (dx - rx) * r, cy + (dy - ry) * r, cx + (dx + rx) * r, cy + (dy + ry) * r), fill=(70, 190, 100, 255))
    elif kind == "sun":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 196, 40, 255))
    elif kind == "hole":
        d.ellipse((cx - r * 1.45, cy - r * .42, cx + r * 1.45, cy + r * .42), outline=(255, 150, 40, 255), width=int(r * .16))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0, 255))
        d.arc((cx - r * 1.45, cy - r * .42, cx + r * 1.45, cy + r * .42), 200, 340, fill=(255, 210, 120, 255), width=int(r * .16))


def _face(height: int) -> Image.Image:
    from generated_animations.avatar import face
    f = face.get()
    im = Image.fromarray(f.frame(0.8, 0.0))          # mouth open in surprise
    im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    a = im.split()[3]
    pad = 14
    big = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    big.paste(a, (pad, pad))
    outline = big.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow.putalpha(big.filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .55)))
    out.alpha_composite(shadow, (10, 12))
    white = Image.new("RGBA", big.size, (255, 255, 255, 255))
    white.putalpha(outline)
    out.alpha_composite(white)
    out.alpha_composite(im, (pad, pad))
    return out


def _text(im: Image.Image, lines: list[str], font, x: int, y: int, accent, line_h: int, accent_idx: int):
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        col = accent if i == accent_idx else (255, 255, 255)
        yy = y + i * line_h
        d.text((x + 6, yy + 8), line, font=font, fill=(0, 0, 0, 170), stroke_width=int(font.size * .09), stroke_fill=(0, 0, 0, 170))
        d.text((x, yy), line, font=font, fill=col + (255,), stroke_width=int(font.size * .09), stroke_fill=(0, 0, 0, 255))


def render(question: str, title: str, tag: str, out: Path, short: bool) -> Path:
    w, h = (1080, 1920) if short else (1280, 720)
    seed = sum(map(ord, title))
    pal = PALETTES[seed % len(PALETTES)]
    accent = pal[2]
    im = _background(w, h, pal, seed)
    kind = next((k for k, rx in SUBJECTS if rx.search(title) or rx.search(question)), None)
    face_im = _face(int(h * (0.52 if short else 0.95)))
    if short:
        _glow(im, w * .5, h * .72, 520, accent, 120)
        _subject(im, kind, w * .80, h * .47, 120, accent)
        im.alpha_composite(face_im, (w // 2 - face_im.width // 2, h - face_im.height + 30))
        font = _font(150)
        lines = _wrap(ImageDraw.Draw(im), question.upper(), font, w - 120)
        while len(lines) > 4 and font.size > 90:
            font = _font(font.size - 12)
            lines = _wrap(ImageDraw.Draw(im), question.upper(), font, w - 120)
        _text(im, lines, font, 60, 150, accent, int(font.size * 1.12), len(lines) - 1)
        tx, ty = 60, 70
    else:
        _glow(im, w * .78, h * .55, 360, accent, 120)
        _subject(im, kind, w * .60, h * .17, 85, accent)
        im.alpha_composite(face_im, (w - face_im.width + 20, h - face_im.height + 40))
        font = _font(112)
        lines = _wrap(ImageDraw.Draw(im), question.upper(), font, int(w * .56))
        while len(lines) > 4 and font.size > 72:
            font = _font(font.size - 8)
            lines = _wrap(ImageDraw.Draw(im), question.upper(), font, int(w * .56))
        block = len(lines) * int(font.size * 1.12)
        _text(im, lines, font, 50, max(90, int((h - block) / 2) - 40), accent, int(font.size * 1.12), len(lines) - 1)
        tx, ty = 50, 36
    if tag:
        tf = _font(40 if not short else 54)
        d = ImageDraw.Draw(im)
        tw = d.textlength(tag.upper(), font=tf)
        d.rounded_rectangle((tx, ty, tx + tw + 40, ty + tf.size + 26), 16, fill=accent + (255,))
        d.text((tx + 20, ty + 11), tag.upper(), font=tf, fill=(20, 20, 40, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out, quality=92)
    return out


def for_script(script, niche: str, lang: str, out_jpg: Path, short: bool) -> Path | None:
    tag = {"Space & Universe": "Space", "How Tech Works": "Tech", "AI Explained": "AI", "Science Explained": "Science"}.get(niche, niche.split(" ")[0] if niche else "")
    return render(question_for(script), script.title, tag if lang == "en" else "", Path(out_jpg), short)
