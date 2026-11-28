# Videosly Shorts: horror ("Quiet Dark") + mystery/crime ("The Fair Clue") - procedure (2 a day)

Owner decisions: 27 Nov 2026 (one horror Short a day by Videosly), 28 Nov 2026 (the connector now needs a composition; add a mysterious voice for horror; add a mystery and crime series; use `.claude/skills/dopamine-storyteller`).
The Videosly MCP connector (tools `mcp__Videously__videosly_*`) is called by Claude in the daily session; no workflow can. If the tools are missing or refuse, skip the step, say so, never fake a result.

**How it works now:** Videosly writes nothing. `videosly_generate_video` REQUIRES `composition` (narration + a caption per picture), `skill`, `title`, `description`. Claude writes all of it; Videosly draws the stills, records the voice and renders.
Two series, one video each per day (Videosly allows 2 YouTube posts a day, so keep it to these two):
| Series | skill | voice | look |
|---|---|---|---|
| Quiet Dark (horror, invented, bloodless) | `horror-story` | voice **Mortimer** (owner choice, 28 Nov 2026) for ALL horror videos, English and Hindi (`VIDEOSLY_HORROR_VOICE`; Videosly has no voice list tool: after generating, `get_scene` shows `voiceId`; if it is not Mortimer, say so) | skill's own dark cinematic horror look |
| The Fair Clue (invented mystery / crime, one fair clue, bloodless; episode numbered in the description) | `short-mystery` | Videosly default narrator (`VIDEOSLY_MYSTERY_VOICE` to pick one) | warm graphic-novel noir `visualStyle` set by `shorts.videosly` |

Real crimes (`case-file`) are NOT used: real victims and private people are off limits. Everything is invented: no real person, brand, place or event; no gore; no child in danger.

## Steps (start FIRST in the day: generating plus rendering takes 25-70 minutes, it overlaps with the batch)
1. `python3 -m shorts.videosly recent` (never repeat a topic). Invent ONE topic per series (horror: a person, an ordinary place, one wrong detail that follows ONE rule; mystery: a personal puzzle with a fair clue that has an innocent first meaning).
2. Read `videosly_get_skill` for the series skill once if you do not remember its rules, and `.claude/skills/dopamine-storyteller/SKILL.md`. Write the hook (3 variations, pick one), the loop ledger, then the composition: 140-175 words (about 60 s), paragraphs as `passage`, 12-14 pictures,
   every caption in the skill's order (framing, subject and action, surroundings, light) ending with the same `The place:` sentence, `references` for every recurring person, quoted text only where a numeral must read, nobody looking into the camera. Self-score the story (dopamine skill, ship at >= 11/14).
3. Save `{composition,title,description,hashtags}` to a json file and run `python3 -m shorts.videosly check-comp <horror|mystery> file.json` (it prints the exact `videosly_generate_video` arguments, with the series voice and look, or what to fix). Call `videosly_generate_video` with exactly those arguments.
4. Poll `videosly_get_video` (json) until `status` is "ready" (playable) and `mp4Status` is "completed" (`downloadUrl`). One waiting loop. `videosly_open_video` lists the scenes; `videosly_get_scene` shows the voice used.
5. Safety check only (gore or a child in danger: do not post, say why). The length never stops a post (owner decision 27 Nov 2026).
6. `meta.json` as before (title <= 65 characters, label it fiction, description >= 80 characters with 2-3 hashtags incl. #Shorts and "The Fair Clue, episode N" / "Quiet Dark" in the first line or the end, 5-8 tags), `python3 -m shorts.videosly check-meta meta.json`, `videosly_list_channels`, `python3 -m shorts.videosly post-args meta.json <videoId> <channelId>`, post (privacy `private` unless `VIDEOSLY_PRIVACY`, `aiGenerated` true).
7. `python3 -m shorts.videosly record entry.json` ({"series","topic","videoId","title","postId","privacy","duration_seconds","posted":true}); commit ONLY `data/videosly/history.json` to `main` (rule 7 exception).
8. Final summary: for each series the topic, title, duration, privacy, post status/URL, or why it was skipped.

Horror is produced in English AND Hindi (same story, `language` "hi", Devanagari narration, English captions, voice Mortimer); mystery stays English unless the owner asks.

## Honest limits
- Videosly's picture style and narrators are its own; Claude can set `visualStyle` and `voiceId` but cannot list the voices. AI-drawn stills are always labelled synthetic.
- Horror and mystery are tests: judge each on its own numbers after a week (views per day vs the channel median).
