"""The 13 graphic kinds of a video plan (title, keyword, stat, steps, flow, build, cycle, race, compare, bars, chat,
quiz, myth) drawn with the animation library, plus the closing outro scene. `render(ctx, scene)` is the single entry
point; everything is time-driven (see timed.py)."""
from __future__ import annotations

import math
import re

import numpy as np
from manim import (Arc, Arrow, Circle, Dot, Line, ManimColor, Rectangle, RoundedRectangle, Text, VGroup, always_redraw,
                   interpolate_color)

from .avatar import expressions, gestures
from .shared import icons, particles, typography
from .timed import level, show, slots

ACC = ["#2EC5FF", "#F4C95D", "#FF8FA3", "#4CD97B", "#9B6BFF"]
DIM, EDGE, INK, MUTED = "#16213E", "#3C4F7A", "#F5F7FA", "#9AA8C7"
GREEN, RED = "#4CD97B", "#FF4D6D"
EXPRESSION = {"title": "curious", "keyword": "happy", "stat": "surprised", "steps": "curious", "flow": "curious",
              "build": "curious", "cycle": "thinking", "race": "excited", "compare": "thinking", "bars": "surprised",
              "chat": "happy", "quiz": "thinking", "myth": "thinking"}


def _lay(ctx):
    L = ctx.layout
    return L, np.array([L.stage_center[0], L.stage_center[1], 0.0]), L.stage_w, L.stage_h


def _txt(ctx, s, size=32, color=INK, width=None, weight="BOLD"):
    size = size * (1.3 if ctx.layout.landscape else 1.0)      # a wide frame is read from further away
    return typography.text(str(s), size, color, weight, width or ctx.layout.stage_w * 0.9, ctx.lang)


def _box(ctx, label, w, h, fill=DIM, edge=EDGE, size=30):
    r = RoundedRectangle(corner_radius=min(0.3, h / 3), width=w, height=h, stroke_color=edge, stroke_width=3,
                         fill_color=fill, fill_opacity=1)
    t = _txt(ctx, label, size, INK, w - 0.4)
    if t.height > h - 0.2:
        t.scale_to_fit_height(h - 0.2)
    t.move_to(r)
    return VGroup(r, t)


def _positions(ctx, n):
    """Centres and box size for n items: a column on a phone, a row on a wide screen."""
    L, C, W, H = _lay(ctx)
    if L.landscape and n <= 4:
        bw, bh = min(W / n - 0.35, 3.4), 1.5
        xs = [C[0] + (k - (n - 1) / 2) * (bw + 0.35) for k in range(n)]
        return [np.array([x, C[1], 0.0]) for x in xs], bw, bh
    bh = min(1.25, H * 0.88 / (n * 1.25))
    bw = W * 0.92
    gap = bh * 0.28
    top = C[1] + (n * bh + (n - 1) * gap) / 2 - bh / 2
    return [np.array([C[0], top - k * (bh + gap), 0.0]) for k in range(n)], bw, bh


def _point_at_active(ctx, times, centres):
    def fn():
        t = ctx.elapsed()
        idx = max([k for k, tt in enumerate(times) if tt <= t] or [0])
        return centres[idx]
    return fn


# ---------------------------------------------------------------------------------- kinds
def title(ctx, g):
    L, C, W, H = _lay(ctx)
    ic = icons.icon(g.get("prop") or "star", min(W, H) * 0.5).move_to(C)
    show(ctx, ic, 0.2, pop=0.25)
    return None


def keyword(ctx, g):
    L, C, W, H = _lay(ctx)
    ic = icons.icon(g.get("prop") or "bulb", min(W, H) * 0.34).move_to(C + (0, H * 0.22, 0))
    h = _txt(ctx, g["headline"], 52, "#FFD166", W * 0.92).move_to(C + (0, -H * 0.06, 0))
    show(ctx, ic, 0.2, pop=0.25)
    show(ctx, h, 0.45)
    if g.get("caption"):
        show(ctx, _txt(ctx, g["caption"], 30, MUTED, W * 0.9, "NORMAL").move_to(C + (0, -H * 0.24, 0)), 0.8)


