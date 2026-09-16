"""The routing policy, declared as data.

A policy expressed as nested `if` statements inside the router can only be argued
with by reading code. Expressed as an ordered list of rules, it can be reviewed by
someone who will never open router.py -- which is the person whose budget it is.

Rules are evaluated in order and the first match wins, so ordering is part of the
policy and deliberately visible.
"""

from __future__ import annotations

# Each rule: an id you can cite in a review, a plain-English reason, the conditions
# that must all hold, and the tier to route to. Conditions are a deliberately small
# vocabulary -- a policy language that can express anything becomes a second program.
#
#   max_input_tokens / min_input_tokens : integer bounds on task size
#   max_complexity / min_complexity     : 1 (trivial) .. 5 (genuinely hard)
#   latency_sensitive                   : bool, task must answer fast
#
# Edit this list to change routing behaviour. No code change is required.
DEFAULT_POLICY: list[dict] = [
    {
        "id": "R1-context-overflow",
        "why": "Input exceeds the small tier's window, so the cheap option is not an option.",
        "when": {"min_input_tokens": 200_001},
        "route_to": "opus",
    },
    {
        "id": "R2-latency-first",
        "why": "The task is latency-sensitive and simple enough that the fast tier holds quality.",
        "when": {"latency_sensitive": True, "max_complexity": 2},
        "route_to": "haiku",
    },
    {
        "id": "R3-trivial",
        "why": "Classification and extraction at this complexity do not repay a larger model.",
        "when": {"max_complexity": 2},
        "route_to": "haiku",
    },
    {
        "id": "R4-moderate",
        "why": "Mid-complexity work where the mid tier has historically held the quality bar.",
        "when": {"max_complexity": 3},
        "route_to": "sonnet",
    },
    {
        "id": "R5-default-hard",
        "why": "Anything harder goes to the strongest model. The default is capability, not thrift.",
        "when": {},
        "route_to": "opus",
    },
]


def matches(rule: dict, features: dict) -> bool:
    """Whether every condition in a rule holds for a task's features.

    An empty condition set matches everything -- that is how the terminal default
    rule is expressed, rather than as a special case in the router.
    """
    conditions = rule["when"]
    for key, expected in conditions.items():
        if key == "max_input_tokens" and features["input_tokens"] > expected:
            return False
        if key == "min_input_tokens" and features["input_tokens"] < expected:
            return False
        if key == "max_complexity" and features["complexity"] > expected:
            return False
        if key == "min_complexity" and features["complexity"] < expected:
            return False
        if key == "latency_sensitive" and features.get("latency_sensitive", False) != expected:
            return False
    return True
