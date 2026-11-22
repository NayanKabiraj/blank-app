"""Assemble a vertical Short: the code-drawn animation + voice-over + ducked background music +
sound effects + hook line. Everything is mixed with FFmpeg (open source)."""
from __future__ import annotations

import logging
import subprocess
import wave
from pathlib import Path

from . import animate, config, music, outro, sfx, tts
from .plan import LangScript

log = logging.getLogger(__name__)


def _run(cmd, cwd=None):
    log.debug("$ %s", " ".join(map(str, cmd)))
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


# ---------------------------------------------------------------- voice
def _voice_track(scenes, lang: str, work: Path, window=None, chapter_starts=frozenset(), style: str = "shorts",
                 gap: float | None = None):
    """Synthesize every scene. With a (min, max) duration window (Shorts) the speech speed is adjusted
    to fit it; without one (documentaries) the voice keeps its natural pace and a longer pause is left
    before each scene in `chapter_starts`. Returns (voice_wav, [(start, end, text), ...] per scene, voice_end)."""
    gap = gap if gap is not None else (config.SCENE_GAP if window else 0.4)
    chap_gap = 0.9

    def render(scale):
        files, durs = [], []
        for i, sc in enumerate(scenes):
            f = work / f"vo_{i}.wav"
            durs.append(tts.synthesize(sc.text, f, lang, scale, style))
            files.append(f)
        return files, durs

    scale = 1.0
    files, durs = render(scale)
    pauses = lambda g: [(g + (chap_gap if i in chapter_starts else 0)) for i in range(1, len(durs))]  # noqa: E731
    if window:
        voice_min = window[0] - config.LEAD_IN - config.TAIL
        voice_max = window[1] - config.LEAD_IN - config.TAIL - 0.5
        total = sum(durs) + sum(pauses(gap))
        if total > voice_max or total < voice_min:
            target = voice_max - 1 if total > voice_max else voice_min + 1
            speech = sum(durs)  # speech portion scales with length_scale, gaps do not
            scale = max(0.78, min(1.18, (target - sum(pauses(gap))) / speech))
            log.info("Voice %.1fs out of range, re-rendering with length_scale=%.2f", total, scale)
            files, durs = render(scale)
            total = sum(durs) + sum(pauses(gap))
        if total < voice_min:  # still short: stretch the pauses between scenes
            gap += (voice_min - total) / max(1, len(durs) - 1)
    log.info("Voice-over: %.1fs of speech, %d scenes", sum(durs), len(durs))

    # Concatenate into one track with lead-in and gaps
    with wave.open(str(files[0]), "rb") as w:
        params = w.getparams()
    sr, width = params.framerate, params.sampwidth
    silence = lambda sec: b"\x00" * (int(sr * sec) * width * params.nchannels)  # noqa: E731
    out = work / "voice.wav"
    timeline, t = [], config.LEAD_IN
    with wave.open(str(out), "wb") as wo:
        wo.setparams(params)
        wo.writeframes(silence(config.LEAD_IN))
        for i, (f, d) in enumerate(zip(files, durs)):
            with wave.open(str(f), "rb") as wi:
                wo.writeframes(wi.readframes(wi.getnframes()))
            timeline.append((t, t + d, scenes[i].text))
            t += d
            if i < len(files) - 1:
                g = gap + (chap_gap if (i + 1) in chapter_starts else 0)
                wo.writeframes(silence(g))
                t += g
    return out, timeline, t


# ---------------------------------------------------------------- video
def _mix(work: Path, voice: Path, total: float, mood: str, out: Path, *, lufs: int = -14, music_volume: float = 0.30,
         sfx_wav: Path | None = None) -> None:
    """Mix voice, ducked music and sound effects under work/video.mp4 (the picture is copied as it is: the scene
    already draws the captions and the hook line)."""
    track = music.pick_track(mood)
    if track:
        log.info("Using music track %s", track.name)
        music_in = ["-stream_loop", "-1", "-i", track]
    else:
        music_in = ["-i", music.synthesize(mood, total, work / "music.wav")]

    # Sound effects on the animation's cues (pops on reveals, a bell on each keyword)
    if sfx_wav is None and config.SFX:   # the director pipeline passes its own cue track
        sfx_wav = sfx.build(work / "timeline.json", total, work / "sfx.wav")
    elif not config.SFX:
        sfx_wav = None
    sfx_in = ["-i", Path(sfx_wav).name] if sfx_wav else []

    fade_out = total - 1.2
    filt = (
        "[1:a]aresample=44100,aformat=channel_layouts=stereo,apad,asplit=2[vo][sc];"
        f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume={music_volume},"
        f"afade=t=out:st={fade_out:.2f}:d=1.2[mu];"
        "[mu][sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[duck];"
        + ("[3:a]aresample=44100,aformat=channel_layouts=stereo[fx];" if sfx_wav else "")
        + f"[vo][duck]{'[fx]' if sfx_wav else ''}amix=inputs={3 if sfx_wav else 2}:duration=first:normalize=0,"
        + f"loudnorm=I={lufs}:TP=-1.5:LRA=11[a]"
    )
    vmap, vcodec = "0:v", ["-c:v", "copy"]
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", "video.mp4", "-i", voice.name, *music_in, *sfx_in,
          "-filter_complex", filt, "-map", vmap, "-map", "[a]", "-t", f"{total:.2f}", *vcodec,
          "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", out.name], cwd=work)
    log.info("Rendered %s (%.1fs)", out, total)


def build(script: LangScript, lang: str, mood: str, work: Path, niche: str = "") -> Path:
    """Render one Short (1080x1920, 40-59 s) and return its path."""
    work = work.resolve()  # FFmpeg runs with cwd=work, so every path must be absolute
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)   # every video ends: "Thanks for watching ... like, share and subscribe"
    voice, timeline, voice_end = _voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    animate.render(script, lang, niche, timeline, total, work)  # writes work/video.mp4 (the picture)
    out = work / f"short_{lang}.mp4"
    _mix(work, voice, total, mood, out)
    return out


def build_documentary(script, lang: str, mood: str, work: Path, niche: str = "") -> tuple[Path, list[tuple[str, float]]]:
    """Render one documentary (1920x1080, natural length). Returns (video path, [(chapter title, start second)])."""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    scenes = script.scenes
    starts, n = {}, 0
    for ch in script.chapters:
        starts[n] = ch.title
        n += len(ch.scenes)
    voice, timeline, voice_end = _voice_track(scenes, lang, work, chapter_starts=frozenset(starts), style="documentary")
    total = voice_end + 3.0
    animate.render(scenes, lang, niche, timeline, total, work, layout="landscape", fps=config.DOC_FPS)
    out = work / f"documentary_{lang}.mp4"
    _mix(work, voice, total, mood, out, lufs=-16, music_volume=0.22)
    chapters = [(title, 0.0 if i == 0 else timeline[i][0]) for i, title in sorted(starts.items())]
    return out, chapters
