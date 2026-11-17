# Director task: Claude directs, GitHub Actions renders

In **director mode** Claude is the creative director. It researches the topic, writes the story, the narration, the
scene-by-scene visual direction (scene type, camera, environment, objects and how they move, on-screen text and its
animation, sound cues) and hands that to the workflow as **one JSON manifest**. The workflow does everything
mechanical: it voices the narration (same Piper voices as before), rebuilds the timeline around the real speech, renders
the scenes with the Three.js engine in `shorts/director/engine/`, mixes voice, music and sound effects, and uploads
(private by default). Claude never writes Three.js code: it only picks from the engine's registered presets.

Nothing is a fixed template. Every scene is built from the manifest's seed and the director's choices (camera path,
particle counts, behaviours, text animation, transitions), so two videos on the same topic do not look alike.

Works for **Shorts** (1080x1920, 30 fps, about 45-59 s) and **documentaries** (1920x1080, 24 fps, 5-10 min), in
**English and Hindi** from the same manifest (`localizations.hi`).

## Steps

**Strategy:** apply the `video-strategy` skill (research evidence, title test, thumbnail concepts, 30-second rule, retention, QA gate).
Every manifest carries a designed **thumbnail**: `"thumbnail": {"headline": "1-4 big words", "concept": "why it works",
"sceneType": "object-assembly", "environment": "holographic-room", "accentWords": {"WORD": "#FFCC33"}}` plus
`localizations.<lang>.thumbnailText`. The title explains the premise, the thumbnail shows the consequence (never the same words). The
workflow renders it with the engine (1280x720, or 720x1280 for Shorts), uploads it with the video and keeps it in the upload queue when
YouTube refuses the video.

1. **Topic and research.** Same as the daily task (`CLAUDE_DAILY_TASK.md` steps 1-3 for a Short,
   `CLAUDE_DOCUMENTARY_TASK.md` for a documentary): check `data/history.json` / `data/documentary_history.json`, pick a
   topic, verify every number with two sources. Never put an unchecked fact in the narration.
2. **Write the manifest** (below). Start from `shorts/director/examples/ai_agents_short.json` (Short) or
   `shorts/director/examples/gps_documentary.json` (documentary: shorter than a real one, but the right shape).
3. **Validate it** before sending: `python -m shorts.director.run --manifest-file m.json --validate-only`. Errors stop
   the render (unregistered preset, scene too long, text too long, same scene type twice in a row...); warnings are advice.
   Fix everything you can. `python -m shorts.director.run schema` lists every registered preset.
4. **Start the workflow** `daily-shorts.yml` on `main` with
   `format: director` (Short) or `format: director-documentary`, `manifest_json: <the whole JSON>`, `langs: en,hi`.
   Leave `dry_run` off for the daily run (the upload stays **private** unless the repository variable says otherwise;
   a manifest can only make it more private, never less). Shorts are saved in `videos/<date>/`, documentaries are
   workflow artifacts (add `keep_in_repo: true` to also commit them).
5. Check the run's log: the engine prints `Manifest check:` warnings, a preflight (a sparse test render that reports text
   that does not fit) and the quality checks (black or frozen frames, loudness). The artifact contains `render-report.json`,
   `thumbnail.jpg`, `contact-sheet.png` and `captions.srt` per language.

## The manifest, compact form

Only the parts in **bold** are required; everything else is filled in deterministically from `randomization.globalSeed`
(camera presets that never repeat back to back, transitions, environments, lights, default objects for the scene type).
Write the rest whenever the story wants a specific choice.

