"""The presenter Pip is the owner's own picture (assets/pip_base.png, transparent backdrop). This module animates it: lip-sync mouth
shapes and eye blinks are painted over the picture, the rest (nodding, tilting, leaning toward what he points at) is done by moving the
whole picture. Coordinates below are pixels of the ORIGINAL picture (assets/pip_source.jpg); P() maps them into the cut-out.
`Face.frame(mouth, blink)` returns an RGBA numpy array."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ASSETS = Path(__file__).parent / "assets"
BASE = ASSETS / "pip_base.png"
SS = 3                                                   # supersampling for the painted shapes
H_OPEN = [0, 10, 20, 32, 44, 56, 68]                     # mouth opening (source px) for the lip-sync levels
W_OPEN = [1.0, 0.99, 0.96, 0.92, 0.88, 0.84, 0.8]
LEVELS = len(H_OPEN)
# the picture's smile: the underside of the upper lip (x, y), left corner -> right corner
LIP = [(440, 966), (480, 978), (530, 984), (580, 982), (630, 972), (680, 958), (708, 948)]
EYES = {"L": (418, 717, 62, 30), "R": (703, 718, 62, 30)}  # eye centre x, y and half width, half height (source px)


class Face:
    def __init__(self):
        meta = json.loads((ASSETS / "pip_meta.json").read_text())
        self.ox, self.oy, self.k = meta["ox"], meta["oy"], meta["scale"]
        self.base = Image.open(BASE).convert("RGBA")
        self.size = self.base.size
        self.mouths = [self._mouth(i) for i in range(1, LEVELS)]
        self.lids = {side: [self._lid(side, f) for f in (0.55, 1.0)] for side in EYES}

    def P(self, x, y):
        return ((x - self.ox) * self.k * SS, (y - self.oy) * self.k * SS)

    def _layer(self):
        return Image.new("RGBA", (self.size[0] * SS, self.size[1] * SS), (0, 0, 0, 0))

    def _finish(self, layer, blur=0.0):
        out = layer.resize(self.size, Image.LANCZOS)
        return out.filter(ImageFilter.GaussianBlur(blur)) if blur else out

    @staticmethod
    def _curve(pts, n=40):
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        gx = np.linspace(xs[0], xs[-1], n)
        return gx, np.interp(gx, xs, ys)

    def _mouth(self, i: int):
        h, wf = H_OPEN[i], W_OPEN[i]
        gx, gy = self._curve(LIP)
        mid = (gx[0] + gx[-1]) / 2
        half = (gx[-1] - gx[0]) / 2
        keep = np.abs(gx - mid) <= half * wf
        gx, gy = gx[keep], gy[keep]
        u = (gx - mid) / (half * wf)
        depth = h * np.clip(1 - u * u, 0, 1) ** 0.6
        im = self._layer()
        d = ImageDraw.Draw(im)
        lip_col = (196, 118, 96, 255)                                         # the picture's lower-lip colour
        # lower lip: a band under the cavity (repaints chin skin/beard a little lower)
        band = [self.P(x, y + dd - 2) for x, y, dd in zip(gx, gy, depth)] + [self.P(x, y + dd + 30 + 0.2 * h) for x, y, dd in zip(gx[::-1], gy[::-1], depth[::-1])]
        d.polygon(band, fill=lip_col)
        # cavity
        cav = [self.P(x, y - 1) for x, y in zip(gx, gy)] + [self.P(x, y + dd) for x, y, dd in zip(gx[::-1], gy[::-1], depth[::-1])]
        d.polygon(cav, fill=(58, 20, 22, 255))
        if h >= 10:                                                           # upper teeth
            th = min(15.0, 6 + h * 0.18)
            t = [self.P(x, y - 1) for x, y in list(zip(gx, gy))[3:-3]] + [self.P(x, y + th * np.clip(1 - uu * uu, 0, 1) ** 0.4)
                                                                         for x, y, uu in list(zip(gx, gy, u))[3:-3][::-1]]
            d.polygon(t, fill=(246, 244, 240, 255))
        if h >= 34:                                                           # tongue
            cx = mid + 8
            cy = float(np.interp(cx, gx, gy)) + h * 0.8
            x0, y0 = self.P(cx - 46, cy - 14)
            x1, y1 = self.P(cx + 46, cy + 10)
            d.ellipse((x0, y0, x1, y1), fill=(196, 96, 98, 255))
        return self._finish(im, 0.6)

    def _sample(self, sx, sy):
        px = np.asarray(self.base)
        x, y = int((sx - self.ox) * self.k), int((sy - self.oy) * self.k)
        return tuple(int(v) for v in px[y - 1:y + 2, x - 1:x + 2, :3].reshape(-1, 3).mean(0))

    def _lid(self, side, frac):
        cx, cy, ew, eh = EYES[side]
        im = self._layer()
        d = ImageDraw.Draw(im)
        col = self._sample(cx, cy + 42) + (255,)                              # skin just under the eye
        top = cy - eh - 4
        bottom = top + (2 * eh + 10) * frac
        d.ellipse((*self.P(cx - ew, top), *self.P(cx + ew, bottom)), fill=col)
        a, b = self.P(cx - ew + 6, bottom - 22), self.P(cx + ew - 6, bottom + 8)
        d.arc((*a, *b), 15, 165, fill=(38, 26, 24, 255), width=int(3.5 * SS))
        return self._finish(im, 2.2)

    def frame(self, mouth: float = 0.0, blink: float = 0.0, sticker: bool = False) -> np.ndarray:
        """mouth 0..1 (0 = the picture's own closed smile), blink 0..1 (1 = shut). sticker=True adds a white paper-cut border and a soft shadow (the vox look)."""
        im = self.base.copy()
        lv = int(round(max(0.0, min(1.0, mouth)) * (LEVELS - 1)))
        if lv > 0:
            im.alpha_composite(self.mouths[lv - 1])
        if blink > 0.08:
            k = 0 if blink < 0.6 else 1
            for side in EYES:
                im.alpha_composite(self.lids[side][k])
        if sticker:
            im = _sticker(im)
        return np.asarray(im)


def _sticker(im: Image.Image, border: int = 7, pad: int = 16) -> Image.Image:
    """White cut-out border + drop shadow around the picture's alpha."""
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.split()[3], (pad, pad))
    edge = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(1.0))
    shadow = Image.new("RGBA", out.size, (34, 30, 28, 0))
    shadow.putalpha(edge.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.4)))
    out.alpha_composite(shadow, (4, 6))
    white = Image.new("RGBA", out.size, (255, 253, 245, 255))
    white.putalpha(edge)
    out.alpha_composite(white)
    out.alpha_composite(im, (pad, pad))
    return out


@lru_cache(maxsize=1)
def get() -> Face:
    return Face()
