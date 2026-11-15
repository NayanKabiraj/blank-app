"""Step 6.3: add background music without re-rendering the picture.
Music is a file from ../../assets/music/ if one exists, else an original calm bed synthesized in code
(shorts/music.py). It is set 20 dB below the voice (integrated LOUDNESS), faded in and out over 1 s,
then everything is normalised to -14 LUFS. The video stream is copied untouched.
Usage: python mix_music.py en hi en-short hi-short"""
import random, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2]))
from shorts import music  # noqa: E402

BELOW_DB = 20.0

def run(*a): return subprocess.run(a, check=True, capture_output=True, text=True)
def dur(f): return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)).stdout)
def lufs(f):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(f), "-af", "ebur128=peak=none", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])

for cut in sys.argv[1:]:
    lang = cut.split("-")[0]; short = cut.endswith("-short")
    out_dir = HERE / "out" / lang; name = "short" if short else "final"
    final = out_dir / f"{name}.mp4"; keep = out_dir / f"{name}.no-music.mp4"
    if not keep.exists(): final.rename(keep)           # keep the voice-only version once
    voice = HERE / "composition" / cut / "assets" / "voiceover.wav"
    total = dur(keep)
    own = sorted((HERE.parents[1] / "assets" / "music").glob("*.*")) if (HERE.parents[1] / "assets" / "music").is_dir() else []
    with tempfile.TemporaryDirectory() as tmp:
        if own:
            track = own[0]
        else:
            random.seed(7); track = music.synthesize("calm", total + 2, Path(tmp) / "bed.wav")
        gain = (lufs(voice) - BELOW_DB) - lufs(track)
        run("ffmpeg", "-y", "-loglevel", "error", "-i", str(keep), "-i", str(voice), "-stream_loop", "-1", "-i", str(track),
            "-filter_complex",
            f"[1:a]aresample=48000,apad[v];[2:a]aresample=48000,volume={gain:.2f}dB,atrim=0:{total:.3f},"
            f"afade=t=in:d=1,afade=t=out:st={total - 1:.3f}:d=1[m];"
            f"[v][m]amix=inputs=2:duration=first:normalize=0,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", str(final))
    print(f"{cut}: music {'file '+own[0].name if own else 'synthesized (calm)'}, gain {gain:+.1f} dB -> {final.relative_to(HERE)} ({dur(final):.1f}s, {lufs(final):.1f} LUFS)")
