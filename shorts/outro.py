"""The closing line every video ends with (English and Hindi), added automatically by the builders.

    "Thanks for watching the video! Please like, share and subscribe to watch more interesting videos like this."

`with_outro(script, lang)` returns a copy of a Short's or documentary's script with one extra final scene
(narration + a Like / Share / Subscribe title card). Plans do NOT write it themselves; it is idempotent
(a script that already ends with it is returned unchanged). Used by compose, stockreel and cinematic; the
generated_animations engine appends the same text as an animated outro scene.
"""
from __future__ import annotations

from .plan import Graphic, Scene

OUTRO_TEXT = {
    "en": "Thanks for watching the video! Please like, share and subscribe to watch more interesting videos like this.",
    "hi": "वीडियो देखने के लिए धन्यवाद! ऐसे ही और दिलचस्प वीडियो देखने के लिए कृपया लाइक, शेयर और सब्सक्राइब करें।",
}
OUTRO_KEYWORD = {"en": "subscribe", "hi": "सब्सक्राइब"}
OUTRO_HEADLINE = {"en": "Like · Share · Subscribe", "hi": "लाइक · शेयर · सब्सक्राइब"}
OUTRO_SECONDS = {"en": 7.0, "hi": 9.0}   # rough speaking time, for length estimates


def outro_scene(lang: str) -> Scene:
    return Scene(text=OUTRO_TEXT[lang], keyword=OUTRO_KEYWORD[lang],
                 graphic=Graphic(kind="title", headline=OUTRO_HEADLINE[lang], prop="heart"))


def has_outro(script, lang: str) -> bool:
    scenes = script.scenes
    return bool(scenes) and OUTRO_KEYWORD[lang] in scenes[-1].text.lower()


def with_outro(script, lang: str):
    """Copy of `script` ending with the outro scene (a documentary gets it inside its last chapter)."""
    if has_outro(script, lang):
        return script
    sc = outro_scene(lang)
    if hasattr(script, "chapters"):
        last = script.chapters[-1]
        chapters = [*script.chapters[:-1], last.model_copy(update={"scenes": [*last.scenes, sc]})]
        return script.model_copy(update={"chapters": chapters})
    return script.model_copy(update={"scenes": [*script.scenes, sc]})
