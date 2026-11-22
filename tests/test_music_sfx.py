import wave

import numpy as np

from shorts import music, sfx


def test_no_bell_cues_anywhere():
    cfg = {"segments": [
        {"start": 0, "end": 6, "hit": 2.0, "graphic": {"kind": "title", "items": []}},
        {"start": 6, "end": 12, "hit": 8.0, "graphic": {"kind": "quiz", "items": ["a", "b", "c"]}},
        {"start": 12, "end": 18, "hit": 14.0, "graphic": {"kind": "keyword", "items": []}},
        {"start": 18, "end": 24, "hit": 20.0, "graphic": {"kind": "stat", "items": []}},
    ]}
    cues = sfx.cues_from_timeline(cfg)
    assert cues and {k for _t, k in cues} == {"pop"}


def test_ambient_music_is_warm_and_not_clipped(tmp_path):
    out = music.synthesize_ambient("inspiring", 12, tmp_path / "a.wav")
    with wave.open(str(out)) as w:
        assert w.getnchannels() == 2 and abs(w.getnframes() / w.getframerate() - 12) < 0.1
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, 2).mean(1) / 32768
    assert np.abs(x).max() < 0.99
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1 / 44100)
    assert sp[fr > 3000].sum() / sp.sum() < 0.05          # nothing bright or pinging


def test_style_switch(monkeypatch, tmp_path):
    monkeypatch.setenv("MUSIC_STYLE", "classic")
    assert music.synthesize("calm", 3, tmp_path / "c.wav").exists()


def test_default_music_is_classic_inspiring_and_ignores_library(monkeypatch, tmp_path):
    monkeypatch.delenv("MUSIC_STYLE", raising=False)
    monkeypatch.delenv("MUSIC_MOOD", raising=False)
    monkeypatch.delenv("MUSIC_LIBRARY", raising=False)
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "song.mp3").write_bytes(b"x" * 10)
    monkeypatch.setattr(music.config, "MUSIC_DIR", lib)
    assert music.pick_track("calm") is None                      # third-party files are never picked by default
    monkeypatch.setenv("MUSIC_LIBRARY", "on")
    assert music.pick_track("calm") is not None
    seen = {}
    monkeypatch.delenv("MUSIC_LIBRARY")
    monkeypatch.setattr(music, "synthesize_classic", lambda mood, d, o: seen.setdefault("m", mood) and o)
    music.synthesize("mysterious", 3, tmp_path / "x.wav")
    assert seen["m"] == "inspiring"
