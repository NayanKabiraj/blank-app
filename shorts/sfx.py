"""Sound effects synthesized in code, placed on the animation's own cues.

Cue times come from the renderer's timeline (work/timeline.json): a pop when a diagram, chat bubble, quiz
answer or number lands, and a soft bell on each scene's keyword. Everything is generated with numpy (no downloaded sounds), deterministic, and mixed
quietly under the voice by compose.py.
"""
from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np

SR = 44100


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(0, t - attack) / decay)


def pop() -> np.ndarray:
    n = int(SR * 0.14)
    t = np.arange(n) / SR
    freq = 900 * np.exp(-t * 28) + 220
    phase = 2 * np.pi * np.cumsum(freq) / SR
    return np.sin(phase) * _env(n, 0.002, 0.045) * 0.9


def bell() -> np.ndarray:
    n = int(SR * 0.7)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 1318.5 * t) + 0.45 * np.sin(2 * np.pi * 1975.5 * t)
            + 0.2 * np.sin(2 * np.pi * 2637 * t))
    return tone * _env(n, 0.003, 0.22) * 0.35


def cues_from_timeline(cfg: dict) -> list[tuple[float, str]]:
    """Mirror the cue times used by shorts/explainer/scene.js."""
    cues = []
    intro, outro = 0.6, 0.3
    for s in cfg.get("segments", []):
        g = s.get("graphic") or {}
        kind, hit, start, end, n = g.get("kind"), s.get("hit"), s["start"], s["end"], len(g.get("items") or [])
        if kind in ("title", "keyword"):
            cues.append(((max(start + 0.05, hit - 0.6) if hit else start + 0.1) + 0.1, "pop"))
        elif kind == "stat":
            c0 = max(start, hit - 1.5) if hit else start
            cues.append((c0 + 1.4, "pop"))
        elif kind == "chat" and n:                       # one pop per bubble
            t0, step = start + intro * 0.8, max(1.2, end - outro - (start + intro * 0.8)) / (n + 0.4)
            cues += [(t0 + j * step, "pop") for j in range(min(n, 4))]
        elif kind == "quiz" and n:                       # options land, then the answer is revealed
            cues.append((start + intro, "pop"))
            rev = min(end - 0.9, max(start + 2.0, hit if hit and hit > start + 2.0 else start + (end - start) * 0.68))
            cues.append((rev, "pop"))
        elif kind == "myth":                             # the myth is struck out, the fact stamps in
            strike = start + max(1.0, (hit - start) if hit else (end - start) * 0.42)
            cues += [(strike, "pop"), (strike + 0.35, "pop")]
        else:                                            # diagrams: flow, steps, build, cycle, race, compare, bars
            cues.append((start + 0.12, "pop"))
        # (no chime on the keyword: it was annoying; the caption highlight carries the emphasis)
    return [(t, k) for t, k in sorted(cues) if t >= 0]


def build(cfg_path: Path, total: float, out: Path, volume: float = 0.35) -> Path | None:
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    sounds = {"pop": pop()}
    track = np.zeros(int(SR * (total + 1)))
    for t, kind in cues_from_timeline(cfg):
        snd = sounds[kind]
        a = int(t * SR)
        b = min(len(track), a + len(snd))
        if a < b:
            track[a:b] += snd[: b - a]
    track = np.clip(track * volume, -1, 1)
    pcm = (track * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out


# ---------------------------------------------------------------- director mode: cue-based effects
def impact() -> np.ndarray:
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t * 6) + 38) / SR) * np.exp(-t * 4.5)
    rng = np.random.default_rng(7)
    crack = rng.standard_normal(n) * np.exp(-t * 30) * 0.5
    return (thump * 0.9 + crack) * 0.8


def riser(length: float = 1.6) -> np.ndarray:
    n = int(SR * length)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / length) ** 2) / SR)
    env = (t / length) ** 2.2
    return (noise * 0.25 + sweep * 0.6) * env * 0.55


def digital() -> np.ndarray:
    n = int(SR * 0.5)
    out = np.zeros(n)
    for k, f in enumerate((880, 1320, 1760, 1320)):
        a, m = int(k * 0.07 * SR), int(0.06 * SR)
        tt = np.arange(m) / SR
        out[a:a + m] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 35) * 0.5
    return out


def whoosh(length: float = 0.7) -> np.ndarray:
    n = int(SR * length)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    noise = rng.standard_normal(n)
    k = np.exp(-((t - length * 0.55) ** 2) / (2 * (length * 0.2) ** 2))
    # crude band-pass sweep: moving average whose width shrinks as the whoosh peaks
    sm = np.convolve(noise, np.ones(24) / 24, mode="same")
    return (0.55 * sm + 0.25 * noise * k) * k


def pulse() -> np.ndarray:
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 120 * t) * np.exp(-t * 11) * 0.7


def sub() -> np.ndarray:
    n = int(SR * 1.0)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 48 * t) * np.exp(-t * 3) * 0.8


def click() -> np.ndarray:
    n = int(SR * 0.06)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) * 0.4


KINDS = {"impact": impact, "riser": riser, "digital": digital, "scan": digital, "assembly": digital, "whoosh": whoosh,
         "transition": whoosh, "pulse": pulse, "sub": sub, "bass": sub, "click": click}


def kind_for(asset_id: str):
    """Pick a synthesizer from an asset id such as 'impact-deep-01' or 'riser-short-01' (no asset files are needed)."""
    a = (asset_id or "").lower()
    for key, fn in KINDS.items():
        if key in a:
            return fn
    return pulse


def build_cues(cues: list[tuple[float, str, float]], total: float, out: Path, volume: float = 0.5) -> Path | None:
    """cues = [(second, assetId, gain 0..1)] -> one wav track."""
    if not cues:
        return None
    track = np.zeros(int(SR * (total + 2)))
    cache: dict = {}
    for t, asset, gain in cues:
        fn = kind_for(asset)
        snd = cache.setdefault(fn, fn())
        a = int(max(0.0, t) * SR)
        b = min(len(track), a + len(snd))
        if a < b:
            track[a:b] += snd[: b - a] * gain
    track = np.clip(track * volume, -1, 1)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())
    return out
