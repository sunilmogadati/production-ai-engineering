#!/usr/bin/env python3
"""Step 02 — The four terminal values, provoked on purpose.

`stop_reason` is the entire loop mechanism, so it is worth seeing each value
arrive rather than reading a list of them.

  end_turn    finished normally
  tool_use    wants a tool, will continue once it has the result
  max_tokens  ran out of room MID-SENTENCE -- not finished, though it looks it

The fourth, `refusal`, is a safety decline. We do not provoke it here; just know
it exists and that it must not be blindly retried.

The lesson is the third one. A loop written as `while stop_reason == "tool_use"`
treats max_tokens as success and hands a truncated half-answer to a user.

Run:  python3 02_stop_reason.py
"""

from _tools import INCIDENT, MODEL, SYSTEM, TOOLS, client, cost_of

api = None


def ask(label, *, max_tokens, tools=None, prompt=INCIDENT):
    global api
    api = api or client()
    kwargs = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools

    r = api.messages.create(**kwargs)
    text = "".join(b.text for b in r.content if b.type == "text").strip()
    print(f"  {label:<34} stop_reason = {r.stop_reason:<12} ${cost_of(r.usage):.6f}")
    if text:
        tail = text[-70:].replace("\n", " ")
        print(f"      ends with: …{tail}")
    return r


def main() -> None:
    print("\n  Step 02 — provoking each terminal value\n")

    ask("no tools, room to finish", max_tokens=400,
        prompt="In two sentences, what is a p99 latency?")

    ask("tools offered", max_tokens=1000, tools=TOOLS)

    # A generous question with almost no room to answer it.
    ask("tiny max_tokens", max_tokens=32,
        prompt="Explain, in detail, how database connection pool exhaustion cascades across services.")

    print()
    print("  Look at the third one. It stopped mid-sentence.")
    print("  A loop that only checks for 'tool_use' calls that a finished answer")
    print("  and returns it to the user. Nothing errors. Nothing logs.")
    print()
    print("  Handle every terminal value -- silence on the others looks like success.")
    print()


if __name__ == "__main__":
    main()
