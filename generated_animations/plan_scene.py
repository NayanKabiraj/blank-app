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
    def __init__(self, scenes, boundaries, timeline_rows, layout, lang, narration=None, shots=(), look="classic", **kwargs):
        self.plan_scenes, self.boundaries, self.rows = scenes, boundaries, timeline_rows
        self.shots = list(shots)
        self.layout, self.lang, self.narration, self.look = layout, lang, narration, look
        super().__init__(**kwargs)

    def construct(self):
        from manim import config
        L = self.layout
        vox = self.look == "vox"
        self.camera.background_color = "#EEE6D5" if vox else BG
        fw, fh = config.frame_width, config.frame_height
        self.timeline = Timeline(self)
        self.add(self.timeline.make_clock())
        rig = CameraRig(self)
        if vox:
            from .shared import vox as voxkit
            sky = voxkit.paper_bg(fw * 1.05, fh * 1.05, res=L.star_res)
            sky.set_z_index(-10)
            self.add(sky)
        else:
            sky = lighting.starfield(fw * 1.05, fh * 1.05, res=L.star_res)
            sky.set_z_index(-10)
            vig = lighting.vignette(fw, fh)
            vig.set_z_index(9)
            self.add(sky, vig)
        level = (lambda t: self.narration.level(t)) if self.narration else None
        self.avatar = Avatar(rig, self.timeline, mouth_level=level, position=L.avatar_pos, scale=L.avatar_scale, sticker=vox)
        self.avatar.set_z_index(12)
        self.add(self.avatar)

        n = len(self.plan_scenes)
        shots = {sh.scenes[0]: sh for sh in self.shots}
        in_shot = {i for sh in self.shots for i in sh.scenes}
        i = 0
        while i < n:
            group = shots[i].scenes if i in shots else [i]
            if i not in shots and i in in_shot:     # (cannot happen for a well-formed pack)
                i += 1
                continue
            first, last = group[0], group[-1]
            start_t = self.timeline.t
            win = max(0.5, self.boundaries[last + 1] - start_t)           # absolute targets: no frame-rounding drift
            subs = []
            for j in group:
                s_j, e_j, _t = self.rows[j]
                subs.append({"text": self.plan_scenes[j]["text"], "start": max(0.0, s_j - start_t), "end": e_j - start_t,
                             "graphic": self.plan_scenes[j].get("graphic")})
            cfg = {"narration": subs[0]["text"], "pad_before": subs[0]["start"], "narration_seconds": subs[0]["end"] - subs[0]["start"],
                   "subs": subs}
            ctx = SceneContext(self, rig, self.avatar, self.timeline, win, first, cfg, fw, fh, start=start_t,
                               layout=L, lang=self.lang, is_last=(last == n - 1), look=self.look)
            if i in shots:
                for k, sub in enumerate(subs):
                    nxt = subs[k + 1]["start"] if k + 1 < len(subs) else None
                    kinds.caption_track(ctx, sub["text"], sub["start"], sub["end"] - sub["start"], last_of_scene=(sub is subs[-1]),
                                        hide_at=nxt)
                shots[i].module.animate(ctx)
            else:
                kinds.render(ctx, self.plan_scenes[i])
            ctx.pad()
            for o in list(ctx.objects):
                o.clear_updaters()
                self.remove(o)
            ctx.objects.clear()
            self.avatar.look_at(None)
            i = last + 1
