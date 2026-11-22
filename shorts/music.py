"""Background music.

Default: an original track synthesized with numpy ("classic" style, mood "inspiring") - no downloaded audio, so it cannot be a copyrighted
recording. (Old text, only used with MUSIC_LIBRARY=on:) If you drop royalty-free tracks into assets/music/ (optionally in a sub-folder named after
the mood, e.g. assets/music/calm/), one is picked at random. Otherwise an original
copyright-free track is synthesized on the fly with numpy, so Content ID never flags it.
"""
from __future__ import annotations

import math
import os
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
    """Third-party tracks from assets/music/ are IGNORED unless MUSIC_LIBRARY=on, so by default every video's music is the
    original code-generated track below (no samples, no recordings, no downloaded audio: nothing for Content ID to match)."""
    if os.getenv("MUSIC_LIBRARY", "off").strip().lower() != "on":
        return None
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


def _reverb(sig: np.ndarray, seconds: float = 2.4, wet: float = 0.38, seed: int = 21) -> np.ndarray:
    """Stereo reverb by FFT convolution with a decaying-noise impulse response (no extra dependencies)."""
    rng = np.random.default_rng(seed)
    n = int(SR * seconds)
    t = np.arange(n) / SR
    out = np.zeros_like(sig)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t / (seconds / 4.5))
        ir = np.convolve(ir, np.ones(6) / 6, mode="same")           # soften the highs
        ir[: int(SR * 0.012)] *= np.linspace(0, 1, int(SR * 0.012))  # tiny pre-delay ramp
        size = len(sig) + n
        spec = np.fft.rfft(sig[:, ch], size) * np.fft.rfft(ir, size)
        out[:, ch] = np.fft.irfft(spec, size)[: len(sig)]
    out /= max(1e-9, np.abs(out).max()) / max(1e-9, np.abs(sig).max())
    return sig * (1 - wet) + out * wet


def _lowpass(x: np.ndarray, k: int) -> np.ndarray:
    return np.convolve(x, np.ones(k) / k, mode="same")


def _pad_voice(freq: float, n: int, detune=(0.996, 1.0, 1.004)) -> np.ndarray:
    """A warm, slightly detuned pad voice: a few harmonics, low-passed so nothing sparkles or rings."""
    t = np.arange(n) / SR
    v = np.zeros(n)
    for d in detune:
        for h, a in ((1, 1.0), (2, 0.35), (3, 0.16), (4, 0.07)):
            v += a * np.sin(2 * np.pi * freq * d * h * t + h)
    return _lowpass(v, 3) / len(detune)


def synthesize_ambient(mood: str, duration: float, out_wav: Path) -> Path:
    """Warm evolving pads, a deep sub, slow shimmer and a soft room reverb: no plucks, no drums, nothing that pings."""
    bpm, root, prog, minor, _drums = MOODS.get(mood, MOODS["calm"])
    root += random.choice([-2, 0, 2, 3]) - 12
    scale = MINOR if minor else MAJOR
    hold = 4 * 60.0 / bpm * 2                     # each chord lasts two bars
    n_chord = int(SR * hold)
    fade = int(SR * min(2.5, hold * 0.45))
    total = int(SR * duration)
    left, right = np.zeros(total + n_chord + fade), np.zeros(total + n_chord + fade)

    def deg(d, octave=0):
        return root + scale[d % 7] + 12 * (d // 7 + octave)

    k = 0
    while k * n_chord < total:
        s = k * n_chord
        d = prog[(k + k // 8) % len(prog)]
        notes = [deg(d, 1), deg(d + 2, 1), deg(d + 4, 1), deg(d + 7, 1)]
        n = n_chord + fade                          # overlap with the next chord for a seamless blend
        env = np.minimum(1, np.linspace(0, 1, n) * (n / fade)) * np.minimum(1, np.linspace(1, 0, n) * (n / fade))
        for j, nt in enumerate(notes):
            v = _pad_voice(_hz(nt), n) * env * 0.05
            pan = 0.5 + 0.3 * math.sin(j * 1.7 + k)
            left[s:s + n] += v * (1 - pan) * 1.6
            right[s:s + n] += v * pan * 1.6
        sub = np.sin(2 * np.pi * _hz(deg(d, -1)) * np.arange(n) / SR) * env * 0.16      # deep sub
        left[s:s + n] += sub
        right[s:s + n] += sub
        # a high, very quiet shimmer an octave above the pad: it breathes, it never pings
        sh = _pad_voice(_hz(deg(d + 4, 3)), n, (0.998, 1.002)) * env * 0.012 * (0.6 + 0.4 * np.sin(np.arange(n) / SR * 0.7))
        left[s:s + n] += sh
        right[s:s + n] += sh[::-1] * 0.8
        k += 1
    stereo = np.stack([left[:total], right[:total]], axis=1)
    # slow breathing of the whole bed
    swell = 0.9 + 0.1 * np.sin(2 * np.pi * np.arange(total) / SR / 11.0)
    stereo *= swell[:, None]
    stereo = _reverb(stereo)
    f = int(SR * 2.0)
    stereo[:f] *= np.linspace(0, 1, f)[:, None]
    stereo[-f:] *= np.linspace(1, 0, f)[:, None]
    stereo /= max(1e-9, np.abs(stereo).max()) / 0.8
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2), wf.setsampwidth(2), wf.setframerate(SR)
        wf.writeframes((stereo * 32767).astype("<i2").tobytes())
    return out_wav


def synthesize(mood: str, duration: float, out_wav: Path) -> Path:
    """The background track, always generated in code. MUSIC_MOOD (default "inspiring") is used for every video; set MUSIC_MOOD=plan to
    follow each plan's own mood. MUSIC_STYLE=classic (default: the pad + plucked-arpeggio + light drums track) or ambient (warm pads only)."""
    chosen = os.getenv("MUSIC_MOOD", "inspiring").strip().lower()
    if chosen != "plan":
        mood = chosen if chosen in MOODS else "inspiring"
    if os.getenv("MUSIC_STYLE", "classic").strip().lower() == "ambient":
        return synthesize_ambient(mood, duration, out_wav)
    return synthesize_classic(mood, duration, out_wav)


def synthesize_classic(mood: str, duration: float, out_wav: Path) -> Path:
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
        d = prog[(bar + bar // 16) % len(prog)]   # the progression shifts every 16 bars, so long tracks keep moving
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
