#!/usr/bin/env python3
"""Step 02 — The same work on three tiers.

One prompt, one incident, three models. This is the comparison every tier table
is really claiming, run for real.

Watch two things:
  1. The price gap between tiers is large and obvious.
  2. The ANSWER gap on an easy task is small -- often nothing.

That second observation is what makes routing tempting. Step 04 tests whether it
survives contact with the rest of the system.

Run:  python3 02_three_tiers.py
"""

from _shared import HAIKU, OPUS, SONNET, call, row
from incidents import MODERATE

SYSTEM = (
    "You triage production incidents. Reply with exactly three lines:\n"
    "SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>\n"
    "LIKELY CAUSE: <one sentence>\n"
    "FIRST ACTION: <one sentence>"
)


def main() -> None:
    print("\n  Step 02 — same incident, three tiers\n")

    results = []
    for model in (HAIKU, SONNET, OPUS):
        result = call(model, SYSTEM, MODERATE, max_tokens=300)
        results.append(result)
        print(f"  --- {model}")
        for line in result.text.splitlines():
            print(f"      {line}")
        print()

    print("  Comparison\n")
    for result in results:
        print(row(result.model, result))

    cheapest = min(results, key=lambda r: r.cost)
    dearest = max(results, key=lambda r: r.cost)
    print()
    print(f"  {dearest.model} cost {dearest.cost / cheapest.cost:.1f}x what {cheapest.model} did.")
    print("  Now read the three answers again. Is it 1 answer's worth of better?")
    print("  On a HARD incident it often is. On this one, decide for yourself.")
    print()


if __name__ == "__main__":
    main()
