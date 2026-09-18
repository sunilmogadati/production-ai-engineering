#!/usr/bin/env python3
"""Step 01 (Python) — one call, priced.

The smallest complete thing: a client, a request, an answer, and what it cost.

Three things worth noticing:
  1. The client takes NO arguments. The key comes from ANTHROPIC_API_KEY, and
     base_url is only needed when talking to a proxy -- not with your own key.
  2. The cost comes from response.usage: what the API says it actually used,
     not an estimate.
  3. The response is a LIST of content blocks, not a string. Check .type before
     reading .text -- a thinking block or a tool_use block has no .text.

Run:  python3 01_hello.py
"""

from __future__ import annotations

import os
import sys

try:
    import anthropic
except ImportError:
    sys.exit("pip install anthropic   (or: uv run --with anthropic python 01_hello.py)")

MODEL = "claude-haiku-4-5"          # complete as written -- no date suffix
RATE_IN, RATE_OUT = 1.00, 5.00      # $ per million tokens, verified 2026-09-16


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set.\n  export ANTHROPIC_API_KEY=sk-ant-...")

    client = anthropic.Anthropic()   # no api_key, no base_url -- both come from the environment

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system="You explain engineering ideas to experienced developers. Two sentences, no preamble.",
        messages=[{"role": "user", "content": "What does an LLM harness do that the model does not?"}],
    )

    answer = "".join(b.text for b in response.content if b.type == "text")
    usage = response.usage
    cost = (usage.input_tokens * RATE_IN + usage.output_tokens * RATE_OUT) / 1_000_000

    print(f"\n  model : {response.model}")
    print(f"  stop  : {response.stop_reason}")
    print(f"\n  {answer.strip()}\n")
    print(f"  tokens: in={usage.input_tokens}  out={usage.output_tokens}")
    print(f"  cost  : ${cost:.6f}")
    print("\n  You are set up. Next: builds/01-model-routing/\n")


if __name__ == "__main__":
    main()
