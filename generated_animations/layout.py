"""Screen layouts for plan-driven rendering (a Short is vertical 9x16 units, a documentary landscape 16x9)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Layout:
    name: str
    frame_w: float
    frame_h: float
    headline_y: float
    headline_w: float
    stage_center: tuple
    stage_w: float
    stage_h: float
    caption_y: float
    caption_x: float
    caption_w: float
    caption_chars: int
    caption_size: int
    avatar_pos: tuple
    avatar_scale: float
    pixels: tuple          # (width, height) of the final picture
    star_res: tuple

    @property
    def landscape(self) -> bool:
        return self.frame_w > self.frame_h


VERTICAL = Layout("vertical", 9.0, 16.0, 6.8, 7.4, (0.0, 1.9), 8.0, 7.0, -2.9, 0.0, 8.0, 34, 32,
                  (-2.6, -8.0), 0.92, (1080, 1920), (540, 960))
LANDSCAPE = Layout("landscape", 16.0, 9.0, 3.75, 13.0, (1.9, 0.35), 11.0, 5.3, -3.35, 1.9, 11.5, 54, 34,
                   (-6.1, -4.0), 0.62, (1280, 720), (960, 540))
