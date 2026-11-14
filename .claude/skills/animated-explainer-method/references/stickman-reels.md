# Stickman explainer reels

Stick-figure explainers are the other big faceless format, next to 3D cartoons. Grow With
Kaz covers it in "How to Make VIRAL Stick Figure Animation for YouTube Faceless channel
($200/Day)" (`gGx6GFrZMGM`, about 212k views, Feb 2025). In the Claude Code tutorial
(`3tpaWHaiLQ8`), the default character options Claude offered were "stick figure styles"
and "more detailed humanoid" designs. A case study cited in search results describes a
channel built on deliberately crude MS Paint stick figures with a strong script.

Sources for this file: the Kaz transcripts listed in SKILL.md, plus web-search summaries of
stickman tutorials, style guides and tool pages (Nov 2026). The stick-figure video's own
transcript couldn't be read (vidIQ credits ran out, and YouTube and recap sites are blocked
from this environment), so its exact steps aren't quoted here.

## The look

- **Background:** plain white or very light grey, almost no texture. Nothing competes with
  the point being made.
- **Lines:** black, marker-like, slightly uneven strokes. The figures are bodies made of
  lines with a circle head. Contrast comes from the black lines and bold text.
- **Colour:** used sparingly, as one accent per scene: red for loss or danger, green for
  money or gain, a highlight on the key word. Everything else is black and white.
- **Faces:** two dots and a mouth line, *exaggerated* (wide-eyed shock, a flat-line stare,
  a big grin). The expression carries the joke.
- **Props:** drawn simply in the same marker style (coins, phone, brain, clock, house,
  arrow, graph line). One prop per idea, and labels written right on the drawing.
- **Motion:** small and snappy: a figure walks in, points, shrugs or falls over; objects pop
  in with a little overshoot; lines "draw on" stroke by stroke (whiteboard style); slow
  push-ins on the key moment. Hard cuts between ideas.
- **Two variants:** the *doodle/whiteboard* look (calm, one subject drawn on a white page)
  for how-things-work topics, and the *classic stickman* (bigger expressions, slapstick) for
  funny or dramatic money and psychology explainers.

## Where it works

Money ("why people stay broke", inflation, compound interest as a concept), psychology and
behaviour (habits, procrastination, why we overthink), productivity and study tips, life
lessons, and quick history. These are explainers only: no investment or medical advice
(the daily-task rules still apply).

## Script and pacing

Same craft as `script-patterns.md`, with a heavier dose of humour:
- Use a **relatable "you" scenario** as the hook: "You get paid on Friday. By Monday,
  it's gone." The stick figure *is* the viewer.
- Put **a visual joke every 5–8 seconds**: the figure's reaction undercuts the line (a
  "totally fine" voice-over while the figure stands in a burning room).
- Pacing matters more than polish. Every sentence is a new drawing or a new pose, and there
  are no static beats longer than about 3 seconds.
- **Check every claim.** AI-written scripts state country-specific or wrong facts with
  confidence. Read each line, fix the numbers, add one example of your own, and cut
  anything you can't defend.

## The workflow people use

LLM script → TTS voice-over split by scene → each scene matched to a stick-figure drawing or
animation → captions and sound effects → render. Common tools are ChatGPT, DeepSeek or Claude
for the script; ElevenLabs for the voice; and Canva, CapCut or Grease Pencil for the visuals.
The code-only version, the one this repo would use, is Claude drawing the figures as SVG/canvas
or three.js lines and rendering frame by frame. Community Claude skills such as "stix" (text
→ 8-second stick-figure clip) and Remotion-based Shorts projects show it can be done.

## Adding it to this repo's renderer (not built yet)

The current `cartoon3d` style has a 3D coral mascot. A stickman look would be a new
`VISUAL_STYLE` (for example `stickman`), with:
1. A flat orthographic scene (or a 2D canvas/SVG layer) on a white background, with black
   stroked lines and stroke widths that scale with the output size.
2. A stick-figure rig built from line segments (head circle, torso, two-segment arms and
   legs) with a few poses (stand, point, shrug, walk, fall, cheer) blended as a function of `t`,
   and face states (neutral, shock, grin, flat).
3. The same five layouts (`title`, `keyword`, `stat`, `steps`, `compare`) redrawn as
   whiteboard doodles: draw-on strokes, a hand-drawn bar chart for `compare`, and a
   tally or coin pile drawn stroke by stroke for `stat`.
4. Optionally, a `pose` field per scene in the plan, so the script can direct the joke.
Keep every frame a pure function of `t`, as `cartoon-explainer` requires.
