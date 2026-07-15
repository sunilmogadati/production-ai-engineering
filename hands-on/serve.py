"""Session 5: SERVE TIME - use the saved model to score prospects.

This is ml10 (load-and-predict) turned into a real HTTP API:

  * Startup: load models/prospect_model.joblib (NO retraining, no trainers!)
  * GET /api/meta -> return model card (version, accuracy, thresholds)
  * GET /api/prospects?limit=N -> score the lead pool, bucket hot/warm/cold
  * POST /api/score -> score one lead (what-if form from the UI)
  * GET / -> serve the React UI (static/index.html)

TRAIN TIME vs SERVE TIME:
  ml11_train_and_save_prospect_model.py = TRAIN TIME
    - Reads historical data (leads.csv)
    - Trains the model
    - Saves two files (model.joblib + model.json)

  This file (serve.py) = SERVE TIME
    - Loads the saved files (never retrains!)
    - For each HTTP request, predicts using the loaded model
    - Returns results as JSON

The key: the model is trained ONCE (expensive, offline, careful).
Then served MANY TIMES (fast, cheap, repeatable).

Run from the repo root (after ml11):

    ./venv/bin/uvicorn serve:app --reload

Then open http://127.0.0.1:8000
"""

import json
import time
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MODEL_PATH = Path("models/prospect_model.joblib")
META_PATH = Path("models/prospect_model.json")
LEADS_PATH = Path("data/leads.csv")
STATIC_DIR = Path("static")

# Probability thresholds for the three temperature buckets.
HOT_THRESHOLD = 0.66
WARM_THRESHOLD = 0.33

# ========================================================================
# STARTUP: Load the model files once (not on every request!)
# ========================================================================
# If the model file doesn't exist, stop immediately with a helpful message.
if not MODEL_PATH.exists():
    raise SystemExit(
        "models/prospect_model.joblib not found. "
        "Run: ./venv/bin/python ml11_train_and_save_prospect_model.py"
    )

# Load the model from the .joblib file (trained weights, tree structure).
# This happens ONCE when the server starts, then reused for all requests.
model = joblib.load(MODEL_PATH)

# Load the metadata from the .json file (feature contract, accuracy).
# This tells us what features the model expects and in what order.
metadata = json.loads(META_PATH.read_text())

# ========================================================================
# LIGHTWEIGHT MONITORING (in-memory)
# ========================================================================
# WHY: in production you must be able to answer "is the model still healthy?"
# at any moment. These counters are a teaching-grade baseline. Real systems
# export the same ideas to Prometheus / Grafana / CloudWatch -- but the
# questions are identical:
#   - how long has the server been up?          (liveness)
#   - is the model actually loaded?             (readiness)
#   - how many predictions have we served?      (volume)
#   - what is the AVERAGE predicted probability? (a shift over time = possible DRIFT)
SERVER_START = time.time()
SCORES_SERVED = 0
PROBABILITY_SUM = 0.0

app = FastAPI(title="Prospect Scoring API")


class Lead(BaseModel):
    customer_id: str = "CUST-9000"
    intent_signal: int = Field(ge=0, le=100, examples=[80])
    budget: float = Field(gt=0, examples=[120.0])
    ad_source: Literal["tv", "social", "email"] = "tv"
    prior_purchases: int = Field(ge=0, examples=[1])


class ScoredProspect(BaseModel):
    customer_id: str
    intent_signal: int
    budget: float
    ad_source: str
    prior_purchases: int
    probability: float
    temperature: Literal["hot", "warm", "cold"]


def build_features(lead: Lead) -> list[float]:
    """
    Convert a Lead into the feature vector the model expects.

    THE FEATURE CONTRACT (CRITICAL!):
    The model was trained on features in this EXACT order:
      ["intent_signal", "budget", "prior_purchases", "ad_tv", "ad_social", "ad_email"]

    If you build features in a different order, predictions are GARBAGE.
    If you add/remove features, the model crashes.

    This function ensures we always build features in the correct order.
    That's why we save metadata['features'] - so serve.py knows the contract
    even if it's deployed years later by someone who wasn't at training time.

    Args:
        lead: A Lead object with intent_signal, budget, ad_source, prior_purchases

    Returns:
        A list of floats in the exact order the model expects
    """
    return [
        lead.intent_signal,                     # Feature 1: intent (0-100)
        lead.budget,                            # Feature 2: budget ($)
        lead.prior_purchases,                   # Feature 3: prior purchases (count)
        1 if lead.ad_source == "tv" else 0,     # Feature 4: ad_tv (one-hot)
        1 if lead.ad_source == "social" else 0, # Feature 5: ad_social (one-hot)
        1 if lead.ad_source == "email" else 0,  # Feature 6: ad_email (one-hot)
    ]


