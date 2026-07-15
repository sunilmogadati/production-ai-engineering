"""ML demo 04: random forest - many trees vote, one answers.

Session 4 step 2. One tree is readable but fragile (change the data a little,
get a different tree). A random forest trains hundreds of slightly different
trees and lets them vote. More robust, less readable.

Run from the repo root (after ml01):

    ./venv/bin/python ml04_random_forest.py
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from ai01_rules_baseline import rule_predict

FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]


def main() -> None:
    df = pd.read_csv("data/leads.csv")
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(train[FEATURES], train["converted"])
    accuracy = model.score(test[FEATURES], test["converted"])

    rules_acc = (
        pd.Series(
            [rule_predict(r.intent_signal, r.budget, r.ad_source) for r in test.itertuples()],
            index=test.index,
        )
        == test["converted"]
    ).mean()

    print("Random forest: 300 trees vote on each lead")
    print("=" * 68)
    print(f"Hand-written rules accuracy (same test set) : {100 * rules_acc:.1f}%")
    print(f"Random forest accuracy                      : {100 * accuracy:.1f}%")
    print()
    print("Which signals mattered most (feature importance):")
    for name, importance in sorted(zip(FEATURES, model.feature_importances_), key=lambda x: -x[1]):
        bar = "#" * int(importance * 60)
        print(f"  {name:<16} {importance:.3f} {bar}")
    print()
    print("Trade-off: we gained robustness but lost the readable tree.")
    print("You cannot print 300 trees on a slide - explainability now needs tooling.")


if __name__ == "__main__":
    main()
