#!/usr/bin/env python3
"""Step 03 — The lever before the second model.

Step 02 made routing look obvious: the cheap tier costs a fraction of the dear one.
This step introduces the option that tier table never mentions.

`effort` trades thoroughness against token spend WITHIN one model. Same model,
same prompt, three settings. It costs one line of code, adds no second model, no
classifier, and no second cache.

If a strong model at low effort lands where you need it, you have your saving --
and you still have one model, one set of failure modes, one eval baseline.

Measure this before you build a router. That is the entire lesson.

Note: effort is not accepted on every tier -- Haiku 4.5 rejects it. This step
uses Opus for that reason.

Run:  python3 03_effort.py
"""

from _shared import OPUS, call, row
from incidents import COMPLEX

SYSTEM = (
    "You are a staff engineer triaging a production incident. "
    "Give your leading hypothesis and the single next diagnostic step."
)


def main() -> None:
    print("\n  Step 03 — one model, three effort levels\n")

    results = []
    for effort in ("low", "medium", "high"):
        result = call(OPUS, SYSTEM, COMPLEX, max_tokens=1200, effort=effort)
        results.append((effort, result))
        print(f"  --- effort={effort}")
        for line in result.text.splitlines()[:6]:
            print(f"      {line}")
        print()

    print("  Comparison\n")
    for effort, result in results:
        print(row(f"{OPUS} @ {effort}", result))

    low = results[0][1]
    high = results[-1][1]
    print()
    print(f"  low effort cost {low.cost / high.cost * 100:.0f}% of high effort on the same model.")
    print("  Thinking tokens bill as output, so effort moves the output side.")
    print()
    print("  The question for your workload: did low effort get the RIGHT hypothesis?")
    print("  If yes, you just found a saving with no router, no classifier, and no")
    print("  second cache. If no, that is real evidence that the task needs more.")
    print()


if __name__ == "__main__":
    main()
