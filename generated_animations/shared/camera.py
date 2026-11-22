"""Camera controller + HUD pinning.

The scene's camera is Manim's moving frame. Anything that must stay screen-fixed while the camera pushes
in or pans (headline, captions, the presenter avatar, transition overlays) is `pin`ned: each frame it is
re-placed relative to the live frame, so layering/depth works - world objects move with the camera, the
HUD does not.
"""
from __future__ import annotations

import numpy as np
from manim import ORIGIN

from .motion import ease_in_out_cubic


class CameraRig:
    def __init__(self, scene):
        self.scene = scene
        self.frame = scene.camera.frame
        self.base_w = self.frame.width
        self._home = (self.frame.get_center().copy(), self.frame.width)

    # -- HUD -------------------------------------------------------------------------------
    def hud_transform(self, mobject):
        """Apply the frame's zoom + position to a mobject built in canonical (unzoomed) screen coordinates."""
        k = self.frame.width / self.base_w
        mobject.scale(k, about_point=ORIGIN)
        mobject.shift(self.frame.get_center())
        return mobject

    def pin(self, mobject, canonical: bool = True):
        """Keep `mobject` screen-fixed (`canonical`: it was built in unzoomed screen coordinates, so it is first
        placed into the current frame): each frame it is scaled/shifted by the frame's change since the last
        frame (style, opacity and any animation running on the mobject itself are left alone)."""
        if canonical:
            self.hud_transform(mobject)
        state = {"k": self.frame.width / self.base_w, "c": self.frame.get_center().copy()}

        def follow(m):
            k = self.frame.width / self.base_w
            c = self.frame.get_center().copy()
            if abs(k - state["k"]) > 1e-9:
                m.scale(k / state["k"], about_point=state["c"])
            if np.linalg.norm(c - state["c"]) > 1e-9:
                m.shift(c - state["c"])
            state["k"], state["c"] = k, c
        mobject.add_updater(follow)
        return mobject

    # -- moves -----------------------------------------------------------------------------
    def push_in(self, focus, zoom: float = 1.4, run_time: float = 1.5):
        """Zoom toward `focus` (point or mobject): zoom > 1 pushes in."""
        target = focus.get_center() if hasattr(focus, "get_center") else np.asarray(focus, dtype=float)
        self.scene.play(self.frame.animate.set(width=self.base_w / zoom).move_to(target),
                        run_time=run_time, rate_func=ease_in_out_cubic)

    def pan_to(self, point, run_time: float = 1.2):
        self.scene.play(self.frame.animate.move_to(np.asarray(point, dtype=float)), run_time=run_time,
                        rate_func=ease_in_out_cubic)

    def drift(self, dx: float, dy: float, run_time: float):
        """Slow handheld-style drift, used to keep a long hold from feeling frozen."""
        self.scene.play(self.frame.animate.shift(np.array([dx, dy, 0.0])), run_time=run_time,
                        rate_func=lambda t: t)

    def shake(self, amplitude: float = 0.08, run_time: float = 0.4, steps: int = 6):
        for i in range(steps):
            s = amplitude * (1 if i % 2 else -1) * (1 - i / steps)
            self.scene.play(self.frame.animate.shift(np.array([s, s / 2, 0.0])), run_time=run_time / steps)

    def reset(self, run_time: float = 0.8):
        c, w = self._home
        self.scene.play(self.frame.animate.set(width=w).move_to(c), run_time=run_time,
                        rate_func=ease_in_out_cubic)
