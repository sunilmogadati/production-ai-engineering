"""The router: choose a model, and say why.

The rule this module exists to enforce is that a routing decision is never returned
without the rule that produced it. A bare model name is an instruction; a model name
plus the rule that chose it is an argument, and an argument can be reviewed.

It also refuses to hide the classifier. Deciding where to route is itself a model
call with a price, charged on every request -- including the ones that end up at the
expensive model anyway. Folding that into the routed call makes routing look cheaper
than it is, which is exactly the error this build exists to correct.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import policy as policy_module
import pricing

# The classifier runs on the cheapest tier -- there is no sense paying a large model
# to decide which model to pay. Its cost is small per call and relentless in aggregate.
CLASSIFIER_MODEL = pricing.MODELS["haiku"].model_id

# A classification call is a short prompt and a very short answer. These are the
# token counts the accounting assumes; the live path replaces them with measured ones.
CLASSIFIER_INPUT_TOKENS = 220
CLASSIFIER_OUTPUT_TOKENS = 8


@dataclass(frozen=True)
class Decision:
    """A routing decision and everything needed to argue with it."""

    model_id: str
    rule_id: str
    rule_why: str
    routed_cost_usd: float
    classifier_cost_usd: float

    @property
    def total_cost_usd(self) -> float:
        """What the request actually costs: the routed call plus the decision itself."""
        return self.routed_cost_usd + self.classifier_cost_usd

    def as_dict(self) -> dict:
        out = asdict(self)
        out["total_cost_usd"] = self.total_cost_usd
        return out


def classifier_cost_usd(
    input_tokens: int = CLASSIFIER_INPUT_TOKENS,
    output_tokens: int = CLASSIFIER_OUTPUT_TOKENS,
) -> float:
    """What it costs to decide where to route. Never folded into the routed call."""
    return pricing.cost_usd(CLASSIFIER_MODEL, input_tokens, output_tokens)


def route(task: dict, rules: list[dict] | None = None) -> Decision:
    """Select a model for a task and return the decision with its reasoning.

    `task` carries the features the policy reads: input_tokens, expected output_tokens,
    complexity (1-5) and whether it is latency-sensitive.
    """
    rules = policy_module.DEFAULT_POLICY if rules is None else rules

    features = {
        "input_tokens": task["input_tokens"],
        "complexity": task["complexity"],
        "latency_sensitive": task.get("latency_sensitive", False),
    }

    for rule in rules:
        if not policy_module.matches(rule, features):
            continue

        model_id = pricing.MODELS[rule["route_to"]].model_id

        # A rule may select a model the input cannot physically fit into. Routing to
        # it anyway would turn a cost decision into a runtime failure, so the guard
        # lives here and reports itself as its own rule rather than silently correcting.
        if not pricing.fits_context(model_id, task["input_tokens"]):
            model_id = pricing.MODELS["opus"].model_id
            return Decision(
                model_id=model_id,
                rule_id=f"{rule['id']}+context-guard",
                rule_why=(
                    f"{rule['why']} Overridden: the input does not fit "
                    f"{rule['route_to']}'s context window."
                ),
                routed_cost_usd=pricing.cost_usd(
                    model_id, task["input_tokens"], task["output_tokens"]
                ),
                classifier_cost_usd=classifier_cost_usd(),
            )

        return Decision(
            model_id=model_id,
            rule_id=rule["id"],
            rule_why=rule["why"],
            routed_cost_usd=pricing.cost_usd(
                model_id, task["input_tokens"], task["output_tokens"]
            ),
            classifier_cost_usd=classifier_cost_usd(),
        )

    # Unreachable with DEFAULT_POLICY, whose last rule matches everything. A custom
    # policy without a terminal rule fails here rather than returning a silent default.
    raise ValueError(
        f"no rule matched task {task.get('id', '<unnamed>')!r}; "
        "a policy needs a terminal rule with empty conditions"
    )
