"""The presenter avatar "Pip": one consistent character, rebuilt every frame from a handful of trackers.

State (all ValueTrackers, so ordinary Manim animations drive them):
  pos x/y/scale ........ where Pip stands (movement.py)
  expr[...] ............ face (expressions.py)
  pose_* weights ....... arm gestures (gestures.py)
  gaze target .......... Pip's eyes + head follow a world-space point or moving mobject
Automatic behaviours: idle breathing/sway, eye blinks, and lip-sync from the narration's loudness envelope.
"""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Circle, Ellipse, Line, RoundedRectangle, Sector, ValueTracker, VGroup)

from .expressions import EXPRESSIONS

SKIN, HAIR, SHIRT, SHIRT_DARK, EYE_W, INK = "#F2C6A0", "#2B1B14", "#2EC5FF", "#1B8FC2", "#FFFFFF", "#1A1A1A"

REST_R = (-math.pi / 2 + 0.28, -math.pi / 2 + 0.12)
REST_L = (-math.pi / 2 - 0.28, -math.pi / 2 - 0.12)
UPPER, FORE = 0.95, 0.85
SHOULDER_R, SHOULDER_L = np.array([0.78, -0.62, 0.0]), np.array([-0.78, -0.62, 0.0])


def _lerp_angle(a: float, b: float, w: float) -> float:
    return a + (b - a) * w


