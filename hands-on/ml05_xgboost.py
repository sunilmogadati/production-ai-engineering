"""ML demo 05: gradient boosting (XGBoost) - the tabular data benchmark.

Session 4 step 3. Boosting builds trees one after another, where each new
tree focuses on the mistakes of the previous ones. XGBoost is the
industry-standard implementation and the model to beat on tabular data.

Run from the repo root (after ml01):

    ./venv/bin/python ml05_xgboost.py

Classroom-safe fallback: if xgboost is not installed (it needs libomp on
macOS), this script automatically uses scikit-learn's gradient boosting
instead, so the demo never blocks the class.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from ai01_rules_baseline import rule_predict

FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]

try:
    from xgboost import XGBClassifier

    MODEL_NAME = "XGBoost"
    model = XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
    )
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier

    MODEL_NAME = "Gradient boosting (scikit-learn fallback - xgboost not installed)"
    model = HistGradientBoostingClassifier(max_iter=300, max_depth=4, random_state=42)


def main() -> None:
    df = pd.read_csv("data/leads.csv")
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    model.fit(train[FEATURES], train["converted"])
    accuracy = model.score(test[FEATURES], test["converted"])

    rules_acc = (
        pd.Series(
            [rule_predict(r.intent_signal, r.budget, r.ad_source) for r in test.itertuples()],
            index=test.index,
        )
        == test["converted"]
    ).mean()

    short_name = MODEL_NAME.split(" (")[0]
    print(f"{MODEL_NAME}: trees that learn from each other's mistakes")
    print("=" * 68)
    print(f"{'Hand-written rules accuracy (same test set)':<44}: {100 * rules_acc:.1f}%")
    print(f"{short_name + ' accuracy':<44}: {100 * accuracy:.1f}%")
    print()
    print("The model ladder for this dataset (run each script to see it):")
    print("  hand-written rules  ->  logistic regression  ->  tree  ->  forest  ->  boosting")
    print("  (explainable, brittle)                          (accurate, needs tooling to explain)")
    print()
    print("Model choice is a business decision, not a leaderboard decision:")
    print("  - need to defend every decision to a regulator? tree or logistic")
    print("  - need best accuracy on tabular data? boosting")
    print("  - need a robust default? random forest")


if __name__ == "__main__":
    main()
