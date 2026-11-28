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

## Hard rules (strengthened 28 Nov 2026)

### 1. Hook test (all must pass, else rewrite)
- First sentence <= 14 words, a concrete image or a broken fact (a number, a rule, a place that should not be). No "Have you ever", no "Today", no name-the-topic opener.
- A viewer who sees only the first line can state the question it raises.
- It never explains; it shows something wrong.

### 2. Loop ledger (write it before the script)
List every loop as `opens at beat N -> pays off at beat M`. Rules:
- Exactly ONE primary loop, opened in beat 1-2, paid in the last content beat.
- A micro-loop every 8-10 seconds (Shorts: every 2nd scene); each answer must open a bigger question, never a dead end.
- No loop is left open at the end except the one deliberate echo. Nothing opened is forgotten.
- No stretch of more than 10 seconds without a new fact, image, question or turn.

### 3. Reversal types (pick one, name it in `Loops:`)
Wrong-culprit (it was not who/what we thought) / hidden constraint (a rule revealed late) / scale flip (far bigger or smaller) / self-reference (it was about the viewer or the narrator) / cost reveal (the "win" has a price). The reversal must be seeded by a detail planted earlier (a fair clue), landing at 55-70% of the runtime, never in the last 2 seconds.

### 4. Specificity and sensory craft
- Replace every adjective-emotion with an action, number, object or sound ("his hands shook at 0:09", not "terrified").
- One precise detail per beat (badge, date, humming), no stock phrases ("little did he know", "suddenly", "a chill ran down", "in a world where").
- Vary sentence length: short for the turn, one longer sentence of texture before it.
- Second person and rhetorical questions at most twice per script.

### 5. Endings
Pick one: implied (the viewer does the maths) / echo (last line reframes the first) / earned reveal (answer to the primary loop plus one new question). Never explain the twist after delivering it; never end on a moral or a summary; for explainers end with the answer, the one-line reframe, then the next-video question.

### 6. Explainer and Myth Buster adaptation
Hook = the belief or paradox stated as fact; "But" turn by scene 3; mechanism told as cause -> effect ("because ... therefore ..."), never "and then"; the reframe is a sentence the viewer can repeat to a friend. Long-form: each chapter ends by opening the next chapter's question.

### 7. Banned (the storycheck flags these)
Throat-clearing, greetings, "In this video we'll explore", filler transitions, rhetorical question stacks, explaining the joke, hedges ("perhaps", "somewhat"), three-item lists by reflex, "delve", "tapestry", "journey", "unlock", and any sentence that does not move a loop.

### 8. Self-score before shipping (0-2 each, ship only at >= 11/14)
Hook image / Primary loop / Micro-loop cadence / Reversal fairness / Specificity / Ending trust / Zero fluff. Record the score and the one weakest line you fixed in `Loops:` (plan) or `history.json` note (Videosly).

### 9. Safety (always wins)
Horror: invented, bloodless, no child in danger, no real person/brand/place, labelled fiction. Explainers: two sources per claim, no medical/finance/legal advice. Dopamine craft never justifies a false claim, a misleading title or a fake cliffhanger the video does not pay off (clickbait without payoff is a policy and retention risk).
