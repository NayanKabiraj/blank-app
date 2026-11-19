"""One drawer per `shorts.plan.Graphic.kind` (title/keyword/stat/steps/flow/build/cycle/race/compare/bars/
chat/quiz/myth) plus a branded outro - the same `kind` vocabulary the whiteboard explainer uses
(shorts/explainer/scene.js), so any existing plan renders here unchanged; only the picture is cinematic
instead of a marker-drawn whiteboard. Each function takes a progress fraction `p` in [0, 1] across the
scene's own on-screen time and an `accent` hex colour, and draws onto an already-backgrounded RGBA canvas
- callers (`renderer.py`) composite the glow/particle layers separately so a drawer never has to think
about the background.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import animations, effects, typography

W, H = 1080, 1920


def _rgb(hexcolor: str) -> tuple[int, int, int]:
    h = hexcolor.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgba(hexcolor: str, a: int) -> tuple[int, int, int, int]:
    return (*_rgb(hexcolor), a)


def headline_caption(canvas, headline: str, caption: str, lang: str, p: float, accent: str, w: int, h: int,
                      size: int = 92) -> None:
    animations.draw_title(canvas, headline, lang, (w // 2, int(h * 0.20)), int(w * 0.86), min(1.0, p / 0.5),
                           accent=accent, size=size)
    if caption:
        animations.draw_caption(canvas, caption, lang, w // 2, int(h * 0.30), int(w * 0.8),
                                 max(0.0, (p - 0.35) / 0.4), accent=accent)


# ---------------------------------------------------------------- simple kinds
def title(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    animations.draw_title(canvas, g.headline, lang, (w // 2, h // 2), int(w * 0.86), p, accent=accent, size=104)


def keyword(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    headline_caption(canvas, g.headline, g.caption, lang, p, accent, w, h, size=88)
    # a glowing underline sweeping in beneath the headline
    draw = ImageDraw.Draw(canvas, "RGBA")
    if p > 0.45:
        bw = w * 0.5 * effects.ease_in_out((p - 0.45) / 0.35)
        y = int(h * 0.36)
        draw.rounded_rectangle([w / 2 - bw / 2, y, w / 2 + bw / 2, y + 6], radius=3, fill=_rgba(accent, 220))


_DEVANAGARI_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")


def stat(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """A big number counts up, then the caption settles underneath."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    digits = "".join(ch for ch in g.headline if ch.isdigit())
    count_p = effects.ease_out_cubic(min(1.0, p / 0.55))
    if digits and count_p < 1.0:
        n = int(digits) if len(digits) <= 6 else int(digits[:6])
        shown = g.headline.replace(digits, str(int(n * count_p)))
    else:
        shown = g.headline
    if lang == "hi":   # Devanagari digits: the bundled Kalam fallback font has no Western digit glyphs
        shown = shown.translate(_DEVANAGARI_DIGITS)
    f, lines = typography.fit_size(draw, shown, lang, int(w * 0.8), int(h * 0.22), 190, bold=True)
    line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * 1.15
    y = h * 0.42 - line_h * len(lines) / 2
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    for ln in lines:
        lw = draw.textlength(ln, font=f)
        gdraw.text((w / 2 - lw / 2, y), ln, font=f, fill=_rgba(accent, 255))
        y += line_h
    canvas.alpha_composite(effects.glow(glow_layer, radius=18, boost=1.3))
    if g.caption:
        animations.draw_caption(canvas, g.caption, lang, w // 2, int(h * 0.56), int(w * 0.8),
                                 max(0.0, (p - 0.6) / 0.3), accent=effects.PALETTE["white"], size=42)


