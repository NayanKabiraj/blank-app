import json
import wave
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from generated_animations.authoring import safety
from generated_animations.authoring.inspect_frames import check_frame, contact_sheet
from generated_animations.registry import animation_registry as reg

TOPIC = "gps_how_it_works"


def test_safety_passes_shipped_scenes():
    assert safety.scan_dir(reg.topic_dir(TOPIC)) == []


@pytest.mark.parametrize("src", [
    "import os\n", "import subprocess\n", "from shorts import tts\n", "x = eval('1')\n", "open('f')\n",
    "import socket\n", "y = __import__('os')\n", "k = 'my_api_key'\n", "def f(:\n", "import requests\n",
])
def test_safety_rejects_dangerous_code(src):
    assert safety.scan_source(src, "bad.py")


def test_safety_allows_manim_numpy():
    assert safety.scan_source("import numpy as np\nfrom manim import Circle\nfrom generated_animations.shared import diagrams\n") == []


def test_config_matches_modules_and_modules_define_animate():
    cfg = reg.load_config(TOPIC)
    for s in cfg["scenes"]:
        src = (reg.topic_dir(TOPIC) / f"{s['module']}.py").read_text()
        assert "def animate(ctx)" in src and s["narration"]


def test_approval_flow_detects_edits(tmp_path, monkeypatch):
    monkeypatch.setattr(reg, "APPROVED", tmp_path / "approved.json")
    ok, _ = reg.check_approved(TOPIC)
    assert not ok
    reg.approve(TOPIC, "tester")
    assert reg.check_approved(TOPIC)[0]
    data = json.loads((tmp_path / "approved.json").read_text())
    data[TOPIC]["files"]["scene_001.py"] = "0" * 64   # simulate an edit after review
    (tmp_path / "approved.json").write_text(json.dumps(data))
    ok, why = reg.check_approved(TOPIC)
    assert not ok and "changed" in why


def test_plan_durations_cover_narration():
    from generated_animations.pipeline import plan_durations
    cfg = reg.load_config(TOPIC)
    d = plan_durations(cfg, [5.0, 4.0, 9.0, 8.0, 12.0], 24)
    assert all(x >= n + 0.9 for x, n in zip(d, [5, 4, 9, 8, 12]))
    assert all(abs(x * 24 - round(x * 24)) < 1e-6 for x in d)


def test_narration_envelope(tmp_path):
    from generated_animations.audio import Narration
    sr = 22050
    t = np.arange(sr * 2) / sr
    sig = (np.sin(2 * np.pi * 220 * t) * (t > 1) * 0.5 * 32767).astype(np.int16)
    p = tmp_path / "n.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(sig.tobytes())
    n = Narration(p)
    assert n.level(0.5) < 0.1 < 0.5 < n.level(1.5)


def test_frame_checker_flags_blank_and_clipped(tmp_path):
    blank = tmp_path / "blank.png"; Image.new("RGB", (100, 200), (6, 9, 18)).save(blank)
    assert "blank_frame" in check_frame(blank)["issues"]
    arr = np.full((200, 100, 3), 10, np.uint8); arr[:, 0:5] = 255
    clipped = tmp_path / "clip.png"; Image.fromarray(arr).save(clipped)
    assert check_frame(clipped)["edge_ink"] > 0.35


def test_contact_sheet(tmp_path):
    ps = []
    for i in range(3):
        p = tmp_path / f"frame_{i:02d}_0{i}.0s.png"; Image.new("RGB", (90, 160), (i * 40, 0, 0)).save(p); ps.append(p)
    assert contact_sheet(ps, tmp_path / "s.png", cols=3).exists()


def test_every_scene_module_imports():
    pytest.importorskip("manim")
    for m in reg.scene_modules(TOPIC):
        assert callable(m.animate)
