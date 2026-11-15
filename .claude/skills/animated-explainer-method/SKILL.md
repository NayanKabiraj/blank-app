---
name: animated-explainer-method
description: The "Claude-made animated explainer" method studied from the Grow With Kaz YouTube channel (faceless 3D and character-animation explainers built entirely in code, with no AI video generators), adapted to this repo's daily Shorts pipeline. Use when choosing a niche or sub-niche, generating video ideas, writing the narration of a plan (hook, story beats, wit, analogy), directing the visuals scene by scene, or planning a longer animated explainer. Pairs with the explainer-diagram skill (the renderer).
---

# Animated explainer method (studied from @GrowWithKaz)

Grow With Kaz (about 113k subscribers in Nov 2026) teaches people to run faceless channels.
In November 2026, its fastest-growing uploads all show one workflow: getting Claude Code to
draw **every frame of an animated explainer in code** (three.js for 3D, Remotion for
captions, audio and the final render) instead of paying for AI video tools. The examples
cover money/psychology explainers with stick figures, prehistoric sea creatures, map
animations and wordless short films. Each took about 10–45 minutes to generate.

This repo has the rendering half: the one and only look of the channel is the **whiteboard explainer** (a hand
drawing marker diagrams, a smiling sun, chat bubbles, quizzes, drawn by code in `shorts/explainer/`, see the
`explainer-diagram` skill). This skill covers the other half, the part that makes these videos get
watched: the niche, the idea, the script, and how each line becomes a visual.

## The workflow, as the channel teaches it

1. **Run a "master prompt"** that proposes niches and **untapped sub-niches** that suit
   animation (psychology, money, history, science, what-if, animals, survival,
   self-improvement).
2. **Pick one sub-niche and generate about 10 video ideas**, each with a one-line story
   summary. Pick the strongest one.
3. **Choose a length** (Shorts: 45–55 s; long: 3, 6, 10 or 15 min. Rendering takes roughly
   an hour per 10 minutes).
4. **Generate the script.**
5. **Make the voice-over** in parts (they use ElevenLabs; this repo uses `shorts/tts.py`).
6. **Feed the script and voice-over to the animation skill**, which builds scenes timed to
   the narration. Long videos are done part by part.
7. **Add sound effects and music, then render.** Adjust the character style or colours by
   asking Claude for alternative designs with visual examples.
8. **Stick to one recognizable style per channel.** "Pick one broad niche, find a unique
   sub-niche within it, and build your channel around that." Don't clone the channel
   you learned from.

The style skill itself was built by **studying reference videos frame by frame** (screenshots
of characters, motion, transitions, palette) and writing those rules down. Do the same when
adding a new look here: capture frames, list what is consistent, and encode it in
`scene.js` as layouts plus written rules in `explainer-diagram`.

Use the prompt in `references/master-prompt.md` for steps 1–4. It's written for this repo's
plan format.

## Script craft (what the narration in their examples does)

These patterns come from the narration of the videos they made on the channel. Details and
worked examples are in `references/script-patterns.md`.

- **Open on a concrete, surprising claim, not a definition.** "For years, one number
  supposedly explained how much money you needed to be happy: seventy-five thousand
  dollars." / "One of the most feared hunters of its world opened its mouth. And there were
  no teeth inside. There were blades."
