"""ML demo 09: train, evaluate, and SAVE the model (train time).

This is one half of the real ML lifecycle. This script:

1. trains logistic regression on data/leads.csv
2. measures honest accuracy on a held-out test set
3. saves the model file + a metadata sidecar (version, accuracy, features)

The other half is ml10_load_and_predict.py - a SEPARATE program that never
sees the training data. The models/ files are the handoff between them.

Run from the repo root (after ml01):

    ./venv/bin/python ml09_train_and_save.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# The feature contract: ml10 (and later, the serving API) must build
# features in EXACTLY this order.
FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]

MODEL_PATH = Path("models/lead_model.joblib")
META_PATH = Path("models/lead_model.json")


def main() -> None:
    df = pd.read_csv("data/leads.csv")
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    # .values strips column names so predict time can pass plain lists.
    model = LogisticRegression(max_iter=2000)
    model.fit(train[FEATURES].values, train["converted"])
    accuracy = model.score(test[FEATURES].values, test["converted"])

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metadata = {
        "model_version": "1.0",
        "model_type": "LogisticRegression",
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "test_accuracy": round(accuracy, 4),
        "features": FEATURES,
        "training_rows": len(train),
    }
    META_PATH.write_text(json.dumps(metadata, indent=2))

    print("Train time is DONE. Artifacts on disk:")
    print(f"  {MODEL_PATH}  (the model)")
    print(f"  {META_PATH}    (version, accuracy, feature contract)")
    print()
    print(f"Test accuracy: {100 * accuracy:.1f}%  |  model_version: {metadata['model_version']}")
    print()
    print("Next: ml10_load_and_predict.py uses these files WITHOUT retraining")
    print("and without ever reading the training data.")


if __name__ == "__main__":
    main()
