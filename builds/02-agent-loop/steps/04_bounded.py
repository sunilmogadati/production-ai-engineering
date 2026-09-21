#!/usr/bin/env python3
"""Step 04 — The three bounds.

Step 03 works, and has no upper limit on what it can spend. This adds the limits,
and sets one of them deliberately low so you watch it trip.

Three bounds, because they catch three different failures:

  MAX_TURNS   a model that keeps calling tools without converging.
              Protects the LOGIC.
  MAX_COST    a few enormous turns rather than many small ones.
              Protects the INVOICE -- and this is the one teams forget.
  MAX_SECONDS a slow tool, a hung request, a retry storm.
              Protects the USER, who is still waiting.

An iteration cap alone feels safe and is not. Ten turns sounds bounded until one
carries a 400,000-token context. Ten bounded iterations is an unbounded bill.

Run:  python3 04_bounded.py           # MAX_TURNS is set to 2 so you see it trip
      python3 04_bounded.py --full    # realistic bounds; runs to completion
"""

import sys
import time

from _tools import INCIDENT, MODEL, SYSTEM, TOOLS, client, cost_of, run_tool

FULL = "--full" in sys.argv

MAX_TURNS = 8 if FULL else 2       # deliberately too low by default
MAX_COST = 0.50
MAX_SECONDS = 90


def main() -> None:
    api = client()
    messages = [{"role": "user", "content": INCIDENT}]
    total_cost = 0.0
    started = time.time()
    turn = 0
    stopped_by = None

    print(f"\n  Step 04 — bounded  (turns<={MAX_TURNS}  cost<=${MAX_COST}  time<={MAX_SECONDS}s)\n")

    while True:
        # --- the bounds are checked BEFORE spending, not after ---
        if turn >= MAX_TURNS:
            stopped_by = f"MAX_TURNS ({MAX_TURNS})"
            break
        if total_cost >= MAX_COST:
            stopped_by = f"MAX_COST (${MAX_COST})"
            break
        if time.time() - started >= MAX_SECONDS:
            stopped_by = f"MAX_SECONDS ({MAX_SECONDS})"
            break

        turn += 1
        response = api.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM, tools=TOOLS, messages=messages
        )
        total_cost += cost_of(response.usage)
        messages.append({"role": "assistant", "content": response.content})

        print(f"  turn {turn}: {response.stop_reason:<10} "
              f"in={response.usage.input_tokens:>6} running=${total_cost:.6f} "
              f"{time.time()-started:>5.1f}s")

        if response.stop_reason != "tool_use":
            break

        results = []
        for block in response.content:
            if block.type == "tool_use":
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(block.name, block.input),
                })
        messages.append({"role": "user", "content": results})

    print()
    if stopped_by:
        # A bound tripping is a VISIBLE outcome. It never gets dressed up as an answer.
        print(f"  STOPPED BY A BOUND: {stopped_by}")
        print("  The agent had not finished. This is a partial result and is labelled as one.")
        print("  In production this is where a human gets paged -- not where we guess.")
        if not FULL:
            print("\n  Re-run with --full for realistic bounds:  python3 04_bounded.py --full")
    else:
        answer = "".join(b.text for b in response.content if b.type == "text")
        print("  COMPLETED\n")
        for line in answer.strip().splitlines()[:12]:
            print(f"    {line}")

    worst_case = MAX_COST
    print(f"\n  {turn} turns, ${total_cost:.6f} spent, {time.time()-started:.1f}s")
    print(f"  Worst case for this configuration is ${worst_case:.2f} per incident, by construction.")
    print("  That is the number a design review asks for. Now you have it.\n")


if __name__ == "__main__":
    main()