```jsonc
{
  "schemaVersion": "1.0.0",
  "job": { "jobId": "ai-agents-20261116" },
  "creativeBrief": {
    "topic": "...", "niche": "Technology",            // niche: a name from shorts/niches.py
    "format": "short" | "documentary",               // documentary => 1920x1080, 24 fps, relaxed pacing rules
    "targetDurationSeconds": 55,
    "visualStyle": { "tone": ["cinematic", "energetic"] }    // picks the music mood
  },
  "randomization": { "globalSeed": 184276 },          // same seed + same manifest = the same video
  "story": { "title", "hook", "openLoop", "payoff", "callToAction" },
  "chapters": [ { "title": "...", "firstScene": "scene-004" } ],            // documentaries: YouTube chapter markers
  "scenes": [ {
      "sceneType": "network-nodes",
      "storyPhase": "hook|problem|context|development|reveal|payoff|call-to-action",
      "narration": { "text": "What the voice says in this scene." },
      "textElements": [ { "text": "AI WAITS", "animation": "tracking-reveal",
                          "style": { "accentWords": { "WAITS": "#FFCC33" } } } ],
      // optional direction:
      "camera": { "preset": "push-orbit", "target": "central-node", "speed": 0.4 },
      "environment": { "preset": "data-network", "fogDensity": 0.1, "backgroundMotion": "drift" },
      "objects": [ { "id": "central-node", "type": "sphere", "count": 1, "behavior": "pulse", "color": "#775CFF", "audioReactive": true } ],
      "sceneParams": { "dormantUntil": 0.5 },
      "soundEffects": [ { "assetId": "impact-deep-01", "atSeconds": 0.2, "volume": 0.8 } ],
      "transitionOut": { "type": "light-sweep", "durationSeconds": 0.5 }
  } ],
  "publishingMetadata": { "title", "description", "tags": [], "hashtags": [] },
  "localizations": { "hi": { "title", "description", "tags", "chapters": [],
      "scenes": { "scene-001": { "narration": "...", "text": { "<textElement id>": "..." },
                                 "accentWords": { "<textElement id>": { "शब्द": "#FFCC33" } } } } } }
}
```

Every scene is **spoken**: the narration is the clock. The workflow synthesizes it, then moves each scene to start just
before its first word and keeps texts and sound cues at the same relative position inside the speech. So you never have to
guess timings: `startSeconds`/`durationSeconds` are optional and only a rough plan. Do give `textElements[].id` when you
localize (so the Hindi text can be matched), and a Hindi entry for **every** scene (the render fails without it).

### Registered presets (the engine only knows these)

| field | values |
|---|---|
| `sceneType` | `kinetic-typography` `particle-world` `geometry-swarm` `data-tunnel` `procedural-grid` `object-assembly` `diagram-3d` `image-parallax` `timeline-3d` `wave-field` `network-nodes` `finale` |
| `camera.preset` | `static-drift` `slow-dolly-in` `fast-dolly-in` `dolly-out` `orbit-left` `orbit-right` `crane-up` `crane-down` `fly-through` `whip-pan-left` `whip-pan-right` `handheld-subtle` `follow-target` `push-orbit` `macro-push` `parallax-slide` (plus optional `camera.sequence: [{from: 0.5, preset}]`; scenes over 6.5 s glide into a second preset on their own) |
| `objects[].type` | `particles` `sphere` `central-control-orb` `network-node` `decision-node` `approval-gate` `icosahedron` `torus` `tetrahedron` `columns` `light-bars` `instanced-code-blocks` `task-nodes` `workflow-blocks` `timeline-nodes` (anything else draws a placeholder) |
| `objects[].behavior` | `float` `pulse` `rotate` `assemble` `explode` `scatter` `swarm` `spiral` `orbit` `wave` `fall` `rise` `magnetize` `follow-path` `react-to-audio` |
| `textElements[].animation` | `word-punch` `kinetic-sentence` `character-scatter` `typewriter` `tracking-reveal` `mask-reveal` `impact-zoom` `particle-assemble` `depth-reveal` `word-stack` `slide-and-lock` |
| `transitionOut.type` | `particle-dissolve` `camera-fly-through` `geometry-wipe` `zoom-tunnel` `whip-pan` `object-occlusion` `grid-collapse` `light-sweep` `depth-push` `match-motion` `fade-through-black` (the last scene fades to black) |
| `environment.preset` | `dark-tech` `neon-grid` `particle-space` `data-network` `abstract-dark` `energy-tunnel` `minimal-light` `digital-city` `wave-space` `holographic-room` |

### Choose the visuals so they act out the sentence (semantic animation)

