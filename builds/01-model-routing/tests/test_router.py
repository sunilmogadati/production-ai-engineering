"""The router's contract: never a decision without its reason."""

import pytest

import policy
import pricing
import router
import tasks


def _task(**overrides):
    base = {
        "id": "T-test",
        "kind": "test",
        "complexity": 3,
        "input_tokens": 5_000,
        "output_tokens": 400,
        "latency_sensitive": False,
    }
    base.update(overrides)
    return base


def test_every_decision_carries_its_rule():
    # The guard this build exists to enforce. A bare model name is an instruction;
    # a model name plus its rule is an argument, and an argument can be reviewed.
    for task in tasks.load():
        decision = router.route(task)
        assert decision.rule_id, f"task {task['id']} routed with no rule"
        assert decision.rule_why, f"task {task['id']} routed with no reason"


def test_classifier_cost_is_reported_separately():
    decision = router.route(_task())
    assert decision.classifier_cost_usd > 0
    assert decision.total_cost_usd == pytest.approx(
        decision.routed_cost_usd + decision.classifier_cost_usd
    )


def test_classifier_cost_is_charged_even_when_routing_to_the_expensive_model():
    # The overhead does not disappear just because the routing decision was "opus".
    decision = router.route(_task(complexity=5))
    assert decision.model_id == "claude-opus-5"
    assert decision.classifier_cost_usd > 0


def test_trivial_work_routes_to_the_small_tier():
    decision = router.route(_task(complexity=1, input_tokens=500))
    assert decision.model_id == "claude-haiku-4-5"


def test_oversized_input_never_routes_to_a_model_that_cannot_hold_it():
    # Routing on complexity alone would send this to the small tier and fail at runtime.
    decision = router.route(_task(complexity=1, input_tokens=400_000))
    assert decision.model_id == "claude-opus-5"
    assert "context" in decision.rule_id


def test_a_policy_without_a_terminal_rule_fails_rather_than_defaulting():
    narrow = [r for r in policy.DEFAULT_POLICY if r["when"]]
    with pytest.raises(ValueError):
        router.route(_task(complexity=5, input_tokens=1_000), rules=narrow)


def test_policy_is_data_not_code():
    # FR-004: a reader changes routing by editing the policy, not the router.
    custom = [{"id": "everything-to-sonnet", "why": "test", "when": {}, "route_to": "sonnet"}]
    decision = router.route(_task(complexity=1), rules=custom)
    assert decision.model_id == pricing.MODELS["sonnet"].model_id
    assert decision.rule_id == "everything-to-sonnet"
