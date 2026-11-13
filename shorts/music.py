"""Background music.

If you drop royalty-free tracks into assets/music/ (optionally in a sub-folder named after
the mood, e.g. assets/music/calm/), one is picked at random. Otherwise an original
copyright-free track is synthesized on the fly with numpy, so Content ID never flags it.
"""
from __future__ import annotations

import random
import wave
from pathlib import Path

import numpy as np

from . import config

SR = 44100
AUDIO_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}

# mood -> (bpm, root midi note, chord progression as scale degrees, minor?, drums?)
MOODS = {
    "calm":       (72,  57, [0, 5, 3, 4], False, False),
    "upbeat":     (112, 60, [0, 4, 5, 3], False, True),
    "dramatic":   (90,  50, [0, 5, 2, 6], True,  True),
    "inspiring":  (96,  55, [0, 4, 5, 3], False, True),
    "mysterious": (80,  52, [0, 1, 5, 4], True,  False),
}
MAJOR, MINOR = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]


def pick_track(mood: str) -> Path | None:
    for folder in (config.MUSIC_DIR / mood, config.MUSIC_DIR):
        if folder.is_dir():
            tracks = [p for p in folder.iterdir() if p.suffix.lower() in AUDIO_EXT]
            if tracks:
                return random.choice(tracks)
    return None


def _hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _tone(freq, n, harmonics=(1.0, 0.5, 0.25), detune=0.003):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, amp in enumerate(harmonics, start=1):
        for d in (-detune, detune):
            out += amp * np.sin(2 * np.pi * freq * k * (1 + d) * t + random.random() * 6.28)
    return out


def synthesize(mood: str, duration: float, out_wav: Path) -> Path:
    bpm, root, prog, minor, drums = MOODS.get(mood, MOODS["calm"])
    root += random.choice([-2, 0, 2, 3])
    scale = MINOR if minor else MAJOR
    beat = 60.0 / bpm
    bar_n = int(SR * beat * 4)
    total = int(SR * duration)
    left, right = np.zeros(total + bar_n), np.zeros(total + bar_n)
    rng = np.random.default_rng()

    def deg(d, octave=0):
        return root + scale[d % 7] + 12 * (d // 7 + octave)

    bar = 0
    while bar * bar_n < total:
        s = bar * bar_n
        d = prog[bar % len(prog)]
        chord = [deg(d), deg(d + 2), deg(d + 4)]
        # Soft pad with slow attack/release
        env = np.minimum(1, np.linspace(0, 4, bar_n)) * np.minimum(1, np.linspace(4, 0, bar_n) + 0.3)
        pad = sum(_tone(_hz(n), bar_n) for n in chord) * env * 0.05
        left[s:s + bar_n] += pad
        right[s:s + bar_n] += pad
        # Bass note on each half bar
        half = bar_n // 2
        for h in range(2):
            b = _tone(_hz(chord[0] - 12), half, (1.0, 0.3)) * np.exp(-np.linspace(0, 3, half)) * 0.12
            left[s + h * half:s + (h + 1) * half] += b
            right[s + h * half:s + (h + 1) * half] += b
        # Plucked arpeggio (8th notes), panned
        step = bar_n // 8
        for i in range(8):
            note = chord[[0, 1, 2, 1, 0, 2, 1, 2][i]] + 12 * (1 + (i % 4 == 3))
            p = _tone(_hz(note), step, (1.0, 0.2)) * np.exp(-np.linspace(0, 6, step)) * 0.06
            pan = 0.5 + 0.35 * np.sin(i)
            left[s + i * step:s + (i + 1) * step] += p * (1 - pan)
            right[s + i * step:s + (i + 1) * step] += p * pan
        # Light drums
        if drums and bar > 0:
            q = bar_n // 4
            kick_t = np.arange(int(SR * 0.25)) / SR
            kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-kick_t * 30)) * kick_t) * np.exp(-kick_t * 12) * 0.25
            hat = rng.standard_normal(int(SR * 0.04)) * np.exp(-np.linspace(0, 8, int(SR * 0.04))) * 0.03
            for i in range(4):
                o = s + i * q
                if i in (0, 2):
                    left[o:o + len(kick)] += kick
                    right[o:o + len(kick)] += kick
                for off in (0, q // 2):
                    left[o + off:o + off + len(hat)] += hat
                    right[o + off:o + off + len(hat)] += hat
        bar += 1

    stereo = np.stack([left[:total], right[:total]], axis=1)
    fade = int(SR * 1.5)
    stereo[:fade] *= np.linspace(0, 1, fade)[:, None]
    stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
    stereo /= max(1e-9, np.abs(stereo).max()) / 0.8
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2), wf.setsampwidth(2), wf.setframerate(SR)
        wf.writeframes((stereo * 32767).astype("<i2").tobytes())
    return out_wav
