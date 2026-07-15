"""ML demo 03: decision tree - a model you can read like rules.

Session 4 opener. The bridge concept:

    A decision tree IS a rule engine - except the machine wrote the rules
    by learning them from data, instead of a developer guessing thresholds.

Run from the repo root (after ml01):

    ./venv/bin/python ml03_decision_tree.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

from ai01_rules_baseline import rule_predict

FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]


def main() -> None:
    # ========================================================================
    # Step 1: Load and prepare the data
    # ========================================================================
    df = pd.read_csv("data/leads.csv")

    # One-hot encode the ad_source (categorical -> numeric).
    # If ad_source == "tv", then ad_tv = 1; else 0.
    # This converts strings ("tv", "social", "email") to numbers (0 or 1).
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    # ========================================================================
    # Step 2: Split into train (80%) and test (20%)
    # ========================================================================
    # The tree learns from TRAIN and is evaluated on TEST.
    # stratify ensures both sets have roughly the same conversion rate (~40%).
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    # ========================================================================
    # Step 3: Train the decision tree
    # ========================================================================
    # A tree learns by:
    #   1. Finding the feature that best splits the data (high information gain)
    #   2. Splitting on that feature at a threshold (e.g., intent > 68)
    #   3. Repeating recursively on each branch until pure or stopping criterion met
    #
    # max_depth=4 limits tree depth -> keeps it readable.
    # Without this, the tree grows very deep and overfits.
    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(train[FEATURES], train["converted"])

    # ========================================================================
    # Step 4: Evaluate on held-out test set
    # ========================================================================
    # Accuracy = (# correct predictions) / (total test samples)
    # This is the percentage of prospects the tree classified correctly.
    accuracy = model.score(test[FEATURES], test["converted"])

    # ========================================================================
    # Step 5: Compare to hand-written rules (our baseline from ml01)
    # ========================================================================
    # We wrote rules by hand: "if intent > 50 and budget > 100, convert".
    # The tree learned rules from data. Which is better?
    rules_acc = (
        pd.Series(
            [rule_predict(r.intent_signal, r.budget, r.ad_source) for r in test.itertuples()],
            index=test.index,
        )
        == test["converted"]
    ).mean()

    print("Decision tree: rules LEARNED from data (not guessed)")
    print("=" * 68)
    print(f"Hand-written rules accuracy (same test set) : {100 * rules_acc:.1f}%")
    print(f"Decision tree accuracy                      : {100 * accuracy:.1f}%")
    print()
    print("The LEARNED rules (read like if-elif-else):")
    print(export_text(model, feature_names=FEATURES, max_depth=3))
    print("Notice:")
    print("  - The tree found thresholds by learning (intent > 68, budget > 114, etc.)")
    print("  - It discovered interactions: prior_purchases + ad_channel + budget")
    print("  - Our hand-written rules MISSED these interactions")
    print()
    print("KEY INSIGHT: You can convert this tree to Python if-else code!")
    print("    def predict(intent, budget, ...):")
    print("        if intent <= 68:")
    print("            return 0  # SKIP")
    print("        elif budget <= 114:")
    print("            return 0  # SKIP")
    print("        else:")
    print("            return 1  # CONVERT")


if __name__ == "__main__":
    main()
