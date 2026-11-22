"""Typography animation: headlines, captions and kinetic word reveals."""
from __future__ import annotations

from manim import DOWN, FadeIn, LaggedStart, RoundedRectangle, Text, UP, VGroup, Write

from .motion import ease_out_back

FONTS = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}


def text(content: str, size: int = 40, color: str = "#FFFFFF", weight: str = "BOLD", max_width: float = 8.0,
         lang: str = "en") -> Text:
    t = Text(content, font_size=size, color=color, weight=weight, font=FONTS.get(lang, FONTS["en"]))
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def headline(content: str, color: str = "#F5F7FA", size: int = 52, max_width: float = 7.4, lang: str = "en") -> Text:
    return text(content, size, color, "BOLD", max_width, lang)


def caption_pill(content: str, color: str = "#FFFFFF", fill: str = "#0B1020", max_width: float = 8.0,
                 chars: int = 34, size: int = 32, lang: str = "en") -> VGroup:
    """Caption on a rounded translucent pill - stays legible over any background."""
    import textwrap
    t = text("\n".join(textwrap.wrap(content, chars)), size, color, "SEMIBOLD", max_width - 0.6, lang)
    pill = RoundedRectangle(corner_radius=0.3, width=t.width + 0.6, height=t.height + 0.4, stroke_width=0,
                            fill_color=fill, fill_opacity=0.72)
    pill.move_to(t)
    return VGroup(pill, t)


def kinetic_words(content: str, size: int = 44, color: str = "#FFFFFF", accent: str = "#FFD166",
                  accent_words: tuple = (), max_width: float = 8.0) -> VGroup:
    """Words laid out in wrapped lines; returns a VGroup of word Texts (animate with `pop_words`)."""
    words = content.split()
    group = VGroup(*[Text(w, font_size=size, weight="BOLD",
                          color=accent if w.strip(".,!?").lower() in accent_words else color) for w in words])
    lines, row, width = [], [], 0.0
    for w in group:
        if row and width + w.width + 0.25 > max_width:
            lines.append(row)
            row, width = [], 0.0
        row.append(w)
        width += w.width + 0.25
    lines.append(row)
    rows = VGroup(*[VGroup(*r).arrange(buff=0.25) for r in lines]).arrange(DOWN, buff=0.3)
    return rows


def pop_words(rows: VGroup, lag: float = 0.12):
    words = [w for r in rows for w in r]
    return LaggedStart(*[FadeIn(w, shift=UP * 0.3, scale=0.8, rate_func=ease_out_back) for w in words],
                       lag_ratio=lag)


def write_text(t: Text, run_time: float = 0.8):
    return Write(t, run_time=run_time)
