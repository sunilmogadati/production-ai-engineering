"""Step 1: minimal FastAPI - just /api/score endpoint + swagger.

No UI yet. This step shows:
  * load the saved model
  * expose it over HTTP (no training!)
  * Swagger auto-docs

Run:
    ./venv/bin/uvicorn serve_step1:app --reload

Then visit:
    http://127.0.0.1:8000/docs  (Swagger UI - try it live)
"""

import json
from pathlib import Path
from typing import Literal

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = Path("models/prospect_model.joblib")
META_PATH = Path("models/prospect_model.json")

if not MODEL_PATH.exists():
    raise SystemExit("models/prospect_model.joblib not found. Run ml11_train_and_save_prospect_model.py first.")

model = joblib.load(MODEL_PATH)
metadata = json.loads(META_PATH.read_text())

app = FastAPI(title="Prospect Scoring - Step 1: Minimal API")


class Lead(BaseModel):
    intent_signal: int = Field(ge=0, le=100, examples=[80])
    budget: float = Field(gt=0, examples=[120.0])
    ad_source: Literal["tv", "social", "email"] = "tv"
    prior_purchases: int = Field(ge=0, examples=[1])


class ScoredLead(BaseModel):
    probability: float
    decision: Literal["hot", "warm", "cold"]


def build_features(lead: Lead) -> list[float]:
    return [
        lead.intent_signal,
        lead.budget,
        lead.prior_purchases,
        1 if lead.ad_source == "tv" else 0,
        1 if lead.ad_source == "social" else 0,
        1 if lead.ad_source == "email" else 0,
    ]


@app.post("/api/score", response_model=ScoredLead)
def score(lead: Lead) -> ScoredLead:
    probability = float(model.predict_proba([build_features(lead)])[0][1])
    if probability >= 0.66:
        decision = "hot"
    elif probability >= 0.33:
        decision = "warm"
    else:
        decision = "cold"
    return ScoredLead(probability=round(probability, 4), decision=decision)
