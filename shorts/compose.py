"""Assemble a vertical Short: the code-drawn animation + voice-over + ducked background music +
sound effects + hook line. Everything is mixed with FFmpeg (open source)."""
from __future__ import annotations

import logging
import subprocess
import wave
from pathlib import Path

from . import animate, config, music, sfx, tts
from .plan import LangScript

log = logging.getLogger(__name__)


def _run(cmd, cwd=None):
    log.debug("$ %s", " ".join(map(str, cmd)))
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


# ---------------------------------------------------------------- voice
def _voice_track(scenes, lang: str, work: Path, window=None, chapter_starts=frozenset()):
    """Synthesize every scene. With a (min, max) duration window (Shorts) the speech speed is adjusted
    to fit it; without one (documentaries) the voice keeps its natural pace and a longer pause is left
    before each scene in `chapter_starts`. Returns (voice_wav, [(start, end, text), ...] per scene, voice_end)."""
    gap = config.SCENE_GAP if window else 0.4
    chap_gap = 0.9

    def render(scale):
        files, durs = [], []
        for i, sc in enumerate(scenes):
            f = work / f"vo_{i}.wav"
            durs.append(tts.synthesize(sc.text, f, lang, scale))
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


# ---------------------------------------------------------------- captions
def _ass_time(s: float) -> str:
    h, m = int(s // 3600), int(s % 3600 // 60)
    return f"{h}:{m:02d}:{s % 60:05.2f}"


def _ass_escape(t: str) -> str:
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def _captions(hook: str, lang: str, out: Path):
    font = config.FONTS[lang]
    # the scene draws its own caption pills; only the hook line is burned in here
    hook_style = ("Style: Hook,{font},80,&H003C8AFF,&H003C8AFF,&H003A2313,&HA0000000,-1,0,0,0,100,100,0,0,3,20,0,8,60,60,120,1"
                  ).format(font=font)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config.WIDTH}
PlayResY: {config.HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{hook_style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if hook:
        lines.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(3.0)},Hook,,0,0,0,,"
                     f"{{\\fad(200,300)}}{_ass_escape(hook)}")
    out.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- video
def _mix(work: Path, voice: Path, total: float, mood: str, out: Path, *, hook: str = "", lang: str = "en",
         fps: int = 30, lufs: int = -14, music_volume: float = 0.30) -> None:
    """Mix voice, ducked music and sound effects under work/video.mp4. With a `hook` the hook line is burned
    in (Shorts); without one the picture is copied as it is (documentaries)."""
    track = music.pick_track(mood)
    if track:
        log.info("Using music track %s", track.name)
        music_in = ["-stream_loop", "-1", "-i", track]
    else:
        music_in = ["-i", music.synthesize(mood, total, work / "music.wav")]

    # Sound effects on the animation's cues (pops on reveals, a bell on each keyword)
    sfx_wav = sfx.build(work / "timeline.json", total, work / "sfx.wav") if config.SFX else None
    sfx_in = ["-i", sfx_wav.name] if sfx_wav else []

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
    if hook:
        _captions(hook, lang, work / "captions.ass")
        filt += ";[0:v]ass=captions.ass:shaping=complex[v]"  # complex shaping for Devanagari
        vmap, vcodec = "[v]", ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(fps)]
    else:
        vmap, vcodec = "0:v", ["-c:v", "copy"]
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", "video.mp4", "-i", voice.name, *music_in, *sfx_in,
          "-filter_complex", filt, "-map", vmap, "-map", "[a]", "-t", f"{total:.2f}", *vcodec,
          "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", out.name], cwd=work)
    log.info("Rendered %s (%.1fs)", out, total)


def build(script: LangScript, lang: str, mood: str, work: Path, niche: str = "") -> Path:
    """Render one Short (1080x1920, 40-59 s) and return its path."""
    work = work.resolve()  # FFmpeg runs with cwd=work, so every path must be absolute
    work.mkdir(parents=True, exist_ok=True)
    voice, timeline, voice_end = _voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    animate.render(script, lang, niche, timeline, total, work)  # writes work/video.mp4 (the picture)
    out = work / f"short_{lang}.mp4"
    _mix(work, voice, total, mood, out, hook=script.hook_text or " ", lang=lang, fps=config.FPS)
    return out


def build_documentary(script, lang: str, mood: str, work: Path, niche: str = "") -> tuple[Path, list[tuple[str, float]]]:
    """Render one documentary (1920x1080, natural length). Returns (video path, [(chapter title, start second)])."""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    scenes = script.scenes
    starts, n = {}, 0
    for ch in script.chapters:
        starts[n] = ch.title
        n += len(ch.scenes)
    voice, timeline, voice_end = _voice_track(scenes, lang, work, chapter_starts=frozenset(starts))
    total = voice_end + 3.0
    animate.render(scenes, lang, niche, timeline, total, work, layout="landscape", fps=config.DOC_FPS)
    out = work / f"documentary_{lang}.mp4"
    _mix(work, voice, total, mood, out, lang=lang, fps=config.DOC_FPS, lufs=-16, music_volume=0.22)
    chapters = [(title, 0.0 if i == 0 else timeline[i][0]) for i, title in sorted(starts.items())]
    return out, chapters
