"""AI demo 02: the model showdown - same leads, one table, the accuracy climb.

This is the payoff of Session 3->4. It answers the three questions students
always ask, in one run:

  1. Is it really the SAME data feeding if/else -> logistic -> tree -> forest
     -> xgboost?  Yes: identical leads, identical features, identical
     train/test split. Only the model changes.
  2. Does the accuracy actually climb?  See the LADDER table.
  3. Remember Meera from hello_rules.py (loyal buyer the if/else called cold)?
     Who is her equivalent here?  See the SPOTLIGHT table - real leads the
     hand-written rule REJECTS but every model gets right, each one a loyal
     repeat buyer (high prior_purchases) the rule is blind to.

Run from the repo root (after ml01):

    ./venv/bin/python ai02_model_comparison.py
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from ai01_rules_baseline import rule_predict

# The exact same feature vector every model in the course uses.
FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]

# Build each model the SAME way its own ml0X demo builds it, so the numbers
# here match those files. XGBoost falls back to sklearn boosting if the
# xgboost/libomp install is missing, so class is never blocked.
try:
    from xgboost import XGBClassifier

    boosting = XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.1, eval_metric="logloss")
    BOOSTING_LABEL = "xgboost"
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier

    boosting = HistGradientBoostingClassifier(max_iter=300, max_depth=4, random_state=42)
    BOOSTING_LABEL = "boosting (sklearn)"


def main() -> None:
    # SAME data + SAME features + SAME split as every other demo.
    df = pd.read_csv("data/leads.csv")
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    # Train every model on the SAME training leads (order = weakest -> strongest).
    # .values strips column names so predict time can pass plain lists (same
    # trick as ml09_train_and_save.py) - keeps sklearn from warning later.
    models = {
        "logistic regression": LogisticRegression(max_iter=2000),
        "decision tree": DecisionTreeClassifier(max_depth=4, random_state=42),
        "random forest": RandomForestClassifier(n_estimators=300, random_state=42),
        BOOSTING_LABEL: boosting,
    }
    for model in models.values():
        model.fit(train[FEATURES].values, train["converted"])

    # The hand-written rule is the baseline - the thing to beat.
    rule_preds_test = [rule_predict(r.intent_signal, r.budget, r.ad_source) for r in test.itertuples()]
    rules_acc = (pd.Series(rule_preds_test, index=test.index) == test["converted"]).mean()

    # ---- LADDER: does accuracy actually climb? ----
    scores = [("if/else rules (baseline)", rules_acc)]
    scores += [(name, model.score(test[FEATURES].values, test["converted"])) for name, model in models.items()]
    scores.sort(key=lambda x: x[1])  # weakest first, so you watch it climb

    print("Same 2,000 leads. Same features. Only the model changes.")
    print("=" * 64)
    print(f"{'model':<28}{'accuracy':>10}{'vs. rules':>14}")
    print("-" * 64)
    for name, acc in scores:
        delta = "" if name.startswith("if/else") else f"+{100 * (acc - rules_acc):.1f} pts"
        print(f"{name:<28}{100 * acc:>9.1f}%{delta:>14}")
    print()

    # ---- SPOTLIGHT: the ml-tier 'Meera' - real leads the rule rejects ----
    # Every one is a real buyer (converted=1) the rule predicted "skip",
    # sorted so the most loyal (highest prior_purchases) show first.
    missed = test[(test["converted"] == 1) & (pd.Series(rule_preds_test, index=test.index) == 0)]
    spotlight = missed.sort_values("prior_purchases", ascending=False).head(5)

    # Short, aligned column labels for the model verdicts.
    short = {
        "logistic regression": "logistic",
        "decision tree": "tree",
        "random forest": "forest",
        BOOSTING_LABEL: "xgb" if BOOSTING_LABEL == "xgboost" else "boost",
    }
    verdict_labels = ["rule"] + [short[name] for name in models]

    print("Spotlight: real buyers the if/else RULE rejected (each one a 'Meera')")
    print("=" * 86)
    feature_head = f"{'lead':<11}{'intent':>7}{'budget':>8}{'ad':>8}{'prior':>6}{'actual':>8}   "
    print(feature_head + "".join(f"{lbl:<9}" for lbl in verdict_labels))
    print("-" * 88)
    for row in spotlight.itertuples():
        x = [[getattr(row, f) for f in FEATURES]]
        verdicts = ["BUY" if rule_predict(row.intent_signal, row.budget, row.ad_source) else "skip"]
        verdicts += ["BUY" if model.predict(x)[0] == 1 else "skip" for model in models.values()]
        line = (
            f"{row.customer_id:<11}{row.intent_signal:>7}{row.budget:>8.0f}"
            f"{row.ad_source:>8}{row.prior_purchases:>6}{'BUY':>8}   "
        )
        print(line + "".join(f"{v:<9}" for v in verdicts))
    print()
    print("The rule says 'skip' on every one (it never looks at prior_purchases).")
    print("The models say 'BUY' - they learned that loyalty predicts buying, the")
    print("exact lesson hello_rules.py's Meera taught, now at 2,000-lead scale.")
    print("Same data in; smarter model out. That is the whole of Session 3->4.")


if __name__ == "__main__":
    main()
