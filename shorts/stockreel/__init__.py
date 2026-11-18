"""A third video style, alongside the whiteboard explainer and the director's dynamic Three.js scenes: real stock
footage (Pexels, free to use, no attribution required) behind the same voice-over, captions, music and upload
pipeline as the rest of the channel. See fetch.py, render.py, build.py and run.py; `shorts/CLAUDE_STOCKREEL_TASK.md`
is the task brief, written the same way as the other two formats.

Why a third style at all: some topics (a city, a kitchen, hands typing, weather, nature) read better with real
footage than a coded 3D scene can give them, and Pexels covers that without any AI-video-generation step (clips
are real camera footage, never generated), which keeps the channel's "no fabricated imagery" rule intact. Topics
better served by a diagram, a comparison or an abstract concept stay on the whiteboard or director pipelines -
this format is an addition, not a replacement, and Claude picks it per `video-strategy` (BUILD/`niches recent`),
never by default.
"""
