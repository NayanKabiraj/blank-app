# Videosly horror Short (1 a day) - procedure

Owner decision (27 Nov 2026): one horror Short a day is made by **Videosly** and posted to the channel. This is the ONLY horror content (the code-made horror niche stays dropped). Videosly is an MCP
connector (tools `mcp__Videously__videosly_*`), so Claude runs these steps in the daily session; no workflow can. If the Videosly tools are missing or refuse (sign-in), skip the step, say so in the final summary, do NOT fake a result.

**What Claude sends: a topic only, as a `prompt`.** Never a `script`, a `composition`, a `content` or a title: Videosly writes the story with the `horror-story` skill, draws the pictures in its own horror look and records the voice.
**What Claude writes itself:** the title, description and tags (from the finished story), and the post.

## Steps
1. `python3 -m shorts.videosly recent` (never repeat). Invent ONE new topic: one line = a person, an ordinary place, and the one thing that is wrong (e.g. "A night-shift guard in an empty office tower notices the lift keeps stopping on a floor that has no button"). Everything invented: no real person, place, brand or event; bloodless; no child in danger; suspense, not gore.
2. `python3 -m shorts.videosly request "<topic>"` -> prints the exact arguments (prompt = "A horror story. <topic>.", skill horror-story, duration medium = 60 s, 9:16). It refuses a topic with gore, a child, a real brand or a repeat. Call `videosly_generate_video` with exactly those arguments (nothing added). Start this FIRST in the day: generating plus rendering takes 25-45 minutes, so do it while the daily batch renders.
3. Poll `videosly_get_video` (json) every few minutes with ONE waiting loop: `playable` becomes true first, `status` "completed" gives `downloadUrl` (the file). Then `videosly_open_video` to read the finished story (the scenes' `script`) and the duration (recorded, not gated).
4. Check the story only for safety: if it shows gore/gross content or a child in danger, do not post (say why, keep the video id, ask the owner). The LENGTH never stops a post (owner decision 27 Nov 2026): whatever length Videosly rendered goes to YouTube; just record it.
5. Write `meta.json` (title <= 65 characters naming the creepy detail without spoiling the end, description 150-300 characters whose first sentence stands alone, says it is a fictional AI-made story, with 2-3 hashtags including #Shorts, 5-8 tags) and run `python3 -m shorts.videosly check-meta meta.json`.
6. `videosly_list_channels` -> the active YouTube channel (CuriousLoop). `python3 -m shorts.videosly post-args meta.json <videoId> <channelId>` prints the exact `videosly_post_video` arguments (privacy `private` by default: rule 6; the owner changes it with the env var `VIDEOSLY_PRIVACY` = public | unlisted | private; `aiGenerated` stays true). Post. Videosly allows 2 YouTube posts a day.
7. Record it: `python3 -m shorts.videosly record entry.json` with {"topic","videoId","title","postId","privacy","duration_seconds","posted":true}; commit ONLY `data/videosly/history.json` straight to `main` (owner-authorised exception to rule 7).
8. Final summary line: topic, title, duration, privacy, post status/URL (from `videosly_list_posts` if it shows one), or why it was skipped.

## Honest limits
- The picture style and voice are Videosly's own defaults for the skill; Claude cannot list or pick them. It is AI-drawn stills (always labelled as altered/synthetic content).
- Horror was this channel's weakest niche by views (see learnings); this is a one-a-day test, judged on its own numbers after a week.
