#!/usr/bin/env python3
"""Step 02 — Matching, then comparing.

Two halves, and the order is the lesson.

PART A gives each tier the work the tier table says it is for: a one-word triage
to the small model, a structured analysis to the mid, a multi-cause investigation
to the large. Every one looks good. That is the table's argument, and it is NOT a
comparison -- the task moved with the model, so nothing is isolated.

PART B holds the task fixed and moves only the model. Now it is a comparison,
and two things are worth watching:
  1. The price gap between tiers is large and obvious.
  2. The ANSWER gap on a moderate task is small -- often nothing.

That second observation is what makes routing tempting. Step 03 tests whether it
survives contact with the rest of the system.

This step also gives you the only LATENCY numbers in the build. Cost is
arithmetic and the bench computes it offline; time has to be measured.

Run:  python3 02_three_tiers.py
"""

from _shared import HAIKU, OPUS, SONNET, call, row
from incidents import COMPLEX, MODERATE, SIMPLE

TRIAGE_ONE_WORD = (
    "You triage production incidents. "
    "Reply with exactly one word: LOW, MEDIUM, HIGH, or CRITICAL."
)

SYSTEM = (
    "You triage production incidents. Reply with exactly three lines:\n"
    "SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>\n"
    "LIKELY CAUSE: <one sentence>\n"
    "FIRST ACTION: <one sentence>"
)

DEEP = (
    "You are a staff engineer triaging a multi-cause production incident. "
    "Give a summary, a ranked list of candidate causes with the evidence for each, "
    "and the single next diagnostic step."
)


def main() -> None:
    print("\n  Step 02 — matching, then comparing\n")

    # ---- Part A: each tier on the task it is supposed to suit -------------
    # This is the tier table made concrete. Every model gets the work the table
    # says it is for, so each looks good. Nothing is being compared yet.
    print("  PART A — each tier on its matched task\n")

    matched = [
        (HAIKU,  SIMPLE,   "one-word triage",        TRIAGE_ONE_WORD, 16),
        (SONNET, MODERATE, "structured analysis",    SYSTEM,          300),
        (OPUS,   COMPLEX,  "multi-cause reasoning",  DEEP,            900),
    ]

    part_a = []
    for model, incident, label, system, max_tok in matched:
        r = call(model, system, incident, max_tokens=max_tok)
        part_a.append(r)
        print(f"  --- {model}  ({label})")
        for line in r.text.splitlines()[:4]:
            print(f"      {line}")
        print(f"      {r.seconds:.2f}s  ${r.cost:.6f}\n")

    print("  Each one looks good, because each got the work it was picked for.")
    print("  That is the tier table's whole argument -- and it is not a comparison.\n")

    # ---- Part B: all three on the SAME task -------------------------------
    # Now it is a comparison, because only one variable moved.
    print("  " + "-" * 74)
    print("\n  PART B — the same incident on all three\n")

    results = []
    for model in (HAIKU, SONNET, OPUS):
        r = call(model, SYSTEM, MODERATE, max_tokens=300)
        results.append(r)
        print(f"  --- {model}")
        for line in r.text.splitlines():
            print(f"      {line}")
        print()

    print("  Comparison\n")
    for r in results:
        print(row(r.model, r))

    cheapest = min(results, key=lambda x: x.cost)
    dearest = max(results, key=lambda x: x.cost)
    slowest = max(results, key=lambda x: x.seconds)
    fastest = min(results, key=lambda x: x.seconds)

    print()
    print(f"  cost : {dearest.model} cost {dearest.cost / cheapest.cost:.1f}x what {cheapest.model} did.")
    print(f"  time : {slowest.model} took {slowest.seconds / fastest.seconds:.1f}x as long as {fastest.model}.")
    print()
    print("  Now read the three answers again. Is it that multiple of better?")
    print("  On a HARD incident it often is. On this one, decide for yourself --")
    print("  and notice you now have a latency number, which the offline bench cannot give you.")
    print()


if __name__ == "__main__":
    main()