def stat(ctx, g):
    L, C, W, H = _lay(ctx)
    head = str(g["headline"])
    m = re.search(r"\d[\d,]*\.?\d*", head)
    t0 = slots(ctx, 2)[0]
    if m:
        raw = m.group(0)
        val = float(raw.replace(",", ""))
        dec = len(raw.split(".")[1]) if "." in raw else 0
        comma = "," in raw
        pre, post = head[:m.start()], head[m.end():]
        steps = 24
        frames = VGroup()
        for k in range(steps + 1):
            v = val * k / steps
            s = f"{v:,.{dec}f}" if comma else f"{v:.{dec}f}"
            frames.add(_txt(ctx, pre + s + post, 76, "#FFD166", W * 0.92).move_to(C))
        base = [(f, f.get_family()) for f in frames]

        def upd(_m):
            p = min(1.0, max(0.0, (ctx.elapsed() - t0) / 1.4))
            idx = int((1 - (1 - p) ** 3) * steps)
            fade = 1.0 - (min(1.0, max(0.0, (ctx.elapsed() - (ctx.duration - 0.2)) / 0.2)) if not ctx.is_last else 0.0)
            for k, f in enumerate(frames):
                on = (k == idx and ctx.elapsed() >= t0 - 0.05) * fade
                for s in f.get_family():
                    s.set_fill(opacity=on, family=False)
        upd(frames)
        frames.add_updater(upd)
        ctx.scene.add(frames)
        frames.set_z_index(3)
        ctx.objects.append(frames)
    else:
        show(ctx, _txt(ctx, head, 76, "#FFD166", W * 0.92).move_to(C), t0)
    if g.get("caption"):
        show(ctx, _txt(ctx, g["caption"], 32, MUTED, W * 0.9, "NORMAL").move_to(C + (0, -H * 0.2, 0)), t0 + 0.4)


def steps(ctx, g, connect=True, packets=False):
    items = g.get("items") or []
    pts, bw, bh = _positions(ctx, len(items))
    times = slots(ctx, len(items))
    boxes = []
    for k, (label, p) in enumerate(zip(items, pts)):
        b = _box(ctx, label, bw, bh, size=30 if not ctx.layout.landscape else 26).move_to(p)
        boxes.append(b)
        accent = ACC[k % len(ACC)]
        rect = b[0]

        def lit(_m, rect=rect, tk=times[k], accent=accent):
            f = level(ctx, tk, 0.3)
            rect.set_fill(interpolate_color(ManimColor(DIM), ManimColor(accent), f * 0.75), opacity=rect.get_fill_opacity(), family=False)
        b.add_updater(lit)
        show(ctx, b, max(0.15, times[k] - 0.5) if not packets else 0.2 + 0.25 * k)
    if connect and len(items) > 1:
        for k in range(len(items) - 1):
            a, b2 = pts[k], pts[k + 1]
            d = (b2 - a) / max(1e-6, np.linalg.norm(b2 - a))
            ext = (bh / 2 if abs(d[1]) > abs(d[0]) else bw / 2)
            arr = Arrow(a + d * (ext + 0.02), b2 - d * (ext + 0.02), buff=0, color=MUTED, stroke_width=5,
                        max_tip_length_to_length_ratio=0.5)
            show(ctx, arr, times[k + 1] - 0.4, z=2)
            if packets:
                s_fn, e_fn = (lambda p0=a + d * ext: p0), (lambda p1=b2 - d * ext: p1)
                pk = particles.signal_packets(s_fn, e_fn, ctx.timeline, ACC[k % len(ACC)], n=3, period=1.3, size=0.09)
                ctx.add(pk, z=4)
    ctx.avatar.look_at(None)
    return _point_at_active(ctx, times, pts)


def flow(ctx, g):
    return steps(ctx, g, packets=True)


def build(ctx, g):
    L, C, W, H = _lay(ctx)
    items = g.get("items") or []
    n = len(items)
    times = slots(ctx, n)
    bh = min(1.3, H * 0.85 / n)
    centres = []
    for k, label in enumerate(items):          # first item is the bottom layer
        y = C[1] - H * 0.42 + bh / 2 + k * (bh + 0.1)
        w = W * (0.95 - 0.1 * k)
        b = _box(ctx, label, w, bh, fill=ACC[k % len(ACC)] if True else DIM, edge=INK, size=30)
        b[1].set_color("#0B1020")
        b.move_to((C[0], y, 0))
        centres.append(np.array([C[0], y, 0.0]))
        show(ctx, b, times[k], pop=0.2)
    return _point_at_active(ctx, times, centres)


