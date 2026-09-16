"""Cost arithmetic for Claude model selection.

The point of this module is that it never touches the network. Token pricing is
arithmetic over a published rate table, which means a team can price a workload
exactly -- before spending anything, and before arguing about which model to use.

Every rate carries the date it was taken. A rate table without a date is a rate
table nobody can tell is stale.
"""

from __future__ import annotations

from dataclasses import dataclass

# Rates verified 2026-09-16 against Anthropic's published model pricing.
# Dollars per million tokens. Identifiers carry no date suffix -- appending one
# (a habit picked up from older model families) produces a model that does not exist.
RATES_TAKEN_ON = "2026-09-16"
RATES_SOURCE = "Anthropic published model pricing"


@dataclass(frozen=True)
class Model:
    """A candidate model: what it is called, what it costs, how much it can hold."""

    model_id: str
    input_per_mtok: float
    output_per_mtok: float
    context_window: int


# The three tiers a routing decision actually chooses between.
MODELS: dict[str, Model] = {
    "opus": Model("claude-opus-5", 5.00, 25.00, 1_000_000),
    "sonnet": Model("claude-sonnet-5", 2.00, 10.00, 1_000_000),
    "haiku": Model("claude-haiku-4-5", 1.00, 5.00, 200_000),
}

# Haiku 4.5 predates the 5-family thinking parameter and configures it differently.
# The bench reads this rather than assuming one request shape across all tiers --
# assuming one shape is how a configuration matrix dies on its third row.
FIVE_FAMILY = frozenset({"claude-opus-5", "claude-sonnet-5"})


def cost_usd(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Price one call. Pure arithmetic -- no network, no client, no key.

    Rates are per million tokens, so both sides divide by 1e6.
    """
    model = model_by_id(model_id)
    return (
        input_tokens * model.input_per_mtok
        + output_tokens * model.output_per_mtok
    ) / 1_000_000


def model_by_id(model_id: str) -> Model:
    """Look a model up by its wire identifier, failing loudly on an unknown one."""
    for model in MODELS.values():
        if model.model_id == model_id:
            return model
    raise KeyError(
        f"unknown model id {model_id!r}; known: "
        f"{sorted(m.model_id for m in MODELS.values())}"
    )


def fits_context(model_id: str, input_tokens: int) -> bool:
    """Whether the input fits at all.

    Worth its own function because context is a hard constraint, not a preference:
    a cheaper model that cannot hold the input is not a cheaper option, it is a
    different failure. Haiku's window is a fifth of the others'.
    """
    return input_tokens <= model_by_id(model_id).context_window
