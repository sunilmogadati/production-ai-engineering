"""The bench: compare the router against the thing it has to beat.

A bench that only measures the router tells you how the router performs. It does not
tell you whether you should have built one. So every run includes single-model
baselines -- the same workload on one model at varying effort -- and the router is one
row in that table rather than the premise of it.

Two categories of number come out of here and they are never mixed:

  COMPUTED  arithmetic over published rates and token counts. Exact. No API call.
            Per-token cost, cache write/read cost, context-window fit.

  ASSUMED   an input this bench cannot know without running against the live API.
            Effort's effect on output tokens, and how often a tier needs a retry at
            a given complexity. Every assumption is declared in ASSUMPTIONS below and
            echoed into the report, so a reader can see what the conclusion rests on.

Nothing here is labelled MEASURED until a live run produces it (--live), which writes
results/live.json. Until then the report says so.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pricing
import router as router_module
import tasks as tasks_module

RESULTS = Path(__file__).resolve().parent.parent / "results"

# ---------------------------------------------------------------------------
# COMPUTED inputs -- published, exact.
# ---------------------------------------------------------------------------

# Cached prefix reads bill at roughly a tenth of the input rate; writing the cache
# costs roughly a quarter more than an uncached read. These multipliers are the
# mechanism behind the cascade's hidden cost, so they are stated, not buried.
CACHE_READ_MULTIPLIER = 0.1
CACHE_WRITE_MULTIPLIER = 1.25

# Every request in this workload carries the same system prompt and tool definitions.
# This is what a cache holds -- and what a second model in the cascade cannot reuse,
# because caches are scoped to a model.
SHARED_PREFIX_TOKENS = 4_000

# ---------------------------------------------------------------------------
# ASSUMED inputs -- replace these with measurements from a live run.
# ---------------------------------------------------------------------------

ASSUMPTIONS = {
    "effort_output_multiplier": {
        # Effort trades thoroughness against tokens within one model. Thinking tokens
        # bill as output, so lower effort is cheaper on the output side. The shape is
        # documented; these specific ratios are a placeholder until measured.
        "low": 0.45,
        "medium": 0.70,
        "high": 1.00,
        "xhigh": 1.60,
    },
    "retry_rate": {
        # How often a tier fails a task badly enough to need a second attempt, by task
        # complexity. This is the number that decides whether a cascade is cheaper, and
        # it is the one number you cannot get without running your own workload.
        "claude-haiku-4-5": {1: 0.01, 2: 0.04, 3: 0.18, 4: 0.40, 5: 0.60},
        "claude-sonnet-5": {1: 0.01, 2: 0.01, 3: 0.04, 4: 0.14, 5: 0.28},
        "claude-opus-5": {1: 0.00, 2: 0.01, 3: 0.02, 4: 0.05, 5: 0.10},
    },
    "note": (
        "effort_output_multiplier and retry_rate are ASSUMED, not measured. They are "
        "the two inputs that decide whether routing wins. Run --live against your own "
        "workload before trusting any conclusion that depends on them."
    ),
}

# When a tier fails a task, retrying the same tier mostly reproduces the same failure --
# a model that could not do the work does not usually do it on the second attempt. Real
# pipelines escalate instead, which is why a failed cheap call costs cheap-call money
# AND strong-call money. Modelling a retry as a repeat of the same call is the single
# most common way a cost comparison flatters the cheap tier.
ESCALATION_MODEL = "claude-opus-5"


def input_cost(model_id: str, input_tokens: int, cache_warm: bool) -> float:
    """Price the input side of one call, accounting for the model's own cache.

    The prefix is billed at the write rate the first time this model sees it and at
    the read rate afterwards. The rest of the input is billed in full every time.
    """
    prefix = min(SHARED_PREFIX_TOKENS, input_tokens)
    remainder = input_tokens - prefix
    multiplier = CACHE_READ_MULTIPLIER if cache_warm else CACHE_WRITE_MULTIPLIER

    prefix_cost = pricing.cost_usd(model_id, int(prefix * multiplier), 0)
    remainder_cost = pricing.cost_usd(model_id, remainder, 0)
    return prefix_cost + remainder_cost


def run_configuration(
    name: str,
    task_list: list[dict],
    *,
    fixed_model: str | None,
    effort: str,
    use_cache: bool = True,
) -> dict:
    """Run one configuration over the whole task set and total it up.

    `fixed_model=None` means route per task; otherwise every task goes to that model.
    """
    effort_multiplier = ASSUMPTIONS["effort_output_multiplier"][effort]
    retry_rates = ASSUMPTIONS["retry_rate"]

    warm_models: set[str] = set()
    total_routed = 0.0
    total_classifier = 0.0
    total_retry = 0.0
    decisions = []

    for task in task_list:
        if fixed_model is None:
            decision = router_module.route(task)
            model_id = decision.model_id
            classifier = decision.classifier_cost_usd
            rule_id = decision.rule_id
        else:
            model_id = fixed_model
            # A single-model configuration makes no routing decision, so it pays no
            # classifier cost. That is part of why it is a serious contender.
            classifier = 0.0
            rule_id = "fixed"

            # A fixed model still has to hold the input. A task that does not fit is
            # not silently priced as though it did.
            if not pricing.fits_context(model_id, task["input_tokens"]):
                model_id = pricing.MODELS["opus"].model_id
                rule_id = "fixed+context-guard"

        cache_warm = use_cache and model_id in warm_models
        warm_models.add(model_id)

        output_tokens = int(task["output_tokens"] * effort_multiplier)
        call_cost = (
            input_cost(model_id, task["input_tokens"], cache_warm)
            + pricing.cost_usd(model_id, 0, output_tokens)
        )

        # Cost per COMPLETED task: a retry is charged to the configuration that needed
        # it, and it escalates rather than repeating the failed call. The escalation
        # lands on its own model's cache, which for a cheap-tier configuration is cold
        # -- so the failure costs the first call, the stronger call, and a cache write.
        retry_rate = retry_rates[model_id][task["complexity"]]
        escalate_to = ESCALATION_MODEL
        escalation_warm = use_cache and escalate_to in warm_models
        retry_cost = retry_rate * (
            input_cost(escalate_to, task["input_tokens"], escalation_warm)
            + pricing.cost_usd(escalate_to, 0, output_tokens)
        )
        if retry_rate > 0:
            # An escalation warms the strong model's cache for everything after it.
            warm_models.add(escalate_to)

        total_routed += call_cost
        total_classifier += classifier
        total_retry += retry_cost
        decisions.append(
            {"task_id": task["id"], "model_id": model_id, "rule_id": rule_id}
        )

    total = total_routed + total_classifier + total_retry
    return {
        "configuration": name,
        "effort": effort,
        "cache_enabled": use_cache,
        "distinct_models_used": sorted({d["model_id"] for d in decisions}),
        "cost_calls_usd": round(total_routed, 4),
        "cost_classifier_usd": round(total_classifier, 4),
        "cost_escalations_usd": round(total_retry, 4),
        "cost_total_usd": round(total, 4),
        "cost_per_completed_task_usd": round(total / len(task_list), 6),
        "latency_note": "UNMEASURED - requires a live run",
        "quality_note": "UNMEASURED - requires a live run",
        "decisions": decisions,
    }


def offline_report(task_list: list[dict]) -> dict:
    """The full comparison, computed with no API key and no network."""
    configurations = [
        run_configuration("router (policy-based cascade)", task_list, fixed_model=None, effort="high"),
        run_configuration("opus only @ high", task_list, fixed_model="claude-opus-5", effort="high"),
        run_configuration("opus only @ medium", task_list, fixed_model="claude-opus-5", effort="medium"),
        run_configuration("opus only @ low", task_list, fixed_model="claude-opus-5", effort="low"),
        run_configuration("sonnet only @ high", task_list, fixed_model="claude-sonnet-5", effort="high"),
        run_configuration("haiku only @ high", task_list, fixed_model="claude-haiku-4-5", effort="high"),
        # The same cascade with caching switched off, to isolate how much of the
        # router's cost is the cache split rather than the per-token rates.
        run_configuration(
            "router (no cache reuse)", task_list, fixed_model=None, effort="high", use_cache=False
        ),
    ]
    return {
        "mode": "offline",
        "rates_taken_on": pricing.RATES_TAKEN_ON,
        "rates_source": pricing.RATES_SOURCE,
        "task_count": len(task_list),
        "shared_prefix_tokens": SHARED_PREFIX_TOKENS,
        "assumptions": ASSUMPTIONS,
        "configurations": configurations,
    }


def print_table(report: dict) -> None:
    """Human-readable summary. The decisions list stays in the JSON."""
    print(f"\n  {report['task_count']} tasks | rates taken {report['rates_taken_on']} | mode: {report['mode']}")
    print(f"  {'configuration':<32} {'models':>7} {'calls':>9} {'classif':>9} {'escalate':>9} {'TOTAL':>10} {'per task':>10}")
    print("  " + "-" * 92)
    for c in report["configurations"]:
        print(
            f"  {c['configuration']:<32} {len(c['distinct_models_used']):>7} "
            f"{c['cost_calls_usd']:>9.3f} {c['cost_classifier_usd']:>9.3f} "
            f"{c['cost_escalations_usd']:>9.3f} {c['cost_total_usd']:>10.3f} "
            f"{c['cost_per_completed_task_usd']:>10.5f}"
        )
    print("\n  Cost figures above are COMPUTED from published rates, under the ASSUMED")
    print("  effort and retry inputs printed in the JSON report. Latency and quality are")
    print("  UNMEASURED until a live run.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare routing against single-model baselines.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="call the real API to measure latency and replace the assumed inputs (spends money)",
    )
    args = parser.parse_args()

    task_list = tasks_module.load()

    if args.live:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set. The offline path needs no key -- run without --live."
            )
        raise SystemExit(
            "The live path is scaffolded but not yet implemented (see RUNBOOK.md). "
            "It is deliberately absent rather than stubbed with invented numbers."
        )

    report = offline_report(task_list)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "offline.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print_table(report)
    print(f"  full report written to {RESULTS / 'offline.json'}\n")


if __name__ == "__main__":
    main()
