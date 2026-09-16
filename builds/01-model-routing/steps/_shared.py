"""Shared helpers for the model-selection steps.

Deliberately tiny. Everything here exists so the numbered steps can stay about
one idea each instead of re-implementing plumbing.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

try:
    import anthropic
except ImportError:
    sys.exit("pip install anthropic  (or: uv run --with anthropic python <step>.py)")

# Current model identifiers, verified 2026-09-16. These strings are complete as
# written -- appending a date suffix produces a model that does not exist.
OPUS = "claude-opus-5"
SONNET = "claude-sonnet-5"
HAIKU = "claude-haiku-4-5"

# Dollars per million tokens, same source as ../src/pricing.py.
RATES = {
    OPUS:   {"in": 5.00, "out": 25.00},
    SONNET: {"in": 2.00, "out": 10.00},
    HAIKU:  {"in": 1.00, "out":  5.00},
}


def client() -> "anthropic.Anthropic":
    """An API client, with a readable error when the key is missing."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Only these steps need it. The bench in ../src/ runs with no key at all."
        )
    return anthropic.Anthropic()


def cost_usd(model: str, usage) -> float:
    """Price a call from what the API says it actually used.

    Note this reads usage off the RESPONSE rather than estimating. The model
    decides how many output tokens to spend, so the only honest cost is the
    reported one.
    """
    rate = RATES[model]
    return (usage.input_tokens * rate["in"] + usage.output_tokens * rate["out"]) / 1_000_000


@dataclass
class Result:
    """One call, with everything needed to compare it against another."""

    model: str
    text: str
    seconds: float
    input_tokens: int
    output_tokens: int
    cost: float


def call(model: str, system: str, prompt: str, max_tokens: int = 1024, effort: str | None = None) -> Result:
    """One request, timed and priced.

    `effort` trades thoroughness against token spend WITHIN a model. It is the
    lever to reach for before adding a second model -- which is the whole point
    of step 03. Not every tier accepts it, so it is only sent when asked for.
    """
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    if effort:
        kwargs["output_config"] = {"effort": effort}

    started = time.time()
    response = client().messages.create(**kwargs)
    elapsed = time.time() - started

    text = "".join(b.text for b in response.content if b.type == "text")
    return Result(
        model=model,
        text=text.strip(),
        seconds=elapsed,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost=cost_usd(model, response.usage),
    )


def row(label: str, r: Result) -> str:
    """One comparison line. Cost is shown to 6 places because these are cents."""
    return (
        f"  {label:<22} {r.seconds:>6.2f}s  "
        f"in={r.input_tokens:>6}  out={r.output_tokens:>5}  ${r.cost:>9.6f}"
    )
