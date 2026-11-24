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
    "hi": os.getenv("PIPER_VOICE_HI", "hi_IN-pratham-medium"),
}
# Picture engine: "generated" = the generated_animations (Manim) engine (default), "whiteboard" = the older
# Node/Playwright whiteboard explainer. Voices are strict: English = edge Andrew, Hindi = Piper pratham, no fallback.
# Languages produced by default: English + Hindi (Hindi re-enabled 24 Nov 2026; plans need a `hindi` block, the same vox pack serves both languages).
# VIDEO_LANGS=en makes a run English only.
LANGS = os.getenv("VIDEO_LANGS", "en,hi").strip()
ENGINE = os.getenv("VIDEO_ENGINE", "generated").strip().lower()
# Look of the generated_animations videos: "vox" (paper cut-out explainer style, the default from 23 Nov 2026) or "classic" (dark space theme; VIDEO_LOOK=classic).
LOOK = os.getenv("VIDEO_LOOK", "vox").strip().lower()

# English narration: Microsoft neural voice through edge-tts (free, no key; falls back to the Piper voice above if it is
# unreachable). Set EN_VOICE=piper to use Piper for English. Hindi stays on Piper.
EN_VOICE = os.getenv("EN_VOICE", "edge:en-US-AndrewNeural").strip()

# Pace of the narration: > 1 is slower (Piper length_scale). English was judged rushed: 1.15 = about 13 % slower. Override with the
# SPEECH_PACE_EN / SPEECH_PACE_HI variables. The Shorts length window still adjusts the speed when a script would run too long.
SPEECH_PACE = {"en": float(os.getenv("SPEECH_PACE_EN", "1.15")), "hi": float(os.getenv("SPEECH_PACE_HI", "1.0"))}
FONTS = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}

# --- Visuals ---
# Every Short is an animated explainer drawn by code (shorts/explainer/). Code-synthesized sound
# effects (soft pops, no bell) on the animation cues: on unless SFX=off
SFX = os.getenv("SFX", "on").strip().lower() != "off"

# --- YouTube upload ---
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
# ONE YouTube sign-in for every language (owner instruction, 23 Nov 2026): Hindi uploads use the same refresh token as English; a
# separate YT_REFRESH_TOKEN_HI secret is ignored. (YT_REFRESH_TOKEN_EN still wins over YT_REFRESH_TOKEN for the one token.)
_TOKEN = os.getenv("YT_REFRESH_TOKEN_EN") or os.getenv("YT_REFRESH_TOKEN", "")
if YT_CLIENT_SECRET and not _TOKEN:
    # no secret set: use the token the phone sign-in saved (encrypted) in data/ (shorts.ytauth; upload code also tries it first)
    from .ytauth import load_saved_token
    _TOKEN = load_saved_token("en")
# the public HTTPS page Google redirects to after "Allow" (GitHub Pages, docs/oauth/callback.html); add it under Authorized redirect URIs
_repo = os.getenv("GITHUB_REPOSITORY", "NayanKabiraj/blank-app")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI") or "https://{}.github.io/{}/oauth/callback.html".format(*(_repo.split("/", 1)[0].lower(), _repo.split("/", 1)[1]))
YT_REFRESH_TOKENS = {"en": _TOKEN, "hi": _TOKEN}
YT_PRIVACY = os.getenv("YT_PRIVACY", "private")         # private (default) | unlisted | public
# YouTube's "altered or synthetic content" label. Off by default: the videos are animated explainers with a generic
# synthetic narrator. Set the repository variable YT_AI_DISCLOSURE=on to flag every upload as containing synthetic media.
YT_AI_DISCLOSURE = os.getenv("YT_AI_DISCLOSURE", "off").strip().lower() == "on"
YT_CATEGORY_ID = os.getenv("YT_CATEGORY_ID", "27")      # 27 = Education
