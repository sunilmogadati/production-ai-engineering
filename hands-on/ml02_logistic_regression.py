"""ML demo 02: logistic regression - predict conversion yes/no.

The "ML addresses it" moment of Session 3. Same data as the rules baseline,
but instead of hand-writing thresholds we let the model LEARN the weights.

The math in one paragraph (layman's version):
    The model computes a WEIGHTED SUM of the features (like a scorecard:
    so many points per prior purchase, so many per intent point...), then
    squashes that sum through an S-shaped curve (the SIGMOID) so it always
    lands between 0 and 1 - a probability. "Training" means: try weights,
    see how wrong the predictions are on the examples, nudge the weights
    to be less wrong, repeat. The machine tunes the scorecard; we don't.

What to notice in class:
- accuracy jumps over the rules, with zero hand-written elifs
- the model uses prior_purchases (the signal the rules ignored)
- the coefficients are readable: ML can still be explainable

Run from the repo root (after ml01):

    ./venv/bin/python ml02_logistic_regression.py
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from ai01_rules_baseline import rule_predict

# The FEATURES: the model's inputs, always as numbers.
# (Math term: the "feature vector" x - one list of numbers per lead.)
FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]


def load_features() -> pd.DataFrame:
    # STEP 1: load the 2,000 historical leads (features + known outcome).
    # Math term: this is the DATASET; the "converted" column is the LABEL y
    # (the right answer we want the model to learn to predict).
    df = pd.read_csv("data/leads.csv")

    # STEP 2: ONE-HOT ENCODING - turn text into numbers.
    # An equation cannot multiply a weight by the word "tv". So the single
    # text column ad_source becomes three 0/1 columns: ad_tv, ad_social,
    # ad_email. Exactly one of them is 1 per lead ("one hot").
    # Layman's version: three light switches instead of one label.
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)
    return df


def rules_accuracy(df: pd.DataFrame) -> float:
    # The BASELINE: run the hand-written rules over the same leads, so the
    # model has something fair to be compared against.
    # (Golden habit: never report a model's score without a baseline.)
    predictions = [
        rule_predict(row.intent_signal, row.budget, row.ad_source) for row in df.itertuples()
    ]
    # ACCURACY = correct predictions / total predictions.
    return (pd.Series(predictions, index=df.index) == df["converted"]).mean()


def main() -> None:
    df = load_features()

    # STEP 3: TRAIN/TEST SPLIT - hold back an exam the model never studies.
    # 80% of leads (1,600) are for learning; 20% (400) are hidden away and
    # only used for grading. Grading on data the model has already seen
    # would be an open-book exam - it proves memorization, not learning.
    # Math terms: TRAINING SET vs TEST SET (a "held-out" set).
    # stratify=... keeps the same %converted in both halves, so the exam
    # is not accidentally easier or harder than the course material.
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    # STEP 4: the MODEL. Logistic regression predicts a probability:
    #
    #     z = w1*intent + w2*budget + w3*prior_purchases + ... + b
    #     probability = sigmoid(z) = 1 / (1 + e^-z)
    #
    # - z is the WEIGHTED SUM (math term: a linear combination). Layman:
    #   a scorecard - each feature contributes points times its weight.
    # - the SIGMOID squashes any score into the 0..1 range, S-shaped:
    #   very negative z -> near 0 (won't buy), very positive -> near 1.
    # - the weights w1..wn are the COEFFICIENTS; b is the INTERCEPT
    #   (the starting score before we know anything about the lead).
    model = LogisticRegression(max_iter=2000)

    # STEP 5: TRAINING (the .fit call - this is the whole "learning" step).
    # Math version: find the weights that make the observed outcomes most
    # probable (MAXIMUM LIKELIHOOD), by GRADIENT DESCENT - measure how
    # wrong the current weights are (the LOSS), nudge each weight downhill,
    # repeat up to max_iter times until the nudges stop helping.
    # Layman's version: turn the knobs until the scorecard best explains
    # what actually happened in the 1,600 training leads.
    model.fit(train[FEATURES], train["converted"])

    # STEP 6: EVALUATION on the held-out 400 leads (the closed-book exam).
    # .score() runs a prediction for each test lead and reports accuracy.
    # A lead is predicted "converts" when its probability >= 0.5
    # (math term: the DECISION BOUNDARY/THRESHOLD - and it's a business
    # dial: lower it to catch more buyers at the cost of more false alarms).
    accuracy = model.score(test[FEATURES], test["converted"])

    print("Logistic regression: will this lead convert? (yes/no classification)")
    print("=" * 68)
    print(f"Training leads   : {len(train)}")
    print(f"Test leads       : {len(test)} (held out - the model never saw these)")
    print()
    # Head-to-head on the SAME test set - the only fair comparison.
    print(f"Rules baseline accuracy (same test set) : {100 * rules_accuracy(test):.1f}%")
    print(f"Logistic regression accuracy            : {100 * accuracy:.1f}%")
    print()

    # STEP 7: EXPLAINABILITY - read the learned weights.
    # A positive coefficient pushes the probability UP (toward "buys"),
    # a negative one pushes it DOWN. Bigger magnitude = stronger push
    # per unit of that feature. (Caveat for class: features have different
    # scales - budget runs 20-300, prior_purchases 0-5 - so compare
    # direction and story, not raw magnitude across features.)
    print("What the model learned (coefficients, higher = pushes toward convert):")
    for name, coef in sorted(zip(FEATURES, model.coef_[0]), key=lambda x: -abs(x[1])):
        print(f"  {name:<16} {coef:+.3f}")
    print()
    print("Notice: prior_purchases has real weight - the rules never looked at it.")
    print("Nobody wrote an elif. The model found the pattern in the data.")


if __name__ == "__main__":
    main()
