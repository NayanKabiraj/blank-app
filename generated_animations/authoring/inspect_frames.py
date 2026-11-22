"""Visual feedback loop helpers: extract frames, run automated checks, build a contact sheet.

Automated checks (NumPy/Pillow) catch what code success cannot: blank/near-empty frames, content clipped at
the frame edge, a frame that is dead static, and left/right or top/bottom imbalance. They do not replace
looking: the contact sheet is written so a human (or Claude, via the image viewer) can check the frames,
and every report says manual_review_needed.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def extract_frames(video: Path, out_dir: Path, times: list[float]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, t in enumerate(times):
        p = out_dir / f"frame_{i:02d}_{t:05.1f}s.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(p)], check=True)
        if p.exists():
            paths.append(p)
    return paths


def check_frame(path: Path) -> dict:
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    lum = a.mean(axis=2)
    h, w = lum.shape
    bg = np.median(lum[: h // 20])
    ink = np.abs(lum - bg) > 28
    cover = float(ink.mean())
    edge = max(ink[:3].mean(), ink[-3:].mean(), ink[:, :3].mean(), ink[:, -3:].mean())
    ys, xs = np.nonzero(ink)
    cx = float(xs.mean() / w - 0.5) if len(xs) else 0.0
    cy = float(ys.mean() / h - 0.5) if len(ys) else 0.0
    issues = []
    if lum.std() < 6:
        issues.append("blank_frame")
    if cover < 0.02:
        issues.append("almost_empty")
    return {"frame": path.name, "ink_coverage": round(cover, 3), "edge_ink": round(float(edge), 3),
            "balance_x": round(cx, 3), "balance_y": round(cy, 3), "issues": issues}


def check_motion(paths: list[Path]) -> list[str]:
    issues = []
    imgs = [np.asarray(Image.open(p).convert("L"), dtype=np.float32) for p in paths]
    for i in range(1, len(imgs)):
        if np.abs(imgs[i] - imgs[i - 1]).mean() < 0.4:
            issues.append(f"frames {i - 1}->{i} nearly identical (static?)")
    return issues


def contact_sheet(paths: list[Path], out: Path, cols: int = 5, thumb_w: int = 216) -> Path:
    ims = [Image.open(p).convert("RGB") for p in paths]
    th = int(thumb_w * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (th + 16)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x, y = (i % cols) * thumb_w, (i // cols) * (th + 16)
        sheet.paste(im.resize((thumb_w, th)), (x, y + 16))
        d.text((x + 3, y + 2), paths[i].stem.replace("frame_", ""), fill=(255, 255, 255))
    sheet.save(out)
    return out


def inspect_video(video: Path, out_dir: Path, every: float = 2.0) -> dict:
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).decode())
    times = list(np.arange(0.5, dur - 0.1, every))
    frames = extract_frames(video, out_dir, [float(t) for t in times])
    reports = [check_frame(p) for p in frames]
    problems = [f"{r['frame']}: {i}" for r in reports for i in r["issues"]]
    problems += [f"{r['frame']}: content touches frame edge ({r['edge_ink']})" for r in reports if r["edge_ink"] > 0.35]
    problems += check_motion(frames)
    sheet = contact_sheet(frames, out_dir / "contact_sheet.png")
    return {"frames": reports, "problems": problems, "contact_sheet": str(sheet), "manual_review_needed": True}
