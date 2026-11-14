---
name: animated-explainer-method
description: The "Claude-made animated explainer" method studied from the Grow With Kaz YouTube channel (faceless 3D and character-animation explainers built entirely in code, with no AI video generators), adapted to this repo's daily Shorts pipeline. Use when choosing a niche or sub-niche, generating video ideas, writing the narration of a plan (hook, story beats, wit, analogy), directing the visuals scene by scene, or planning a longer animated explainer. Pairs with the cartoon-explainer skill, which covers the renderer itself.
---

# Animated explainer method (studied from @GrowWithKaz)

Grow With Kaz (about 113k subscribers in Nov 2026) teaches people to run faceless channels.
In November 2026, its fastest-growing uploads all show one workflow: getting Claude Code to
draw **every frame of an animated explainer in code** (three.js for 3D, Remotion for
captions, audio and the final render) instead of paying for AI video tools. The examples
cover money/psychology explainers with stick figures, prehistoric sea creatures, map
animations and wordless short films. Each took about 10–45 minutes to generate.

This repo already has the rendering half (`shorts/cartoon3d/`, see the `cartoon-explainer`
skill). This skill covers the other half, the part that makes these videos get watched: the
niche, the idea, the script, and how each line becomes a visual.

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
`scene.js` as props/layouts plus written rules in `cartoon-explainer`.

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
| Hook claim | Hero object appears big and moves (spin, pop, reveal) | `title` + `prop` |
| Name/term + definition | Object on a pedestal, label and one-line caption | `keyword` + `prop` |
| Process / "how" | Character hops through numbered steps as each lights up | `steps` (2–4 items) |
| Number | Counter ticks up while a pile or bar grows to scale | `stat` (verified number) |
| Old vs new / before vs after | Two things side by side, bars rise | `compare` (+ `values`) |
| Analogy | Everyday object stands in for the idea | `keyword` with a matching `prop`, or `compare` |
| Close | Hero object returns, takeaway + follow line | `title` |

Rules carried over from the channel's style:
- **A consistent mascot or character** drives the story across scenes (here: the coral
  mascot). Keep its look stable and let it react: hop on steps, wave on the close.
- **Movement in every scene**, with smooth transitions and no static slides. Everything in
  `scene.js` is animated as a function of `t`.
- **Simple shapes, a limited palette, bold outlines**: readable on a phone at a glance.
- **Captions on screen**, plus **sound effects** on reveals (pop, whoosh, coin tick) when the
  pipeline supports them. Background music matches `mood`.
- If a topic would really benefit from a new prop or layout, add it (see "Extending the
  style" in `cartoon-explainer`) rather than forcing a poor match.

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
