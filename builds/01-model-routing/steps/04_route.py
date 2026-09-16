#!/usr/bin/env python3
"""Step 04 — A router that tells you why.

Now build the thing the tier table implies: classify the incident, send it to a
matching model.

Two details that most routing examples skip, and both are the point:

  1. The classifier is a model call. It has a price, and it is charged on EVERY
     incident -- including the ones that route to the expensive model anyway.
     This step prints it as its own line. Never fold it into the routed call.

  2. Every decision reports the rule that made it. A bare model name is an
     instruction; a model name plus its rule is an argument, and an argument can
     be reviewed by the person whose budget it is.

Run:  python3 04_route.py
"""

from _shared import HAIKU, OPUS, SONNET, call, cost_usd
from incidents import COMPLEX, MODERATE, SIMPLE

CLASSIFIER_SYSTEM = (
    "Rate how hard this production incident is to diagnose, 1 to 5. "
    "1 = a single obvious cause. 5 = several interacting changes with no clear culprit. "
    "Reply with only the digit."
)

TRIAGE_SYSTEM = (
    "You are a staff engineer triaging a production incident. "
    "Give severity, your leading hypothesis, and the next diagnostic step."
)

# The policy, as data. Edit this to change routing; no other file changes.
# First match wins, so the order is part of the policy.
POLICY = [
    {"id": "R1-trivial",  "max_complexity": 2, "model": HAIKU,
     "why": "A single obvious cause does not repay a larger model."},
    {"id": "R2-moderate", "max_complexity": 3, "model": SONNET,
     "why": "Mid-difficulty work where the mid tier holds the quality bar."},
    {"id": "R3-default",  "max_complexity": 5, "model": OPUS,
     "why": "Interacting causes need the strongest model. The default is capability."},
]


def classify(incident: str) -> tuple[int, float]:
    """Decide how hard this is -- and report what deciding cost."""
    result = call(HAIKU, CLASSIFIER_SYSTEM, incident, max_tokens=8)
    digits = [c for c in result.text if c.isdigit()]
    complexity = int(digits[0]) if digits else 3  # unreadable answer -> assume middle
    return complexity, result.cost


def route(complexity: int) -> dict:
    for rule in POLICY:
        if complexity <= rule["max_complexity"]:
            return rule
    return POLICY[-1]


def main() -> None:
    print("\n  Step 04 — routing, with the reasoning shown\n")

    total_routed = total_classifier = 0.0

    for name, incident in (("SIMPLE", SIMPLE), ("MODERATE", MODERATE), ("COMPLEX", COMPLEX)):
        complexity, classifier_cost = classify(incident)
        rule = route(complexity)
        result = call(rule["model"], TRIAGE_SYSTEM, incident, max_tokens=600)

        total_routed += result.cost
        total_classifier += classifier_cost

        print(f"  {name}")
        print(f"    complexity : {complexity}")
        print(f"    rule       : {rule['id']} — {rule['why']}")
        print(f"    model      : {rule['model']}")
        print(f"    routed     : ${result.cost:.6f}")
        print(f"    classifier : ${classifier_cost:.6f}   <- charged even when routing to opus")
        print()

    total = total_routed + total_classifier
    print(f"  routed calls : ${total_routed:.6f}")
    print(f"  classifier   : ${total_classifier:.6f}  ({total_classifier / total * 100:.1f}% of the bill)")
    print(f"  TOTAL        : ${total:.6f}")
    print()
    print("  Small per request. Charged on every request, forever. That is a tax,")
    print("  and it is the smallest of the three things a tier table leaves out.")
    print("  The other two -- cache splitting and escalation -- are in ../src/bench.py.")
    print()


if __name__ == "__main__":
    main()
