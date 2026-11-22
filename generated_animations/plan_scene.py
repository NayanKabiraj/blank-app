"""One Manim scene that plays a whole video plan: every plan scene becomes a time window (taken from the narration
timeline) in which kinds.render draws the scene's graphic, captions and the presenter."""
from __future__ import annotations

from manim import MovingCameraScene

from . import kinds
from .avatar import Avatar
from .runtime import SceneContext, Timeline
from .shared import lighting
from .shared.camera import CameraRig

BG = "#060912"


class PlanScene(MovingCameraScene):
    def __init__(self, scenes, boundaries, timeline_rows, layout, lang, narration=None, **kwargs):
        self.plan_scenes, self.boundaries, self.rows = scenes, boundaries, timeline_rows
        self.layout, self.lang, self.narration = layout, lang, narration
        super().__init__(**kwargs)

    def construct(self):
        from manim import config
        L = self.layout
        self.camera.background_color = BG
        fw, fh = config.frame_width, config.frame_height
        self.timeline = Timeline(self)
        self.add(self.timeline.make_clock())
        rig = CameraRig(self)
        sky = lighting.starfield(fw * 1.05, fh * 1.05, res=L.star_res)
        sky.set_z_index(-10)
        vig = lighting.vignette(fw, fh)
        vig.set_z_index(9)
        self.add(sky, vig)
        level = (lambda t: self.narration.level(t)) if self.narration else None
        self.avatar = Avatar(rig, self.timeline, mouth_level=level, position=L.avatar_pos, scale=L.avatar_scale)
        self.avatar.set_z_index(12)
        self.add(self.avatar)

        n = len(self.plan_scenes)
        for i, scene in enumerate(self.plan_scenes):
            start_t = self.timeline.t
            win = max(0.5, self.boundaries[i + 1] - start_t)           # absolute targets: no frame-rounding drift
            s_i, e_i, _text = self.rows[i]
            cfg = {"narration": scene["text"], "pad_before": max(0.0, s_i - start_t), "narration_seconds": e_i - s_i}
            ctx = SceneContext(self, rig, self.avatar, self.timeline, win, i, cfg, fw, fh, start=start_t,
                               layout=L, lang=self.lang, is_last=(i == n - 1))
            kinds.render(ctx, scene)
            ctx.pad()
            for o in list(ctx.objects):
                o.clear_updaters()
                self.remove(o)
            ctx.objects.clear()
            self.avatar.look_at(None)
