"""Builds the Manim mobjects for one storyboard scene's elements, and the reusable primitives
(arrows, highlights, simple diagrams, doodle characters) the spec asks for by name in section
11: `animate_arrow()`, `highlight_element()`, `animate_diagram()`, `create_doodle_character()`.
Also the five scene templates (hook, explainer_diagram, comparison, timeline, takeaway) - which
element layout each template gets is decided here, reading the already-built element list from
storyboard_engine (so the creative choice of *what* to show stays in the storyboard, and this
module only decides *where on screen* / *with what Manim animation*).
"""
from __future__ import annotations

import math
from typing import List, Tuple

from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Circle, Create, FadeIn, GrowArrow,
                    Indicate, Line, Mobject, SurroundingRectangle, Text, VGroup, Write)

from ..schemas.storyboard_schema import Scene, SceneElement
from . import svg_animator
from .sketch_renderer import Palette, accent_for

_FONT = {"en": None, "hi": "Noto Sans Devanagari"}   # Manim/Pango resolves "en" fine with the default font


def _font_for(lang: str) -> str | None:
    return _FONT.get(lang)


def add_paper_texture(manim_scene, palette: Palette) -> None:
    """A faint grid of dots standing in for paper grain (spec: 'subtle paper textures') -
    cheap to draw, never the focal point, matches the whiteboard/colourful look."""
    dots = VGroup(*[
        Circle(radius=0.01, color=palette.ink, fill_opacity=0.08, stroke_width=0)
        .move_to((x, y, 0))
        for x in range(-6, 7, 2) for y in range(-7, 8, 2)
    ])
    manim_scene.add(dots)


def create_doodle_character(pose: str, colour: str) -> Mobject:
    """A minimal reusable stick-figure doodle (spec section 10: 'simple doodle characters' /
    'lightweight reusable vector assets rather than ... paid image-generation services').
    `pose` is a label only for now (walking/pointing/thinking/surprised/explaining/looking) -
    each pose nudges the arm/head so the six poses are visually distinct without needing six
    separate hand-drawn assets.
    """
    head = Circle(radius=0.25, color=colour, stroke_width=5)
    body = Line(ORIGIN, DOWN * 0.8, color=colour, stroke_width=5).next_to(head, DOWN, buff=0)
    arm_angle = {"pointing": 20, "explaining": 35, "surprised": 70, "thinking": -20,
                 "walking": 45, "looking": 10}.get(pose, 30)
    arm = Line(ORIGIN, RIGHT * 0.6, color=colour, stroke_width=5).rotate(math.radians(arm_angle))
    arm.move_to(body.get_center() + UP * 0.1)
    legs = VGroup(
        Line(ORIGIN, DOWN * 0.5 + LEFT * 0.2, color=colour, stroke_width=5),
        Line(ORIGIN, DOWN * 0.5 + RIGHT * 0.2, color=colour, stroke_width=5),
    ).move_to(body.get_bottom())
    return VGroup(head, body, arm, legs)


def animate_arrow(manim_scene, start, end, colour: str, run_time: float = 0.8) -> Mobject:
    arrow = Arrow(start, end, color=colour, stroke_width=6, buff=0.1)
    manim_scene.play(GrowArrow(arrow), run_time=run_time)
    return arrow


def highlight_element(manim_scene, mobject: Mobject, colour: str, run_time: float = 0.6) -> Mobject:
    box = SurroundingRectangle(mobject, color=colour, buff=0.15)
    manim_scene.play(Create(box), Indicate(mobject, color=colour), run_time=run_time)
    return box


def animate_diagram(manim_scene, parts: List[Mobject], run_time: float = 1.0) -> None:
    """Reveals a multi-part diagram (e.g. a timeline track or a process flow) one part at a
    time, left to right - a process the 'timeline'/'explainer_diagram' templates use."""
    for part in parts:
        manim_scene.play(Create(part), run_time=run_time / max(1, len(parts)))


# ---------------------------------------------------------------- per-template layout

def _label(text: str, colour: str, lang: str, size: int = 40) -> Text:
    """Text sized to fit the live frame width, so a long caption wraps in scale rather than
    running off the edge of a narrow vertical frame."""
    from manim import config as manim_config

    kwargs = {"font_size": size, "color": colour}
    font = _font_for(lang)
    if font:
        kwargs["font"] = font
    label = Text(text, **kwargs)
    max_w = manim_config.frame_width * 0.85
    if label.width > max_w:
        label.scale_to_fit_width(max_w)
    return label


def _frame_point(x: float, y: float) -> Tuple[float, float, float]:
    """Frame fractions (-0.5..0.5) -> Manim scene coordinates for the live frame size."""
    from manim import config as manim_config

    return (x * manim_config.frame_width, y * manim_config.frame_height, 0)


