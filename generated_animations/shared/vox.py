"""The "vox" look: an explainer-journalism style built from drawn paper cut-outs - a warm paper background, torn cards with a white border and a soft
shadow, marker-highlighted words, tape labels, curved doodle arrows, a little stop-motion jitter, and the presenter as a sticker.

A pack opts in with  "look": "vox"  in its shots.json. Newspaper clippings that fly in (vox.newspaper + vox.arrive) are for dated history and news-like facts. The helpers return ordinary Manim mobjects (constant part counts), so shots use them like any other:
    from generated_animations.shared import vox
    ctx.add(vox.torn_card(5.2, 3.2, seed=3), z=2)             # a torn paper card (put drawings on top of it)
    vox.marker(ctx, label, t_in=1.0, dur=0.7)                 # yellow marker swipe behind a text mobject
    vox.tape(ctx, "THE 65 METRE SEA", center, color=vox.RED)  # a tape label
Colours are the palette below; text on paper should be vox.INK. No image assets are needed (the paper texture is generated)."""
from __future__ import annotations

import math

import numpy as np
from manim import CurvedArrow, ImageMobject, Line, Polygon, Rectangle, RoundedRectangle, Text, VGroup, always_redraw

PAPER, INK, CREAM = "#EEE6D5", "#221E1C", "#FFFDF5"
YEL, BLUE, RED, GREEN, NAVY, ORANGE, PINK = "#FFD640", "#2E86D6", "#E2423C", "#5E9A5A", "#2B3A67", "#F08A3C", "#F2A5B8"
SOFT = "#8A8070"


