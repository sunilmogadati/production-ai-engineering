"""The bench's contract: it runs with no key, and it never lets the router grade itself."""

import os

import bench
import tasks


def test_offline_bench_runs_with_no_api_key(monkeypatch):
    # SC-001. The offline path is the one a reader runs first, and it must not need
    # a credential -- or the build fails Constitution V on the reader's first attempt.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    report = bench.offline_report(tasks.load())
    assert report["mode"] == "offline"
    assert report["configurations"]


def test_report_includes_at_least_one_single_model_baseline():
    # FR-006, SC-004. Without a baseline the bench measures how the router performs,
    # not whether it should exist.
    report = bench.offline_report(tasks.load())
    single_model = [c for c in report["configurations"] if len(c["distinct_models_used"]) == 1]
    assert single_model, "no single-model baseline in the report"


def test_effort_is_part_of_a_configurations_identity():
    report = bench.offline_report(tasks.load())
    for configuration in report["configurations"]:
        assert configuration["effort"] in bench.ASSUMPTIONS["effort_output_multiplier"]


def test_assumed_inputs_are_declared_in_the_report():
    # SC-005. The conclusion rests on these; a reader must be able to see them.
    report = bench.offline_report(tasks.load())
    assert "effort_output_multiplier" in report["assumptions"]
    assert "retry_rate" in report["assumptions"]
    assert "ASSUMED" in report["assumptions"]["note"]


def test_unmeasured_figures_say_so_rather_than_carrying_a_number():
    report = bench.offline_report(tasks.load())
    for configuration in report["configurations"]:
        assert configuration["latency_note"].startswith("UNMEASURED")
        assert configuration["quality_note"].startswith("UNMEASURED")


def test_cache_reuse_changes_the_answer():
    # The mechanism behind the cascade's hidden cost. If switching caching off does
    # not move the number, the bench is not modelling the thing it claims to model.
    task_list = tasks.load()
    warm = bench.run_configuration("r", task_list, fixed_model=None, effort="high", use_cache=True)
    cold = bench.run_configuration("r", task_list, fixed_model=None, effort="high", use_cache=False)
    assert cold["cost_total_usd"] > warm["cost_total_usd"]


def test_classifier_cost_is_zero_for_single_model_configurations():
    # A fixed-model configuration makes no routing decision, so it pays no routing tax.
    report = bench.offline_report(tasks.load())
    for configuration in report["configurations"]:
        if len(configuration["distinct_models_used"]) == 1:
            assert configuration["cost_classifier_usd"] == 0.0


def test_cost_per_completed_task_counts_escalations():
    # FR-007. A cheaper call that needed a stronger second call is not a cheaper call.
    task_list = tasks.load()
    haiku = bench.run_configuration(
        "haiku", task_list, fixed_model="claude-haiku-4-5", effort="high"
    )
    assert haiku["cost_escalations_usd"] > 0
    assert haiku["cost_total_usd"] > haiku["cost_calls_usd"]
