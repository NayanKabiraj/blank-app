"""Sound effects synthesized in code, placed on the animation's own cues.

Cue times come from the renderer's timeline (work/cartoon.json): a pop when a thought bubble, diagram board or number lands, and a soft bell on each scene's
keyword. Everything is generated with numpy (no downloaded sounds), deterministic, and mixed
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


def whoosh(rng) -> np.ndarray:
    n = int(SR * 0.42)
    noise = rng.standard_normal(n)
    # one-pole low-pass with a cutoff sweeping up then down: air rushing past
    t = np.linspace(0, 1, n)
    cutoff = 300 + 5200 * np.sin(np.pi * t) ** 2
    alpha = 1 - np.exp(-2 * np.pi * cutoff / SR)
    out = np.empty(n)
    y = 0.0
    for i in range(n):
        y += alpha[i] * (noise[i] - y)
        out[i] = y
    out = out * np.sin(np.pi * t) ** 1.5
    return out / (np.abs(out).max() + 1e-9) * 0.55


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
    """Mirror the cue times used by shorts/cartoon2d/scene.js."""
    cues = []
    segs = cfg.get("segments", [])
    for i, s in enumerate(segs):
        g = s.get("graphic") or {}
        kind, hit, start, end = g.get("kind"), s.get("hit"), s["start"], s["end"]
        if kind in ("title", "keyword"):
            cues.append(((max(start + 0.05, hit - 0.6) if hit else start + 0.1) + 0.1, "pop"))
        elif kind in ("flow", "race", "build", "cycle"):
            cues.append((start + 0.12, "pop"))
        elif kind == "stat":
            c0 = max(start, hit - 1.5) if hit else start
            cues.append((c0 + 1.4, "pop"))
        if hit:
            cues.append((hit - 0.03, "bell"))
    return [(t, k) for t, k in cues if t >= 0]


def build(cfg_path: Path, total: float, out: Path, volume: float = 0.35) -> Path | None:
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    rng = np.random.default_rng(7)
    sounds = {"pop": pop(), "bell": bell()}
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
