import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse


app = FastAPI(title="FastAPI AI/ML Demo: Call Center and Streaming")


class CallTranscript(BaseModel):
    customer_id: str = Field(min_length=1, examples=["CUST-1024"])
    call_text: str = Field(min_length=10, examples=["Hi, I saw the TV ad and want to order the blue vacuum."])
    channel: Literal["phone", "web", "sms"] = "phone"


class LeadScoringRequest(BaseModel):
    customer_id: str
    product: str
    ad_source: str = Field(default="tv", examples=["tv", "social", "email"])
    budget: float = Field(gt=0)
    intent_signal: int = Field(ge=0, le=100, description="Higher means stronger buying intent")


class LeadScoringResponse(BaseModel):
    customer_id: str
    score: float
    decision: Literal["hot", "warm", "cold"]
    reason: str


class UpsellRequest(BaseModel):
    customer_id: str
    base_product: str
    customer_segment: Literal["new", "repeat", "vip"]


class UpsellResponse(BaseModel):
    customer_id: str
    recommendation: str
    confidence: float


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "AI/ML demo is ready. Use the call center example to test scoring, classification, and streaming."
    }


@app.post("/nlp/classify-call")
async def classify_call(transcript: CallTranscript) -> dict[str, str]:
    text = transcript.call_text.lower()

    if any(word in text for word in ["refund", "cancel", "complaint"]):
        intent = "service_recovery"
    elif any(word in text for word in ["buy", "order", "purchase", "want to order"]):
        intent = "purchase_intent"
    elif any(word in text for word in ["price", "cost", "discount"]):
        intent = "price_check"
    else:
        intent = "general_inquiry"

    return {
        "customer_id": transcript.customer_id,
        "channel": transcript.channel,
        "intent": intent,
    }


@app.post("/ml/score-lead", response_model=LeadScoringResponse)
async def score_lead(request: LeadScoringRequest) -> LeadScoringResponse:
    base_score = request.intent_signal * 0.6
    budget_score = 20 if request.budget >= 100 else 10 if request.budget >= 50 else 0
    ad_score = 10 if request.ad_source == "tv" else 5 if request.ad_source == "social" else 3
    score = min(100.0, base_score + budget_score + ad_score)

    if score >= 75:
        decision = "hot"
        reason = "Strong intent and good budget fit."
    elif score >= 45:
        decision = "warm"
        reason = "Some buying signal, but still needs follow-up."
    else:
        decision = "cold"
        reason = "Low intent or weak budget fit."

    await asyncio.sleep(0.2)
    return LeadScoringResponse(
        customer_id=request.customer_id,
        score=round(score, 1),
        decision=decision,
        reason=reason,
    )


@app.post("/ml/upsell", response_model=UpsellResponse)
async def upsell(request: UpsellRequest) -> UpsellResponse:
    if request.customer_segment == "vip":
        recommendation = f"Offer premium protection for {request.base_product} and a bundle discount."
        confidence = 0.92
    elif request.customer_segment == "repeat":
        recommendation = f"Offer a related accessory with a small loyalty discount for {request.base_product}."
        confidence = 0.78
    else:
        recommendation = f"Offer the starter version of {request.base_product} with free shipping."
        confidence = 0.64

    return UpsellResponse(
        customer_id=request.customer_id,
        recommendation=recommendation,
        confidence=confidence,
    )


@app.get("/ml/stream-score")
async def stream_score(customer_id: str = "CUST-1024") -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        updates = [
            {"stage": "load", "message": f"Loading model for {customer_id}"},
            {"stage": "feature_engineering", "message": "Extracting intent, budget, and channel features"},
            {"stage": "prediction", "message": "Running lead score model"},
            {"stage": "done", "message": "Score ready: hot lead"},
        ]

        for item in updates:
            yield f"data: {json.dumps(item)}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
