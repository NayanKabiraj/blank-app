"""Writes assets/pip_speaking.gif: the presenter picture talking (lip-sync cycle + blink + a little sway). Run:
python -m generated_animations.avatar.make_gif"""
import math
from pathlib import Path

from PIL import Image

from . import face

OUT = Path(__file__).parent / "assets" / "pip_speaking.gif"


def main(fps: int = 15, seconds: float = 4.0, width: int = 360):
    f = face.get()
    frames = []
    for i in range(int(fps * seconds)):
        t = i / fps
        # a talking rhythm: syllables of varying loudness, with short closed pauses
        syl = abs(math.sin(t * 9.5)) * (0.55 + 0.45 * math.sin(t * 2.3)) if (t % 2.0) < 1.5 else 0.0
        blink = 1.0 if 2.55 < t < 2.72 else 0.0
        im = Image.fromarray(f.frame(syl, blink))
        canvas = Image.new("RGBA", im.size, (22, 27, 62, 255))
        sway = math.sin(t * 2 * math.pi / seconds * 2) * 1.5
        im = im.rotate(sway, resample=Image.BICUBIC, center=(im.width / 2, im.height * 0.9))
        canvas.alpha_composite(im)
        frames.append(canvas.convert("RGB").resize((width, int(width * im.height / im.width)), Image.LANCZOS))
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)


if __name__ == "__main__":
    main()
