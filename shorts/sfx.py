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
            cues.append((rev, "bell"))
        elif kind == "myth":                             # the myth is struck out, the fact stamps in
            strike = start + max(1.0, (hit - start) if hit else (end - start) * 0.42)
            cues += [(strike, "pop"), (strike + 0.35, "pop")]
        else:                                            # diagrams: flow, steps, build, cycle, race, compare, bars
            cues.append((start + 0.12, "pop"))
        if hit:
            cues.append((hit - 0.03, "bell"))
    return [(t, k) for t, k in sorted(cues) if t >= 0]


def build(cfg_path: Path, total: float, out: Path, volume: float = 0.35) -> Path | None:
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
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
