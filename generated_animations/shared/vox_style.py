"""Vox style v2: measured numbers for the paper cut-out look (easings, durations, borders, shadows, colours).

Numbers come from the public style guide of github.com/ilomon10/vox-style-animation (docs CC BY 4.0, (c) ilomon10 and contributors; measured
from reference videos, no footage copied) and from the MIT-licensed vox skills CK42BB/vox-explainer-skill and Alisa0808/vox-director (rules only, none of
their code or paid-API pipeline is used). Attribution is in generated_animations/VOX_STYLE_V2.md.

    from generated_animations.shared import vox_style as vs
    x = vs.enter(progress)               # 0..1 progress -> eased 0..1 (fast start, long settle; the default entrance)
    vs.rim(card)                         # hard yellow offset echo behind a card
    vs.drift(t, dur, amount=0.04)        # slow 2D push-in factor for a shot (1.0 -> 1.04)
"""
from __future__ import annotations

import math

import numpy as np
from manim import VGroup

# --- palette (voxExplainer measured): neutrals 85-95% of the frame, ONE accent 2-8%; ink is never black, paper never white
PAPER, PAPER_HI, INK, STICKY, HIGHLIGHT = "#D6D3D3", "#E6E5E6", "#514F53", "#F3DA44", "#FFF80F"
DESK_PAPER, DESK, TAPE, INK_BROWN = "#F9EFE6", "#EFE3DA", "#F9EC00", "#482F1D"
DATA_BAD, DATA_GOOD = "#C03D40", "#4AB541"                   # red = on/bad, green = off/good

# --- materials (fractions of the frame width / px at 1080p)
PRINT_BORDER = 0.05                                          # a photo print's white border is ~5% of its width
STICKER_EDGE_PX = (4, 6)                                     # cut-out sticker outline
SHADOW_CONTACT = (3, 4, 6, 0.45)                             # dx, dy, blur px, alpha (a print lying on paper)
SHADOW_LIFTED = (4, 10, 14, 0.55)                            # a print lifted off the paper
RIM_OFFSET_PX = (9, 12)                                      # hard yellow offset rim behind a card
TAPE_W_FRAC = 0.42                                           # tape width as a share of the photo width
CORNER_RADIUS_PX = (8, 9)                                    # prints; video panels 24-38

# --- durations (seconds)
DUR = dict(title_rise=0.50, prop_enter=0.58, prop_enter_big=0.83, cutout_slide=1.17, tape_unfurl=0.42, sticky_peel=0.33, exit=0.42, box_wipe=0.90,
           highlighter=0.50, draw_on=0.33, caption_fade=0.33, bar_grow=0.60, push=1.33, settle=1.5)
BEAT = 1.0                                                   # a visual beat ~1 s; a shot 3-6 s (voxExplainer median 2.8 s); never > ~7 s
DRAWING_RATE = 12                                            # drawings/s: hold each drawing 2 frames at 24 fps ("on twos") for the hand-made feel
BOIL_PX = 1.1                                                # paper-desk hold boil jitter

# --- easings (cubic-bezier); 90% of the travel in the first third of the duration; no bounce, no elastic
EASE = dict(enter=(0.16, 1, 0.3, 1), enter_big=(0.22, 1, 0.36, 1), exit=(0.32, 0, 0.67, 0), gravity=(0.5, 0, 0.75, 0), push=(0.5, 0, 0, 1),
            settle=(0, 0.8, 0.15, 1), whip=(0.45, 0, 0.4, 0.95), highlighter=(0.3, 0, 0.5, 1), pop=(0.45, 0.2, 0.4, 1.2))


def bez(x1: float, y1: float, x2: float, y2: float):
    """cubic-bezier(x1,y1,x2,y2) as a function of progress 0..1 (CSS semantics)."""
    def bx(s): return 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
    def by(s): return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3

    def f(x: float) -> float:
        x = max(0.0, min(1.0, x))
        lo, hi = 0.0, 1.0
        for _ in range(28):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if bx(mid) < x else (lo, mid)
        return by((lo + hi) / 2)
    return f


enter, exit_, push, settle, pop = (bez(*EASE[k]) for k in ("enter", "exit", "push", "settle", "pop"))


def drift(t: float, dur: float, amount: float = 0.04) -> float:
    """Slow 2D push-in over a whole shot: scale factor 1.0 -> 1+amount (3-5% is the rule; never a snap or punch-in)."""
    return 1.0 + amount * push(max(0.0, min(1.0, t / max(dur, 0.01))))


def rim(mob, dx: float = 0.07, dy: float = -0.09, color: str = STICKY, opacity: float = 0.95) -> VGroup:
    """A hard, un-blurred offset echo of a card (the yellow rim behind a photo card). Returns VGroup(echo, mob); add the group."""
    echo = mob.copy().set_fill(color, opacity=opacity).set_stroke(color, width=0, opacity=0)
    echo.shift(np.array([dx, dy, 0.0]))
    return VGroup(echo, mob)
