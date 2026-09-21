#!/usr/bin/env python3
"""Step 05 — When a tool fails, and the mistakes that train the model worse.

Three things go wrong around tools. Two of them produce no error at all, which
is what makes them expensive.

  1. A tool RAISES. Return a tool_result with is_error=True. Do not drop it --
     a dangling tool_use with no result is an invalid conversation.
  2. PARALLEL results split across messages. One assistant turn can request
     several tools; all results belong in ONE user message. Split them and the
     model quietly stops making parallel calls. No error, just slower agents.
  3. A retried turn re-runs a tool you already ran. If it books, charges, sends
     or deletes, that is a real second side effect.

This step breaks a tool on purpose and shows the model recovering when told the
truth.

Run:  python3 05_failures.py
"""

from _tools import MODEL, SYSTEM, TOOLS, client, cost_of, run_tool

INCIDENT = (
    "checkout-api is degraded. Check its metrics, then its dependencies, "
    "then say what you would investigate next."
)

# A counter proving the idempotency point: a tool can be invoked more than once
# across a run, and your code is what decides whether that is safe.
CALLS: dict[str, int] = {}


def run_tool_that_sometimes_fails(name: str, args: dict) -> tuple[str, bool]:
    """Returns (content, is_error). The dependency lookup is broken on purpose."""
    CALLS[name] = CALLS.get(name, 0) + 1

    if name == "get_dependencies":
        # A real outage, reported honestly rather than hidden.
        return ("ServiceUnavailable: dependency-graph API returned 503 "
                "after 3 retries. Data unavailable."), True

    return run_tool(name, args), False


def main() -> None:
    api = client()
    messages = [{"role": "user", "content": INCIDENT}]
    total = 0.0

    print("\n  Step 05 — a broken tool, reported honestly\n")

    for turn in range(1, 7):
        response = api.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM, tools=TOOLS, messages=messages
        )
        total += cost_of(response.usage)
        messages.append({"role": "assistant", "content": response.content})

        requested = [b for b in response.content if b.type == "tool_use"]
        print(f"  turn {turn}: {response.stop_reason:<10} tools requested: "
              f"{[b.name for b in requested] or 'none'}")

        if response.stop_reason != "tool_use":
            break

        results = []
        for block in requested:
            content, is_error = run_tool_that_sometimes_fails(block.name, block.input)
            flag = "  <- ERROR, reported as one" if is_error else ""
            print(f"        {block.name}: {content[:60]}{flag}")
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": content,
                "is_error": is_error,          # the honest report
            })

        # Still ONE message, even when some of the results are failures.
        messages.append({"role": "user", "content": results})

    answer = "".join(b.text for b in response.content if b.type == "text")
    print("\n  ANSWER\n")
    for line in answer.strip().splitlines()[:12]:
        print(f"    {line}")

    print(f"\n  ${total:.6f} total")
    print(f"  tool invocations this run: {CALLS}")
    print()
    print("  Two things to take away:")
    print("    The agent was told a tool failed and worked around it. Tell it the truth.")
    print("    Check that call count. If a tool books, charges, sends or deletes,")
    print("    'called twice' is a real second side effect. Idempotent, or deduplicated.")
    print()


if __name__ == "__main__":
    main()
