---
name: dopamine-storyteller
description: Crafts high-retention stories, scripts, and narratives engineered around curiosity gaps, open loops, rising stakes, and dopamine-driven anticipation. Use whenever the user asks to write a story, video script, hook, thread, case study, or narrative content designed to hook and hold viewer attention.
---

# Dopamine-Driven Storytelling

## Core Objective
Engineer every story around **anticipation and open loops**. Viewer attention and dopamine peak not just at the final resolution, but during the active prediction phase: when the audience senses a gap between what they know and what they need to find out.

## Mandatory Story Architecture
Follow these five stages in sequence for every narrative:

1. **The Pattern-Interrupt Hook (First 3 Seconds / First 2 Sentences)**
   - Open *in medias res* (middle of action), with a bold contradiction, a high-stakes dilemma, or a vivid sensory detail.
   - **Rule:** Never open with background context, throat-clearing, greetings, or generic introductions.
2. **The Open Curiosity Loop**
   - Plant an explicit or implicit unanswered question immediately after the hook.
   - Give the audience a specific outcome to anticipate (e.g., *"He had 14 minutes to fix a mistake nobody knew he made"*).
   - Keep this primary loop open until the climax.
3. **Escalating Stakes & Micro-Loops**
   - Introduce clear consequences: what the protagonist stands to lose or gain.
   - Layer smaller **micro-loops** every 2-3 paragraphs or beats: resolve one small question while immediately opening a bigger one.
   - Alternate pacing: fast, punchy sentences for momentum, then slow down with sharp sensory details right before a turning point.
4. **The Pattern Break / Reversal**
   - Subvert the audience's expected prediction at the midpoint or climax.
   - Introduce a complication, hidden constraint, or perspective shift that forces the audience to recalculate what happens next.
5. **The Earned Payoff & Echo**
   - Close the main curiosity loop cleanly and decisively.
   - End with a resonant final line, insight, or lingering question that leaves a lasting impression.

## Strict Constraints
- **Show, don't summarize:** Replace abstract emotions (*"he was terrified"*) with concrete physical actions or stakes (*"his hands shook as the countdown hit 0:09"*).
- **Zero fluff:** Cut any sentence that does not advance tension, reveal character, or deepen the curiosity gap.
- **Format adaptation:** Automatically adapt length, pacing, and beat markers to the requested medium (e.g., short-form video script, long-form article, brand story, or fiction).

## Output Format
When generating a story, structure your response cleanly as follows:
1. **Hook Variations (3 Options):** Provide three distinct opening angles (e.g., *In Medias Res*, *Contrarian/Twist*, *High-Stakes Question*) before committing to the strongest one.
2. **The Story / Script:** Deliver the full narrative cleanly without mid-story commentary.
3. **Retention Breakdown (Brief):** Bullet the primary open loop, the midpoint pattern break, and where the payoff lands.

## How this repository uses it (owner instruction, 28 Nov 2026)
- Applies to EVERY narration Claude writes: Shorts, documentaries (per chapter: each chapter opens a loop the previous one planted), Myth Busters, and Videosly horror (see below). Combine with `strategy/story-craft.md` and `shorts.storycheck`.
- In the pipeline the three hook variations and the retention breakdown go in the plan's `research_summary` (`Hooks:` line = the 3 variations and the pick; add `Loops:` = primary loop, midpoint reversal, payoff scene). The narration itself carries no commentary. The pipeline adds the closing line; never write it.
- Budget fit: Short hook <= 14 words, scene 2 intro <= 22 words, the reversal lands around scene 3-4 (myth: "That's false."), the payoff in the last content scene.
- Videosly horror: the topic prompt is still topic only (rule 22), but phrase the topic with a built-in open loop and reversal ("a lift stops on a floor that has no button" - the question is the topic). When the write-the-story route is in use, write the story with the five stages; a story read back from Videosly is judged against them for the notes in `history.json`.
