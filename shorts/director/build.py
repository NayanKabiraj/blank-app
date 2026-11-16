"""Render one language of a director manifest: narration (same voices as the template pipeline) -> narration-synced
timeline -> Three.js frames -> audio mix -> final.mp4 + captions + thumbnail + contact sheet + render report."""
from __future__ import annotations

import copy
import json
import logging
import math
import os
import re
import subprocess
import wave
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from .. import compose, config, music, sfx
from . import manifest as M

log = logging.getLogger(__name__)
DIR = Path(__file__).resolve().parent
SCENE_GAP = 0.42     # silence between spoken scenes: the transition plays across it
LEAD = 0.18          # a scene starts this long before its first word
MOODS = {"cinematic": "dramatic", "energetic": "upbeat", "intelligent": "inspiring", "urgent": "dramatic", "calm": "calm",
         "mysterious": "mysterious", "warm": "calm", "inspiring": "inspiring"}


def music_mood(m: dict) -> str:
    mood = (m.get("audio", {}).get("music", {}) or {}).get("mood")
    if mood in music.MOODS:
        return mood
    for tone in m.get("creativeBrief", {}).get("visualStyle", {}).get("tone", []):
        if tone in MOODS:
            return MOODS[tone]
    return "dramatic"


# ---------------------------------------------------------------- timeline
def retime(m: dict, lang: str, work: Path) -> tuple[dict, Path, float, list]:
    """Synthesize the narration scene by scene and rebuild the timeline around the real speech.

    Returns (manifest with real scene times, voice wav, total seconds, sound cues [(second, assetId, gain)]).
    Every scene starts just before its first word and ends when the next one begins; text and sound cues planned
    inside a scene keep their position relative to the spoken words (a text planned for the middle of the narration still
    lands on the middle of the real speech)."""
    doc = M.is_documentary(m)
    scenes = m["scenes"]
    chap = {sid: title for title, sid in M.chapters(m)}
    starts = frozenset(i for i, sc in enumerate(scenes) if sc["sceneId"] in chap and i > 0)
    items = [SimpleNamespace(text=sc["narration"]["text"].strip()) for sc in scenes]
    target = m["creativeBrief"]["targetDurationSeconds"]
    window = None if doc else (min(config.MIN_DURATION, 0.75 * target), config.MAX_DURATION)
    voice, tl, voice_end = compose._voice_track(items, lang, work, window=window, chapter_starts=starts,
                                                style="documentary" if doc else "shorts", gap=SCENE_GAP)
    total = voice_end + 3.0 if doc else min(config.MAX_DURATION, max(window[0], voice_end + config.TAIL))
    out = copy.deepcopy(m)
    bounds = [0.0] + [max(tl[i - 1][1] + 0.05, tl[i][0] - LEAD) for i in range(1, len(scenes))] + [total]
    cues = []
    sfx_cfg = m["audio"].get("soundEffects", {})
    for i, sc in enumerate(out["scenes"]):
        t0, t1 = bounds[i], bounds[i + 1]
        s, e = tl[i][0], tl[i][1]
        n0, n1 = sc["narration"]["startSeconds"], sc["narration"]["endSeconds"]
        k = (e - s) / (n1 - n0) if n1 - n0 > 0.1 else 1.0
        f = lambda x: s + (x - n0) * k  # noqa: E731 - planned time -> real time
        sc["startSeconds"], sc["endSeconds"], sc["durationSeconds"] = round(t0, 3), round(t1, 3), round(t1 - t0, 3)
        sc["narration"]["startSeconds"], sc["narration"]["endSeconds"] = round(s, 3), round(e, 3)
        for te in sc.get("textElements", []):
            a = max(t0 + 0.02, f(te["startSeconds"]))
            b = min(t1 - 0.05, f(te["startSeconds"] + te["durationSeconds"]))
            if b - a < 0.6:
                b = min(t1 - 0.05, a + 0.6)
            te["startSeconds"], te["durationSeconds"] = round(a - t0, 3), round(max(0.4, b - a), 3)   # scene-local from here on
        per_scene = []
        for fx in sc.get("soundEffects", []) or []:
            per_scene.append((f(fx["atSeconds"]), fx["assetId"], float(fx.get("volume", 0.6))))
        if sfx_cfg.get("enabled", True):
            tr = sc.get("transitionOut", {})
            if i < len(scenes) - 1 and tr.get("type") in ("camera-fly-through", "whip-pan", "zoom-tunnel", "light-sweep", "depth-push", "geometry-wipe", "match-motion"):
                tw = t1 - tr.get("durationSeconds", 0.5) * 0.7
                if not any(abs(c[0] - tw) < 0.35 for c in per_scene):
                    per_scene.append((tw, "whoosh-transition", 0.4))
            if sc.get("textElements") and len(per_scene) < sfx_cfg.get("maximumEffectsPerScene", 3):
                per_scene.append((t0 + sc["textElements"][0]["startSeconds"], "click-ui", 0.25))
        cues += per_scene[: sfx_cfg.get("maximumEffectsPerScene", 3) + 1]
    out["_timeline"] = {"total": total, "bounds": bounds, "speech": [(a, b) for a, b, _ in tl]}
    return out, voice, total, cues


