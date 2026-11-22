"""Writes SRT and ASS subtitle files from a cue list. ASS carries the mobile-safe styling
(font, size, margin, Devanagari font for Hindi) that burned-in subtitles need; SRT is the
plain, player-agnostic sidecar file (spec section 14: "optional separate subtitle files").
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from .subtitle_generator import SubtitleCue

ASS_FONT = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}


def _ts_srt(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    ms = int((s - int(s)) * 1000)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"


def write_srt(cues: List[SubtitleCue], out: Path) -> Path:
    lines = []
    for i, c in enumerate(cues, 1):
        lines.append(f"{i}\n{_ts_srt(c.start)} --> {_ts_srt(c.end)}\n{c.text}\n")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _ts_ass(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    cs = int((s - int(s)) * 100)
    return f"{int(h):d}:{int(m):02d}:{int(s):02d}.{cs:02d}"


def write_ass(cues: List[SubtitleCue], out: Path, lang: str, resolution: tuple[int, int] = (1080, 1920)) -> Path:
    w, h = resolution
    font = ASS_FONT.get(lang, "Noto Sans")
    margin_v = int(h * 0.09)   # mobile-safe: well clear of the bottom edge
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Bold, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{int(h * 0.036)},&H00FFFFFF,&H00202020,1,2,0,1,2,120,120,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for c in cues:
        lines.append(f"Dialogue: 0,{_ts_ass(c.start)},{_ts_ass(c.end)},Default,,0,0,0,,{c.text}\n")
    out.write_text("".join(lines), encoding="utf-8")
    return out
