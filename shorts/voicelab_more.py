"""Voice samples from several free text-to-speech engines, to compare them (run in CI: python shorts/voicelab_more.py <out dir>).

Same two paragraphs for every voice. Engines: Microsoft neural voices through the edge-tts package (free, no key, unofficial
endpoint), Google Translate TTS through gTTS (free, unofficial), and higher quality Piper voices (open source, offline).
Prints one line per sample with the time it took and writes timing.txt.
"""
import asyncio
import subprocess
import sys
import time
import wave
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "voicelab_more")
OUT.mkdir(parents=True, exist_ok=True)
EN = ("Every June, a whole country looks up at the sky and holds its breath. Farmers, cities, even stock markets wait for "
      "one thing: the first rain of the monsoon. But here's the strange part. Rain doesn't fall by magic. "
      "Do you know what powers it?")
HI = ("हर जून में पूरा देश आसमान की ओर देखता है। किसान, शहर, यहाँ तक कि शेयर बाज़ार भी एक ही चीज़ का इंतज़ार करते हैं: "
      "मॉनसून की पहली बारिश। पर अजीब बात यह है कि बारिश जादू से नहीं गिरती। क्या आप जानते हैं वह क्या है?")
log = []


def mp3(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-b:a", "128k", str(dst)], check=True)


def duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def run(name, fn):
    t0 = time.time()
    try:
        fn()
        secs = duration(OUT / f"{name}.mp3")
        line = f"{name}: {secs:.1f}s of audio in {time.time() - t0:.1f}s"
    except Exception as e:  # noqa: BLE001
        line = f"{name}: FAILED {type(e).__name__}: {str(e)[:150]}"
    print(line, flush=True)
    log.append(line)


def edge(name, voice, text, rate="+0%", pitch="+0Hz"):
    def go():
        import edge_tts
        asyncio.run(edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(OUT / f"{name}.mp3")))
    run(name, go)


def gtts(name, lang, tld, text):
    def go():
        from gtts import gTTS
        gTTS(text, lang=lang, tld=tld).save(str(OUT / f"{name}.mp3"))
    run(name, go)


def piper(name, voice, text):
    def go():
        from piper import PiperVoice
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from shorts import tts
        onnx, cfg = tts._voice_files(voice)
        v = PiperVoice.load(onnx, config_path=cfg)
        wav = OUT / f"{name}.wav"
        with wave.open(str(wav), "wb") as wf:
            v.synthesize_wav(text, wf)
        mp3(wav, OUT / f"{name}.mp3")
        wav.unlink()
    run(name, go)


# English
for voice in ("en-IN-NeerjaNeural", "en-IN-PrabhatNeural", "en-US-AndrewNeural", "en-US-AriaNeural", "en-US-GuyNeural"):
    edge("edge-en-" + voice.split("-")[2].replace("Neural", "").lower() + "-" + voice[3:5].lower(), voice, EN)
gtts("gtts-en-india", "en", "co.in", EN)
for voice in ("en_US-ryan-high", "en_US-lessac-high", "en_US-hfc_female-medium"):
    piper("piper-" + voice, voice, EN)
# Hindi
for voice in ("hi-IN-MadhurNeural", "hi-IN-SwaraNeural"):
    edge("edge-hi-" + voice.split("-")[2].replace("Neural", "").lower(), voice, HI)
gtts("gtts-hi", "hi", "co.in", HI)
for voice in ("hi_IN-priyamvada-medium", "hi_IN-rohan-medium", "hi_IN-pratham-medium"):
    piper("piper-" + voice, voice, HI)
(OUT / "timing.txt").write_text("\n".join(log) + "\n")