def caption_chunks(m: dict, lang: str) -> list[dict]:
    """Word-by-word captions: <= maximumWordsPerCaption words per chunk, cut at punctuation; each word timed by its length
    inside its scene's speech."""
    mx = m["captions"].get("maximumWordsPerCaption", 5)
    chunks = []
    for sc in m["scenes"]:
        ws = M.words(sc["narration"]["text"])
        if not ws:
            continue
        s, e = sc["narration"]["startSeconds"], sc["narration"]["endSeconds"]
        wt = [len(w) + 1.6 for w in ws]
        tot, acc, times = sum(wt), 0.0, []
        for w, x in zip(ws, wt):
            times.append((s + (e - s) * acc / tot, s + (e - s) * (acc + x) / tot))
            acc += x
        cur = []
        for i, w in enumerate(ws):
            cur.append({"w": w, "start": round(times[i][0], 3), "end": round(times[i][1], 3)})
            end_of_phrase = re.search(r"[.,;:?!।]$", w) and len(cur) >= 2
            if len(cur) >= mx or end_of_phrase or i == len(ws) - 1:
                chunks.append({"start": cur[0]["start"], "end": cur[-1]["end"], "words": cur})
                cur = []
    # no gaps inside a scene's flow: a chunk lingers until the next one starts (at most 0.35 s)
    for a, b in zip(chunks, chunks[1:]):
        if b["start"] > a["end"]:
            a["end"] = round(min(b["start"], a["end"] + 0.35), 3)
    return chunks


def srt(chunks: list[dict], out: Path) -> None:
    ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int((x % 1) * 1000):03d}"  # noqa: E731
    out.write_text("\n".join(f"{i + 1}\n{ts(c['start'])} --> {ts(c['end'])}\n{' '.join(w['w'] for w in c['words'])}\n" for i, c in enumerate(chunks)), encoding="utf-8")


# ---------------------------------------------------------------- audio analysis
def audio_analysis(voice: Path, total: float, fps: int, mood: str) -> dict:
    """Narration loudness per video frame (what `react-to-audio` and `audioReactive` follow) and the beat grid of the
    synthesized music (beat = minor beat actions, every 4th = major, at least minimumSecondsBetweenMajorActions apart)."""
    with wave.open(str(voice), "rb") as w:
        sr, ch, raw = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    n = int(math.ceil(total * fps)) + 2
    per = sr / fps
    rms = np.array([np.sqrt(np.mean(x[int(i * per):int((i + 1) * per)] ** 2)) if int(i * per) < len(x) else 0.0 for i in range(n)])
    rms = np.convolve(rms, np.ones(3) / 3, mode="same")
    ref = np.percentile(rms[rms > 0], 95) if (rms > 0).any() else 1.0
    env = np.clip(rms / ref, 0, 1)
    bpm = music.MOODS.get(mood, music.MOODS["dramatic"])[0]
    beat = 60.0 / bpm
    beats = [round(k * beat, 3) for k in range(int(total / beat) + 1)]
    major, last = [], -9.0
    for k, b in enumerate(beats):
        if k % 4 == 0 and b - last >= 1.2:
            major.append(b)
            last = b
    return {"env": [round(float(v), 3) for v in env], "beats": beats, "major": major, "bpm": bpm}


