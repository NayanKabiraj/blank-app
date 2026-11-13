"""The channel's fixed explainer niches and the daily rotation.

Every video is an explainer: it answers one "how does X work?" or "why does X happen?"
question. The niche of the day is the one that has gone longest without a video, so the
channel cycles through all of them. Edit NICHES to change the line-up.

    python -m shorts.niches next     # today's niche, example topics and topics to avoid
    python -m shorts.niches list     # all niches
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field

from . import config


@dataclass
class Niche:
    name: str            # goes into plan.niche and the on-screen label
    hindi: str           # Hindi name, for the Hindi title/description if useful
    angle: str           # what an explainer in this niche answers
    examples: list[str] = field(default_factory=list)


NICHES: list[Niche] = [
    Niche("How Tech Works", "टेक्नोलॉजी कैसे काम करती है",
          "How an everyday technology works inside, step by step.",
          ["How does UPI move money in two seconds?", "How does GPS know where you are?",
           "How does Wi-Fi send data through the air?", "How does a QR code store information?",
           "How does a touchscreen feel your finger?", "How does noise cancelling work?"]),
    Niche("AI Explained", "AI आसान भाषा में",
          "How artificial intelligence and modern computing actually work, without hype.",
          ["How does a chatbot predict the next word?", "How does face unlock recognise you?",
           "What is a neural network, really?", "How do recommendation feeds choose videos?",
           "How does a computer chip do billions of steps a second?"]),
    Niche("Science Explained", "विज्ञान की बातें",
          "The physics or chemistry behind something people see every day.",
          ["Why is the sky blue?", "How does a microwave heat food?", "Why does ice float?",
           "Why do onions make you cry?", "How does a pressure cooker cook faster?",
           "Why does metal feel colder than wood?"]),
    Niche("Space & Universe", "अंतरिक्ष और ब्रह्मांड",
          "How things in space work, explained from first principles.",
          ["Why is a day on Venus longer than its year?", "How do rockets steer in space?",
           "Why does the Moon show phases?", "How do we know how far stars are?",
           "What happens inside a black hole?"]),
    Niche("Human Body", "हमारा शरीर",
          "How the body does something remarkable (biology only, never medical advice).",
          ["Why do we yawn?", "How does the body heal a cut?", "How do eyes see colour?",
           "What happens in the brain while we sleep?", "How do muscles get stronger?"]),
    Niche("Brain & Psychology", "दिमाग और मनोविज्ञान",
          "Why the mind behaves the way it does, backed by research.",
          ["Why do we procrastinate?", "How are habits formed?", "Why do songs get stuck in our head?",
           "How does memory store a moment?", "Why does time fly when we're having fun?"]),
    Niche("Money Explained", "पैसे की समझ",
          "How money and the economy work (concepts only, never investment advice).",
          ["What actually causes inflation?", "How do banks create money?",
           "How does compound interest grow?", "Why do prices end in 99?",
           "How does a credit score work?"]),
    Niche("Earth & Nature", "धरती और प्रकृति",
          "The mechanism behind a natural phenomenon.",
          ["How does the monsoon form?", "What causes earthquakes?", "How does lightning form?",
           "Why are rainbows curved?", "How do volcanoes erupt?"]),
    Niche("How It's Made", "चीज़ें कैसे बनती हैं",
          "How an everyday object goes from raw material to product.",
          ["How is glass made from sand?", "How are computer chips made?", "How is paper made?",
           "How is chocolate made from cocoa beans?", "How is steel made?"]),
    Niche("Engineering Marvels", "इंजीनियरिंग के कमाल",
          "How a structure or machine is engineered to work.",
          ["How do planes stay in the air?", "How do bridges carry heavy trucks?",
           "How does a metro train stop so precisely?", "How do dams make electricity?",
           "How do skyscrapers survive strong wind?"]),
    Niche("History of Ideas", "खोज और आविष्कार",
          "How a world-changing idea or invention came about and why it mattered.",
          ["How was zero invented in India?", "How did the printing press change the world?",
           "How did people tell time before clocks?", "How was electricity discovered?",
           "How did the first vaccine come about?"]),
]
NAMES = [n.name for n in NICHES]


def _history() -> list[dict]:
    if config.HISTORY_FILE.exists():
        return json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def next_niche(history: list[dict] | None = None) -> Niche:
    """The niche that has gone longest without a video (never-used ones first, in list order)."""
    history = _history() if history is None else history
    last_used = {}
    for idx, h in enumerate(history):
        last_used[h.get("niche")] = idx
    return min(NICHES, key=lambda n: (last_used.get(n.name, -1), NAMES.index(n.name)))


def _cli() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    if cmd == "list":
        print(json.dumps([asdict(n) for n in NICHES], ensure_ascii=False, indent=2))
        return 0
    if cmd == "next":
        history = _history()
        n = next_niche(history)
        done = [h["topic"] for h in history if h.get("niche") == n.name]
        print(json.dumps({**asdict(n), "already_covered": done}, ensure_ascii=False, indent=2))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
