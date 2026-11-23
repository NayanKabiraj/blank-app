"""The presenter "Pip": the owner's own cartoon picture (avatar/assets/pip_base.png), animated.

The picture's mouth is lip-synced to the narration (face.py paints mouth shapes in the picture's style), the eyes blink, and the whole
picture breathes, sways, nods and leans toward whatever he looks at or points at. Same public API as before, so shots keep working:
  x / y / s trackers ... where Pip stands: (x, y) is the bottom centre of the picture, s the scale (movement.py)
  expr[...] ............ expressions.py (mouth_o opens the mouth, brow_raise / smile lift and brighten him a little)
  pose[...] ............ gestures.py: point = lean toward the target, wave = happy sway, present = open lean, shrug = tilt + lift
  look_at(...) ......... his head turns slightly toward a world point
Automatic: idle breathing/sway, blinks, lip-sync from the narration's loudness envelope.
"""
from __future__ import annotations

import math

import numpy as np
from manim import Group, ImageMobject, ValueTracker

from . import face
from .expressions import EXPRESSIONS

HEIGHT = 4.6          # canonical height (frame units) of the picture at scale 1


class Avatar(Group):
    def __init__(self, rig, timeline, mouth_level=None, position=(-2.6, -8.0), scale: float = 0.92, seed: int = 11, sticker: bool = False):
        super().__init__()
        self.rig, self.timeline = rig, timeline
        self.mouth_level = mouth_level or (lambda t: 0.0)
        self.x, self.y, self.s = ValueTracker(position[0]), ValueTracker(position[1]), ValueTracker(scale)
        self.expr = {k: ValueTracker(v) for k, v in EXPRESSIONS["neutral"].items()}
        self.pose = {k: ValueTracker(0.0) for k in ("point", "wave", "present", "shrug")}
        self.look_fn = None
        self.point_fn = None
        self.facing = ValueTracker(0.0)
        rng = np.random.default_rng(seed)
        self._blinks = np.cumsum(rng.uniform(2.2, 4.2, 40))
        self._mouth = 0.0
        self._lv = 0
        self._face = face.get()
        self._sticker = sticker
        arr = self._face.frame(0, 0, sticker)
        self._h, self._w = arr.shape[:2]
        self._img = ImageMobject(arr)
        self._template = self._img.points.copy()
        self._img.set_resampling_algorithm(2)       # smooth
        self.add(self._img)
        self.add_updater(lambda m: m._refresh())
        self._refresh()

    # -- helpers (same names as the old avatar; shots and gestures use them) -------------
    def _world(self, canon_pt):
        k = self.rig.frame.width / self.rig.base_w
        return np.asarray(canon_pt, float) * k + self.rig.frame.get_center()

    def _to_canon(self, world_pt):
        k = self.rig.frame.width / self.rig.base_w
        return (np.asarray(world_pt, float) - self.rig.frame.get_center()) / k

    def look_at(self, target):
        if target is None:
            self.look_fn = None
        elif callable(target):
            self.look_fn = target
        elif hasattr(target, "get_center"):
            self.look_fn = target.get_center
        else:
            self.look_fn = lambda p=np.asarray(target, float): p
        return self

    def set_point_target(self, target):
        if callable(target):
            self.point_fn = target
        elif hasattr(target, "get_center"):
            self.point_fn = target.get_center
        else:
            self.point_fn = lambda p=np.asarray(target, float): p
        return self

    def _blink(self, t: float) -> float:
        for b in self._blinks:
            if 0 <= t - b < 0.18:
                return math.sin((t - b) / 0.18 * math.pi)
        return 0.0

    def _direction(self, fn, origin):
        if fn is None:
            return 0.0, 0.0
        d = np.asarray(fn(), float) - origin
        n = max(1e-6, float(np.linalg.norm(d[:2])))
        return d[0] / n, d[1] / n

    # -- one frame ----------------------------------------------------------------------
    def _refresh(self):
        t = self.timeline.t
        w = {k: v.get_value() for k, v in self.pose.items()}
        e = {k: v.get_value() for k, v in self.expr.items()}
        x, y, s = self.x.get_value(), self.y.get_value(), self.s.get_value()
        # lip-sync: smoothed loudness -> a mouth level; the expression can hold the mouth open too (surprise)
        self._mouth += (min(1.0, self.mouth_level(t) * 1.25) - self._mouth) * 0.5
        mouth = max(self._mouth, e["mouth_o"] * 0.7)
        lv = int(round(max(0.0, min(1.0, mouth)) * (face.LEVELS - 1)))
        blink_amt = self._blink(t) if e["eye_open"] > 0.5 else 1.0
        blink_lv = 0 if blink_amt < 0.12 else (1 if blink_amt < 0.6 else 2)
        key = (lv, blink_lv)
        if key != getattr(self, "_key", None):
            self._key = key
            self._img.pixel_array = self._face.frame(lv / (face.LEVELS - 1), 0.0 if blink_lv == 0 else (0.5 if blink_lv == 1 else 1.0), self._sticker)
        head_world = self._world((x, y + HEIGHT * s * 0.62, 0))
        gx, gy = self._direction(self.look_fn, head_world)
        px, py = self._direction(self.point_fn, head_world) if w["point"] > 0.01 else (0.0, 0.0)
        # body language: tilt (degrees), lift and lean (fractions of the picture)
        tilt = 1.6 * math.sin(t * 1.3) + 5.0 * gx * self.facing.get_value() + w["point"] * (-9.0 * px) \
            + w["wave"] * 7.0 * math.sin(t * 7.0) + w["shrug"] * 7.0 + w["present"] * 4.0 + 3.0 * e["brow_tilt"]
        bob = 0.012 * math.sin(t * 2.1) + w["point"] * 0.02 * math.sin(t * 5.0) + w["shrug"] * 0.04 + w["wave"] * 0.02 * math.sin(t * 7.0 + 1.0) \
            + 0.02 * e["brow_raise"]
        lean = 0.02 * gx + w["point"] * 0.07 * px + w["present"] * 0.03
        breathe = 1.0 + 0.006 * math.sin(t * 2.1) + 0.012 * max(0.0, e["smile"] - 0.35) + 0.01 * w["present"]
        h = HEIGHT * s * breathe
        wd = h * self._w / self._h
        img = self._img
        img.points = self._template.copy()
        img.stretch_to_fit_height(h)
        img.stretch_to_fit_width(wd)
        img.move_to(np.array([x + lean * wd, y + h / 2 + bob * h, 0.0]))
        img.rotate(math.radians(tilt), about_point=np.array([x, y + h * 0.1, 0.0]))
        self.rig.hud_transform(img)
        return self

    def _build(self):          # kept for API compatibility with older callers
        self._refresh()
        return self