def build_elements(scene: Scene, palette: Palette, lang: str) -> List[Tuple[Mobject, SceneElement]]:
    """Turns scene.elements into (Mobject, SceneElement) pairs, positioned by scene.template.
    Positions are placeholders built for a 1080x1920-equivalent Manim frame (default Manim
    coordinate units, which `video_engine` maps onto whichever pixel resolution is requested -
    the layout logic here never hardcodes pixels)."""
    out: List[Tuple[Mobject, SceneElement]] = []
    for i, elem in enumerate(scene.elements):
        colour = accent_for(palette, i)  # palette colour is the only style default left
        if elem.type == "character":
            mobj = create_doodle_character(elem.name, colour)
        elif elem.type in ("svg_illustration", "diagram"):
            mobj = svg_animator.load_or_placeholder(elem.name, colour)
        elif elem.type == "arrow":
            mobj = Arrow((-1.2, 0, 0), (1.2, 0, 0), color=colour, stroke_width=6, buff=0.1)
        elif elem.type == "highlight":
            mobj = SurroundingRectangle(Circle(radius=0.6), color=colour)
        else:   # label
            mobj = _label(elem.text or elem.name, palette.ink if elem.type == "label" else colour, lang)
        start = elem.keyframes[0] if elem.keyframes else None
        if start is not None:
            mobj.move_to(_frame_point(start.x, start.y))
            mobj.scale(start.scale).set_opacity(start.opacity)
        elif elem.position is not None:
            mobj.move_to(_frame_point(*elem.position))
        out.append((mobj, elem))
    return out


_ANIM_RUNTIME = {"progressive_stroke_draw": 1.1, "draw_from_start": 0.8, "fade_in": 0.5,
                 "pop_in": 0.5, "slide_in": 0.6}


def reveal_time(scene: Scene) -> float:
    return sum(_ANIM_RUNTIME.get(e.animation, 0.5) for e in scene.elements) + 0.3


MOTION_STEPS = 8


STAGGER = 0.06   # each later element starts a little after the one before (overlapping action)


def _smoothstep(f: float) -> float:
    """Ease-in-out: motion starts and ends gently instead of at constant speed (linear looks robotic)."""
    f = min(1.0, max(0.0, f))
    return f * f * (3 - 2 * f)


def _sample_keyframes(elem: SceneElement, u: float):
    """Position/scale/opacity of an element at fraction u (0..1) of the scene, eased between its
    authored keyframes."""
    frames = elem.keyframes
    if u <= frames[0].t:
        k = frames[0]
        return k.x, k.y, k.scale, k.opacity
    for a, b in zip(frames, frames[1:]):
        if a.t <= u <= b.t:
            f = _smoothstep(0.0 if b.t == a.t else (u - a.t) / (b.t - a.t))
            lerp = lambda p, q: p + (q - p) * f   # noqa: E731
            return lerp(a.x, b.x), lerp(a.y, b.y), lerp(a.scale, b.scale), lerp(a.opacity, b.opacity)
    k = frames[-1]
    return k.x, k.y, k.scale, k.opacity


def motion_plays(mobjects: List[Tuple[Mobject, SceneElement]], scene_seconds: float):
    """Returns the Manim plays that move every element with keyframes through its path. Steps are
    shared across elements and played together, so the whole motion takes exactly `budget`
    seconds regardless of how many elements or keyframes a scene has."""
    moving = [(i, m, e) for i, (m, e) in enumerate(mobjects) if e.keyframes]
    if not moving:
        return []
    per_step = scene_seconds / MOTION_STEPS
    plays = []
    for step in range(1, MOTION_STEPS + 1):
        u = step / MOTION_STEPS
        anims = []
        for i, mobj, elem in moving:
            x, y, scale, opacity = _sample_keyframes(elem, min(1.0, u - i * STAGGER))
            target = mobj.copy().move_to(_frame_point(x, y)).scale(scale).set_opacity(opacity)
            anims.append(mobj.animate.become(target))
        plays.append((anims, per_step))
    return plays


def animate_in(manim_scene, mobject: Mobject, elem: SceneElement) -> None:
    rt = _ANIM_RUNTIME.get(elem.animation, 0.5)
    if elem.animation == "progressive_stroke_draw":
        manim_scene.play(Create(mobject), run_time=rt)
    elif elem.animation == "draw_from_start":
        manim_scene.play(GrowArrow(mobject) if isinstance(mobject, Arrow) else Create(mobject), run_time=rt)
    elif elem.animation == "pop_in":
        from manim.utils.rate_functions import ease_out_back

        manim_scene.play(Write(mobject) if isinstance(mobject, Text) else FadeIn(mobject, scale=1.2),
                         run_time=rt, rate_func=ease_out_back)
    elif elem.animation == "slide_in":
        manim_scene.play(FadeIn(mobject, shift=UP * 0.4), run_time=rt)
    else:   # fade_in
        manim_scene.play(FadeIn(mobject), run_time=rt)
