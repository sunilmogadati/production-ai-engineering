#!/usr/bin/env python3
"""Step 03 — The minimal agent, in about twenty lines.

This is the whole pattern. Everything after this step adds safety, not capability.

Watch the transcript: the agent finds when the problem started, discovers its own
service has not deployed in days, looks at what it depends on, and lands on the
dependency that shipped 55 minutes ago. No single tool call gets there -- which is
why the loop exists.

Three details that matter more than they look:
  - The ASSISTANT message is appended with response.content unchanged. Not the
    text -- the blocks. The tool_use block has to go back or the conversation is
    incoherent.
  - ALL tool results go back in ONE user message. Splitting them teaches the
    model to stop making parallel calls.
  - Every value of stop_reason is handled, not just tool_use.

Run:  python3 03_the_loop.py
"""

from _tools import INCIDENT, MODEL, SYSTEM, TOOLS, client, cost_of, run_tool


def main() -> None:
    api = client()
    messages = [{"role": "user", "content": INCIDENT}]
    total_cost = 0.0
    turn = 0

    print("\n  Step 03 — the loop\n")

    while True:
        turn += 1
        response = api.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM, tools=TOOLS, messages=messages
        )
        total_cost += cost_of(response.usage)

        # The assistant's blocks go back verbatim -- tool_use blocks included.
        messages.append({"role": "assistant", "content": response.content})

        print(f"  turn {turn}: stop_reason={response.stop_reason}  "
              f"in={response.usage.input_tokens} out={response.usage.output_tokens}")

        if response.stop_reason != "tool_use":
            break

        # Run every requested tool, collect every result.
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            output = run_tool(block.name, block.input)
            print(f"        -> {block.name}({block.input}) => {output[:72]}")
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })

        # ONE user message carrying ALL results.
        messages.append({"role": "user", "content": results})

    # Every terminal value gets a distinct outcome. None is silently "success".
    print()
    if response.stop_reason == "end_turn":
        answer = "".join(b.text for b in response.content if b.type == "text")
        print("  ANSWER\n")
        for line in answer.strip().splitlines():
            print(f"    {line}")
    elif response.stop_reason == "max_tokens":
        print("  TRUNCATED — this is NOT an answer. Raise max_tokens and re-run.")
    elif response.stop_reason == "refusal":
        print("  DECLINED — do not retry this unchanged.")
    else:
        print(f"  UNEXPECTED stop_reason: {response.stop_reason}")

    print(f"\n  {turn} turns, ${total_cost:.6f} total")
    print("  Note the input tokens climbing each turn: you resend everything, every time.\n")


if __name__ == "__main__":
    main()
