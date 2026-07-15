"""ML demo 10: load the saved model and predict (predict time).

The other half of the lifecycle. Notice what this script does NOT do:

- it does NOT import scikit-learn's trainers
- it does NOT read data/leads.csv
- it does NOT retrain anything

It loads two files from models/ and predicts. This is exactly what a
serving API will do in Session 5 - just wrapped in FastAPI.

Run from the repo root (after ml09):

    ./venv/bin/python ml10_load_and_predict.py
"""

import json
from pathlib import Path

import joblib

MODEL_PATH = Path("models/lead_model.joblib")
META_PATH = Path("models/lead_model.json")


def build_features(intent_signal: int, budget: float, ad_source: str, prior_purchases: int) -> list[float]:
    """The feature contract: same order as training (see metadata 'features')."""
    return [
        intent_signal,
        budget,
        prior_purchases,
        1 if ad_source == "tv" else 0,
        1 if ad_source == "social" else 0,
        1 if ad_source == "email" else 0,
    ]


def main() -> None:
    if not MODEL_PATH.exists():
        raise SystemExit("models/lead_model.joblib not found. Run ml09_train_and_save.py first.")

    model = joblib.load(MODEL_PATH)
    metadata = json.loads(META_PATH.read_text())

    print(f"Loaded model_version {metadata['model_version']} "
          f"({metadata['model_type']}, test accuracy {100 * metadata['test_accuracy']:.1f}%, "
          f"trained {metadata['trained_at']})")
    print()

    new_leads = [
        # (name, intent, budget, ad_source, prior_purchases)
        ("high-intent TV lead", 90, 200.0, "tv", 1),
        ("a Meera: low intent, loyal", 30, 70.0, "social", 5),
        ("cold email lead", 15, 30.0, "email", 0),
    ]

    for name, intent, budget, ad, prior in new_leads:
        features = [build_features(intent, budget, ad, prior)]
        probability = model.predict_proba(features)[0][1]
        decision = "CALL" if probability >= 0.5 else "skip"
        print(f"  {name:<28} -> {decision}  (conversion probability {probability:.0%})")

    print()
    print("No training data, no retraining - just the file and the feature contract.")
    print("Session 5 wraps exactly this in a FastAPI /predict endpoint.")


if __name__ == "__main__":
    main()
