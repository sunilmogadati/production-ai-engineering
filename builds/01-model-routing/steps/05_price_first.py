#!/usr/bin/env python3
"""Step 05 — Know the bill before you send the request.

Everything so far measured cost AFTER spending it. This step prices the input
side BEFORE any generation happens, using the token-counting endpoint.

Why it matters: input cost is knowable in advance and, for long-context work, it
dominates. A 200,000-token document sent to the wrong tier is a decision you can
evaluate before you make it -- not one you discover on the invoice.

Only the output side needs measuring, because only the model decides that.

Run:  python3 05_price_first.py
"""

from _shared import HAIKU, OPUS, RATES, SONNET, client
from incidents import COMPLEX

SYSTEM = "You are a staff engineer triaging a production incident."


def main() -> None:
    api = client()

    counted = api.messages.count_tokens(
        model=OPUS,
        system=SYSTEM,
        messages=[{"role": "user", "content": COMPLEX}],
    )
    input_tokens = counted.input_tokens

    print("\n  Step 05 — price it before you send it\n")
    print(f"  input tokens (counted, not estimated): {input_tokens}")
    print()
    print(f"  {'model':<22} {'input cost':>12} {'+1k output':>12}")
    print("  " + "-" * 48)
    for model in (HAIKU, SONNET, OPUS):
        rate = RATES[model]
        in_cost = input_tokens * rate["in"] / 1_000_000
        out_cost = 1_000 * rate["out"] / 1_000_000
        print(f"  {model:<22} ${in_cost:>11.6f} ${in_cost + out_cost:>11.6f}")

    print()
    print("  Counting is free and instant. Multiply by your request volume and you")
    print("  have a monthly figure before writing the integration.")
    print()
    print("  Now scale it: the same arithmetic over a whole workload is ../src/pricing.py,")
    print("  and the full comparison -- including cache splitting and escalation -- is")
    print("  ../src/bench.py, which runs with no API key at all.")
    print()


if __name__ == "__main__":
    main()