def bucket(probability: float) -> Literal["hot", "warm", "cold"]:
    if probability >= HOT_THRESHOLD:
        return "hot"
    if probability >= WARM_THRESHOLD:
        return "warm"
    return "cold"


def score(lead: Lead) -> ScoredProspect:
    """
    Score a single lead using the trained model.

    Flow:
      1. Convert the Lead to a feature vector (build_features)
      2. Pass to model.predict_proba to get P(conversion)
      3. Bucket the probability into hot/warm/cold
      4. Return the full result

    Args:
        lead: A Lead object with all required fields

    Returns:
        A ScoredProspect with the probability and temperature
    """
    # Build the feature vector (MUST be in the correct order!)
    features = build_features(lead)

    # predict_proba returns [[P(no_conversion), P(conversion)]]
    # We want P(conversion), which is index [0][1]
    probability = float(model.predict_proba([features])[0][1])

    # --- monitoring hook: count predictions + accumulate a simple drift signal ---
    # WHY here: this is the one place every prediction flows through, so it is the
    # correct spot to record volume and the running mean probability.
    global SCORES_SERVED, PROBABILITY_SUM
    SCORES_SERVED += 1
    PROBABILITY_SUM += probability

    return ScoredProspect(
        customer_id=lead.customer_id,
        intent_signal=lead.intent_signal,
        budget=round(lead.budget, 2),
        ad_source=lead.ad_source,
        prior_purchases=lead.prior_purchases,
        probability=round(probability, 4),
        temperature=bucket(probability),
    )


@app.get("/health")
def health() -> dict:
    """
    Liveness + readiness probe.

    Container orchestrators (Docker, Kubernetes) hit this URL on a schedule to
    decide whether the service is up and ready to receive traffic. If it stops
    returning 200, the platform can restart or stop routing to this container.

    Keep it CHEAP and DEPENDENCY-FREE: no database calls, no model inference -
    just "am I alive and is the model loaded?".
    """
    return {
        "status": "ok",                              # liveness: the process is answering
        "model_loaded": model is not None,           # readiness: the model is in memory
        "model_version": metadata.get("model_version"),
        "model_type": metadata.get("model_type"),
        "trained_at": metadata.get("trained_at"),
        "uptime_seconds": round(time.time() - SERVER_START, 1),
    }


@app.get("/metrics")
def metrics() -> dict:
    """
    A teaching-grade monitoring snapshot (the seed of real observability).

    'mean_predicted_probability' is a simple DRIFT signal: if the average score
    the model hands out drifts far from its training-time behavior, that is a cue
    to investigate the incoming data (has the world changed? is a feature broken?).
    In production you would ship these numbers to Prometheus/Grafana - the idea is
    the same, only the plumbing is fancier.
    """
    mean_prob = round(PROBABILITY_SUM / SCORES_SERVED, 4) if SCORES_SERVED else None
    return {
        "scores_served": SCORES_SERVED,
        "mean_predicted_probability": mean_prob,   # watch this for drift over time
        "uptime_seconds": round(time.time() - SERVER_START, 1),
    }


@app.get("/api/meta")
def get_meta() -> dict:
    """Model card for the UI header: version, type, accuracy, thresholds."""
    return {**metadata, "hot_threshold": HOT_THRESHOLD, "warm_threshold": WARM_THRESHOLD}


@app.get("/api/prospects", response_model=list[ScoredProspect])
def get_prospects(limit: int = 120) -> list[ScoredProspect]:
    """Score a pool of leads and return them sorted hottest-first."""
    if not LEADS_PATH.exists():
        raise HTTPException(status_code=500, detail="data/leads.csv not found")

    df = pd.read_csv(LEADS_PATH).head(limit)
    scored = [
        score(
            Lead(
                customer_id=row.customer_id,
                intent_signal=int(row.intent_signal),
                budget=float(row.budget),
                ad_source=row.ad_source,
                prior_purchases=int(row.prior_purchases),
            )
        )
        for row in df.itertuples()
    ]
    scored.sort(key=lambda p: p.probability, reverse=True)
    return scored


@app.post("/api/score", response_model=ScoredProspect)
def post_score(lead: Lead) -> ScoredProspect:
    """Score a single lead typed into the UI's what-if form."""
    return score(lead)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Serve any other static assets (kept last so /api/* wins).
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