# ---------------------------------------------------------------- diagrams
def _node_positions(n: int, w: int, h: int, vertical: bool = True) -> list[tuple[int, int]]:
    margin_top, margin_bot = h * 0.42, h * 0.84
    if vertical:
        if n == 1:
            return [(w // 2, int((margin_top + margin_bot) / 2))]
        step = (margin_bot - margin_top) / (n - 1)
        return [(w // 2, int(margin_top + step * i)) for i in range(n)]
    margin_l, margin_r = w * 0.12, w * 0.88
    y = int((margin_top + margin_bot) / 2)
    if n == 1:
        return [(w // 2, y)]
    step = (margin_r - margin_l) / (n - 1)
    return [(int(margin_l + step * i), y) for i in range(n)]


def steps(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """2-4 stages, one lit at a time, connected by a glowing line that grows downward."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items = g.items or []
    n = max(1, len(items))
    pts = _node_positions(n, w, h, vertical=True)
    draw = ImageDraw.Draw(canvas, "RGBA")
    reveal_p = max(0.0, (p - 0.2) / 0.75)
    for i in range(n - 1):
        local = effects.ease_in_out(min(1.0, max(0.0, reveal_p * n - i)))
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        draw.line([x0, y0, x0, y0 + (y1 - y0) * local], fill=_rgba(accent, 160), width=4)
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    for i, (x, y) in enumerate(pts):
        lit = min(1.0, max(0.0, reveal_p * n - i + 0.3))
        r = 14 + 4 * lit
        col = accent if lit > 0.5 else effects.PALETTE["white"]
        a = int(255 * (0.35 + 0.65 * lit))
        gdraw.ellipse([x - r, y - r, x + r, y + r], fill=_rgba(col, a))
    canvas.alpha_composite(effects.glow(glow_layer, radius=16, boost=1.2))
    f = typography.font(lang, 38, bold=False)
    for i, (x, y) in enumerate(pts):
        lit = min(1.0, max(0.0, reveal_p * n - i))
        if lit <= 0 or i >= len(items):
            continue
        txt = items[i]
        tw = draw.textlength(txt, font=f)
        tx = min(w - tw - 24, x + 36)
        draw.text((tx, y - 18), txt, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * lit)))


def flow(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """2-4 stages left to right in a chain, with a dot flowing along the connectors."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items = g.items or []
    n = max(1, len(items))
    pts = _node_positions(n, w, h, vertical=False)
    draw = ImageDraw.Draw(canvas, "RGBA")
    for i in range(n - 1):
        draw.line([*pts[i], *pts[i + 1]], fill=_rgba(effects.PALETTE["white"], 70), width=3)
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    for x, y in pts:
        gdraw.ellipse([x - 16, y - 16, x + 16, y + 16], fill=_rgba(effects.PALETTE["white"], 220))
    travel = max(0.0, (p - 0.15) / 0.75) % 1.0
    if n > 1:
        seg = travel * (n - 1)
        i0 = min(n - 2, int(seg))
        local = seg - i0
        x0, y0 = pts[i0]
        x1, y1 = pts[i0 + 1]
        dx, dy = x0 + (x1 - x0) * local, y0 + (y1 - y0) * local
        gdraw.ellipse([dx - 11, dy - 11, dx + 11, dy + 11], fill=_rgba(accent, 255))
    canvas.alpha_composite(effects.glow(glow_layer, radius=20, boost=1.4))
    f = typography.font(lang, 30, bold=False)
    for i, (x, y) in enumerate(pts):
        if i >= len(items):
            continue
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.1) * 2 - i * 0.15)))
        if reveal <= 0:
            continue
        lines = typography.wrap(draw, items[i], f, int(w / n) - 10)
        ly = y + 28
        for ln in lines:
            tw = draw.textlength(ln, font=f)
            draw.text((x - tw / 2, ly), ln, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))
            ly += 34


def build(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """2-4 layers stacking up from the bottom, one at a time."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items = g.items or []
    n = max(1, len(items))
    draw = ImageDraw.Draw(canvas, "RGBA")
    box_h, gap = (h * 0.4) / max(3, n), 10
    base_y = h * 0.84
    bw = w * 0.74
    f = typography.font(lang, 36, bold=False)
    for i, text in enumerate(items):
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.2) * n * 1.3 - (n - 1 - i))))
        if reveal <= 0:
            continue
        y1 = base_y - i * (box_h + gap)
        y0 = y1 - box_h
        rise = (1 - reveal) * 40
        col = accent if i == n - 1 else effects.PALETTE["white"]
        draw.rounded_rectangle([w / 2 - bw / 2, y0 + rise, w / 2 + bw / 2, y1 + rise], radius=14,
                                fill=_rgba(col, int(60 + 40 * reveal)), outline=_rgba(col, int(255 * reveal)), width=2)
        tw = draw.textlength(text, font=f)
        draw.text((w / 2 - tw / 2, (y0 + y1) / 2 - 16 + rise), text, font=f,
                   fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))


def cycle(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """3-4 states around a loop with a token travelling round it."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items = g.items or []
    n = max(1, len(items))
    cx, cy, r = w / 2, h * 0.58, w * 0.32
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=_rgba(effects.PALETTE["white"], 90), width=3)
    pts = [(cx + r * math.cos(2 * math.pi * i / n - math.pi / 2), cy + r * math.sin(2 * math.pi * i / n - math.pi / 2))
           for i in range(n)]
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    for x, y in pts:
        gdraw.ellipse([x - 14, y - 14, x + 14, y + 14], fill=_rgba(effects.PALETTE["white"], 230))
    travel = max(0.0, (p - 0.1) / 0.85) * 1.4 % 1.0
    tx = cx + r * math.cos(2 * math.pi * travel - math.pi / 2)
    ty = cy + r * math.sin(2 * math.pi * travel - math.pi / 2)
    gdraw.ellipse([tx - 12, ty - 12, tx + 12, ty + 12], fill=_rgba(accent, 255))
    canvas.alpha_composite(effects.glow(glow_layer, radius=18, boost=1.3))
    f = typography.font(lang, 30, bold=False)
    for i, (x, y) in enumerate(pts):
        if i >= len(items):
            continue
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.15) * 2 - i * 0.12)))
        if reveal <= 0:
            continue
        label = items[i]
        lines = typography.wrap(draw, label, f, int(w * 0.32))
        ly = y + (26 if y > cy else -26 - 34 * len(lines))
        for ln in lines:
            tw = draw.textlength(ln, font=f)
            draw.text((x - tw / 2, ly), ln, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))
            ly += 34