def cycle(ctx, g):
    L, C, W, H = _lay(ctx)
    items = g.get("items") or []
    n = len(items)
    r = min(W, H) * 0.34
    ring = Circle(radius=r, stroke_color=EDGE, stroke_width=4).move_to(C)
    show(ctx, ring, 0.1, pop=0, z=1)
    times = slots(ctx, n)
    centres = []
    for k, label in enumerate(items):
        a = math.pi / 2 - 2 * math.pi * k / n
        p = C + np.array([r * math.cos(a), r * math.sin(a), 0.0])
        b = _box(ctx, label, min(W * 0.46, 3.4), 0.95, fill=DIM, edge=ACC[k % len(ACC)], size=26).move_to(p)
        centres.append(p)
        show(ctx, b, times[k] - 0.3 if k else 0.2)
    tok = Dot(C, radius=0.16, color="#FFD166")
    tok.add_updater(lambda m: m.move_to(C + np.array([r * math.cos(math.pi / 2 - 2 * math.pi * ctx.elapsed() / 4.0),
                                                       r * math.sin(math.pi / 2 - 2 * math.pi * ctx.elapsed() / 4.0), 0.0])))
    ctx.add(tok, z=5)
    return _point_at_active(ctx, times, centres)


def race(ctx, g):
    L, C, W, H = _lay(ctx)
    items = (g.get("items") or ["A", "B"])[:2]
    vals = (g.get("values") or [2, 1])[:2]
    vmax = max(vals)
    for k, (label, v) in enumerate(zip(items, vals)):
        y = C[1] + (0.9 if k == 0 else -0.9) * (H * 0.2)
        track = RoundedRectangle(corner_radius=0.2, width=W * 0.92, height=0.5, stroke_color=EDGE, stroke_width=3, fill_color=DIM, fill_opacity=1).move_to((C[0], y, 0))
        lab = _txt(ctx, f"{label}", 30, ACC[k], W * 0.8).move_to((C[0], y + 0.75, 0))
        show(ctx, track, 0.15)
        show(ctx, lab, 0.3)
        speed = 0.6 * (v / vmax) + 0.05
        dots = VGroup(*[Dot(radius=0.13, color=ACC[k]) for _ in range(6)])

        def move(m, y=y, speed=speed):
            for j, d in enumerate(m):
                ph = ((ctx.elapsed() * speed) + j / 6.0) % 1.0
                d.move_to((C[0] - W * 0.44 + W * 0.88 * ph, y, 0))
        move(dots)
        dots.add_updater(move)
        ctx.add(dots, z=4)


def compare(ctx, g):
    L, C, W, H = _lay(ctx)
    items = (g.get("items") or ["A", "B"])[:2]
    vals = (g.get("values") or [1, 1])[:2]
    vmax = max(vals)
    rmax = min(W * 0.24, H * 0.36)
    for k, (label, v) in enumerate(zip(items, vals)):
        r = max(0.45, rmax * math.sqrt(v / vmax))
        x = C[0] + (-1 if k == 0 else 1) * W * 0.25
        d = Circle(radius=r, stroke_color=INK, stroke_width=3, fill_color=ACC[k], fill_opacity=0.85).move_to((x, C[1] + 0.3, 0))
        t = _txt(ctx, label, 28, INK, W * 0.45).move_to((x, C[1] - rmax - 0.5, 0))
        show(ctx, d, 0.3 + 0.5 * k, pop=0.35)
        show(ctx, t, 0.5 + 0.5 * k)


def bars(ctx, g):
    L, C, W, H = _lay(ctx)
    items = g.get("items") or []
    vals = g.get("values") or [1] * len(items)
    vmax = max(vals)
    n = len(items)
    bh = min(0.9, H * 0.7 / n)
    times = slots(ctx, n)
    for k, (label, v) in enumerate(zip(items, vals)):
        y = C[1] + (n - 1) * (bh + 0.7) / 2 - k * (bh + 0.7)
        full = max(0.25, W * 0.7 * v / vmax)
        lab = _txt(ctx, label, 28, INK, W * 0.9).move_to((C[0], y + bh / 2 + 0.3, 0))
        bar = Rectangle(width=full, height=bh, stroke_width=0, fill_color=ACC[k % len(ACC)], fill_opacity=1)
        left = np.array([C[0] - W * 0.4, y, 0.0])
        bar.move_to(left + (full / 2, 0, 0))
        bar0 = bar.copy()
        val = _txt(ctx, f"{v:g}", 30, INK, 2.5).move_to(left + (full + 0.55, 0, 0))
        show(ctx, lab, times[k] - 0.2 if k else 0.2)
        # grow: stretch the bar horizontally from its left edge by an updater on the scene clock
        bar.save_state()
        state = {"p": 1.0}

        def grow(m, bar0=bar0, left=left, tk=times[k], state=state, full=full):
            p = max(0.02, level(ctx, tk, 0.9))
            m.stretch_to_fit_width(full * p)
            m.move_to(left + (full * p / 2, 0, 0))
        grow(bar)
        bar.add_updater(grow)
        show(ctx, bar, times[k], pop=0)
        show(ctx, val, times[k] + 0.9)