# ---------------------------------------------------------------- render
def engine_cfg(m: dict, lang: str, total: float, chunks: list[dict], analysis: dict) -> dict:
    res, fps = m["creativeBrief"]["resolution"], m["creativeBrief"]["framesPerSecond"]
    scenes = []
    for sc in m["scenes"]:
        spec = copy.deepcopy(sc)
        scenes.append({"spec": spec, "t0": sc["startSeconds"], "t1": sc["endSeconds"], "transitionOut": sc.get("transitionOut", {})})
        # the narration window is scene-local inside the engine
    slim = {k: m[k] for k in ("renderSettings", "brandSystem", "randomization", "captions", "audio") if k in m}
    doc = M.is_documentary(m)
    return {"width": res["width"], "height": res["height"], "fps": fps, "total": total, "lang": lang, "manifest": slim, "scenes": scenes,
            "captions": chunks, "audio": {k: analysis[k] for k in ("env", "beats", "major")},
            "workers": int(os.getenv("RENDER_WORKERS", str(max(2, min(4, os.cpu_count() or 2))))),
            # software WebGL is the bottleneck: the 3D world is drawn at a fraction of the output size and upsampled, while the text
            # overlay and captions stay at full resolution (the difference is invisible under bloom; it is 2-3x faster)
            "renderScale": float(os.getenv("DIRECTOR_SCALE", "0.55" if doc else "0.7")),
            "msaa": int(os.getenv("DIRECTOR_MSAA", "0")), "crf": 26 if doc else 23, "jpegQuality": 90}


def run_node(cfg: dict, out: Path, work: Path, sample: int = 0) -> dict:
    cfg_path = work / ("preflight.json" if sample else "director.json")
    cfg = {**cfg, **({"sample": sample, "workers": min(cfg["workers"], 2)} if sample else {})}
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["node", str(DIR / "render.cjs"), str(cfg_path), str(out)], check=True, cwd=DIR)
    rep = out if sample else Path(str(out) + ".report.json")
    return json.loads(rep.read_text())