def compare(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """Two discs, sized by their values - a simple, legible side-by-side comparison."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items, values = (g.items or ["A", "B"])[:2], (g.values or [1, 1])[:2]
    mx = max(values) or 1
    max_r = w * 0.26
    cy = h * 0.58
    centers = [w * 0.3, w * 0.7]
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = typography.font(lang, 34, bold=False)
    for i, (label, val) in enumerate(zip(items, values)):
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.2) * 2.2 - i * 0.2)))
        r = max_r * (val / mx) * reveal
        col = accent if i == 0 else effects.PALETTE["purple"]
        glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(glow_layer).ellipse([centers[i] - r, cy - r, centers[i] + r, cy + r], fill=_rgba(col, 190))
        canvas.alpha_composite(effects.glow(glow_layer, radius=16, boost=1.1))
        tw = draw.textlength(label, font=f)
        draw.text((centers[i] - tw / 2, cy + max_r + 24), label, font=f,
                   fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))


def bars(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    """2-4 horizontal bars growing to their values."""
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=76)
    items, values = g.items or [], g.values or []
    n = max(1, len(items))
    mx = max(values) if values else 1
    top, bot, left = h * 0.42, h * 0.8, w * 0.08
    bar_w, gap = w * 0.76, 20
    bar_h = min(70, (bot - top - gap * (n - 1)) / n)
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = typography.font(lang, 32, bold=False)
    for i in range(n):
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.2) * 2.2 - i * 0.18)))
        y0 = top + i * (bar_h + gap)
        val = values[i] if i < len(values) else 0
        frac = (val / mx) if mx else 0
        draw.rounded_rectangle([left, y0, left + bar_w, y0 + bar_h], radius=10, outline=_rgba(effects.PALETTE["white"], 60), width=2)
        draw.rounded_rectangle([left, y0, left + bar_w * frac * reveal, y0 + bar_h], radius=10, fill=_rgba(accent, 210))
        label = items[i] if i < len(items) else ""
        draw.text((left + 10, y0 - 34), label, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))


# ---------------------------------------------------------------- conversation kinds
def chat(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.2), accent, w, h, size=70)
    items = g.items or []
    n = max(1, len(items))
    top = h * 0.4
    bubble_h, gap = 90, 16
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = typography.font(lang, 32, bold=False)
    for i, text in enumerate(items):
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.15) * n * 1.3 - i)))
        if reveal <= 0:
            continue
        mine = i % 2 == 1
        bw = min(w * 0.72, draw.textlength(text, font=f) + 70)
        x0 = (w - bw - 30) if mine else 30
        y0 = top + i * (bubble_h + gap)
        slide = (1 - reveal) * (30 if mine else -30)
        col = accent if mine else effects.PALETTE["white"]
        draw.rounded_rectangle([x0 + slide, y0, x0 + bw + slide, y0 + bubble_h], radius=22,
                                fill=_rgba(col, int(45 * reveal)), outline=_rgba(col, int(220 * reveal)), width=2)
        lines = typography.wrap(draw, text, f, int(bw - 40))
        ly = y0 + bubble_h / 2 - 18 * len(lines)
        for ln in lines:
            draw.text((x0 + 20 + slide, ly), ln, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))
            ly += 36


def quiz(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.25), accent, w, h, size=70)
    items = g.items or []
    n = max(1, len(items))
    top = h * 0.42
    box_h, gap = 110, 18
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = typography.font(lang, 34, bold=False)
    reveal_answer = p > 0.72
    for i, text in enumerate(items):
        reveal = effects.ease_out_cubic(min(1.0, max(0.0, (p - 0.15) * n * 1.2 - i)))
        if reveal <= 0:
            continue
        y0 = top + i * (box_h + gap)
        is_answer = g.answer is not None and i == g.answer
        col = accent if (is_answer and reveal_answer) else effects.PALETTE["white"]
        draw.rounded_rectangle([w * 0.1, y0, w * 0.9, y0 + box_h], radius=18,
                                fill=_rgba(col, 60 if (is_answer and reveal_answer) else 20),
                                outline=_rgba(col, int(230 * reveal)), width=3 if (is_answer and reveal_answer) else 2)
        lines = typography.wrap(draw, text, f, int(w * 0.72))
        ly = y0 + box_h / 2 - 20 * len(lines)
        for ln in lines:
            tw = draw.textlength(ln, font=f)
            draw.text((w / 2 - tw / 2, ly), ln, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(255 * reveal)))
            ly += 40


def myth(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    headline_caption(canvas, g.headline, "", lang, min(1.0, p / 0.2), accent, w, h, size=70)
    items = (g.items or ["", ""])[:2]
    draw = ImageDraw.Draw(canvas, "RGBA")
    f, _ = typography.fit_size(draw, items[0] or "", lang, int(w * 0.8), 300, 38, min_size=26, bold=False)
    top = h * 0.44
    reveal0 = effects.ease_out_cubic(min(1.0, p / 0.35))
    lines0 = typography.wrap(draw, items[0], f, int(w * 0.8))
    y = top
    for ln in lines0:
        tw = draw.textlength(ln, font=f)
        draw.text((w / 2 - tw / 2, y), ln, font=f, fill=(*_rgb(effects.PALETTE["white"]), int(200 * reveal0)))
        if p > 0.4:
            strike_p = effects.ease_in_out((p - 0.4) / 0.2)
            yy = y + (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) / 2
            draw.line([w / 2 - tw / 2, yy, w / 2 - tw / 2 + tw * strike_p, yy], fill=_rgba("#FF5C5C", 230), width=4)
        y += 46
    if p > 0.55:
        reveal1 = effects.ease_out_cubic((p - 0.55) / 0.4)
        lines1 = typography.wrap(draw, items[1], f, int(w * 0.8))
        y = top + len(lines0) * 46 + 60
        for ln in lines1:
            tw = draw.textlength(ln, font=f)
            draw.text((w / 2 - tw / 2, y), ln, font=f, fill=(*_rgb(accent), int(255 * reveal1)))
            y += 46


KINDS = {
    "title": title, "keyword": keyword, "stat": stat, "steps": steps, "flow": flow, "build": build,
    "cycle": cycle, "race": compare, "compare": compare, "bars": bars, "chat": chat, "quiz": quiz, "myth": myth,
}


def draw_scene(canvas, g, lang: str, p: float, accent: str, w: int = W, h: int = H) -> None:
    fn = KINDS.get(getattr(g, "kind", None), keyword)
    fn(canvas, g, lang, p, accent, w, h)


# ---------------------------------------------------------------- outro
def outro(canvas, title_text: str, lang: str, p: float, w: int = W, h: int = H) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    reveal = effects.ease_out_cubic(min(1.0, p / 0.5))
    f = typography.font(lang, 58, bold=True)
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)
    lines = typography.wrap(draw, title_text, f, int(w * 0.78))
    line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * 1.2
    y = h * 0.42 - line_h * len(lines) / 2
    for ln in lines:
        tw = draw.textlength(ln, font=f)
        gdraw.text((w / 2 - tw / 2, y), ln, font=f, fill=_rgba(effects.PALETTE["gold"], int(255 * reveal)))
        y += line_h
    canvas.alpha_composite(effects.glow(glow_layer, radius=14, boost=1.2))
    if p > 0.3:
        sub_reveal = effects.ease_out_cubic((p - 0.3) / 0.5)
        sub = "आगे देखते रहें" if lang == "hi" else "Follow for more"
        f2 = typography.font(lang, 38, bold=False)
        tw = draw.textlength(sub, font=f2)
        draw.text((w / 2 - tw / 2, y + 30), sub, font=f2, fill=(*_rgb(effects.PALETTE["white"]), int(220 * sub_reveal)))
