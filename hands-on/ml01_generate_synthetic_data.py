"""ML demo 01: generate a synthetic call-center leads dataset.

Creates data/leads.csv with 2,000 leads. Exactly FOUR features per lead - the
same small vocabulary we use all through Session 3:

  - intent_signal   : buying intent, 0-100. The productionized version of
                      hello_rules.py's buying_keywords (same idea, computed
                      upstream from the transcript, just on a 0-100 scale).
  - budget          : what the caller says they can spend, in dollars.
  - ad_source       : which campaign brought them in (tv / social / email).
  - prior_purchases : completed orders from the order history table -
                      the loyalty signal the hand-written rules never look at.

Plus two things that are NOT features: converted (the yes/no we predict) and
order_value (the dollar amount we predict for linear regression).

Feature provenance note (objective data only): intent_signal is NOT a gut
feeling - in a real pipeline it is computed upstream from the call transcript
(buying keywords, questions asked), exactly like /nlp/classify-call in
main_ai.py. budget comes from what the caller states; ad_source from the
campaign tracking code; prior_purchases from the order history table.

The ground truth deliberately contains patterns that keyword/threshold rules
cannot express:

1. prior_purchases matters a lot (the rules ignore it completely).
2. Ad source interacts with budget: TV converts HIGH-budget leads,
   social converts LOW-budget leads. A flat "+10 for tv" rule misses this.
3. Intent only matters above a threshold (nonlinear), it is not a straight line.

Run from the repo root:

    ./venv/bin/python ml01_generate_synthetic_data.py
"""

import csv
import math
import random
from pathlib import Path

SEED = 42
N_LEADS = 2000
OUTPUT = Path("data/leads.csv")

AD_SOURCES = ["tv", "social", "email"]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def true_conversion_probability(intent: int, budget: float, ad_source: str, prior_purchases: int, rng: random.Random) -> float:
    """The hidden pattern the rules cannot see. ML has to discover this from data."""
    logit = -3.2

    # Nonlinear intent: a threshold effect, not a straight line.
    if intent >= 60:
        logit += 2.2

    # Loyalty signal the rule engine never looks at.
    logit += 0.8 * prior_purchases

    # Interaction: WHICH budget converts depends on the ad source.
    # (A single "budget" weight cannot express this - budget HELPS tv leads
    # and HURTS social leads. Trees can learn it; straight lines cannot.)
    if ad_source == "tv":
        logit += 2.8 if budget >= 120 else -0.8
    elif ad_source == "social":
        logit += 2.6 if budget < 80 else -0.8
    else:  # email
        logit += 0.3

    # Real data is noisy.
    logit += rng.gauss(0, 0.35)
    return sigmoid(logit)


def true_order_value(intent: int, budget: float, ad_source: str, prior_purchases: int, rng: random.Random) -> float:
    """Order value for converted leads (mostly linear, good for linear regression)."""
    value = 40 + 1.8 * budget + 0.9 * intent + 25 * prior_purchases
    if ad_source == "tv":
        value += 30
    return round(max(20.0, value + rng.gauss(0, 25)), 2)


def main() -> None:
    rng = random.Random(SEED)
    OUTPUT.parent.mkdir(exist_ok=True)

    rows = []
    for i in range(1, N_LEADS + 1):
        intent = rng.randint(0, 100)
        budget = round(rng.uniform(20, 300), 2)
        ad_source = rng.choice(AD_SOURCES)
        prior_purchases = rng.choices([0, 1, 2, 3, 4, 5], weights=[40, 25, 15, 10, 6, 4])[0]

        p = true_conversion_probability(intent, budget, ad_source, prior_purchases, rng)
        converted = 1 if rng.random() < p else 0
        order_value = true_order_value(intent, budget, ad_source, prior_purchases, rng) if converted else 0.0

        rows.append(
            {
                "customer_id": f"CUST-{1000 + i}",
                "intent_signal": intent,
                "budget": budget,
                "ad_source": ad_source,
                "prior_purchases": prior_purchases,
                "converted": converted,
                "order_value": order_value,
            }
        )

    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    converted_count = sum(r["converted"] for r in rows)
    print(f"Wrote {len(rows)} leads to {OUTPUT}")
    print(f"Converted: {converted_count} ({100 * converted_count / len(rows):.1f}%)")
    print()
    print("Hidden patterns baked into this data (the reveal for class):")
    print("  1. prior_purchases strongly predicts conversion - the rules IGNORE it")
    print("  2. tv converts HIGH budget, social converts LOW budget - rules add a flat bonus")
    print("  3. intent only matters above 60 - rules treat it as a straight line")


if __name__ == "__main__":
    main()