| the narration is about... | scene type | objects + behaviour that say it |
|---|---|---|
| the hook, a bold claim | `kinetic-typography` | `particles` `explode`, text `impact-zoom` / `word-punch`, `fast-dolly-in` |
| a flow of data or code | `procedural-grid` | `instanced-code-blocks` `follow-path`; the red "reject" slash lands at 55 % |
| a system that waits, then reacts | `network-nodes` | `sphere` + `network-node` `float`; `sceneParams.dormantUntil` lights the centre mid-scene |
| something being built or revealed | `object-assembly` | `icosahedron` `assemble` + `torus` `orbit`, text `particle-assemble` |
| one thing splitting into many steps | `data-tunnel` | `task-nodes` (a growing task tree) + `particles` `follow-path`, `fly-through` |
| a loop or workflow | `diagram-3d` | `workflow-blocks` `pulse` (a spark travels round; blocks light in turn) |
| a person or team in control | `geometry-swarm` | `central-control-orb` `pulse` + `tetrahedron` `swarm` |
| value moving, growth, comparison | `wave-field` | `columns` `wave` (a few columns rise and glow at 60 %) |
| a list of things that matter | `kinetic-typography` | `light-bars` `rise`, text `kinetic-sentence` |
| a history, a roadmap, "then... later..." | `timeline-3d` | `timeline-nodes` `follow-path`, `follow-target` camera |
| decisions, approval, review | `network-nodes` | `approval-gate` + `decision-node` `magnetize` (some are sent back in red) |
| the close, the call to action | `finale` | `particles` `magnetize`, text `particle-assemble` |

`sceneParams` (optional, per scene): `dormantUntil` (0-1, network scenes: the centre node stays dark until then), `reject`
(0-1, network scenes with an `approval-gate`: share of decisions that are turned down).

### Rules the validator checks (and the viewer feels)

- **Shorts**: hook within 2.5 s; scenes 1.5-6 s; at most 3 text elements per scene and 8 words per element; narration at most
  165 words per minute; a pattern interrupt about every 7 s and a visual change every 3 s; an open loop in the hook that is
  closed before 55 s; story phases hook, problem, context, development, reveal, payoff, call-to-action in that order;
  no scene type, camera preset or transition twice in a row; at least 5 scene types; legible text (contrast 4.5+).
  Keep the whole narration to about 100-125 words so the real voice finishes under 59 s (Hindi: about 85-105).
- **Documentaries**: scenes 2.5-14 s (aim for 6-10 s, one or two sentences), chapters every 1-2 minutes (at least 3, listed in
  `chapters`), at least 7 scene types, a new on-screen idea at least every 6 s, a real ending that answers the opening
  question. 5-10 minutes: about 35-75 scenes. Verified facts only; mark approximations ("about", "roughly").
- **Text** is short and big: an element is a label, a number or a slogan, never a sentence. Use `accentWords` on the one
  word that matters. Uppercase is automatic for English.
- Everything is spoken in both languages. Hindi: natural spoken Hindi, numbers as words in narration, Latin digits fine in on-screen text.
- Do not use third-party logos, copyrighted characters or flashing effects. Explainers only, never financial or medical advice.

## What the pipeline does (so you know what to expect)

1. `shorts.director.manifest` completes and validates the manifest. Errors stop the run before any rendering.
2. Narration: each scene is voiced with the usual TTS (`shorts/tts.py`, Piper by default, Parler if enabled), and
   fitted to the length window the same way the template videos are.
3. Timeline: scene boundaries follow the speech; texts and sound cues keep their place relative to the words.
4. `shorts/director/engine` renders every frame in headless Chromium (software WebGL), deterministic and parallel:
   camera, particles, 3D objects, bloom, transitions, per-word captions. The 3D world is drawn at 70 % (Shorts) or
   55 % (documentaries) of the output size and upsampled; text and captions are always full resolution.
5. Audio: the narration, music (ducked under the voice, beat grid shared with the picture) and sound effects from
   the cues, normalized to about -16 LUFS. Audio-reactive objects follow the voice's loudness.
6. Quality control and deliverables: black/frozen-frame and loudness checks, thumbnail, contact sheet, captions, report.

Rendering time on a GitHub runner: a Short takes about 15-20 minutes per language, a documentary about 12 minutes of
rendering per minute of video per language (a 6-minute documentary is about 75 minutes per language). The job limit is 6 hours.
