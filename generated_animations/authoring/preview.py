"""Low-res preview of a plan's animation + one contact sheet of frames to inspect (replaces ad-hoc scripts).

    python -m generated_animations.authoring.preview plan.json --lang en            # Short, English  -> /tmp/ga_preview/<lang>/short_en.mp4 + sheet_en.png
    python -m generated_animations.authoring.preview plan.json --lang hi            # the Hindi twin (Devanagari text fit)
    python -m generated_animations.authoring.preview plan.json --lang en --doc      # documentary (landscape)
    python -m generated_animations.authoring.preview plan.json --sheet-only video.mp4

Uses fake narration timing (SHORTS_FAKE_TTS=1) and a small render scale (GA_PIXEL_SCALE=0.4): about 3-6 minutes for a Short. Open the printed sheet PNG with one image read: 12 frames
spread across the video; check overlaps, clipping, dead moments, text that does not fit (especially Hindi), beats that do not leave before the next one appears.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def contact_sheet(video: Path, out: Path, n: int = 12, width: int = 270, cols: int = 6) -> Path:
    from PIL import Image
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]))
    frames = []
    for i in range(1, n + 1):
        f = out.parent / f"_f{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(dur * (i + 0.3) / (n + 2)), "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:-1", str(f)], check=True)
        frames.append(Image.open(f).copy())
        f.unlink()
    w, h = frames[0].size
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows))
    for i, im in enumerate(frames):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--lang", default="en", choices=["en", "hi"])
    ap.add_argument("--doc", action="store_true")
    ap.add_argument("--out", default="/tmp/ga_preview")
    ap.add_argument("--sheet-only", default="")
    a = ap.parse_args()
    out_dir = Path(a.out) / a.lang
    out_dir.mkdir(parents=True, exist_ok=True)
    if a.sheet_only:
        print(contact_sheet(Path(a.sheet_only), out_dir / "sheet.png", width=400 if a.doc else 270, cols=4 if a.doc else 6))
        return 0
    os.environ.setdefault("SHORTS_FAKE_TTS", "1")
    os.environ.setdefault("GA_PIXEL_SCALE", "0.4")
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    from shorts import compose
    from shorts.plan import DocPlan, Plan
    t0 = time.time()
    text = Path(a.plan).read_text(encoding="utf-8")
    if a.doc:
        plan = DocPlan.model_validate_json(text)
        script = plan.english if a.lang == "en" else plan.hindi
        video, _ch = compose.build_documentary(script, a.lang, plan.mood, out_dir / "work", plan.niche)
    else:
        plan = Plan.model_validate_json(text)
        script = plan.english if a.lang == "en" else plan.hindi
        video = compose.build(script, a.lang, plan.mood, out_dir / "work", plan.niche)
    sheet = contact_sheet(Path(video), out_dir / f"sheet_{a.lang}.png", n=24 if a.doc else 12, width=400 if a.doc else 270, cols=4 if a.doc else 6)
    print(f"video: {video}\nsheet: {sheet}\n{round(time.time() - t0)} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
