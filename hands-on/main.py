from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import json
import os


# Create the FastAPI app.
app = FastAPI()

# Enable CORS so React can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# This class describes the employee data returned by the API.
class Employee(BaseModel):
    id: int
    name: str
    department: str


# Request/Response models for transcript analysis
class TranscriptRequest(BaseModel):
    transcript: str
    analysis_type: str  # "summarize", "classify", or "structured"


class TranscriptAnalysis(BaseModel):
    analysis_type: str
    result: dict


@app.get("/{id}")
async def welcome(id: int):
    """Return a message, or raise a 400 error for invalid IDs."""
    # Raise a 400 Bad Request when the client sends an invalid value.
    if id < 1:
        raise HTTPException(status_code=400, detail="id must be greater than 0")

    return {"message": f"Hi, my id is, {id}"}


@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int):
    """Return one employee, or raise a 404 error if it does not exist."""
    fake_employees = {
        1: Employee(id=1, name="Anita", department="Engineering"),
        2: Employee(id=2, name="Rahul", department="HR"),
    }

    # Raise a 404 Not Found when the requested item does not exist.
    if employee_id not in fake_employees:
        raise HTTPException(status_code=404, detail="Employee not found")

    return fake_employees[employee_id]


# ============================================================
# TRANSCRIPT ANALYSIS ENDPOINTS (Step 7: Real LLM)
# ============================================================

def get_analysis_prompt(transcript: str, analysis_type: str) -> str:
    """Generate the appropriate prompt based on analysis type."""
    base = f"Transcript:\n{transcript}\n\n"

    if analysis_type == "summarize":
        return base + """Analyze this sales call transcript.
Extract and provide:
1. Summary (2-3 sentences)
2. Prospect name
3. Company name
4. Pain points mentioned (list)
5. Interest level (Low/Medium/High)
6. Next steps


Format your response as JSON with keys: summary, prospect, company, painPoints, interest, nextStep"""

    elif analysis_type == "classify":
        return base + """Based on this call transcript, classify the lead quality.

Rate on these factors:
- Budget availability
- Timeline urgency
- Problem clarity
- Decision authority
- Buying signals

Provide JSON response with keys:
- leadQuality (format: "🔥 HOT" or "🟠 WARM" or "❄️ COLD")
- buyingIntent (1-10 score)
- signals (array of 3-5 key signals)
- reasoning (1 sentence explaining classification)"""

    elif analysis_type == "structured":
        return base + """Extract call details as structured JSON with these exact fields:
- prospect_name
- company
- industry
- company_size
- pain_points (array)
- solution_interest
- budget
- timeline
- decision_maker (true/false)
- buying_intent_score (1-10)
- lead_classification (hot/warm/cold)
- recommended_action

Return ONLY valid JSON, no explanation."""

    raise HTTPException(status_code=400, detail=f"Unknown analysis_type: {analysis_type}")


@app.post("/analyze-transcript", response_model=TranscriptAnalysis)
async def analyze_transcript(request: TranscriptRequest):
    """Analyze a sales call transcript using Claude API."""

    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = get_analysis_prompt(request.transcript, request.analysis_type)

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If not JSON, return as plain text
            result = {"text": response_text}

        return TranscriptAnalysis(
            analysis_type=request.analysis_type,
            result=result
        )

    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")