def qc(video: Path, m: dict, work: Path) -> dict:
    """Quality checks on the finished file, driven by the manifest's qualityControl block when present."""
    q = m.get("qualityControl", {})
    rep: dict = {"issues": []}

    def ff(*args):
        return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr
    if q.get("detectBlackFrames", True):
        # the closing fade to black is expected: look at everything but the last second
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout or 0)
        out = ff("-i", str(video), "-t", f"{max(1.0, dur - 1.2):.2f}", "-vf", f"blackdetect=d={q.get('maximumBlackFrameDurationSeconds', 0.3)}:pix_th=0.06", "-an", "-f", "null", "-")
        blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", out)
        rep["blackFrames"] = blacks
        rep["issues"] += [f"black frames {a}-{b}s" for a, b in blacks]
    if q.get("detectFrozenFrames", True):
        out = ff("-i", str(video), "-vf", f"freezedetect=n=-55dB:d={q.get('maximumFrozenFrameDurationSeconds', 1.2)}", "-an", "-f", "null", "-")
        frozen = re.findall(r"freeze_start: ([\d.]+)", out)
        rep["frozenFrames"] = frozen
        rep["issues"] += [f"frozen picture from {a}s" for a in frozen]
    out = ff("-i", str(video), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    if i:
        rep["integratedLufs"] = float(i[-1])
        lo, hi = q.get("minimumIntegratedLufs", -18), q.get("maximumIntegratedLufs", -13)
        if not lo - 1 <= rep["integratedLufs"] <= hi + 1:
            rep["issues"].append(f"loudness {rep['integratedLufs']} LUFS outside {lo}..{hi}")
    if p:
        rep["truePeakDb"] = float(p[-1])
    return rep


def build(m: dict, lang: str, work: Path, out_dir: Path) -> dict:
    """Render `m` (a completed, localized manifest) in one language. Returns the report (paths + checks)."""
    work = Path(work).resolve()
    out_dir = Path(out_dir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    timed, voice, total, cues = retime(m, lang, work)
    mood = music_mood(m)
    fps = m["creativeBrief"]["framesPerSecond"]
    chunks = caption_chunks(timed, lang)
    analysis = audio_analysis(voice, total, fps, mood)
    cfg = engine_cfg(timed, lang, total, chunks, analysis)
    # preflight: a sparse run of the real renderer to catch engine errors and text overflow before the long render
    if m.get("qualityControl", {}).get("runPreflightRender", True) and os.getenv("DIRECTOR_PREFLIGHT", "on") != "off":
        sample = max(fps // 2, int(math.ceil(total * fps / 36)))
        pre = run_node(cfg, work / "preflight.out.json", work, sample=sample)
        if pre["textOverflow"]:
            log.warning("Text does not fit its safe area: %s", ", ".join(pre["textOverflow"]))
    video = work / "video.mp4"
    log.info("Rendering %d scenes, %.1fs, %dx%d @ %dfps with %d workers", len(timed["scenes"]), total, cfg["width"], cfg["height"], fps, cfg["workers"])
    render = run_node(cfg, video, work)
    cue_wav = sfx.build_cues(cues, total, work / "cues.wav") if config.SFX and m["audio"].get("soundEffects", {}).get("enabled", True) else None
    doc = M.is_documentary(m)
    final = work / "final.mp4"
    compose._mix(work, voice, total, mood, final, lufs=m["audio"]["narration"].get("targetLufs", -16), music_volume=0.22 if doc else 0.30, sfx_wav=cue_wav)
    # deliverables
    srt(chunks, out_dir / "captions.srt")
    (out_dir / "captions.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "beat-map.json").write_text(json.dumps({k: analysis[k] for k in ("bpm", "beats", "major")}), encoding="utf-8")
    (out_dir / "video-manifest.json").write_text(json.dumps({k: v for k, v in timed.items() if k != "_timeline"}, ensure_ascii=False, indent=1), encoding="utf-8")
    narr = out_dir / "narration.wav"
    narr.write_bytes(voice.read_bytes())
    video_out = out_dir / "final.mp4"
    video_out.write_bytes(final.read_bytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(1.6, total / 4):.2f}", "-i", str(video_out), "-frames:v", "1", str(out_dir / "thumbnail.png")], check=False)
    step = max(2, int(total / 12))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_out), "-vf", f"fps=1/{step},scale=360:-1,tile=6x2", "-frames:v", "1", str(out_dir / "contact-sheet.png")], check=False)
    checks = qc(video_out, m, work)
    report = {"lang": lang, "seconds": round(total, 2), "scenes": len(timed["scenes"]), "frames": render["frames"], "renderSeconds": round(render["seconds"]),
              "textOverflow": render["textOverflow"], "voiceEngine": config.TTS_ENGINE, "music": mood, "checks": checks,
              "timeline": [{"sceneId": s["sceneId"], "start": s["startSeconds"], "end": s["endSeconds"]} for s in timed["scenes"]],
              "files": {"video": str(video_out), "thumbnail": str(out_dir / "thumbnail.png"), "captions": str(out_dir / "captions.srt")}}
    (out_dir / "render-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("Rendered %s %.1fs, issues: %s", lang, total, checks["issues"] or "none")
    chap_t = []
    for title, sid in M.chapters(m):
        sc = next(s for s in timed["scenes"] if s["sceneId"] == sid)
        chap_t.append((title, 0.0 if sc["order"] == 1 else sc["startSeconds"]))
    report["chapters"] = chap_t
    return report
