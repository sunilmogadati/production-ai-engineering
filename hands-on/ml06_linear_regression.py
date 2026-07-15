"""ML demo 06: linear regression - predict order VALUE (a number, not yes/no).

Session 3 pairing with ml02:
- logistic regression answers "WILL they buy?"  (classification)
- linear regression answers "HOW MUCH will they spend?"  (regression)

Run from the repo root (after ml01):

    ./venv/bin/python ml06_linear_regression.py
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]


def main() -> None:
    df = pd.read_csv("data/leads.csv")
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    # Only converted leads have an order value to predict.
    buyers = df[df["converted"] == 1]
    train, test = train_test_split(buyers, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(train[FEATURES], train["order_value"])
    predictions = model.predict(test[FEATURES])

    mae = mean_absolute_error(test["order_value"], predictions)
    # Naive baseline: always guess the average order value.
    naive_mae = mean_absolute_error(test["order_value"], [train["order_value"].mean()] * len(test))

    print("Linear regression: how much will this buyer spend?")
    print("=" * 68)
    print(f"Buyers in dataset       : {len(buyers)}")
    print(f"Average order value     : ${buyers['order_value'].mean():.2f}")
    print()
    print(f"Naive guess (always predict the average) is off by : ${naive_mae:.2f} per order")
    print(f"Linear regression is off by                        : ${mae:.2f} per order")
    print()
    print("What the model learned ($ impact per unit):")
    for name, coef in sorted(zip(FEATURES, model.coef_), key=lambda x: -abs(x[1])):
        print(f"  {name:<16} {coef:+.2f}")
    print()
    print("Example predictions vs actual (first 5 test buyers):")
    for (_, row), predicted in list(zip(test.iterrows(), predictions))[:5]:
        print(f"  predicted ${predicted:7.2f}   actual ${row['order_value']:7.2f}")
    print()
    print("Classification answers WILL THEY BUY. Regression answers HOW MUCH.")


if __name__ == "__main__":
    main()