- **Set the scene with a time and place** when the topic has one ("About three hundred and
  sixty million years ago, in a warm, shallow sea that once covered what is now Ohio…").
- **Add one dry, witty line per minute** that lands the point: "Congratulations, your
  emotions had a salary cap." / "You can be proud of your career while spending Tuesday
  arguing with a printer."
- **Use a twist or "then someone checked" beat**: the old answer, then new evidence that
  changed it ("Then in twenty twenty-three, a study compared…"). It keeps people watching
  past the halfway point.
- **Back the twist with named, checkable specifics**: who, which year, how many (450,000
  survey responses; nearly a thousand fish species). Never invent them.
- **Define each term in the same breath**: "an armored fish from a group called placoderms."
- **Make abstract ideas physical with an analogy**: "like a knight's helmet fused to a chest
  plate."
- Keep sentences short and spoken. One idea per sentence, so each sentence can be a shot.

For this repo's Shorts, fit those beats into the explainer structure in
`shorts/CLAUDE_DAILY_TASK.md`: hook → short answer → mechanism → number → analogy → close.
The wit line usually fits after the short answer or the number, and the twist goes in the
mechanism.

## Visual direction (one sentence = one shot)

Every line of narration should have something on screen that *acts it out*, not just text:

| Narration beat | What the animation does | Plan field in this repo |
|---|---|---|
| Hook claim | The icon pops in with burst lines | `title` + `prop` |
| Question to the viewer, "you ask, I answer" | A text-message exchange: viewer bubble, typing dots, answer bubble | `chat` (2-4 bubbles) |
| "Think you know?" | A multiple-choice question, a countdown, then the right option lights up | `quiz` (+ `answer`) |
| A common belief that is wrong | The myth is struck out, the truth stamps in | `myth` |
| Name/term + definition | Icon in a turning ring, one-line caption | `keyword` + `prop` |
| Process / "how" | Numbered nodes light up, or dots flow from A to B | `steps`, `flow`, `build`, `cycle` |
| Number | Counter ticks up, ten dots fill | `stat` (verified number) |
| Several things measured against each other | Bars grow to their values | `bars` |
| Two speeds / two rates | Dots race along two lanes, counters show who arrives | `race` |
| Old vs new / two sizes | Two discs, area follows the values | `compare` (+ `values`) |
| Close | Icon returns, a question for the comments | `keyword` or `title` |

Rules carried over from the channel's style:
- **One guiding character** carries the story: here a smiling sun moves from scene to scene.
- **Movement in every scene**, with smooth transitions and no static slides. Everything in
  `scene.js` is animated as a function of `t`.
- **Simple marker shapes, a limited palette, pastel fills**: readable on a phone at a glance. The accent colour follows the niche.
- **Captions on screen**, plus **sound effects** on reveals (pop, bell). Background music matches `mood`.
- If a topic would really benefit from a new layout or icon, add it (see "Extending" in `explainer-diagram`)
  rather than forcing a poor match.

## Make it a conversation

People stay for a *dialogue*, not a lecture. Every script should:
- ask the viewer something in scene 1 or 2 ("Weird, right?", "Ever felt this at a scary scene?"),
- answer its own questions out loud and let a `chat` scene play the question-and-answer,
- challenge the viewer once with a `quiz` ("Quick quiz: ...") or a `myth` ("Think it's X? That's the myth."),
- ask for a guess before the number ("Guess how many..."),
- end by asking the viewer something they can answer in the comments ("Which one is you? Tell me below!").
`shorts.plan validate` checks for this (3+ questions, one early, a question at the end, a chat/quiz/myth scene).

## Niche advice for this channel

The channel's niches (`shorts/niches.py`) already suit this style. When choosing topics,
favour the ones the channel shows doing best in animation:
- **Money and psychology "why" questions** (why people stay broke, how inflation hits daily
  life, the happiness-and-income study). Use them as explainers only, never as financial
  advice.
- **Strange animals, prehistoric creatures and sea life**, told as a mini-story with a reveal.
- **History and science what-ifs**, with a time-and-place opening.
Rotation and the "already covered" rule in the daily task still apply.

## Longer animated explainers (beyond Shorts)

To make a 3–10 minute version, the channel's approach scales up:
1. Write the full script, then split it into 2–3 parts of about 1.5–3 minutes each.
2. Generate the voice-over per part and build the scenes per part, timed to the audio.
3. Review each part before generating the next one, then join them and add sound effects.
The current pipeline (`shorts/plan.py`) validates 40–59 s plans only, so a long format needs
its own plan model and compose step before it can be automated.

## Source

Studied on 2026-11-14 from Grow With Kaz (`@GrowWithKaz`, channel ID
`UCnGPmAcR-LCVm_TPxQ633Xw`), mainly these transcripts:
- "I Made VIRAL Animation Videos Using Claude Code (FREE Plugin)", `3tpaWHaiLQ8`
- "I Made Viral NEW AI Animation Videos Using ONLY Claude (FREE Plugin)", `Yj5LpSq_7xI`
- "This AI YouTube Niche Is EXPLODING! (Make Videos With Claude Code/Free Plugin)", `Ock60o-Glh4`
Their downloadable plugins and master prompts were not used. The prompt in `references/`
was written fresh for this repo from the steps they describe.
