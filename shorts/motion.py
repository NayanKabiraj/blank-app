"""Motion-graphics visuals rendered with Manim Community (MIT, https://www.manim.community).

Draws the whole vertical video track in code, no stock footage: a dark animated dot-field
backdrop, white line graphics with purple glowing highlights, count-up numbers, flow
steps and comparisons, a niche label at the top and a progress bar at the bottom.
What each scene shows comes from the plan's `graphic` field (see shorts/plan.py), so
no per-video animation code is needed. Captions and audio are added later by compose.py.
"""
from __future__ import annotations

import logging
import math
import re
import shutil
import subprocess
from pathlib import Path

from . import config
from .plan import Graphic, LangScript

log = logging.getLogger(__name__)

BG = "#0b0c11"
WHITE = "#f4f4f7"
GREY = "#9aa0ad"
PURPLE = "#8b5cf6"
PURPLE_SOFT = "#c4b5fd"
FONTS = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}

# Manim frame: 9 x 16 units -> 1 unit = 120 px at 1080x1920.
FRAME_W, FRAME_H = 9.0, 16.0
CONTENT_TOP, CONTENT_BOTTOM = 5.2, -1.9   # keep clear of the hook (top) and captions (bottom)
INTRO, OUTRO = 0.7, 0.4


def _wrap(text: str, max_chars: int) -> str:
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def _is_devanagari(s: str) -> bool:
    return any("ऀ" <= c <= "ॿ" for c in s)


def _fallback_graphic(text: str) -> Graphic:
    words = text.replace("।", " ").replace(".", " ").split()
    return Graphic(kind="keyword", headline=" ".join(words[:3]), caption=" ".join(words[3:9]))


def _parse_number(s: str):
    """'71 km/s' -> ('', 71.0, ' km/s', 0, False); returns None if there's no number."""
    m = re.match(r"^(\D*?)(-?\d[\d,]*(?:\.\d+)?)(.*)$", s.strip())
    if not m:
        return None
    raw = m.group(2)
    decimals = len(raw.split(".")[1]) if "." in raw else 0
    return m.group(1), float(raw.replace(",", "")), m.group(3), decimals, "," in raw


def _fmt(v: float, decimals: int, commas: bool) -> str:
    return f"{v:,.{decimals}f}" if commas else f"{v:.{decimals}f}"


