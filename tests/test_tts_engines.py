from pathlib import Path

from shorts import config, tts


def test_english_uses_edge_and_falls_back_to_piper(monkeypatch, tmp_path):
    monkeypatch.delenv("SHORTS_FAKE_TTS", raising=False)
    monkeypatch.setattr(config, "EN_VOICE", "edge:en-US-AndrewNeural")
    monkeypatch.setitem(tts._state, "edge", None)
    seen = {}
    monkeypatch.setattr(tts, "_edge", lambda text, out, scale: seen.setdefault("edge", scale) or 1.5)
    monkeypatch.setattr(tts, "_piper", lambda *a: 9.0)
    assert tts.synthesize("hi", tmp_path / "a.wav", "en", 1.1) == 1.1
    assert seen["edge"] == 1.1                      # no Piper pace correction applied to the edge voice

    def boom(*a):
        raise RuntimeError("offline")
    monkeypatch.setattr(tts, "_edge", boom)
    assert tts.synthesize("hi", tmp_path / "b.wav", "en") == 9.0   # falls back to Piper
    assert tts._state["edge"] is False


def test_hindi_stays_on_piper_pratham(monkeypatch, tmp_path):
    monkeypatch.delenv("SHORTS_FAKE_TTS", raising=False)
    monkeypatch.setattr(tts, "_piper", lambda *a: 4.0)
    assert tts.synthesize("नमस्ते", tmp_path / "h.wav", "hi") == 4.0
    assert config.VOICES["hi"] == "hi_IN-pratham-medium" or "PIPER_VOICE_HI" in __import__("os").environ