def chat(ctx, g):
    L, C, W, H = _lay(ctx)
    items = g.get("items") or []
    n = len(items)
    times = slots(ctx, n)
    bh = min(1.15, H * 0.9 / n - 0.15)
    top = C[1] + (n * (bh + 0.15)) / 2 - bh / 2
    for k, text in enumerate(items):
        viewer = k % 2 == 0
        w = W * 0.78
        b = _box(ctx, text, w, bh, fill="#27427A" if viewer else "#1E6B4E", edge="#6D8FD6" if viewer else GREEN, size=28)
        x = C[0] + (-W * 0.11 if viewer else W * 0.11)
        b.move_to((x, top - k * (bh + 0.15), 0))
        show(ctx, b, times[k] - 0.2 if k else 0.2, pop=0.2)


def quiz(ctx, g):
    L, C, W, H = _lay(ctx)
    items = g.get("items") or []
    answer = g.get("answer") or 0
    n = len(items)
    q = _txt(ctx, g["headline"], 44, "#FFD166", W * 0.95).move_to(C + (0, H * 0.4, 0))
    show(ctx, q, 0.15)
    bh = min(1.0, H * 0.62 / n - 0.15)
    t_reveal = ctx.config.get("pad_before", 0.3) + ctx.config.get("narration_seconds", ctx.duration) * 0.72
    for k, label in enumerate(items):
        y = C[1] + H * 0.12 - k * (bh + 0.2)
        b = _box(ctx, label, W * 0.8, bh, size=30).move_to((C[0], y, 0))
        rect = b[0]

        def reveal(_m, rect=rect, k=k):
            f = level(ctx, t_reveal, 0.3)
            target = GREEN if k == answer else "#2A1620"
            rect.set_fill(interpolate_color(ManimColor(DIM), ManimColor(target), f * (0.8 if k == answer else 0.9)), opacity=rect.get_fill_opacity(), family=False)
        b.add_updater(reveal)
        show(ctx, b, 0.4 + 0.2 * k)
    ring_c = C + np.array([W * 0.38, H * 0.4, 0.0])
    ring = always_redraw(lambda: VGroup(Circle(radius=0.3, stroke_color="#FFFFFF", stroke_opacity=0.35, stroke_width=3),
                                        Arc(radius=0.3, start_angle=math.pi / 2, angle=-2 * math.pi * min(1.0, max(0.0, (ctx.elapsed() - 0.4) / max(0.5, t_reveal - 0.4))),
                                            stroke_color="#FFD166", stroke_width=6)).move_to(ring_c))
    ring._dynamic = True
    ctx.add(ring, z=4)


def myth(ctx, g):
    L, C, W, H = _lay(ctx)
    items = (g.get("items") or ["", ""])[:2]
    t_strike = ctx.config.get("pad_before", 0.3) + ctx.config.get("narration_seconds", ctx.duration) * 0.35
    if L.landscape:
        pos = [C + (-W * 0.25, 0, 0), C + (W * 0.25, 0, 0)]
        bw, bh = W * 0.46, H * 0.6
    else:
        pos = [C + (0, H * 0.22, 0), C + (0, -H * 0.22, 0)]
        bw, bh = W * 0.95, H * 0.38
    myth_b = _box(ctx, items[0], bw, bh, fill="#3A1822", edge=RED, size=34).move_to(pos[0])
    tag1 = _txt(ctx, "MYTH" if ctx.lang == "en" else "भ्रम", 28, RED, 3).next_to(myth_b, (0, 1, 0), buff=0.12)
    truth_b = _box(ctx, items[1], bw, bh, fill="#123B2C", edge=GREEN, size=34).move_to(pos[1])
    tag2 = _txt(ctx, "TRUTH" if ctx.lang == "en" else "सच", 28, GREEN, 3).next_to(truth_b, (0, 1, 0), buff=0.12)
    show(ctx, myth_b, 0.2); show(ctx, tag1, 0.2)
    strike = Line(myth_b.get_left() + (0.2, 0, 0), myth_b.get_right() - (0.2, 0, 0), color=RED, stroke_width=10)
    show(ctx, strike, t_strike, pop=0)
    show(ctx, truth_b, t_strike + 0.5, pop=0.2); show(ctx, tag2, t_strike + 0.5)


KINDS = {"title": title, "keyword": keyword, "stat": stat, "steps": steps, "flow": flow, "build": build, "cycle": cycle,
         "race": race, "compare": compare, "bars": bars, "chat": chat, "quiz": quiz, "myth": myth}