def paper_bg(width: float, height: float, res=(540, 960), seed: int = 1) -> ImageMobject:
    """Warm paper with a faint grain and a few fibres; drawn once."""
    rng = np.random.default_rng(seed)
    h, w = res[1], res[0]
    base = np.ones((h, w, 3)) * np.array([238, 230, 213])
    from PIL import Image
    small = (rng.random((max(2, h // 70), max(2, w // 70))) * 255).astype("uint8")
    blot = np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC)).astype(float) / 255.0
    base += ((blot - 0.5) * 255 * 0.03)[..., None]
    base += rng.normal(0, 3.2, (h, w, 1))
    for _ in range(int(h * w / 2500)):
        x, y = int(rng.integers(2, w - 2)), int(rng.integers(2, h - 2))
        a = rng.random() * 6.28
        for s in range(6):
            xx, yy = int(x + math.cos(a) * s), int(y + math.sin(a) * s)
            if 0 <= xx < w and 0 <= yy < h:
                base[yy, xx] -= 12
    arr = np.dstack([np.clip(base, 0, 255), np.full((h, w), 255)]).astype(np.uint8)
    img = ImageMobject(arr)
    img.set_resampling_algorithm(2)
    img.stretch_to_fit_width(width)
    img.stretch_to_fit_height(height)
    return img


def _torn_points(w: float, h: float, seed: int, amp: float):
    rng = np.random.default_rng(seed)
    pts = []
    n = 14
    for k in range(n):
        pts.append((-w / 2 + w * k / n, h / 2 + rng.uniform(-amp, amp)))
    for k in range(n):
        pts.append((w / 2 + rng.uniform(-amp, amp), h / 2 - h * k / n))
    for k in range(n):
        pts.append((w / 2 - w * k / n, -h / 2 + rng.uniform(-amp, amp)))
    for k in range(n):
        pts.append((-w / 2 + rng.uniform(-amp, amp), -h / 2 + h * k / n))
    return [np.array([x, y, 0.0]) for x, y in pts]


def torn_card(w: float, h: float, seed: int = 0, fill: str = CREAM, amp: float = 0.045, rot: float = 0.0) -> VGroup:
    """A torn paper card: soft shadow, white torn border, a fill. Draw on top of it; scale/rotate/move the whole group."""
    pts = _torn_points(w, h, seed, amp)
    card = Polygon(*pts, stroke_color="#FFFFFF", stroke_width=9, fill_color=fill, fill_opacity=1)
    shadow = Polygon(*pts, stroke_width=0, fill_color=INK, fill_opacity=0.24).shift(np.array([0.08, -0.1, 0.0]))
    g = VGroup(shadow, card)
    if rot:
        g.rotate(math.radians(rot))
    return g


def cutout(mob, border: float = 8.0, shadow: float = 0.22) -> VGroup:
    """Turn any shape/group into a paper cut-out: white border stroke around it and a drop shadow under it."""
    sh = mob.copy().set_stroke(INK, width=0).set_fill(INK, opacity=shadow).shift(np.array([0.07, -0.09, 0.0]))
    edge = mob.copy().set_stroke("#FFFFFF", width=border, opacity=1).set_fill("#FFFFFF", opacity=1)
    return VGroup(sh, edge, mob)


def tape(ctx, label: str, center, color: str = RED, width: float = 4.2, size: int = 30, rot: float = 2.0) -> VGroup:
    t = ctx.text(label, size, "#FFFFFF", max(1.0, width - 0.4)).move_to(center)
    body = RoundedRectangle(corner_radius=0.05, width=max(width, t.width + 0.5), height=t.height + 0.42, stroke_color="#FFFFFF", stroke_width=5, fill_color=color, fill_opacity=1).move_to(center)
    sh = body.copy().set_stroke(INK, width=0).set_fill(INK, opacity=0.22).shift(np.array([0.06, -0.08, 0.0]))
    g = VGroup(sh, body, t)
    g.rotate(math.radians(rot), about_point=center)
    return g


def marker(ctx, text_mob, t_in: float, dur: float = 0.7, color: str = YEL, z: int = 2):
    """A highlighter swipe that draws left to right behind `text_mob` (already added at a higher z). Returns the swipe mobject."""
    from ..timed import level, window
    x0, x1 = text_mob.get_left()[0] - 0.12, text_mob.get_right()[0] + 0.12
    y0, y1 = text_mob.get_bottom()[1] - 0.08, text_mob.get_top()[1] + 0.1

    def make():
        f = level(ctx, t_in, dur)
        xe = x0 + (x1 - x0) * f
        return Polygon(np.array([x0, y0 + 0.05, 0.0]), np.array([xe, y0 - 0.02, 0.0]), np.array([xe + 0.04, y1 + 0.03, 0.0]), np.array([x0 - 0.04, y1 - 0.05, 0.0]),
                       stroke_width=0, fill_color=color, fill_opacity=0.92 * (1.0 if f > 0.001 else 0.0) * window(ctx, 0.0, None)())
    m = always_redraw(make)
    m._dynamic = True
    ctx.add(m, z=z)
    return m


def doodle_arrow(start, end, color: str = RED, angle: float = 0.7, width: float = 7.0):
    a = CurvedArrow(np.asarray(start, float), np.asarray(end, float), angle=angle, color=color, stroke_width=width)
    a.tip.set_fill(color, opacity=1)
    return a


def boil(mob, fps: float = 10.0, rot: float = 0.35, shift: float = 0.02, seed: int = 0):
    """Stop-motion 'boil': the mobject re-jitters a hair ten times a second (relative moves, so it composes with other animation)."""
    rng = np.random.default_rng(seed)
    st = {"i": -1, "a": 0.0, "dx": 0.0, "dy": 0.0}

    def upd(m):
        scene_t = getattr(upd, "clock", None)
        t = scene_t() if scene_t else 0.0
        i = int(t * fps)
        if i != st["i"]:
            st["i"] = i
            na, ndx, ndy = math.radians(rng.uniform(-rot, rot)), rng.uniform(-shift, shift), rng.uniform(-shift, shift)
            m.rotate(na - st["a"], about_point=m.get_center())
            m.shift(np.array([ndx - st["dx"], ndy - st["dy"], 0.0]))
            st.update(a=na, dx=ndx, dy=ndy)
    return upd, st


# ------------------------------------------------------------------------------ newspaper
SERIF = "DejaVu Serif"
NEWSPRINT = "#F3EDDC"


def _serif(text: str, size: float, color: str = INK, weight: str = "BOLD", max_width: float = 4.0):
    t = Text(text, font_size=size, color=color, weight=weight, font=SERIF)
    if t.width > max_width:
        t.scale_to_fit_width(max_width)
    return t


def newspaper(ctx, masthead: str, headline: str, date: str = "", w: float = 4.6, h: float = 3.6, seed: int = 0, rot: float = -3.0, photo: bool = True) -> VGroup:
    """A newspaper front-page clipping (newsprint card, masthead, rules, date line, big serif headline, grey text columns, a hatched photo box). Centered on the origin: move_to it, then arrive() it.
    Use it for dated history, announcements, discoveries, records, studies or anything that reads like a news item (see AUTHORING.md: when to use it)."""
    import textwrap
    g = VGroup(torn_card(w, h, seed=seed, fill=NEWSPRINT, amp=0.05))
    top = h / 2 - 0.45
    g.add(_serif(masthead.upper(), 26, INK, "BOLD", w - 0.8).move_to(np.array([0, top, 0.0])))
    for dy, sw in ((top - 0.34, 4), (top - 0.42, 2)):
        g.add(Line(np.array([-w / 2 + 0.3, dy, 0.0]), np.array([w / 2 - 0.3, dy, 0.0]), color=INK, stroke_width=sw))
    if date:
        g.add(_serif(date, 14, SOFT, "NORMAL", w - 0.8).move_to(np.array([0, top - 0.68, 0.0])))
    hl = _serif("\n".join(textwrap.wrap(headline.upper(), 18)), 30, INK, "BOLD", w - 0.8).move_to(np.array([0, top - 1.35, 0.0]))
    g.add(hl)
    y0 = hl.get_bottom()[1] - 0.25
    colw = (w - 0.9) / 2
    if photo:                                                   # a hatched photo box on the left, text bars on the right
        ph = Rectangle(width=colw, height=min(1.0, max(0.5, y0 - (-h / 2 + 0.35))), stroke_color=INK, stroke_width=3, fill_color="#CFC8B6", fill_opacity=1).move_to(np.array([-w / 2 + 0.3 + colw / 2, y0 - 0.5, 0.0]))
        g.add(ph)
        for k in range(1, 6):
            g.add(Line(ph.get_left() + np.array([0.0, -ph.height / 2 + k * ph.height / 6, 0.0]), ph.get_right() + np.array([0.0, -ph.height / 2 + k * ph.height / 6, 0.0]), color="#B7AE9C", stroke_width=2))
    for k in range(4):
        g.add(Line(np.array([w / 2 - 0.3 - colw, y0 - 0.12 - 0.26 * k, 0.0]), np.array([w / 2 - 0.3 - (0.0 if k % 2 == 0 else 0.35), y0 - 0.12 - 0.26 * k, 0.0]), color=SOFT, stroke_width=3))
    g.rotate(math.radians(rot))
    return g


def arrive(ctx, mob, t_in: float, t_out=None, dur: float = 0.6, side: str = "right", spin: float = 16.0, z: int = 6):
    """The mobject slides/spins in from off-screen at t_in (overshooting a little, like a page slapped down) and slides out at t_out. Position the mobject where it should END UP first."""
    from ..timed import level
    final = mob.get_center().copy()
    off = {"right": np.array([11.0, 0.0, 0.0]), "left": np.array([-11.0, 0.0, 0.0]), "top": np.array([0.0, 14.0, 0.0]), "bottom": np.array([0.0, -14.0, 0.0])}[side]
    st = {"a": 0.0}

    def back(x: float) -> float:                               # ease-out with a small overshoot
        x = max(0.0, min(1.0, x))
        c1 = 1.4
        return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2

    def upd(m):
        fin = back(level(ctx, t_in, dur))
        fout = 0.0 if t_out is None else max(0.0, min(1.0, level(ctx, t_out, 0.45)))
        pos = final + off * (1 - fin) - off * 1.3 * fout
        want = spin * (1 - fin) - spin * 0.4 * fout
        m.rotate(math.radians(want - st["a"]), about_point=m.get_center())
        st["a"] = want
        m.shift(pos - m.get_center())
    upd(mob)
    mob.add_updater(upd)
    ctx.add(mob, z=z)
    return mob
