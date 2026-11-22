"""Narration + music for generated videos.

Narration reuses the repository's own `shorts.tts` (Piper) when it works. If it cannot (no voice models
reachable, e.g. a sandbox without network), an offline flite voice from ffmpeg is used instead and the
provenance is recorded as 'flite-fallback' - it is NOT Piper and sounds robotic. Music is the repo's own
numpy synthesizer (`shorts.music`). Narration modules themselves are not modified.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 22050


def _ffmpeg(*args: str):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def wav_seconds(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def flite_voice(text: str, out_wav: Path, voice: str = "slt") -> Path:
    safe = text.replace("\\", " ").replace("'", "").replace(":", " ").replace(";", ",").replace("%", " percent")
    _ffmpeg("-f", "lavfi", "-i", f"flite=text='{safe}':voice={voice}", "-ar", str(SR), "-ac", "1", str(out_wav))
    return out_wav


def synthesize_line(text: str, out_wav: Path, lang: str = "en", voice: str = "auto") -> tuple[Path, str]:
    """Returns (wav, provider)."""
    if voice in ("auto", "piper"):
        try:
            from shorts import tts
            tts.synthesize(text, out_wav, lang, 1.0, "shorts")
            return out_wav, "piper"
        except Exception as exc:   # noqa: BLE001 - any TTS failure falls back, recorded below
            if voice == "piper":
                raise
            print(f"[audio] Piper unavailable ({type(exc).__name__}); using offline flite voice")
    return flite_voice(text, out_wav), "flite-fallback"


class Narration:
    """Placed narration track with a loudness envelope for lip-sync."""

    def __init__(self, wav_path: Path, fps: int = 24):
        _tmp = Path(wav_path)
        with wave.open(str(_tmp)) as w:
            raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            sr = w.getframerate()
            if w.getnchannels() > 1:
                raw = raw.reshape(-1, w.getnchannels()).mean(axis=1)
        hop = max(1, int(sr / fps / 2))
        n = len(raw) // hop
        rms = np.sqrt((raw[: n * hop].reshape(n, hop) ** 2).mean(axis=1)) if n else np.zeros(1)
        rms = rms / (np.percentile(rms, 95) + 1e-6) if rms.size else rms
        self.env, self.step = np.clip(rms, 0, 1), hop / sr

    def level(self, t: float) -> float:
        i = int(t / self.step)
        return float(self.env[i]) if 0 <= i < len(self.env) else 0.0


def place_track(lines: list[Path], starts: list[float], total: float, out_wav: Path) -> Path:
    """Mix per-scene narration wavs at their scene start times into one mono track of length `total`."""
    n = int(total * SR)
    track = np.zeros(n, dtype=np.float32)
    for wav, start in zip(lines, starts):
        with wave.open(str(wav)) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
            if w.getframerate() != SR:
                raise ValueError("narration wavs must be 22050 Hz mono")
        i = int(start * SR)
        track[i:i + len(data)] += data[: max(0, n - i)]
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())
    return out_wav


def mix_final(video: Path, voice: Path, mood: str, total: float, out: Path, work: Path) -> str:
    """Voice + ducked music + loudness normalisation, muxed under the picture. Returns music provenance."""
    from shorts import music
    track = music.pick_track(mood)
    music_wav = track or music.synthesize(mood, total, work / "music.wav")
    filt = ("[1:a]aresample=44100,aformat=channel_layouts=stereo,apad,asplit=2[vo][sc];"
            f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.30,afade=t=out:st={total - 1.2:.2f}:d=1.2[mu];"
            "[mu][sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[duck];"
            "[vo][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    loop = ["-stream_loop", "-1"] if track else []
    _ffmpeg("-i", str(video), "-i", str(voice), *loop, "-i", str(music_wav), "-filter_complex", filt,
            "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
            str(out))
    return "library-track" if track else "synthesized-numpy (shorts.music)"