NO_TOP_HEADLINE = {"stat", "quiz", "keyword"}


def outro(ctx):
    """Closing scene: Like / Share / Subscribe buttons pop in one after another."""
    from .shared.outro_scene import COLORS, LABELS, _button
    L, C, W, H = _lay(ctx)
    h = typography.headline("Thanks for watching!" if ctx.lang == "en" else "धन्यवाद!", "#221E1C" if getattr(ctx, "look", "classic") == "vox" else "#FFD166",
                            max_width=ctx.layout.headline_w, lang=ctx.lang).move_to((0, ctx.layout.headline_y, 0))
    show(ctx, h, 0.1, pop=0, z=10)
    times = slots(ctx, 3, lead=0.5)
    if L.landscape:
        xs = [C[0] + (k - 1) * 3.9 for k in range(3)]
        pos = [np.array([x, C[1], 0.0]) for x in xs]
    else:
        pos = [np.array([C[0], C[1] + (1 - k) * 1.5, 0.0]) for k in range(3)]
    for k, (label, col) in enumerate(zip(LABELS[ctx.lang], COLORS)):
        b = _button(label, col, ctx.lang).move_to(pos[k])
        show(ctx, b, times[k], pop=0.3)
    return None


def render(ctx, scene: dict):
    """Draw one plan scene (a dict with text, keyword, graphic) and start the avatar's reaction."""
    from shorts.outro import OUTRO_TEXT
    g = scene.get("graphic") or {"kind": "keyword", "headline": " ".join(scene["text"].split()[:3])}
    kind = g["kind"] if g.get("kind") in KINDS else "keyword"
    is_outro = scene["text"] == OUTRO_TEXT[ctx.lang]
    if is_outro:
        point = outro(ctx)
        kind = "title"
    else:
        if kind not in NO_TOP_HEADLINE:
            h = typography.headline(g["headline"], "#F5F7FA", max_width=ctx.layout.headline_w, lang=ctx.lang)
            h.move_to((0, ctx.layout.headline_y, 0))
            show(ctx, h, 0.1, pop=0, z=10)
        point = KINDS[kind](ctx, g)
    caption_track(ctx, scene["text"])
    # the presenter reacts: expression, then points at whatever is being explained
    ctx.avatar.look_at(None)
    anims = [expressions.set_expression(ctx.avatar, "happy" if is_outro else EXPRESSION.get(kind, "neutral"), 0.35)]
    if is_outro:
        anims.append(gestures.wave(ctx.avatar, 0.4))
    elif callable(point):
        anims.append(gestures.point_at(ctx.avatar, point, 0.5))
    elif kind in ("compare", "bars", "stat"):
        anims.append(gestures.present(ctx.avatar, 0.5))
    else:
        anims.append(gestures.rest(ctx.avatar, 0.5))
    ctx.play(*anims, run_time=0.5)


def caption_track(ctx, text: str, t0=None, span=None, last_of_scene: bool = True, hide_at=None):
    """The narration as caption pills, one sentence at a time, timed by each sentence's share of the speech."""
    L = ctx.layout
    sents = ctx.sentences(text, t0, span)
    for k, (s, t0, t1) in enumerate(sents):
        vox = getattr(ctx, "look", "classic") == "vox"
        pill = typography.caption_pill(s, color="#221E1C" if vox else "#FFFFFF", fill="#FFFDF5" if vox else "#0B1020", opacity=0.94 if vox else 0.72,
                                       max_width=L.caption_w, chars=L.caption_chars, size=L.caption_size, lang=ctx.lang)
        pill.move_to((L.caption_x, L.caption_y, 0))
        show(ctx, pill, t0, dur=0.2, pop=0, z=11, fade_out=(k == len(sents) - 1) and last_of_scene and not ctx.is_last)
        if k + 1 < len(sents):   # hand over to the next sentence
            _expire(ctx, pill, sents[k + 1][1])
        elif hide_at is not None:   # last sentence of a scene inside a longer shot: hide when the next scene's caption starts
            _expire(ctx, pill, hide_at)


def _expire(ctx, pill, t_end):
    """Hide a caption pill when the next sentence starts (it was shown with show(); multiply a second fade in)."""
    base = [(s, s.get_fill_opacity(), s.get_stroke_opacity()) for s in pill.get_family() if hasattr(s, "get_fill_opacity")]

    def upd(_m):
        if ctx.elapsed() >= t_end:
            for s, _fo, _so in base:
                s.set_fill(opacity=0, family=False)
                s.set_stroke(opacity=0, family=False)
    pill.add_updater(upd)
