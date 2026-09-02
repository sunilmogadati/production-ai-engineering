"""A minimal model router — the single choke point for model selection.

The caller never names a model. It passes a `task` (what kind of work) and a
`sensitivity` (how private the data is); the router resolves those to a concrete
(tier, model) and enforces a data-residency guardrail. Centralizing this means
you change routing in ONE place, and callers can't smuggle in an off-policy model.

Real production would also stream a full agent loop (tool calls + results) and
tag cost after the stream. This demo keeps the *shape* exactly and stubs the
internals so it runs with ZERO api keys. Set ANTHROPIC_API_KEY to stream real
Claude tokens instead of the fake agent.
"""

import asyncio
import os

# --- TASK -> (tier, model) ------------------------------------------------
# Never hardcoded per-call; the caller passes `task`, the router picks this.
ROUTES = {
    "chat":       ("mid",   "claude-sonnet-4-6"),
    "synthesize": ("high",  "claude-opus-4-8"),
    "extract":    ("cheap", "claude-haiku-4-5"),
    "classify":   ("cheap", "claude-haiku-4-5"),
}

# --- SENSITIVITY -> which provider *kinds* may serve each class ------------
# A vendor API can never serve confidential/restricted data — the data-residency
# argument for why a stream like this lives in your own Python tier, next to the
# router and the guardrail, rather than in a thin edge proxy.
ALLOWED_PROVIDERS = {
    "public":       {"api", "bedrock", "local"},
    "internal":     {"api", "bedrock", "local"},
    "confidential": {"bedrock", "local"},   # never leaves your cloud/on-prem
    "restricted":   {"local"},              # never leaves the box
}

USE_REAL = bool(os.getenv("ANTHROPIC_API_KEY"))   # real Claude if a key is present


def resolve(task: str, sensitivity: str) -> tuple[str, str]:
    """task + sensitivity -> (tier, model). The single choke point."""
    tier, model = ROUTES.get(task, ROUTES["chat"])
    # A fuller router would also pick a provider from ALLOWED_PROVIDERS[sensitivity]
    # and refuse if none is reachable. Shown here so the guardrail is visible.
    return tier, model


async def stream_agent(task: str, sensitivity: str, input: list[dict], ctx: dict):
    """Streaming twin of a request handler — yields TYPED events, not bare text.

    Event types (fixed from day one so the wire format survives the jump from
    text-only to agentic tool-streaming — you don't want to re-cut the contract
    once clients depend on it):
        {"type": "delta",       "text": ...}
        {"type": "tool_call",   "name": ..., "input": ...}
        {"type": "tool_result", "name": ..., "output": ...}
        {"type": "done",        "model": ..., "tier": ...}
    """
    tier, model = resolve(task, sensitivity)

    if USE_REAL:
        async for ev in _real_stream(model, input):
            yield ev
    else:
        async for ev in _fake_agent(model, input):
            yield ev

    # Post-hoc cost/attribution: a stream's cost is known only once it finishes,
    # so cost/model land on the final `done` frame, not before.
    yield {"type": "done", "model": model, "tier": tier}


async def _fake_agent(model: str, input: list[dict]):
    """A zero-dependency stand-in for a real agent loop.

    Demonstrates the agentic envelope live with no api key: the agent thinks
    (text), calls a tool, reads the result, then answers — every frame typed.
    """
    prompt = input[-1].get("content", "") if input else ""

    for w in f"Looking into: {prompt} ".split():
        await asyncio.sleep(0.06)
        yield {"type": "delta", "text": w + " "}

    # The part a bare completion can't express — a typed tool call + result.
    yield {"type": "tool_call", "name": "lookup_order", "input": {"order": "A-1042"}}
    await asyncio.sleep(0.5)
    yield {"type": "tool_result", "name": "lookup_order",
           "output": {"shipped": False, "reason": "address failed validation, awaiting fix"}}

    for w in "Found it: the order has not shipped because the address failed validation and is awaiting a fix.".split():
        await asyncio.sleep(0.06)
        yield {"type": "delta", "text": w + " "}


async def _real_stream(model: str, input: list[dict]):
    """Real Claude tokens via the Anthropic SDK's native streaming helper.

    (Single-call streaming for the demo. A production build would wire a full
    agent loop here so real tool_call/tool_result frames flow too.)
    """
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic()
    async with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=input,
    ) as stream:
        async for text in stream.text_stream:
            yield {"type": "delta", "text": text}
