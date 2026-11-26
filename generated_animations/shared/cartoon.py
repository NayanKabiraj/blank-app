"""2D cartoon character for vox packs (26 Nov 2026): a friendly astronaut with an outlined, flat look (big visor, eyes that look and blink, a mouth, gloves).
Constant part count, so it can be redrawn every frame inside `b.live(...)`.

    from generated_animations.shared.cartoon import astro, ear, eye_icon
    b.live(lambda a: astro(b.C + v(0, -0.2), 1.0, hl=(-0.2, 0.1), hr=(0.2, 0.1), mouth=0.6, a=a), b.t0 + 0.1, z=6)   # clapping
`hl`/`hr` = where the left/right glove is, relative to the body centre (before scaling); the arm is drawn from the shoulder to the glove."""
from __future__ import annotations

import numpy as np
from manim import Arc, Circle, Ellipse, Line, RoundedRectangle, VGroup

INK, WHITE, SUIT_SHADE, VISOR, ORANGE, PACK = "#221E1C", "#FFFDF5", "#E3DCCB", "#1F3350", "#F08A3C", "#B9B4C8"


def _p(x, y):
    return np.array([float(x), float(y), 0.0])


def astro(c, s: float = 1.0, hl=(-0.95, -0.75), hr=(0.95, -0.75), look=(0.0, 0.0), mouth: float = 0.0, blink: float = 1.0, a: float = 1.0, smile: float = 1.0) -> VGroup:
    g = VGroup()
    g.add(RoundedRectangle(corner_radius=0.18, width=0.55, height=1.05, stroke_color=INK, stroke_width=5, fill_color=PACK, fill_opacity=1).move_to(_p(-0.62, -0.1)))   # backpack
    for sx in (-0.2, 0.2):                                                                                                                                    # legs + boots
        g.add(RoundedRectangle(corner_radius=0.14, width=0.34, height=0.7, stroke_color=INK, stroke_width=5, fill_color=WHITE, fill_opacity=1).move_to(_p(sx, -1.05)))
        g.add(RoundedRectangle(corner_radius=0.12, width=0.46, height=0.24, stroke_color=INK, stroke_width=5, fill_color=ORANGE, fill_opacity=1).move_to(_p(sx + 0.03, -1.43)))
    for sx, h in ((-0.55, hl), (0.55, hr)):                                                                                                                   # arms (outline under, suit colour over)
        sh, hand = _p(sx, 0.05), _p(h[0], h[1])
        g.add(Line(sh, hand, color=INK, stroke_width=30), Line(sh, hand, color=WHITE, stroke_width=20))
    g.add(RoundedRectangle(corner_radius=0.3, width=1.1, height=1.25, stroke_color=INK, stroke_width=5, fill_color=WHITE, fill_opacity=1).move_to(_p(0, -0.2)))   # body
    g.add(RoundedRectangle(corner_radius=0.08, width=0.5, height=0.3, stroke_color=INK, stroke_width=4, fill_color=ORANGE, fill_opacity=1).move_to(_p(0, -0.22)))
    g.add(Circle(radius=0.62, stroke_color=INK, stroke_width=5, fill_color=WHITE, fill_opacity=1).move_to(_p(0, 0.85)))                                        # helmet
    g.add(RoundedRectangle(corner_radius=0.3, width=1.0, height=0.7, stroke_color=INK, stroke_width=4, fill_color=VISOR, fill_opacity=1).move_to(_p(0.04, 0.85)))
    for ex in (-0.2, 0.22):
        g.add(Ellipse(width=0.26, height=0.3 * max(0.08, blink), stroke_width=0, fill_color=WHITE, fill_opacity=1).move_to(_p(ex, 0.92)))                     # eyes
        g.add(Circle(radius=0.075 * 1.0, stroke_width=0, fill_color=INK, fill_opacity=1).move_to(_p(ex + 0.06 * look[0], 0.92 + 0.05 * look[1])).scale([1, max(0.1, blink), 1]))
    mo = Ellipse(width=0.22 + 0.06 * smile, height=0.05 + 0.2 * mouth, stroke_width=0, fill_color=WHITE if mouth > 0.05 else "#FF8FA3", fill_opacity=1).move_to(_p(0.02, 0.66))
    g.add(mo)
    g.add(Arc(radius=0.2, start_angle=2.2, angle=0.7, stroke_color="#FFFFFF", stroke_width=4, stroke_opacity=0.8).move_to(_p(-0.32, 1.08)))                  # shine
    for h in (hl, hr):                                                                                                                                        # gloves
        g.add(Circle(radius=0.17, stroke_color=INK, stroke_width=4, fill_color=ORANGE, fill_opacity=1).move_to(_p(h[0], h[1])))
    g.scale(s).move_to(np.asarray(c, float))
    g.set_opacity(a) if a < 0.999 else None
    return g


def ear(c, s: float = 1.0, col: str = INK, a: float = 1.0) -> VGroup:
    g = VGroup(Arc(radius=0.55, start_angle=-0.6, angle=3.9, stroke_color=col, stroke_width=7, stroke_opacity=a), Arc(radius=0.3, start_angle=0.2, angle=3.2, stroke_color=col, stroke_width=6, stroke_opacity=a),
               Arc(radius=0.12, start_angle=0.5, angle=3.2, stroke_color=col, stroke_width=5, stroke_opacity=a))
    return g.scale(s).move_to(np.asarray(c, float))


def eye_icon(c, s: float = 1.0, col: str = INK, a: float = 1.0) -> VGroup:
    g = VGroup(Ellipse(width=1.3, height=0.7, stroke_color=col, stroke_width=7, stroke_opacity=a, fill_color="#FFFFFF", fill_opacity=a), Circle(radius=0.23, stroke_width=0, fill_color=col, fill_opacity=a))
    return g.scale(s).move_to(np.asarray(c, float))