def render(script: LangScript, lang: str, niche: str, timeline, total: float, work: Path) -> Path:
    """Render the silent video track (1080x1920, 30 fps) and return its path."""
    from manim import (DOWN, RIGHT, UP, Circle, Create, DashedVMobject,
                       Dot, FadeIn, FadeOut, LaggedStart, Line, Rectangle, RoundedRectangle,
                       Scene, Text, ValueTracker, VGroup, Write, always_redraw, linear,
                       smooth, tempconfig)

    font = FONTS[lang]
    script_scenes = script.scenes

    # Same segmentation as the footage path: scene i shows until scene i+1 starts.
    segments = []
    for i, (start, _end, text) in enumerate(timeline):
        seg_start = 0.0 if i == 0 else start
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        g = script_scenes[i].graphic or _fallback_graphic(text)
        segments.append((seg_start, seg_end, g))

    def T(s: str, size: float = 1.0, color: str = WHITE, bold: bool = True):
        """Text with every line centred (Pango left-aligns multi-line text)."""
        lines = [Text(line, font=font, weight="BOLD" if bold else "NORMAL", color=color).scale(size)
                 for line in s.split("\n") if line.strip()]
        if len(lines) == 1:
            return lines[0]
        return VGroup(*lines).arrange(DOWN, buff=0.18 * size)

    def fit(m, max_w: float, max_h: float):
        if m.width > max_w:
            m.scale_to_fit_width(max_w)
        if m.height > max_h:
            m.scale_to_fit_height(max_h)
        return m

    def glow(m, color=PURPLE):
        layers = VGroup()
        for w, o in ((34, 0.05), (22, 0.08), (12, 0.14), (5, 0.25)):
            c = m.copy()
            c.set_fill(opacity=0).set_stroke(color, width=w, opacity=o)
            layers.add(c)
        return layers

    chars = 13 if lang == "en" else 16  # Devanagari strings count matras as characters

    class Short(Scene):
        def construct(self):
            clock = {"t": 0.0}

            # --- animated dot field (the backdrop never stops moving)
            dots = VGroup()
            for gx in range(13):
                for gy in range(23):
                    x, y = -4.5 + gx * 0.75, -8.25 + gy * 0.75
                    d = Dot([x, y, 0], radius=0.028, color="#cfe0ff")
                    d.base = (x, y)
                    dots.add(d)

            def wave(m, dt):
                clock["t"] += dt
                t = clock["t"]
                for d in m:
                    x, y = d.base
                    k = math.sin(t * 1.1 + x * 0.55 + y * 0.35)
                    d.move_to([x, y + 0.08 * k, 0])
                    d.set_opacity(0.10 + 0.22 * (0.5 + 0.5 * k))
            dots.add_updater(wave)
            self.add(dots)

            # --- niche label (top) and progress bar (bottom)
            pill_txt = T(niche.upper(), 0.5, PURPLE_SOFT)
            pill = RoundedRectangle(corner_radius=0.36, width=pill_txt.width + 0.9, height=0.8,
                                    stroke_color=PURPLE, stroke_width=3, fill_color=BG, fill_opacity=0.8)
            hud = VGroup(pill, pill_txt.move_to(pill)).move_to([0, 6.95, 0])
            track = Line([-4.5, -7.82, 0], [4.5, -7.82, 0], stroke_color="#2a2b33", stroke_width=10)
            bar = always_redraw(lambda: Line(
                [-4.5, -7.82, 0], [-4.5 + 9.0 * min(1.0, clock["t"] / total) + 1e-3, -7.82, 0],
                stroke_color=PURPLE, stroke_width=10))
            self.add(track, bar, hud)

            for i, (seg_start, seg_end, g) in enumerate(segments):
                group, intro, hold = self.build(g, i)
                self.play(*intro, run_time=INTRO)
                remaining = seg_end - self.renderer.time - OUTRO
                hold(max(0.2, remaining))
                self.play(FadeOut(group, shift=UP * 0.25), run_time=OUTRO)

        # Each builder returns (group, intro animations, hold(seconds) callable)
        def build(self, g: Graphic, i: int):
            kind = g.kind
            if kind == "stat" and _parse_number(g.headline):
                return self.stat(g)
            if kind == "steps" and len(g.items) >= 2:
                return self.steps(g)
            if kind == "compare" and len(g.items) == 2:
                return self.compare(g)
            if kind == "title":
                return self.title(g)
            return self.keyword(g)

        def slow_push(self, group):
            def hold(sec):
                self.play(group.animate.scale(1.04), run_time=sec, rate_func=linear)
            return hold

        def title(self, g):
            head = fit(T(_wrap(g.headline, chars), 1.9), 8.2, 5.0)
            parts = [head]
            if g.caption:
                cap = fit(T(_wrap(g.caption, 22), 0.8, GREY, bold=False), 8.0, 2.0)
                cap.next_to(head, DOWN, buff=0.5)
                parts.append(cap)
            body = VGroup(*parts).move_to([0, 1.7, 0])
            halo = glow(head)
            group = VGroup(halo, body)
            intro = [Write(head), FadeIn(halo)] + ([FadeIn(parts[1], shift=UP * 0.2)] if g.caption else [])
            return group, intro, self.slow_push(group)

        def keyword(self, g):
            head = fit(T(_wrap(g.headline, chars), 1.6), 7.4, 3.8)
            box = RoundedRectangle(corner_radius=0.35, width=head.width + 1.1, height=head.height + 0.9,
                                   stroke_color=PURPLE, stroke_width=5, fill_color=PURPLE, fill_opacity=0.12)
            head.move_to(box)
            card = VGroup(box, head)
            halo = glow(box)
            parts = [VGroup(halo, card)]
            if g.caption:
                cap = fit(T(_wrap(g.caption, 22), 0.8, GREY, bold=False), 8.0, 2.2)
                cap.next_to(card, DOWN, buff=0.55)
                parts.append(cap)
            group = VGroup(*parts).move_to([0, 1.8, 0])
            intro = [Create(box), FadeIn(halo), Write(head)]
            if g.caption:
                intro.append(FadeIn(parts[1], shift=UP * 0.2))
            return group, intro, self.slow_push(group)

        def stat(self, g):
            prefix, value, suffix, decimals, commas = _parse_number(g.headline)
            tracker = ValueTracker(0)

            def number():
                n = T(prefix + _fmt(tracker.get_value(), decimals, commas), 3.4, PURPLE_SOFT)
                u = T(suffix.strip(), 1.2, WHITE) if suffix.strip() else None
                grp = VGroup(n, u).arrange(DOWN, buff=0.3) if u else VGroup(n)
                return fit(grp, 5.6, 4.2).move_to([0, 2.9, 0])
            num = always_redraw(number)
            ring = Circle(radius=3.25, stroke_color=PURPLE, stroke_width=7).move_to([0, 2.9, 0])
            dash = DashedVMobject(Circle(radius=3.65, stroke_color=PURPLE_SOFT, stroke_width=3),
                                  num_dashes=40).move_to([0, 2.9, 0])
            halo = glow(ring)
            parts = [halo, ring, dash, num]
            cap = None
            if g.caption:
                cap = fit(T(_wrap(g.caption, 22), 0.8, WHITE, bold=False), 8.0, 1.6)
                cap.move_to([0, -1.25, 0])
                parts.append(cap)
            group = VGroup(*parts)
            intro = [Create(ring), FadeIn(halo), FadeIn(dash),
                     tracker.animate(rate_func=smooth).set_value(value)]
            self.add(num)
            if cap:
                intro.append(FadeIn(cap, shift=UP * 0.2))

            def hold(sec):
                self.play(dash.animate.rotate(0.6 * sec / 3), run_time=sec, rate_func=linear)
            return group, intro, hold

        def steps(self, g):
            items = g.items[:4]
            head = fit(T(_wrap(g.headline, 18), 1.1), 8.0, 2.0)
            boxes, arrows = VGroup(), VGroup()
            for it in items:
                label = fit(T(it, 0.85), 7.0, 0.9)
                box = RoundedRectangle(corner_radius=0.3, width=8.0, height=1.35,
                                       stroke_color=WHITE, stroke_width=3, fill_color=BG, fill_opacity=0.85)
                boxes.add(VGroup(box, label.move_to(box)))
            boxes.arrange(DOWN, buff=0.55)
            for a, b in zip(boxes[:-1], boxes[1:]):
                arrows.add(Line(a.get_bottom(), b.get_top(), stroke_color=GREY, stroke_width=4)
                           .add_tip(tip_length=0.18))
            flow = VGroup(boxes, arrows)
            fit(flow, 8.0, CONTENT_TOP - CONTENT_BOTTOM - head.height - 0.6)
            group = VGroup(head, flow).arrange(DOWN, buff=0.5).move_to([0, 1.65, 0])
            intro = [FadeIn(head, shift=DOWN * 0.2),
                     LaggedStart(*[Create(b[0]) for b in boxes], lag_ratio=0.25),
                     LaggedStart(*[FadeIn(b[1]) for b in boxes], lag_ratio=0.25),
                     LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.3)]

            def hold(sec):
                per = sec / len(boxes)
                for k, b in enumerate(boxes):
                    lit = [b[0].animate.set_stroke(PURPLE, width=6).set_fill(PURPLE, opacity=0.22)]
                    if k:
                        lit.append(boxes[k - 1][0].animate.set_stroke(GREY, width=3).set_fill(BG, opacity=0.85))
                    self.play(*lit, run_time=min(0.4, per * 0.5))
                    self.wait(max(0.0, per - min(0.4, per * 0.5)))
            return group, intro, hold

        def compare(self, g):
            head = fit(T(_wrap(g.headline, 18), 1.1), 8.0, 2.0)
            vals = g.values[:2] if len(g.values) == 2 and max(g.values) > 0 else None
            cols = VGroup()
            for k, label in enumerate(g.items[:2]):
                color = PURPLE if k == 0 else WHITE
                if vals:
                    h = 0.25 + 4.0 * (vals[k] / max(vals))
                    shape = Rectangle(width=2.8, height=h, stroke_color=color, stroke_width=4,
                                      fill_color=color, fill_opacity=0.25 if k == 0 else 0.08)
                    val = T(_fmt(vals[k], 0 if vals[k] >= 10 else 1, vals[k] >= 10000), 0.85, color)
                    val.next_to(shape, UP, buff=0.2)
                    shape = VGroup(shape, val)
                else:
                    shape = Circle(radius=1.6, stroke_color=color, stroke_width=5,
                                   fill_color=color, fill_opacity=0.15 if k == 0 else 0.05)
                lab = fit(T(_wrap(label, 10), 0.8, WHITE), 3.8, 1.6)
                cols.add(VGroup(shape, lab).arrange(DOWN, buff=0.35))
            cols.arrange(RIGHT, buff=1.2, aligned_edge=DOWN)
            vs = T("vs" if lang == "en" else "बनाम", 0.9, GREY).move_to(cols)
            group = VGroup(head, VGroup(cols, vs)).arrange(DOWN, buff=0.7).move_to([0, 1.7, 0])
            intro = [FadeIn(head, shift=DOWN * 0.2),
                     LaggedStart(*[FadeIn(c, shift=UP * 0.4) for c in cols], lag_ratio=0.35),
                     FadeIn(vs)]
            return group, intro, self.slow_push(group)

    media = work / "manim"
    if media.exists():
        shutil.rmtree(media)
    with tempconfig({
        "pixel_width": config.WIDTH, "pixel_height": config.HEIGHT, "frame_rate": config.FPS,
        "frame_width": FRAME_W, "frame_height": FRAME_H, "background_color": BG,
        "media_dir": str(media), "output_file": "motion", "disable_caching": True,
        "verbosity": "WARNING", "progress_bar": "none",
    }):
        Short().render()
    rendered = next(media.rglob("motion.mp4"))
    # Pad or trim to the exact length the audio expects
    out = work / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(rendered), "-vf",
                    "tpad=stop_mode=clone:stop_duration=3,format=yuv420p", "-t", f"{total:.3f}",
                    "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)], check=True)
    log.info("Rendered motion graphics with Manim (%s)", lang)
    return out
