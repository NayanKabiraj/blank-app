"""Advisory narration lint from strategy/story-craft.md:  python3 -m shorts.storycheck plan.json  (exit 0 always; prints findings)."""
from __future__ import annotations

import json
import re
import sys

BANNED_WORDS = ("delve", "realm", "tapestry", "leverage", "synergy", "seamless", "robust", "elevate", "streamline", "game-changer", "game changer", "pivotal",
                "testament", "foster", "empower", "holistic", "unlock", "harness", "ecosystem", "flywheel")
BANNED_PHRASES = ("in today's", "it's important to note", "let's dive in", "let me explain", "let's talk about", "story time", "pov:", "hey guys", "welcome back",
                  "furthermore", "moreover", "that said", "let that sink in", "nobody talks about this", "wait till you see this")
NOT_X_BUT_Y = re.compile(r"\b(it'?s|this is|that'?s) not [^.?!]{1,60}[.,;] ?(it'?s|this is|that'?s) ", re.I)


def check_text(text: str, first: bool = False) -> list[str]:
    low = text.lower()
    out = [f"banned word '{w}'" for w in BANNED_WORDS if re.search(rf"\b{re.escape(w)}\b", low)]
    out += [f"banned phrase '{p}'" for p in BANNED_PHRASES if p in low]
    if NOT_X_BUT_Y.search(text):
        out.append("\"It's not X. It's Y.\" pattern (make Y concrete or state it directly)")
    if first:
        words = text.split()
        if len(words) > 22:
            out.append(f"hook is {len(words)} words (keep the first line short)")
        if not re.search(r"\byou(r)?\b|\?", low) and not re.search(r"\d", low):
            out.append("hook has no 'you', question or number (irrelevance/disinterest risk)")
    return out


def check_plan(plan: dict) -> list[str]:
    res = []
    for lang in ("english", "hindi"):
        block = plan.get(lang) or {}
        for i, sc in enumerate(block.get("scenes", [])):
            for f in check_text(sc.get("text", ""), first=(i == 0 and lang == "english")):
                res.append(f"{lang} scene {i + 1}: {f}")
    return res


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 0
    problems = check_plan(json.load(open(argv[0], encoding="utf-8")))
    print("\n".join(problems) if problems else "storycheck: no findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
