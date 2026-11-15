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

# --- Research / script writing (Claude) ---
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
# Optional: steer the daily research toward a broad area, e.g. "personal finance, tech, health"
NICHE_HINT = os.getenv("NICHE_HINT", "")

# --- Video ---
WIDTH, HEIGHT, FPS = 1080, 1920, 30
MIN_DURATION = 40.0   # seconds (final video)
MAX_DURATION = 59.0   # seconds (final video, stays under 60)
LEAD_IN = 0.4         # silence before the voice starts
TAIL = 1.8            # music-only tail after the voice ends
SCENE_GAP = 0.25      # pause between scenes

# --- Voices (Piper, open source: https://github.com/OHF-Voice/piper1-gpl) ---
VOICES = {
    "en": os.getenv("PIPER_VOICE_EN", "en_US-lessac-medium"),
    "hi": os.getenv("PIPER_VOICE_HI", "hi_IN-pratham-medium"),
}
FONTS = {"en": "Noto Sans", "hi": "Noto Sans Devanagari"}

# --- Visual style ---
# "explainer": dark flat step-by-step diagrams with a guiding spark and caption pills (shorts/explainer/), the default
# "cartoon2d": 2D traditional-animation explainer with a presenter character, by code (shorts/cartoon2d/)
# "stickman": 2D hand-drawn stick figure explainer rendered by code (shorts/stickman/)
# "cartoon3d": 3D cartoon explainer rendered by code with three.js (shorts/cartoon.py)
# "motion": 2D motion graphics drawn in code with Manim (shorts/motion.py)
# "footage": real stock footage per scene (shorts/visuals.py)
# Code-synthesized sound effects on the animation cues (explainer and cartoon2d): on unless SFX=off
SFX = os.getenv("SFX", "on").strip().lower() != "off"
# A real stock photo behind the cartoon presenter in each scene (cartoon2d): on unless STOCK_PHOTOS=off
STOCK_PHOTOS = os.getenv("STOCK_PHOTOS", "on").strip().lower() != "off"
VISUAL_STYLE = os.getenv("VISUAL_STYLE", "explainer").strip().lower() or "explainer"

# --- Stock footage: Pexels if a key is set, else Wikimedia Commons (no key needed) ---
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# --- YouTube upload ---
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKENS = {
    "en": os.getenv("YT_REFRESH_TOKEN_EN") or os.getenv("YT_REFRESH_TOKEN", ""),
    "hi": os.getenv("YT_REFRESH_TOKEN_HI") or os.getenv("YT_REFRESH_TOKEN", ""),
}
YT_PRIVACY = os.getenv("YT_PRIVACY", "public")          # public | unlisted | private
YT_CATEGORY_ID = os.getenv("YT_CATEGORY_ID", "27")      # 27 = Education
