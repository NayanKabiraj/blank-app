"""Central configuration. Everything can be overridden with environment variables
(set them as GitHub Actions secrets / variables)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
VOICES_DIR = Path(os.getenv("VOICES_DIR", ROOT / ".cache" / "voices"))
HISTORY_FILE = DATA_DIR / "history.json"
VIDEOS_DIR = ROOT / "videos"  # every rendered video is kept here

# --- Video ---
WIDTH, HEIGHT, FPS = 1080, 1920, 30
MIN_DURATION = 40.0   # seconds (final video)
MAX_DURATION = 59.0   # seconds (final video, stays under 60)
LEAD_IN = 0.4         # silence before the voice starts
TAIL = 1.8            # music-only tail after the voice ends
SCENE_GAP = 0.25      # pause between scenes

DOC_FPS = 24        # documentaries (1920x1080) are rendered at 24 fps

# --- Voices ---
# Default engine: Piper (small, fast, offline). TTS_ENGINE=parler selects Indic Parler-TTS (AI4Bharat, Apache 2.0,
# expressive but slow on a CPU: about 10-12x real time) with the named speakers below; if it cannot load, Piper is used.
TTS_ENGINE = os.getenv("TTS_ENGINE", "piper").strip().lower()
PARLER_MODEL = os.getenv("PARLER_MODEL", "ai4bharat/indic-parler-tts")
PARLER_SPEAKERS = {"en": os.getenv("PARLER_SPEAKER_EN", "Thoma"), "hi": os.getenv("PARLER_SPEAKER_HI", "Rohit")}

# Piper (open source, fallback): https://github.com/OHF-Voice/piper1-gpl
VOICES = {
    "en": os.getenv("PIPER_VOICE_EN", "en_US-ryan-high"),
    "hi": os.getenv("PIPER_VOICE_HI", "hi_IN-rohan-medium"),
}
FONTS = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}

# --- Visuals ---
# Every Short is an animated explainer drawn by code (shorts/explainer/). Code-synthesized sound
# effects (pop and bell) on the animation cues: on unless SFX=off
SFX = os.getenv("SFX", "on").strip().lower() != "off"

# --- YouTube upload ---
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKENS = {
    "en": os.getenv("YT_REFRESH_TOKEN_EN") or os.getenv("YT_REFRESH_TOKEN", ""),
    "hi": os.getenv("YT_REFRESH_TOKEN_HI") or os.getenv("YT_REFRESH_TOKEN", ""),
}
if YT_CLIENT_SECRET and not (YT_REFRESH_TOKENS["en"] and YT_REFRESH_TOKENS["hi"]):
    # no secret set: use the token that `python -m shorts.ytauth exchange` saved (encrypted) in data/
    from .ytauth import load_saved_token
    for _lang in ("en", "hi"):
        YT_REFRESH_TOKENS[_lang] = YT_REFRESH_TOKENS[_lang] or load_saved_token(_lang)
YT_PRIVACY = os.getenv("YT_PRIVACY", "private")         # private (default) | unlisted | public
# YouTube's "altered or synthetic content" label. Off by default: the videos are animated explainers with a generic
# synthetic narrator. Set the repository variable YT_AI_DISCLOSURE=on to flag every upload as containing synthetic media.
YT_AI_DISCLOSURE = os.getenv("YT_AI_DISCLOSURE", "off").strip().lower() == "on"
YT_CATEGORY_ID = os.getenv("YT_CATEGORY_ID", "27")      # 27 = Education
