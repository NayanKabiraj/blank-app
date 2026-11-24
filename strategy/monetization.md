# The channel's goal: grow and monetize (owner instruction, 24 Nov 2026)

Every video, plan and tool change must serve ONE goal: **subscribers and watch time that qualify the channel for the YouTube Partner Program (ads), safely and for the long run.** A task that does not
help that goal (or protect it) is not the priority. Each plan's `research_summary` carries a `Growth:` line (the validator requires it).

## What "monetized" needs (YouTube Help, checked 24 Nov 2026 via web search; verify in YouTube Studio -> Earn)
- Fan-funding tier: 500 subscribers (+ 3 public uploads in 90 days and either 3,000 public watch hours in 12 months or 3 M public Shorts views in 90 days - details on the Help page).
- Ads tier: **1,000 subscribers AND (4,000 public watch hours in 12 months OR 10 M public Shorts views in 90 days)**.
- Third-party reports (Metricool, Digital Trends, not verified against YouTube's own page) say these rise on **1 Feb 2027 to 8,000 watch hours or 20 M Shorts views**: if true, the window to qualify under the lower bar is short. Treat subscribers as the bottleneck either way.
- Only public views and watch time count (the channel's uploads are public; `channel_trends` flags any video that is not).

## Where the channel stands (24 Nov 2026, `python -m shorts.channel_trends summary` -> `monetization`)
- 47 subscribers (953 to 1,000); about 5 watch hours in the last 28 days (12-month pace at that rate: about 65 h vs 4,000); 1,789 Shorts views in 28 days (vs 10 M in 90 days); **about 1.1 subscribers per 1,000 views**.
- Reading: views are far too few and almost none convert to subscribers. Reach (impressions, retention) and conversion (a reason to subscribe) both have to move; neither is solved by uploading more of the same.

## Policy guardrails (a channel that breaks them is removed from the Partner Program, however many views it has)
- **Inauthentic content (mass-produced / repetitive / template-like)** - YouTube's July 2025 rename of "repetitious content", clarified again July 2026 (TechCrunch, Tubefilter, TechRepublic): channels built on easily mass-produced, template-based videos
  with little variation lose monetization whether or not AI is used; AI for scripting/editing/animation is allowed when the videos give unique value. **So: every video needs its own angle, script and hand-built animation; vary structure
  (question, story, what-if, myth-bust, countdown, mystery); never ship two videos that differ only by topic; a day's 6 uploads are 3 different videos in 2 languages, not 6 clones.** The 6-a-day target is capped by this rule as well as by quota.
- **Off-putting / emotionally manipulative content**: story Shorts stay bloodless suspense with a twist, no shock bait, no real victims, labelled fiction.
- **Synthetic personas on sensitive topics**: no health, medical, legal or financial advice (concept explainers only).
- Sources and facts verified (rule 4); no reused footage; synthetic-content label as configured (`YT_AI_DISCLOSURE`).

## Growth levers every video must pull (write which one in `Growth:`)
1. **Hook and retention** (reach): the viewer's own life in 2 seconds, payoff by ~22 s, a looping last line (`learnings.md` rules 1-2).
2. **A reason to subscribe** (conversion): a series promise inside the first 20 s ("follow for part 2 / the next question"), `next_video` set and answered in the pinned comment, the `cluster` name consistent so the video is one episode of a recognisable series.
3. **Series and cluster depth**: 3+ videos per cluster (e.g. "How AI Thinks", "The Moon"), each linking to the next; return viewers are the subscribers.
4. **Packaging**: title <= 65 characters with a concrete object or number, one thumbnail question with the face (CTR); test and keep what wins.
5. **Consistency**: one look (vox), one voice, a regular schedule so the channel is recognisable.
6. **Owner-side (not automatable from here)**: a clear channel trailer, banner and about text, playlists per cluster, replying to comments, community posts. Ask the owner when this is the bottleneck.

## Milestones and the weekly report
Ladders live in `strategy/milestones.json` (subscribers 50 -> 1,000, public watch hours 100 -> 4,000, Shorts views 10 k -> 10 M, best video, subscribers per 1,000 views, Shorts viewed %, upload streak). Every Sunday 21:00 IST `weekly-report.yml` writes `reports/progress-<date>.md` and opens a GitHub issue with it (phone notification); `python -m shorts.progress milestones` prints the status any time.

## Weekly review (the Sunday run writes one dated line in `learnings.md` Evidence)
Subscribers gained and per 1,000 views, public watch hours, Shorts views, the best 3 and worst 3 videos and why, and whether the guardrails above were respected. If subscribers per 1,000 views stay under about 2 for two weeks, change the conversion
levers (not the upload count) before anything else.
