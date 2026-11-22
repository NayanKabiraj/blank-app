"""One-off: cut the presenter picture (assets/pip_source.jpg, supplied by the owner) out of its white backdrop and halve its size
-> assets/pip_base.png + assets/pip_meta.json (crop offset + scale, so face.py can address the picture in source pixels).
Run:  python -m generated_animations.avatar.make_assets   (the result is committed; not needed at render time)."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

A = Path(__file__).parent / "assets"
SCALE = 0.5


def main():
    im = Image.open(A / "pip_source.jpg").convert("RGB").crop((0, 0, 1080, 1548))   # the strip below is a screenshot overlay
    a = np.asarray(im).astype(int)
    cand = (a.min(2) > 236) & ((a.max(2) - a.min(2)) < 14)      # near-white, unsaturated = the backdrop
    H, W = cand.shape
    seen = np.zeros((H, W), bool)
    stack = [(y, x) for y in range(H) for x in (0, W - 1) if cand[y, x]] + [(0, x) for x in range(W) if cand[0, x]]
    for p in stack:
        seen[p] = True
    while stack:                                                  # flood fill from the border: only the OUTSIDE is removed
        y, x = stack.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and cand[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    alpha = Image.fromarray(((~seen) * 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    bb = out.getbbox()
    out = out.crop(bb)
    out = out.resize((round(out.width * SCALE), round(out.height * SCALE)), Image.LANCZOS)
    out.save(A / "pip_base.png")
    (A / "pip_meta.json").write_text(json.dumps({"ox": bb[0], "oy": bb[1], "scale": SCALE}))
    print(bb, out.size)


if __name__ == "__main__":
    main()
