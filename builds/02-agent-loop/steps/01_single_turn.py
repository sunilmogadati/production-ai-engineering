#!/usr/bin/env python3
"""Step 01 — The model answers once and stops.

Before writing a loop, watch what happens without one.

We hand the model an incident AND the tools, then call it exactly once. It will
ask for a tool. Nobody runs it. Nobody calls again. The conversation ends there,
mid-investigation.

That is the whole reason a loop exists. The model cannot run your functions and
cannot call itself. Everything past this point is your code.

Run:  python3 01_single_turn.py
"""

from _tools import INCIDENT, MODEL, SYSTEM, TOOLS, client, cost_of


def main() -> None:
    response = client().messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM,
        tools=TOOLS,
        messages=[{"role": "user", "content": INCIDENT}],
    )

    print("\n  Step 01 — one call, no loop\n")
    print(f"  stop_reason: {response.stop_reason}")
    print(f"  cost       : ${cost_of(response.usage):.6f}\n")

    for block in response.content:
        if block.type == "text":
            print(f"  said : {block.text.strip()[:200]}")
        elif block.type == "tool_use":
            print(f"  wants: {block.name}({block.input})")

    print()
    if response.stop_reason == "tool_use":
        print("  It asked for a tool and stopped. Nothing ran it.")
        print("  The investigation is frozen here until YOUR code continues it.")
    else:
        print("  It answered without reaching for a tool this time.")
        print("  Run it again -- the decision is the model's, and it varies.")
    print()


if __name__ == "__main__":
    main()
