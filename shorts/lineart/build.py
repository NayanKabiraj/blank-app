"""Render one line-art Short: narration (same TTS as every style, so the voices stay strict) -> cue times -> the scene page in headless Chromium, stepped one frame at a time
(`lineart/scripts/capture.ts`) -> captions -> ducked music mix. The scene reads its timing from the URL (`cues`, `durs`, `total`), so the picture follows the voice."""
from __future__ import annotations

import logging
import math
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import compose, config, outro
from ..director import build as dbuild
from ..stockreel import render as sr

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2] / "lineart"
PORT = 5199
FPS = 30
MOODS = {"calm", "upbeat", "dramatic", "inspiring", "mysterious"}


def scene_dir(scene_id: str) -> Path:
    return ROOT / "scenes" / scene_id


def scene_exists(scene_id: str) -> bool:
    d = scene_dir(scene_id)
    return bool(scene_id) and (d / "index.html").exists() and any(d.glob("*.ts"))


def _chrome() -> str:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    r = subprocess.run(["node", "-e", "import('playwright').then(m=>console.log(m.chromium.executablePath()))"], cwd=ROOT, capture_output=True, text=True)
    path = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    if not path or not Path(path).exists():
        for guess in ("/opt/pw-browsers/chromium", "/usr/bin/chromium", "/usr/bin/google-chrome"):
            if Path(guess).exists():
                return guess
        raise RuntimeError("no Chromium found for the line-art renderer (run `npx playwright install --with-deps chromium` in lineart/)")
    return path


class Server:
    """The scene dev server (vite) for the duration of a render. ANY HTTP answer (even a 404) means it is up; on failure the server's own log is raised with the error."""

    def __init__(self, probe: str = "/lib/ink.ts", log_path: Path | None = None):
        self.probe = probe
        self.log_path = log_path or (Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "lineart_vite.log")

    def __enter__(self):
        if not (ROOT / "node_modules").exists():
            subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=ROOT, check=True)
        self._log = open(self.log_path, "w")
        self.p = subprocess.Popen(["npx", "vite", "--port", str(PORT), "--host", "127.0.0.1", "--strictPort"], cwd=ROOT, stdout=self._log, stderr=subprocess.STDOUT)
        for _ in range(120):
            if self.p.poll() is not None:
                break
            try:
                urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}{self.probe}"), timeout=2)
                return self
            except urllib.error.HTTPError:
                return self                     # the server answered
            except Exception:  # noqa: BLE001
                time.sleep(0.5)
        self._log.flush()
        tail = self.log_path.read_text(errors="replace")[-1500:]
        self.p.terminate()
        raise RuntimeError(f"the line-art dev server did not start (exit {self.p.poll()}). vite log:\n{tail}")

    def __exit__(self, *a):
        self.p.terminate()
        self._log.close()


def url_for(scene_id: str, cues: list[float], durs: list[float], total: float) -> str:
    j = lambda xs: ",".join(f"{x:.3f}" for x in xs)
    return f"http://127.0.0.1:{PORT}/scenes/{scene_id}/?debug&capture&cues={j(cues)}&durs={j(durs)}&total={total:.3f}"


def capture(scene_id: str, cues, durs, total: float, frames_dir: Path) -> int:
    n = math.ceil(total * FPS)
    frames_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "CHROME": _chrome()}
    with Server():
        subprocess.run(["node", "scripts/capture.ts", url_for(scene_id, cues, durs, total), str(frames_dir), str(n), str(FPS), "1080", "1920"], cwd=ROOT, env=env, check=True)
    return n


def build_short(script, lang: str, mood: str, work: Path, scene_id: str) -> tuple[Path, Path]:
    """Returns (video path, a frame picked for the thumbnail)."""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    voice, timeline, voice_end = compose._voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    cues = [s for s, _e, _t in timeline]
    durs = [e - s for s, e, _t in timeline]
    frames = work / "frames"
    n = capture(scene_id, cues, durs, total, frames)
    silent = work / "silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.png"), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-tune", "animation", "-movflags", "+faststart", str(silent)], check=True)
    chunks = dbuild.caption_chunks({"captions": {"maximumWordsPerCaption": 5}, "scenes": [
        {"narration": {"text": sc.text, "startSeconds": s, "endSeconds": e}} for sc, (s, e, _t) in zip(script.scenes, timeline)]}, lang)
    srt = work / "captions.srt"
    dbuild.srt(chunks, srt)
    sr._burn_captions(silent, srt, work / "video.mp4", work, False)
    thumb_frame = work / "thumb_frame.png"
    shutil.copy2(frames / f"f{int(n * 0.74):04d}.png", thumb_frame)
    out = work / f"lineart_{lang}.mp4"
    compose._mix(work, voice, total, mood if mood in MOODS else "mysterious", out)
    shutil.rmtree(frames, ignore_errors=True)
    return out, thumb_frame
