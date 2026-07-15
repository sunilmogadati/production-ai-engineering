"""AI demo 01: evaluate the rule-based lead scorer against real outcomes.

This applies the SAME scoring rules as main_ai.py /ml/score-lead to the
synthetic dataset from ml01_generate_synthetic_data.py, then measures how
often the rules got it right.

This is the "rules break down" moment of Session 3:
- the rules are sensible, explainable, and were fast to write
- but they ignore prior_purchases, miss the ad/budget interaction,
  and treat intent as a straight line

Run from the repo root (after ml01):

    ./venv/bin/python ai01_rules_baseline.py
"""

import csv
from pathlib import Path

DATA = Path("data/leads.csv")


def rule_score(intent_signal: int, budget: float, ad_source: str) -> float:
    """Verbatim logic from main_ai.py score_lead."""
    base_score = intent_signal * 0.6
    budget_score = 20 if budget >= 100 else 10 if budget >= 50 else 0
    ad_score = 10 if ad_source == "tv" else 5 if ad_source == "social" else 3
    return min(100.0, base_score + budget_score + ad_score)


def rule_predict(intent_signal: int, budget: float, ad_source: str) -> int:
    """Predict conversion: warm-or-hot (score >= 45) counts as 'will convert'."""
    return 1 if rule_score(intent_signal, budget, ad_source) >= 45 else 0


def load_leads() -> list[dict]:
    if not DATA.exists():
        raise SystemExit("data/leads.csv not found. Run ml01_generate_synthetic_data.py first.")
    with DATA.open() as f:
        return [
            {
                **row,
                "budget": float(row["budget"]),
                "intent_signal": int(row["intent_signal"]),
                "prior_purchases": int(row["prior_purchases"]),
                "converted": int(row["converted"]),
            }
            for row in csv.DictReader(f)
        ]


def main() -> None:
    leads = load_leads()

    tp = fp = tn = fn = 0
    misses = []
    for lead in leads:
        predicted = rule_predict(lead["intent_signal"], lead["budget"], lead["ad_source"])
        actual = lead["converted"]
        if predicted == 1 and actual == 1:
            tp += 1
        elif predicted == 1 and actual == 0:
            fp += 1
        elif predicted == 0 and actual == 0:
            tn += 1
        else:
            fn += 1
            misses.append(lead)

    total = len(leads)
    converted = tp + fn                       # leads that actually bought
    accuracy = (tp + tn) / total
    baseline = (tn + fp) / total              # accuracy of always guessing "no"
    recall = tp / converted if converted else 0.0        # of real buyers, share caught
    chased = tp + fp                          # leads the rule said to follow up on
    precision = tp / chased if chased else 0.0           # of chased leads, share that bought

    print("Rule-based lead scorer vs. reality")
    print("=" * 60)
    print("The rule (verbatim from main_ai.py /ml/score-lead):")
    print("  score = intent_signal*0.6 + budget_bonus + ad_bonus")
    print("  predict 'will convert' when score >= 45")
    print("  -> notice it NEVER looks at prior_purchases")
    print()
    print(f"Leads evaluated    : {total}")
    print(f"Actually converted : {converted}  ({100 * converted / total:.1f}%)")
    print()
    print("Is the rule any good? Compare it to plain guessing:")
    print(f"  rule accuracy       : {100 * accuracy:.1f}%")
    print(f"  always guess 'no'   : {100 * baseline:.1f}%   (chase nobody; right whenever they don't buy)")
    verdict = "WORSE than" if accuracy < baseline else "barely beats"
    print(f"  -> the hand-written rule is {verdict} guessing. Looks smart; isn't.")
    print()
    print("Where it goes wrong:")
    print(f"  caught {100 * recall:.0f}% of real buyers            -> missed {fn} sales")
    print(f"  of {chased} leads it chased, {100 * precision:.0f}% bought  -> {fp} wasted follow-ups")
    print()
    print("  confusion matrix        rule: convert   rule: no")
    print(f"    actually converted       {tp:>6}        {fn:>6}")
    print(f"    actually did not         {fp:>6}        {tn:>6}")
    print()

    # Real buyers the rule confidently rejected - watch the prior_purchases column.
    print("Buyers the rule REJECTED (why did they buy? look at prior_purchases):")
    for lead in misses[:5]:
        print(
            f"    {lead['customer_id']}  intent={lead['intent_signal']:>3}  "
            f"budget=${lead['budget']:>3.0f}  ad={lead['ad_source']:<6}  "
            f"prior_purchases={lead['prior_purchases']}  -> bought ${lead['order_value']}"
        )
    print()
    print("Loyal repeat buyers (high prior_purchases) - the exact signal the rule")
    print("can't see. Adding an elif per miss never ends and never generalizes.")
    print("Next: ml02_logistic_regression.py learns the pattern from the data instead.")


if __name__ == "__main__":
    main()
