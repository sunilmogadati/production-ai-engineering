#!/usr/bin/env python3
"""Step 01 — One call, and what it cost.

The smallest useful thing: send one message, get one answer, and find out what
you just spent. Everything later in this build is a comparison between calls
like this one.

The idea worth taking away: cost is not a mystery you discover on the invoice.
It is reported on every response, and you can read it.

Run:  python3 01_one_call.py
"""

from _shared import HAIKU, call, row
from incidents import SIMPLE

SYSTEM = "You triage production incidents. Reply with exactly one word: LOW, MEDIUM, HIGH, or CRITICAL."


def main() -> None:
    result = call(HAIKU, SYSTEM, SIMPLE, max_tokens=16)

    print("\n  Step 01 — one call\n")
    print(f"  model:  {result.model}")
    print(f"  answer: {result.text}")
    print()
    print(row("this call", result))
    print()
    print("  That cost is computed from response.usage -- what the API says it actually")
    print("  used, not an estimate. Note how few output tokens a one-word answer needs.")
    print()


if __name__ == "__main__":
    main()
