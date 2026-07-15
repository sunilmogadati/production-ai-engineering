"""ML demo 11: train and SAVE the prospect-scoring model for the API.

Session 5. Same lifecycle as ml09, but we save the model the class picked as
the robust winner: the random forest (~81% on the held-out test set).

THE KEY CONCEPT: "Train Time" vs "Serve Time"
==============================================
This script is TRAIN TIME:
  1. Load historical data (leads.csv)
  2. Train the model on a subset (1,600 leads)
  3. Evaluate on held-out leads (400 leads - the test set)
  4. SAVE two files: the model (.joblib) and metadata (.json)

The serving API (serve.py) is SERVE TIME:
  1. Load the saved files (never retrain!)
  2. For each new prospect request, predict
  3. Return the result over HTTP

This is the PRODUCTION PATTERN:
  - Train once (expensive, needs data scientist, slow)
  - Serve many times (fast, cheap, repeatable)

The .joblib file is binary; the .json file is human-readable.
Together they define the MODEL CARD - a contract between training and serving.

Run from the repo root (after ml01):

    ./venv/bin/python ml11_train_and_save_prospect_model.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ========================================================================
# THE FEATURE CONTRACT
# ========================================================================
# This list defines the exact order of features the model expects.
# CRITICAL: serve.py MUST build features in this EXACT order.
# If you swap columns, predictions are garbage.
# If you add/remove features, the model crashes.
# This is why we save the feature list in metadata.
FEATURES = ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]

# File paths for the two-file pattern
MODEL_PATH = Path("models/prospect_model.joblib")  # The trained weights (binary)
META_PATH = Path("models/prospect_model.json")     # The metadata (human-readable)


def main() -> None:
    # ========================================================================
    # TRAIN TIME STEP 1: Load and prepare data
    # ========================================================================
    df = pd.read_csv("data/leads.csv")
    # One-hot encode ad_source (categorical -> numeric)
    for source in ["tv", "social", "email"]:
        df[f"ad_{source}"] = (df["ad_source"] == source).astype(int)

    # ========================================================================
    # TRAIN TIME STEP 2: Split into train (80%) and test (20%)
    # ========================================================================
    # The model learns from train, is graded on test.
    # The test set is NEVER used during training - it proves the model
    # can predict on data it's never seen before (not just memorize).
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["converted"])

    # ========================================================================
    # TRAIN TIME STEP 3: Train the model
    # ========================================================================
    # Random Forest: 300 trees vote. Each tree is trained on a random
    # subset of the data with a random subset of features (bagging).
    # Why? Because averaging many imperfect predictions is often better
    # than one perfect prediction (that overfits).
    #
    # .values strips column names so we pass plain lists, not DataFrames.
    # This is important for serve time - we won't have column names there!
    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(train[FEATURES].values, train["converted"])

    # ========================================================================
    # TRAIN TIME STEP 4: Evaluate on held-out test set
    # ========================================================================
    # Accuracy = (correct predictions) / (total test samples)
    # This is the number we report: "81% on the test set"
    accuracy = model.score(test[FEATURES].values, test["converted"])

    # ========================================================================
    # TRAIN TIME STEP 5: Save the model (binary)
    # ========================================================================
    # joblib serializes the trained tree structure, feature importances,
    # random seed, etc. - everything needed to make predictions.
    # This file is only readable by scikit-learn (or pickle) - it's binary.
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # ========================================================================
    # TRAIN TIME STEP 6: Save the metadata (human-readable JSON)
    # ========================================================================
    # This is the MODEL CARD - a contract that says:
    #   "This model expects these features, in this order."
    #   "It was trained on this many leads."
    #   "It achieved this accuracy on held-out data."
    #
    # serve.py reads this JSON to know:
    #   1. What features to build (the order!)
    #   2. Whether the model is fresh or stale
    #   3. What accuracy to expect
    #
    # This separation (binary model + JSON metadata) is how different
    # teams stay in sync: data scientist trains, engineer deploys, everyone
    # reads the JSON to understand the contract.
    metadata = {
        "model_version": "1.0",  # Bump this when you retrain
        "model_type": "RandomForestClassifier",  # Model class name
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),  # When trained
        "test_accuracy": round(accuracy, 4),  # Accuracy on held-out set
        "features": FEATURES,  # Feature order (CRITICAL!)
        "training_rows": len(train),  # How much data we had
    }
    META_PATH.write_text(json.dumps(metadata, indent=2))

    # ========================================================================
    # TRAIN TIME STEP 7: Report the outcome
    # ========================================================================
    print("=" * 68)
    print("TRAIN TIME IS DONE.")
    print("=" * 68)
    print()
    print("Artifacts saved on disk:")
    print(f"  {MODEL_PATH}")
    print("    → Binary file with trained weights (300 trees)")
    print()
    print(f"  {META_PATH}")
    print("    → Human-readable contract (features, accuracy, version)")
    print()
    print("Results:")
    print(f"  Test accuracy: {100 * accuracy:.1f}%")
    print(f"  Model version: {metadata['model_version']}")
    print(f"  Training rows: {len(train)}")
    print(f"  Trained at: {metadata['trained_at']}")
    print()
    print("=" * 68)
    print("Next: serve.py LOADS these files (no retraining!) and scores")
    print("      new prospects over HTTP. This is SERVE TIME.")
    print("=" * 68)


if __name__ == "__main__":
    main()
