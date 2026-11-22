"""The presenter Pip is the owner's own picture (assets/pip_base.png). This module animates it: lip-sync mouth shapes and eye blinks are
drawn over the picture (same art style: flat fills, dark-red lips), the rest (nodding, tilting, leaning toward what he points at) is
done by moving the whole picture. `Face.frame(mouth, blink, tilt, ...)` returns an RGBA numpy array."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BASE = Path(__file__).parent / "assets" / "pip_base.png"
SS = 4                                   # supersampling for the painted shapes
MOUTH_C, MOUTH_HALF, MOUTH_Y0, SAG = 291.0, 78.0, 516.0, 17.0     # the picture's own smile: ends at y 516, sags to 533 in the middle
H_OPEN = [0, 6, 12, 19, 26, 33, 40]      # mouth heights for the lip-sync levels
W_OPEN = [1.0, 0.98, 0.92, 0.86, 0.80, 0.74, 0.70]
LEVELS = len(H_OPEN)
EYES = {"L": (198, 400, 42, 33), "R": (373, 395, 42, 33)}        # centre x, y, half width, half height of the eye whites


def _curve(x):
    u = (x - MOUTH_C) / MOUTH_HALF
    return MOUTH_Y0 + SAG * (1 - u * u)


class Face:
    def __init__(self):
        self.base = Image.open(BASE).convert("RGBA")
        self.size = self.base.size
        self.mouths = [self._mouth(i) for i in range(1, LEVELS)]
        self.lids = {side: [self._lid(side, f) for f in (0.55, 1.0)] for side in EYES}

    # -- overlays ----------------------------------------------------------------------
    def _layer(self):
        return Image.new("RGBA", (self.size[0] * SS, self.size[1] * SS), (0, 0, 0, 0))

    def _finish(self, layer):
        return layer.resize(self.size, Image.LANCZOS)

    def _mouth(self, i: int):
        h, wf = H_OPEN[i], W_OPEN[i]
        im = self._layer()
        d = ImageDraw.Draw(im)
        xs = np.linspace(MOUTH_C - MOUTH_HALF * wf, MOUTH_C + MOUTH_HALF * wf, 60)
        top = [(x * SS, (_curve(x) - 4) * SS) for x in xs]
        bot = [(x * SS, (_curve(x) + h * max(0.0, 1 - ((x - MOUTH_C) / (MOUTH_HALF * wf)) ** 2) ** 0.7) * SS) for x in xs[::-1]]
        poly = top + bot
        d.polygon(poly, fill=(78, 22, 34, 255))
        if h >= 12:                                                   # upper teeth
            th = min(9.0, h * 0.42)
            tt = [(x * SS, (_curve(x) - 1) * SS) for x in xs[6:-6]]
            tb = [(x * SS, (_curve(x) - 1 + th * max(0.0, 1 - ((x - MOUTH_C) / (MOUTH_HALF * wf)) ** 2) ** 0.5) * SS) for x in xs[6:-6][::-1]]
            d.polygon(tt + tb, fill=(250, 246, 240, 255))
        if h >= 26:                                                   # tongue
            cx, cy = MOUTH_C, _curve(MOUTH_C) + h * 0.78
            d.ellipse(((cx - 28) * SS, (cy - 9) * SS, (cx + 28) * SS, (cy + 6) * SS), fill=(205, 92, 104, 255))
        d.line(top, fill=(176, 40, 66, 255), width=int(3.2 * SS), joint="curve")        # the red lip line stays on top
        return self._finish(im)

    def _skin(self, side):
        cx, cy, _, _ = EYES[side]
        px = np.asarray(self.base)
        return tuple(int(v) for v in px[cy + 44, cx, :3])               # lens colour just below the eye

    def _lid(self, side, frac):
        cx, cy, ew, eh = EYES[side]
        im = self._layer()
        d = ImageDraw.Draw(im)
        col = self._skin(side) + (255,)
        top = cy - eh - 6
        bottom = top + (2 * eh + 12) * frac
        d.ellipse(((cx - ew - 6) * SS, top * SS, (cx + ew + 6) * SS, bottom * SS), fill=col)
        d.arc(((cx - ew) * SS, (bottom - 30) * SS, (cx + ew) * SS, (bottom + 6) * SS), 20, 160, fill=(40, 28, 28, 255), width=int(4 * SS))
        return self._finish(im)

    # -- a frame -----------------------------------------------------------------------
    def frame(self, mouth: float = 0.0, blink: float = 0.0) -> np.ndarray:
        """mouth 0..1 (0 = the picture's own closed smile), blink 0..1 (1 = shut)."""
        im = self.base.copy()
        lv = int(round(max(0.0, min(1.0, mouth)) * (LEVELS - 1)))
        if lv > 0:
            im.alpha_composite(self.mouths[lv - 1])
        if blink > 0.08:
            k = 0 if blink < 0.6 else 1
            for side in EYES:
                im.alpha_composite(self.lids[side][k])
        return np.asarray(im)


@lru_cache(maxsize=1)
def get() -> Face:
    return Face()