class Avatar(VGroup):
    def __init__(self, rig, timeline, mouth_level=None, position=(-2.4, -4.6), scale: float = 1.0, seed: int = 11):
        super().__init__()
        self.rig, self.timeline = rig, timeline
        self.mouth_level = mouth_level or (lambda t: 0.0)
        self.x, self.y, self.s = ValueTracker(position[0]), ValueTracker(position[1]), ValueTracker(scale)
        self.expr = {k: ValueTracker(v) for k, v in EXPRESSIONS["neutral"].items()}
        self.pose = {k: ValueTracker(0.0) for k in ("point", "wave", "present", "shrug")}
        self.look_fn = None          # callable -> world point, or None (look at camera)
        self.point_fn = None
        self.facing = ValueTracker(0.0)   # head turn toward the stage (-1..1), eased by look_at
        rng = np.random.default_rng(seed)
        self._blinks = np.cumsum(rng.uniform(2.2, 4.2, 40))
        self._mouth = 0.0
        self.add_updater(lambda m: m._refresh())
        self._refresh()

    # -- helpers ---------------------------------------------------------------------------
    def _to_canon(self, world_pt):
        k = self.rig.frame.width / self.rig.base_w
        return (np.asarray(world_pt, float) - self.rig.frame.get_center()) / k

    def _world(self, canon_pt):
        k = self.rig.frame.width / self.rig.base_w
        return np.asarray(canon_pt, float) * k + self.rig.frame.get_center()

    def look_at(self, target):
        """Look at a mobject, a callable returning a world point, or a world point. None = look at viewer."""
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
            if 0 <= t - b < 0.16:
                return math.sin((t - b) / 0.16 * math.pi)
        return 0.0

    # -- geometry --------------------------------------------------------------------------
    def _arm(self, shoulder, a1, a2, pointing: float):
        elbow = shoulder + UPPER * np.array([math.cos(a1), math.sin(a1), 0])
        hand = elbow + FORE * np.array([math.cos(a2), math.sin(a2), 0])
        g = VGroup(
            Line(shoulder, elbow, color=SHIRT_DARK, stroke_width=22),
            Line(elbow, hand, color=SHIRT_DARK, stroke_width=20),
            Circle(radius=0.15, stroke_width=0, fill_color=SKIN, fill_opacity=1).move_to(hand),
        )
        tip = hand + 0.32 * np.array([math.cos(a2), math.sin(a2), 0])
        finger = Line(hand, tip, color=SKIN, stroke_width=9, stroke_opacity=pointing)
        g.add(finger)
        return g

    def _build(self):
        t = self.timeline.t
        e = {k: v.get_value() for k, v in self.expr.items()}
        w = {k: v.get_value() for k, v in self.pose.items()}

        # gaze + head turn toward the target
        gx = gy = 0.0
        if self.look_fn is not None:
            head_world = self._world((self.x.get_value(), self.y.get_value() + 1.0 * self.s.get_value(), 0))
            d = np.asarray(self.look_fn(), float) - head_world
            n = max(1e-6, np.linalg.norm(d[:2]))
            gx, gy = d[0] / n, d[1] / n
        turn = float(np.clip(gx, -1, 1)) * (self.facing.get_value())
        sway = math.sin(t * 1.3) * 0.03
        breathe = 1.0 + 0.012 * math.sin(t * 2.1)
        bob = 0.025 * math.sin(t * 2.1)

        # lip sync (smoothed so the mouth does not flutter)
        target_open = min(1.0, self.mouth_level(t) * 1.6)
        self._mouth += (target_open - self._mouth) * 0.55
        mouth_open = max(self._mouth, e["mouth_o"])

        # body
        body = RoundedRectangle(corner_radius=0.45, width=1.7, height=1.9 * breathe, stroke_width=0,
                                fill_color=SHIRT, fill_opacity=1).move_to((0, -1.5 + 0.5 * (breathe - 1), 0))
        collar = Arc(radius=0.34, start_angle=math.pi, angle=math.pi, stroke_width=8, color=SHIRT_DARK).move_to((0, -0.62, 0))
        neck = Line((0, -0.5, 0), (0, -0.7, 0), color=SKIN, stroke_width=28)

        # arms
        def blend(rest, pt, wave, pres, shr):
            a1 = rest[0]; a2 = rest[1]
            for wt, tgt in ((w["point"], pt), (w["wave"], wave), (w["present"], pres), (w["shrug"], shr)):
                a1 = _lerp_angle(a1, tgt[0], wt); a2 = _lerp_angle(a2, tgt[1], wt)
            return a1, a2
        point_ang = 0.5
        if self.point_fn is not None:
            sh_world = self._world((self.x.get_value() + SHOULDER_R[0] * self.s.get_value(),
                                    self.y.get_value() + SHOULDER_R[1] * self.s.get_value(), 0))
            d = np.asarray(self.point_fn(), float) - sh_world
            point_ang = math.atan2(d[1], d[0])
        rest_sway = 0.05 * math.sin(t * 1.7)
        r1, r2 = blend((REST_R[0] + rest_sway, REST_R[1]), (point_ang, point_ang),
                       (1.15, 1.6 + 0.55 * math.sin(t * 11)), (0.15, 0.75), (-0.25, 0.9))
        l1, l2 = blend((REST_L[0] - rest_sway, REST_L[1]), REST_L, REST_L, (math.pi - 0.6, math.pi - 1.2),
                       (math.pi + 0.25, math.pi - 0.9))
        arm_r = self._arm(SHOULDER_R, r1, r2, w["point"])
        arm_l = self._arm(SHOULDER_L, l1, l2, 0.0)

        # head
        head_c = np.array([0.0 + turn * 0.1, 0.25 + bob, 0.0])
        head = Circle(radius=0.88, stroke_width=0, fill_color=SKIN, fill_opacity=1).move_to(head_c)
        hair = Sector(radius=0.93, angle=math.pi * 0.82, start_angle=math.pi * 0.09, arc_center=head_c + np.array([0, 0.12, 0]),
                      stroke_width=0, fill_color=HAIR, fill_opacity=1)
        eye_y = head_c[1] + 0.12
        eye_open = max(0.0, e["eye_open"] * (1 - 0.95 * self._blink(t)))
        eyes = VGroup()
        for sx in (-1, 1):
            ex = head_c[0] + sx * 0.33 + turn * 0.12
            white = Ellipse(width=0.36, height=0.36 * min(1.3, eye_open), stroke_width=0, fill_color=EYE_W,
                            fill_opacity=1).move_to((ex, eye_y, 0))
            pupil = Circle(radius=0.085, stroke_width=0, fill_color=INK, fill_opacity=1).move_to(
                (ex + gx * 0.07 + turn * 0.04, eye_y + gy * 0.06, 0))
            pupil.set_opacity(1 if eye_open > 0.12 else 0)
            if eye_open <= 0.12:
                white.set_opacity(0)
            eyes.add(white, pupil)
            lid = Line((ex - 0.18, eye_y, 0), (ex + 0.18, eye_y, 0), color=INK, stroke_width=5,
                       stroke_opacity=1 if eye_open <= 0.12 else 0)
            eyes.add(lid)
        brows = VGroup()
        for sx in (-1, 1):
            bx = head_c[0] + sx * 0.33 + turn * 0.12
            by = eye_y + 0.30 + 0.12 * e["brow_raise"]
            tilt = 0.14 * e["brow_tilt"]
            brows.add(Line((bx + sx * 0.17, by - tilt * 0.5, 0), (bx - sx * 0.17, by + tilt * 0.5, 0),
                           color=HAIR, stroke_width=7))
        # mouth: closed = smile arc, open = ellipse
        mx, my = head_c[0] + turn * 0.14, head_c[1] - 0.38
        smile = e["smile"]
        ang = max(0.05, 0.9 * abs(smile))
        arc = Arc(radius=0.34, start_angle=(-math.pi / 2 - ang / 2) if smile >= 0 else (math.pi / 2 - ang / 2),
                  angle=ang, stroke_width=6, color="#8A3B2A").move_to((mx, my + (0.0 if smile >= 0 else -0.05), 0))
        arc.set_stroke(opacity=1 if mouth_open < 0.08 else 0)
        mouth = Ellipse(width=0.30 + 0.12 * smile, height=0.05 + 0.34 * mouth_open, stroke_width=0,
                        fill_color="#6E1F1F", fill_opacity=1 if mouth_open >= 0.08 else 0).move_to((mx, my - 0.03, 0))
        cheeks = VGroup(*[Circle(radius=0.12, stroke_width=0, fill_color="#F08A8A", fill_opacity=0.25 + 0.15 * smile)
                          .move_to((head_c[0] + sx * 0.55 + turn * 0.1, head_c[1] - 0.2, 0)) for sx in (-1, 1)])
        face = VGroup(head, hair, cheeks, eyes, brows, arc, mouth)
        face.rotate(sway + turn * 0.12, about_point=np.array([0, -0.55, 0]))

        full = VGroup(arm_l, body, collar, neck, face, arm_r)
        full.scale(self.s.get_value(), about_point=np.zeros(3))
        full.shift((self.x.get_value(), self.y.get_value(), 0))
        return self.rig.hud_transform(full)

    def _refresh(self):
        # in place: Manim caches the moving-mobject list at the start of each play, so children must keep identity
        self.become(self._build())
