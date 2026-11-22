"""Progressive SVG drawing (spec section 10): reveal an illustration's paths as if being
hand-drawn, outline before fill. Loads `assets/explainer/illustrations/<name>.svg` when that
file exists; otherwise builds a simple procedural placeholder shape from the element's name so
a storyboard never fails to render just because an illustration hasn't been drawn yet (spec
section 12: "generate simple diagrams and icons programmatically").
"""
from __future__ import annotations

from pathlib import Path

from manim import BLUE, Circle, Create, SVGMobject, VGroup

ROOT = Path(__file__).resolve().parents[3]
ILLUSTRATIONS_DIR = ROOT / "assets" / "explainer" / "illustrations"


def _safe_name(name: str) -> str:
    """Only letters, digits, underscore, dash - never treat a storyboard element name as a
    path (spec section 21: safe file-path validation)."""
    return "".join(c for c in name if c.isalnum() or c in "_-") or "shape"


def load_or_placeholder(name: str, colour: str = BLUE, size: float = 1.5):
    path = ILLUSTRATIONS_DIR / f"{_safe_name(name)}.svg"
    if path.is_file():
        mobj = SVGMobject(str(path))
        mobj.set_color(colour)
        return mobj
    # Procedural fallback: a simple ring, recognisable as "an illustration is here" without
    # needing a drawn asset yet. Real illustrations get added to assets/explainer/illustrations/
    # and are picked up automatically, no code change required.
    circle = Circle(radius=size / 2, color=colour, stroke_width=6)
    return VGroup(circle)


def draw_svg_progressively(manim_scene, mobject, run_time: float = 1.2) -> None:
    """The actual 'progressive stroke draw' the spec asks for repeatedly: Manim's `Create`
    animates a VMobject's (or SVGMobject's) points in path order, which is precisely a
    hand-drawn reveal for vector paths."""
    manim_scene.play(Create(mobject), run_time=run_time)
