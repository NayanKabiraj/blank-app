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
def _voice_track(script: LangScript, lang: str, work: Path):
    """Synthesize every scene, fitting the total into the target duration window.
    Returns (voice_wav, [(start, end, text), ...] per scene, voice_end)."""
    voice_min = config.MIN_DURATION - config.LEAD_IN - config.TAIL
    voice_max = config.MAX_DURATION - config.LEAD_IN - config.TAIL - 0.5
    gap = config.SCENE_GAP

    def render(scale):
        files, durs = [], []
        for i, sc in enumerate(script.scenes):
            f = work / f"vo_{i}.wav"
            durs.append(tts.synthesize(sc.text, f, lang, scale))
            files.append(f)
        return files, durs, sum(durs) + gap * (len(durs) - 1)

    scale = 1.0
    files, durs, total = render(scale)
    if total > voice_max or total < voice_min:
        target = voice_max - 1 if total > voice_max else voice_min + 1
        # speech portion scales with length_scale, gaps do not
        speech = total - gap * (len(durs) - 1)
        scale = max(0.78, min(1.18, (target - gap * (len(durs) - 1)) / speech))
        log.info("Voice %.1fs out of range, re-rendering with length_scale=%.2f", total, scale)
        files, durs, total = render(scale)
    if total < voice_min:  # still short: stretch the pauses between scenes
        gap += (voice_min - total) / max(1, len(durs) - 1)
        total = voice_min
    log.info("Voice-over length: %.1fs (%d scenes)", total, len(durs))

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
            timeline.append((t, t + d, script.scenes[i].text))
            t += d
            if i < len(files) - 1:
                wo.writeframes(silence(gap))
                t += gap
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
def build(script: LangScript, lang: str, mood: str, work: Path, niche: str = "") -> Path:
    """Render one Short and return its path."""
    work = work.resolve()  # FFmpeg runs with cwd=work, so every path must be absolute
    work.mkdir(parents=True, exist_ok=True)
    voice, timeline, voice_end = _voice_track(script, lang, work)
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))

    animate.render(script, lang, niche, timeline, total, work)  # writes work/video.mp4 (the picture)

    # Music
    track = music.pick_track(mood)
    if track:
        log.info("Using music track %s", track.name)
        music_in = ["-stream_loop", "-1", "-i", track]
    else:
        music_in = ["-i", music.synthesize(mood, total, work / "music.wav")]

    # Sound effects on the animation's cues (pops on reveals, a bell on each keyword)
    sfx_wav = None
    if config.SFX:
        sfx_wav = sfx.build(work / "timeline.json", total, work / "sfx.wav")
    sfx_in = ["-i", sfx_wav.name] if sfx_wav else []

    _captions(script.hook_text, lang, work / "captions.ass")
    out = work / f"short_{lang}.mp4"
    fade_out = total - 1.2
    filt = (
        "[1:a]aresample=44100,aformat=channel_layouts=stereo,apad,asplit=2[vo][sc];"
        f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.30,"
        f"afade=t=out:st={fade_out:.2f}:d=1.2[mu];"
        "[mu][sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[duck];"
        + ("[3:a]aresample=44100,aformat=channel_layouts=stereo[fx];" if sfx_wav else "")
        + f"[vo][duck]{'[fx]' if sfx_wav else ''}amix=inputs={3 if sfx_wav else 2}:duration=first:normalize=0,"
        + "loudnorm=I=-14:TP=-1.5:LRA=11[a];"
        + "[0:v]ass=captions.ass:shaping=complex[v]"  # complex shaping for Devanagari
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", "video.mp4", "-i", voice.name, *music_in, *sfx_in,
          "-filter_complex", filt, "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
          "-r", str(config.FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
          "-movflags", "+faststart", out.name], cwd=work)
    log.info("Rendered %s (%.1fs)", out, total)
    return out
