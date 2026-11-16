---
name: director-manifest
description: Direct a video as Claude and let GitHub Actions render it. Use when writing the video manifest (story, narration per scene, scene types, camera, environment, objects and behaviours, on-screen text animations, sound cues, Hindi localization) for a dynamic Three.js Short or documentary, when validating one, or when extending the engine (new scene type, camera preset, text animation, transition or object type in shorts/director/engine/). The whiteboard explainer-diagram skill is the template look; this is the director-driven look.
---

# Director manifest (Claude directs, the workflow renders)

Read `shorts/CLAUDE_DIRECTOR_TASK.md`: it has the manifest shape, every registered preset, which visuals suit which
narration, the rules the validator enforces and how to start the workflow (`format: director` or
`director-documentary`, `manifest_json`).

Quick loop:

```bash
python -m shorts.director.run schema                                               # registered presets
python -m shorts.director.run --manifest-file m.json --validate-only               # errors + warnings
SHORTS_FAKE_TTS=1 python -m shorts.director.run --manifest-file m.json --langs en --dry-run --out /tmp/d   # local render (slow: software WebGL)
git checkout -- videos/ data/                                                      # a Short is always saved under videos/
```

Preview single frames without rendering a video: serve `shorts/director/` and call `window.setup(cfg)` then
`window.renderFrame(t)` (see `render.cjs`; `cfg` is what `build.engine_cfg` returns).

## Extending the engine

Everything under `shorts/director/engine/` is a pure function of time (no `Math.random()`, `Date`, CSS animation): frames
are rendered in parallel and in any order, and the same manifest must give the same video.

- **Scene type**: add an entry to `EXTRAS` in `sceneTypes.js`, to `SCENE_TYPES` there and in `manifest.py`, a default object list in `DEFAULT_OBJECTS`, a path in `pathFor` if it uses `follow-path`, and a row in `CLAUDE_DIRECTOR_TASK.md`.
- **Object type / behaviour**: `GROUP`, `layout`, `makeGeometry` and `behave` in `objects.js`, then `OBJECT_TYPES` / `BEHAVIORS` in `manifest.py`.
- **Camera preset**: `cameraPose` in `camera.js` (and `ALT_CAMERA`), `CAMERA_PRESETS` in `manifest.py`.
- **Text animation**: a `case` in `TextElement.update` (`text.js`), `TEXT_ANIMATIONS` in `manifest.py`.
- **Transition**: a branch in `MixShader` (`post.js`), the name in `TRANSITIONS` there and in `manifest.py` (the index + 1 is the shader `type`).
- **Environment**: `PRESETS` / `mk` in `environment.js`, `ENVIRONMENTS` and `ENV_BG` in `manifest.py`.
- Software WebGL is slow (about 0.5 s a frame): keep new effects cheap, no shadows, few lights, no extra full-screen passes.
