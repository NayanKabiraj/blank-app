"""Assemble a vertical Short: voice-over + ducked background music + footage + captions.
All rendering is done with FFmpeg (open source)."""
from __future__ import annotations

import logging
import subprocess
import wave
from pathlib import Path

from . import config, music, tts, visuals
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


def _captions(timeline, hook: str, lang: str, out: Path, words_per_chunk: int = 3):
    font = config.FONTS[lang]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config.WIDTH}
PlayResY: {config.HEIGHT}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,3,2,70,70,560,1
Style: Hook,{font},84,&H0000E5FF,&H0000E5FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,18,0,8,60,60,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if hook:
        lines.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(3.0)},Hook,,0,0,0,,"
                     f"{{\\fad(200,300)}}{_ass_escape(hook)}")
    for start, end, text in timeline:
        words = text.split()
        chunks = [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
        weights = [max(1, len(c)) for c in chunks]
        t, span = start, end - start
        for c, wgt in zip(chunks, weights):
            d = span * wgt / sum(weights)
            lines.append(f"Dialogue: 0,{_ass_time(t)},{_ass_time(t + d)},Cap,,0,0,0,,"
                         f"{{\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}}{_ass_escape(c)}")
            t += d
    out.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- video
def _probe_duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _scene_clip(src: Path, duration: float, out: Path):
    # Long source videos often open with titles or black frames: start a bit in
    src_dur = _probe_duration(src)
    offset = min(src_dur * 0.15, 8.0) if src_dur > duration + 6 else 0.0
    vf = (f"scale={config.WIDTH}:{config.HEIGHT}:force_original_aspect_ratio=increase,"
          f"crop={config.WIDTH}:{config.HEIGHT},setsar=1,fps={config.FPS},"
          f"eq=brightness=-0.06:saturation=1.1,format=yuv420p")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{offset:.2f}", "-stream_loop", "-1",
          "-i", src, "-t", f"{duration:.3f}", "-vf", vf, "-an", "-c:v", "libx264",
          "-preset", "veryfast", "-crf", "21", out])


def build(script: LangScript, lang: str, mood: str, work: Path) -> tuple[Path, list[str]]:
    """Render one Short. Returns (video path, footage credits to add to the description)."""
    work = work.resolve()  # FFmpeg runs with cwd=work, so every path must be absolute
    work.mkdir(parents=True, exist_ok=True)
    voice, timeline, voice_end = _voice_track(script, lang, work)
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))

    # Footage: each scene's clip runs until the next scene starts; last one to the end
    used: set[str] = set()
    clips, credits = [], []
    for i, (start, _end, _t) in enumerate(timeline):
        seg_start = 0.0 if i == 0 else start
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        dur = seg_end - seg_start
        src, credit = visuals.fetch(script.scenes[i].visual_query, work / f"src_{i}.mp4", dur, used)
        if credit:
            credits.append(credit)
        clip = work / f"clip_{i}.mp4"
        _scene_clip(src, dur, clip)
        clips.append(clip)
    (work / "clips.txt").write_text("".join(f"file '{c.name}'\n" for c in clips))
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "clips.txt",
          "-c", "copy", "video.mp4"], cwd=work)

    # Music
    track = music.pick_track(mood)
    if track:
        log.info("Using music track %s", track.name)
        music_in = ["-stream_loop", "-1", "-i", track]
    else:
        music_in = ["-i", music.synthesize(mood, total, work / "music.wav")]

    _captions(timeline, script.hook_text, lang, work / "captions.ass")
    out = work / f"short_{lang}.mp4"
    fade_out = total - 1.2
    filt = (
        "[1:a]aresample=44100,aformat=channel_layouts=stereo,asplit=2[vo][sc];"
        f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.30,"
        f"afade=t=out:st={fade_out:.2f}:d=1.2[mu];"
        "[mu][sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[duck];"
        "[vo][duck]amix=inputs=2:duration=longest:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[a];"
        "[0:v]ass=captions.ass:shaping=complex[v]"  # complex shaping for Devanagari
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", "video.mp4", "-i", voice.name, *music_in,
          "-filter_complex", filt, "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
          "-r", str(config.FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
          "-movflags", "+faststart", out.name], cwd=work)
    log.info("Rendered %s (%.1fs)", out, total)
    return out, credits
