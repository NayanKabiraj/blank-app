"""The director's video manifest: defaults, validation, localisation and the narration-synced timeline.

Claude (the creative director) writes a manifest: story, narration per scene, scene types, camera, environment, text
animations, sound cues. This module completes the parts Claude may leave out, checks the rules the manifest itself
declares (story rules, selection rules, registered presets), swaps in the Hindi text, and converts the planned timeline
into the real one once the narration has been synthesized.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

# --- what the engine (shorts/director/engine/*.js) can draw: keep in step with it
SCENE_TYPES = ["kinetic-typography", "particle-world", "geometry-swarm", "data-tunnel", "procedural-grid", "object-assembly",
               "diagram-3d", "image-parallax", "timeline-3d", "wave-field", "network-nodes", "finale"]
CAMERA_PRESETS = ["static-drift", "slow-dolly-in", "fast-dolly-in", "dolly-out", "orbit-left", "orbit-right", "crane-up",
                  "crane-down", "fly-through", "whip-pan-left", "whip-pan-right", "handheld-subtle", "follow-target",
                  "push-orbit", "macro-push", "parallax-slide"]
BEHAVIORS = ["float", "pulse", "rotate", "assemble", "explode", "scatter", "swarm", "spiral", "orbit", "wave", "fall", "rise",
             "magnetize", "follow-path", "react-to-audio"]
TEXT_ANIMATIONS = ["word-punch", "kinetic-sentence", "character-scatter", "typewriter", "tracking-reveal", "mask-reveal",
                   "impact-zoom", "particle-assemble", "depth-reveal", "word-stack", "slide-and-lock"]
TRANSITIONS = ["particle-dissolve", "camera-fly-through", "geometry-wipe", "zoom-tunnel", "whip-pan", "object-occlusion",
               "grid-collapse", "light-sweep", "depth-push", "match-motion", "fade-through-black"]
ENVIRONMENTS = ["dark-tech", "neon-grid", "particle-space", "data-network", "abstract-dark", "energy-tunnel", "minimal-light",
                "digital-city", "wave-space", "holographic-room"]
OBJECT_TYPES = ["particles", "sphere", "central-control-orb", "network-node", "decision-node", "approval-gate", "icosahedron",
                "torus", "tetrahedron", "columns", "light-bars", "instanced-code-blocks", "task-nodes", "workflow-blocks",
                "timeline-nodes"]
PHASES = ["hook", "problem", "context", "development", "reveal", "payoff", "call-to-action"]
FONT_ROLES = {"primary", "secondary", "monospace", "inter"}
ENV_BG = {"dark-tech": "#04060c", "neon-grid": "#050312", "particle-space": "#02030a", "data-network": "#040810", "abstract-dark": "#05040c",
          "energy-tunnel": "#02040a", "minimal-light": "#0f1630", "digital-city": "#04060e", "wave-space": "#03060f", "holographic-room": "#030a12"}

WPS = {"en": 2.7, "hi": 2.3}   # planning pace (words per second); the real timing comes from the synthesized voice

DEFAULTS: dict[str, Any] = {
    "schemaVersion": "1.0.0",
    "renderSettings": {
        "pixelRatio": 1, "antialias": True, "shadows": False, "toneMapping": "aces-filmic", "exposure": 1.05,
        "motionBlur": {"enabled": False, "strength": 0.35, "samples": 8},
        "postProcessing": {
            "enabled": True, "bloom": {"enabled": True, "strength": 0.55, "radius": 0.45, "threshold": 0.78},
            "filmGrain": {"enabled": True, "strength": 0.015}, "vignette": {"enabled": True, "strength": 0.2},
            "chromaticAberration": {"enabled": True, "strength": 0.015},
            "glitch": {"enabled": True, "maximumStrength": 0.08, "useOnlyOnMajorBeats": True}},
        "safeArea": {"topPercent": 10, "bottomPercent": 18, "leftPercent": 7, "rightPercent": 7},
    },
    "brandSystem": {
        "fontFamily": {"primary": "Inter", "secondary": "Space Grotesk", "monospace": "JetBrains Mono"},
        "defaultPalette": {"background": "#05070D", "primary": "#00D9FF", "secondary": "#775CFF", "accent": "#FFCC33",
                           "danger": "#FF3B6B", "textPrimary": "#FFFFFF", "textSecondary": "#B8C1D9"},
        "typography": {"headlineWeight": 800, "bodyWeight": 500, "maximumHeadlineLines": 3, "uppercaseHeadlines": True,
                       "minimumReadableFontSizePixels": 48, "preferredHeadlineFontSizePixels": 96, "captionFontSizePixels": 54},
    },
    "randomization": {"mode": "seeded", "globalSeed": 1, "reproducible": True, "variationStrength": 0.6},
    "audio": {"narration": {"enabled": True, "targetLufs": -16}, "music": {"enabled": True},
              "soundEffects": {"enabled": True, "maximumEffectsPerScene": 3},
              "beatSync": {"enabled": True, "minimumSecondsBetweenMajorActions": 1.2}},
    "captions": {"enabled": True, "format": "word-by-word", "maximumWordsPerCaption": 5, "highlightColor": "#FFCC33",
                 "defaultColor": "#FFFFFF", "bottomOffsetPercent": 19},
    "director": {
        "storyRules": {"hookWithinSeconds": 2.5, "maximumSceneDurationSeconds": 6, "minimumSceneDurationSeconds": 1.5,
                       "maximumWordsPerTextElement": 8, "maximumTextElementsPerScene": 3, "maximumNarrationWordsPerMinute": 165,
                       "requiredStoryPhases": PHASES, "requireOpenLoop": True, "openLoopCloseBeforeSeconds": 55,
                       "requirePatternInterruptEverySeconds": 7, "requireVisualChangeEverySeconds": 3},
        "selectionRules": {"maximumConsecutiveSameSceneType": 1, "maximumCameraReuseWithinScenes": 3,
                           "maximumTransitionReuseWithinScenes": 4, "maximumPaletteReuseWithinScenes": 5,
                           "minimumSceneTypeVariety": 5},
    },
    "validation": {"maximumAllowedTimelineDriftSeconds": 0.1, "minimumContrastRatio": 4.5, "onWarning": "continue", "onError": "fail"},
}
# documentaries: longer scenes, more of them, a relaxed pace of change
DOC_RULES = {"maximumSceneDurationSeconds": 14, "minimumSceneDurationSeconds": 2.5, "maximumTextElementsPerScene": 3,
             "requireVisualChangeEverySeconds": 6, "requirePatternInterruptEverySeconds": 14, "openLoopCloseBeforeSeconds": None,
             "maximumNarrationWordsPerMinute": 175, "minimumSceneTypeVariety": 7}

SCENE_ENV = {"kinetic-typography": "abstract-dark", "particle-world": "particle-space", "geometry-swarm": "dark-tech",
             "data-tunnel": "energy-tunnel", "procedural-grid": "neon-grid", "object-assembly": "holographic-room",
             "diagram-3d": "dark-tech", "image-parallax": "digital-city", "timeline-3d": "digital-city",
             "wave-field": "wave-space", "network-nodes": "data-network", "finale": "particle-space"}
DEFAULT_OBJECTS = {
    "kinetic-typography": [("particles", 700, "float", "primary")],
    "particle-world": [("particles", 1400, "spiral", "primary")],
    "geometry-swarm": [("central-control-orb", 1, "pulse", "accent"), ("tetrahedron", 28, "swarm", "secondary")],
    "data-tunnel": [("task-nodes", 12, "float", "primary"), ("particles", 320, "follow-path", "secondary")],
    "procedural-grid": [("instanced-code-blocks", 34, "follow-path", "secondary")],
    "object-assembly": [("icosahedron", 1, "assemble", "primary"), ("torus", 4, "orbit", "secondary")],
    "diagram-3d": [("workflow-blocks", 4, "pulse", "secondary")],
    "image-parallax": [("particles", 300, "float", "primary")],
    "timeline-3d": [("timeline-nodes", 8, "follow-path", "primary")],
    "wave-field": [("columns", 20, "wave", "primary")],
    "network-nodes": [("sphere", 1, "pulse", "secondary"), ("network-node", 18, "float", "primary")],
    "finale": [("particles", 2200, "magnetize", "primary")],
}
PHASE_ENERGY = {"hook": 0.95, "problem": 0.7, "context": 0.55, "development": 0.8, "reveal": 0.75, "payoff": 0.7, "call-to-action": 0.92}
PHASE_MOOD = {"hook": "urgent", "problem": "anticipation", "context": "explanatory", "development": "momentum", "reveal": "reveal",
              "payoff": "confident", "call-to-action": "inspiring"}


def deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", (text or "").strip()) if w]


def is_documentary(m: dict) -> bool:
    b = m.get("creativeBrief", {})
    return (b.get("format") or "").lower() == "documentary" or b.get("aspectRatio") == "16:9"


def load(src: str | Path) -> dict:
    text = Path(src).read_text(encoding="utf-8") if not str(src).lstrip().startswith("{") else str(src)
    # tolerate what chat tools and word processors do to JSON: non-breaking spaces, BOM, smart quotes around keys
    text = text.replace("\u00a0", " ").replace("\ufeff", "").replace("\u201c", '"').replace("\u201d", '"')
    return json.loads(text)


# ---------------------------------------------------------------- completion
def complete(m: dict) -> dict:
    """Fill everything Claude may leave out (deterministically, from the manifest's seed) so a compact manifest is enough:
    only `scenes[].sceneType`, `scenes[].narration.text` and `scenes[].textElements` are needed."""
    m = copy.deepcopy(m)
    doc = is_documentary(m)
    base = copy.deepcopy(DEFAULTS)
    if doc:
        base["director"]["storyRules"].update({k: v for k, v in DOC_RULES.items() if k != "minimumSceneTypeVariety"})
        base["director"]["selectionRules"]["minimumSceneTypeVariety"] = DOC_RULES["minimumSceneTypeVariety"]
        base["director"]["selectionRules"]["maximumCameraReuseWithinScenes"] = 6
        base["director"]["selectionRules"]["maximumTransitionReuseWithinScenes"] = 8
        base["director"]["selectionRules"]["maximumPaletteReuseWithinScenes"] = 10
        base["audio"]["narration"]["targetLufs"] = -16
        base["captions"]["bottomOffsetPercent"] = 8
        base["renderSettings"]["safeArea"] = {"topPercent": 8, "bottomPercent": 16, "leftPercent": 6, "rightPercent": 6}
        base["renderSettings"]["postProcessing"]["glitch"]["enabled"] = False
        base["renderSettings"]["postProcessing"]["filmGrain"]["strength"] = 0.012
    m = deep_merge(base, m)
    brief = m.setdefault("creativeBrief", {})
    brief.setdefault("language", "en-IN")
    brief.setdefault("platform", "youtube" if doc else "youtube-shorts")
    brief.setdefault("aspectRatio", "16:9" if doc else "9:16")
    brief.setdefault("resolution", {"width": 1920, "height": 1080} if doc else {"width": 1080, "height": 1920})
    brief.setdefault("framesPerSecond", 24 if doc else 30)
    brief.setdefault("targetDurationSeconds", 420 if doc else 55)
    seed = m["randomization"].get("globalSeed", 1)
    m["randomization"]["globalSeed"] = seed
    m.setdefault("job", {}).setdefault("jobId", "video-" + str(seed))
    pal = m["brandSystem"]["defaultPalette"]
    scenes = m.setdefault("scenes", [])
    n = len(scenes)
    t = 0.0
    last_cam, last_env, last_tr, last_anim = [], None, [], None
    cyc = lambda lst, i: lst[(i * 7 + seed) % len(lst)]  # noqa: E731 - deterministic "random" pick
    for i, sc in enumerate(scenes):
        sc["order"] = i + 1
        sc.setdefault("sceneId", f"scene-{i + 1:03d}")
        sc.setdefault("seed", 1000 + i + 1)
        if "storyPhase" not in sc:
            sc["storyPhase"] = "hook" if i == 0 else "call-to-action" if i == n - 1 else PHASES[1 + (i - 1) * 5 // max(1, n - 2)]
        ph = sc["storyPhase"]
        sc.setdefault("energy", PHASE_ENERGY.get(ph, 0.7))
        sc.setdefault("mood", PHASE_MOOD.get(ph, "explanatory"))
        sc.setdefault("sceneType", "kinetic-typography")
        nar = sc.setdefault("narration", {})
        nw = len(words(nar.get("text", "")))
        if "durationSeconds" not in sc:
            sc["durationSeconds"] = round(max(m["director"]["storyRules"]["minimumSceneDurationSeconds"], nw / WPS["en"] + 0.7), 2)
        sc.setdefault("startSeconds", round(t, 3))
        sc["endSeconds"] = round(sc["startSeconds"] + sc["durationSeconds"], 3)
        t = sc["endSeconds"]
        nar.setdefault("startSeconds", round(sc["startSeconds"] + 0.12, 3))
        nar.setdefault("endSeconds", round(max(nar["startSeconds"] + 0.5, sc["endSeconds"] - 0.25), 3))
        # environment
        env = sc.setdefault("environment", {})
        if "preset" not in env:
            e = SCENE_ENV.get(sc["sceneType"], "abstract-dark")
            if e == last_env:
                e = cyc([x for x in ENVIRONMENTS if x != last_env], i)
            env["preset"] = e
        last_env = env["preset"]
        env.setdefault("fogDensity", 0.08)
        env.setdefault("backgroundMotion", "forward" if sc["energy"] > 0.7 else "drift")
        # camera (never the same preset twice in a row, and each at most maximumCameraReuseWithinScenes times in the window)
        cam = sc.setdefault("camera", {})
        if "preset" not in cam:
            pool = [c for c in CAMERA_PRESETS if c not in last_cam[-3:] and c != "follow-target"]
            cam["preset"] = cyc(pool, i)
        cam.setdefault("target", "")
        cam.setdefault("speed", round(0.35 + 0.55 * sc["energy"], 2))
        cam.setdefault("shake", 0.02 if sc["energy"] > 0.85 else 0)
        cam.setdefault("fov", 50)
        last_cam.append(cam["preset"])
        # objects and lights
        if "objects" not in sc:
            sc["objects"] = [{"id": f"obj-{k + 1}", "type": ty, "count": c, "behavior": b, "color": pal[col], "audioReactive": k == 0}
                             for k, (ty, c, b, col) in enumerate(DEFAULT_OBJECTS.get(sc["sceneType"], DEFAULT_OBJECTS["particle-world"]))]
        sc.setdefault("lights", [{"type": "point", "color": pal["primary"], "intensity": 2.5, "position": {"x": -2, "y": 2, "z": 2}}])
        # text elements
        tes = sc.setdefault("textElements", [])
        for k, te in enumerate(tes):
            te.setdefault("id", f"{sc['sceneId']}-text-{k + 1}")
            if "animation" not in te:
                pool = [a for a in TEXT_ANIMATIONS if a != last_anim and a != "character-scatter"]
                te["animation"] = cyc(pool, i + k)
            last_anim = te["animation"]
            te.setdefault("position", {"x": 0, "y": 0.2 - 1.0 * k, "z": 0})
            te.setdefault("startSeconds", round(nar["startSeconds"] + 0.15 + 0.9 * k, 3))
            te.setdefault("durationSeconds", round(max(1.0, min(sc["endSeconds"] - te["startSeconds"] - 0.1, (nar["endSeconds"] - nar["startSeconds"]) * 0.9)), 3))
            te.setdefault("style", {})
            if ph == "hook" and not doc:
                te["style"].setdefault("scale", 1.25)   # the opening line is the biggest thing on screen
        # transition into the next scene
        tr = sc.setdefault("transitionOut", {})
        if "type" not in tr:
            if i == n - 1:
                tr["type"] = "fade-through-black"
            else:
                pool = [x for x in TRANSITIONS if x not in last_tr[-2:] and x != "fade-through-black"]
                tr["type"] = cyc(pool, i)
        tr.setdefault("durationSeconds", 0.8 if i == n - 1 else 0.55)
        if tr["type"] in ("whip-pan", "match-motion"):
            tr.setdefault("direction", "right" if i % 2 == 0 else "left")
        last_tr.append(tr["type"])
    m["renderSettings"]["durationSeconds"] = round(t, 3)
    m["renderSettings"]["fps"] = brief["framesPerSecond"]
    m["renderSettings"]["totalFrames"] = round(t * brief["framesPerSecond"])
    return m


# ---------------------------------------------------------------- validation
def _hex_lum(h: str) -> float:
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    la, lb = _hex_lum(a), _hex_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def validate(m: dict) -> tuple[list[str], list[str]]:
    """(errors, warnings). Errors stop the render, warnings are only reported. `m` must be completed."""
    errs, warns = [], []
    rules, sel = m["director"]["storyRules"], m["director"]["selectionRules"]
    scenes, doc = m.get("scenes", []), is_documentary(m)
    if not scenes:
        return ["the manifest has no scenes"], warns
    pal = m["brandSystem"]["defaultPalette"]
    for i, sc in enumerate(scenes):
        sid = sc.get("sceneId", f"#{i + 1}")
        if sc["sceneType"] not in SCENE_TYPES:
            errs.append(f"{sid}: unregistered sceneType '{sc['sceneType']}' (the engine would fall back to kinetic-typography)")
        if sc["camera"]["preset"] not in CAMERA_PRESETS:
            errs.append(f"{sid}: unregistered camera preset '{sc['camera']['preset']}'")
        if sc["transitionOut"]["type"] not in TRANSITIONS:
            errs.append(f"{sid}: unregistered transition '{sc['transitionOut']['type']}'")
        if sc["environment"]["preset"] not in ENVIRONMENTS:
            errs.append(f"{sid}: unregistered environment '{sc['environment']['preset']}'")
        for o in sc.get("objects", []):
            if o.get("type") not in OBJECT_TYPES:
                warns.append(f"{sid}: object type '{o.get('type')}' is not registered, a placeholder shape is drawn")
            if o.get("behavior") not in BEHAVIORS:
                warns.append(f"{sid}: behavior '{o.get('behavior')}' is not registered, 'float' is used")
        d = sc["durationSeconds"]
        if d > rules["maximumSceneDurationSeconds"] + 1e-6:
            errs.append(f"{sid}: {d:.1f}s is longer than maximumSceneDurationSeconds ({rules['maximumSceneDurationSeconds']})")
        if d < rules["minimumSceneDurationSeconds"] - 1e-6:
            errs.append(f"{sid}: {d:.1f}s is shorter than minimumSceneDurationSeconds ({rules['minimumSceneDurationSeconds']})")
        tes = sc.get("textElements", [])
        if len(tes) > rules["maximumTextElementsPerScene"]:
            errs.append(f"{sid}: {len(tes)} text elements (max {rules['maximumTextElementsPerScene']})")
        for te in tes:
            if te.get("animation") not in TEXT_ANIMATIONS:
                errs.append(f"{sid}/{te['id']}: unregistered text animation '{te.get('animation')}'")
            if len(words(te["text"])) > rules["maximumWordsPerTextElement"]:
                errs.append(f"{sid}/{te['id']}: more than {rules['maximumWordsPerTextElement']} words on screen")
            if (te.get("style") or {}).get("font", "primary") not in FONT_ROLES:
                warns.append(f"{sid}/{te['id']}: unknown font role, the primary font is used")
            col = (te.get("style") or {}).get("color", pal["textPrimary"])
            bg = ENV_BG.get(sc["environment"]["preset"], pal["background"])
            if contrast(col, bg) < m["validation"]["minimumContrastRatio"]:
                warns.append(f"{sid}/{te['id']}: text colour {col} has contrast {contrast(col, bg):.1f} on the background (< {m['validation']['minimumContrastRatio']})")
            if te["startSeconds"] < sc["startSeconds"] - 0.05 or te["startSeconds"] + te["durationSeconds"] > sc["endSeconds"] + 0.05:
                warns.append(f"{sid}/{te['id']}: text timing falls outside its scene")
        if not words(sc["narration"].get("text", "")):
            errs.append(f"{sid}: no narration text (every scene is spoken so picture and voice stay in sync)")
        nw = len(words(sc["narration"].get("text", "")))
        nd = sc["narration"]["endSeconds"] - sc["narration"]["startSeconds"]
        if nd > 0 and nw / nd * 60 > rules["maximumNarrationWordsPerMinute"] + 1e-6:
            warns.append(f"{sid}: narration pace {nw / nd * 60:.0f} wpm is above {rules['maximumNarrationWordsPerMinute']}")
        if sc["narration"]["endSeconds"] > sc["endSeconds"] + m["validation"].get("maximumAllowedNarrationOverflowSeconds", 0.2):
            errs.append(f"{sid}: narration ends after the scene")
        if i and abs(sc["startSeconds"] - scenes[i - 1]["endSeconds"]) > m["validation"]["maximumAllowedTimelineDriftSeconds"]:
            errs.append(f"{sid}: timeline gap or overlap with the previous scene")
        if i and sc["sceneType"] == scenes[i - 1]["sceneType"] and sel["maximumConsecutiveSameSceneType"] <= 1:
            errs.append(f"{sid}: same sceneType as the scene before")
        if i and sc["camera"]["preset"] == scenes[i - 1]["camera"]["preset"]:
            errs.append(f"{sid}: same camera preset as the scene before")
        if i and sc["transitionOut"]["type"] == scenes[i - 1]["transitionOut"]["type"]:
            errs.append(f"{sid}: same transition as the previous scene")
    for key, limit, label in (("camera", sel["maximumCameraReuseWithinScenes"], "camera preset"), ("transitionOut", sel["maximumTransitionReuseWithinScenes"], "transition")):
        win = 12 if doc else len(scenes)
        for s in range(0, max(1, len(scenes) - win + 1)):
            chunk = [(sc[key].get("preset") or sc[key].get("type")) for sc in scenes[s:s + win]]
            for v in set(chunk):
                if chunk.count(v) > limit:
                    warns.append(f"{label} '{v}' used {chunk.count(v)} times within {len(chunk)} scenes (max {limit})")
                    break
            else:
                continue
            break
    if len({sc["sceneType"] for sc in scenes}) < sel["minimumSceneTypeVariety"]:
        warns.append(f"only {len({sc['sceneType'] for sc in scenes})} different scene types (want {sel['minimumSceneTypeVariety']})")
    ph = [sc["storyPhase"] for sc in scenes]
    missing = [p for p in rules["requiredStoryPhases"] if p not in ph]
    if missing:
        warns.append("story phases missing: " + ", ".join(missing))
    if scenes[0]["storyPhase"] != "hook" or scenes[0]["narration"]["startSeconds"] > rules["hookWithinSeconds"]:
        warns.append("the hook must open the video within hookWithinSeconds")
    if scenes[-1]["storyPhase"] != "call-to-action":
        warns.append("the last scene should be the call-to-action")
    if rules.get("requireOpenLoop") and not m.get("story", {}).get("openLoop"):
        warns.append("story.openLoop is missing (the promise that keeps people watching)")
    # a visual change at least every requireVisualChangeEverySeconds: scene starts and text starts count
    # (a scene longer than 6.5 s gets an automatic camera glide at its midpoint, which counts as a change)
    marks = sorted({sc["startSeconds"] for sc in scenes} | {te["startSeconds"] for sc in scenes for te in sc.get("textElements", [])}
                   | {sc["startSeconds"] + sc["durationSeconds"] / 2 for sc in scenes if sc["durationSeconds"] > 6.5})
    gap = max((b - a for a, b in zip(marks, marks[1:])), default=0)
    if gap > rules["requireVisualChangeEverySeconds"]:
        warns.append(f"{gap:.1f}s without a visual change (max {rules['requireVisualChangeEverySeconds']}s)")
    total = scenes[-1]["endSeconds"]
    tgt = m["creativeBrief"]["targetDurationSeconds"]
    if abs(total - tgt) > 0.2 * tgt:
        warns.append(f"planned length {total:.0f}s is far from the target {tgt}s")
    # the standing strategy (skills/video-strategy): a quality gate, a cluster, follow-ups, a next video and a pinned question
    story, brief = m.get("story", {}), m["creativeBrief"]
    if not story.get("gateScore"):
        warns.append("story.gateScore is missing: score the concept /100 (85+ proceed, 75-84 improve, below 75 rework)")
    elif story["gateScore"] < 75:
        warns.append(f"story.gateScore {story['gateScore']} is below 75: rework the weakest components before rendering")
    if not brief.get("cluster"):
        warns.append("creativeBrief.cluster is missing: name the content cluster")
    if len(story.get("followUps") or []) < 3:
        warns.append("story.followUps: list three follow-up video ideas that continue the cluster")
    pm = m.get("publishingMetadata", {})
    if not pm.get("nextVideo"):
        warns.append("publishingMetadata.nextVideo is missing (the close hands the viewer to the next video)")
    if "?" not in pm.get("pinnedComment", ""):
        warns.append("publishingMetadata.pinnedComment should be one viewer decision as a question")
    for lang, loc in (m.get("localizations") or {}).items():
        if not loc.get("nextVideo") or "?" not in loc.get("pinnedComment", ""):
            warns.append(f"localizations.{lang}: nextVideo and a pinnedComment question are needed")
    th = m.get("thumbnail") or {}
    if th.get("headline") and (len(words(th["headline"])) > 4 or len(th["headline"]) > 24):
        warns.append("thumbnail.headline should be 1-4 big words (at most 24 characters)")
    if not th.get("headline"):
        warns.append("no thumbnail.headline: the hook text is used (write 1-4 words that show the consequence, not the title)")
    for lang, loc in (m.get("localizations") or {}).items():
        if not loc.get("thumbnailText"):
            warns.append(f"localizations.{lang}.thumbnailText is missing: the thumbnail uses the hook text of that language")
    if doc and not m.get("chapters"):
        warns.append("no chapters listed: YouTube chapter markers are made from `chapters` ([{title, firstScene}])")
    if doc and not (4 * 60 <= total <= 11 * 60):
        warns.append(f"a documentary should run about 5-10 minutes; this plans {total / 60:.1f}")
    return errs, warns


# ---------------------------------------------------------------- languages
def localize(m: dict, lang: str) -> dict:
    """The manifest for one language: `localizations.<lang>` replaces text (narration per scene, on-screen text per
    element, title/description/tags, chapter titles). English is the manifest itself."""
    m = copy.deepcopy(m)
    loc = (m.get("localizations") or {}).get(lang)
    if lang != "en" and not loc:
        raise ValueError(f"the manifest has no localizations.{lang} (narration and on-screen text in that language)")
    if loc:
        sc_loc = loc.get("scenes", {})
        for sc in m["scenes"]:
            s = sc_loc.get(sc["sceneId"])
            if not s:
                if lang != "en":
                    raise ValueError(f"localizations.{lang}.scenes has no entry for {sc['sceneId']}")
                continue
            if "narration" in s:
                sc["narration"]["text"] = s["narration"]
            for te in sc.get("textElements", []):
                if te["id"] in (s.get("text") or {}):
                    # accent words are matched by text, so a translation brings its own accentWords
                    te["text"] = s["text"][te["id"]]
                    te.setdefault("style", {})["accentWords"] = (s.get("accentWords") or {}).get(te["id"], {})
        for k in ("title", "description", "tags", "hashtags", "nextVideo", "pinnedComment"):
            if k in loc:
                m.setdefault("publishingMetadata", {})[k] = loc[k]
        if loc.get("chapters"):
            for ch, title in zip(m.get("chapters", []), loc["chapters"]):
                ch["title"] = title
        if loc.get("fullNarration"):
            m.setdefault("story", {})["fullNarration"] = loc["fullNarration"]
    m["creativeBrief"]["language"] = {"en": "en-IN", "hi": "hi-IN"}.get(lang, lang)
    return m


class Script:
    """What upload.upload() needs: title, description, tags."""

    def __init__(self, m: dict):
        p = m.get("publishingMetadata", {})
        tags = list(p.get("tags", []))
        hashtags = " ".join(p.get("hashtags", []))
        self.title = p.get("title") or m.get("story", {}).get("title") or "Video"
        self.description = (p.get("description", "") + (f"\n\n{hashtags}" if hashtags else "")).strip()
        self.tags = tags
        self.hashtags = p.get("hashtags", [])
        self.next_video = p.get("nextVideo", "")
        self.pinned_comment = p.get("pinnedComment", "")


def script(m: dict) -> Script:
    return Script(m)


def privacy(m: dict, configured: str) -> str:
    """The manifest may only make the upload MORE private than the repository setting, never less."""
    order = ["private", "unlisted", "public"]
    want = (m.get("publishingMetadata", {}).get("visibility") or configured).lower()
    return order[min(order.index(want) if want in order else 0, order.index(configured) if configured in order else 0)]


def chapters(m: dict) -> list[tuple[str, str]]:
    """[(title, firstSceneId)] for documentaries."""
    ids = {sc["sceneId"] for sc in m["scenes"]}
    return [(c["title"], c["firstScene"]) for c in m.get("chapters", []) if c.get("firstScene") in ids]
