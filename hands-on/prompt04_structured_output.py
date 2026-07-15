#!/usr/bin/env python3
"""
Prompt Engineering 04: Structured Output (JSON Extraction)

Claude can output JSON. Tell it what JSON shape you want, and it returns that shape.
Then you parse it and use it in code (databases, APIs, downstream functions).

This is how you integrate Claude with your app:
  1. Send unstructured text (email, transcript, feedback)
  2. Ask Claude to extract structured data (JSON)
  3. Parse and validate the JSON
  4. Insert into database / trigger actions

Run:
    python prompt04_structured_output.py
"""

import json
from anthropic import Anthropic

client = Anthropic()

# ============================================================================
# Example: Extract lead info from a sales call transcript
# ============================================================================

# This is raw text from a Zoom transcript
transcript = """
Sales Rep: Hi Sarah, thanks for jumping on the call.

Sarah: Hey! Thanks for making the time. So we've been looking for a way to automate
our sales pipeline. We're spending way too much time on manual data entry.

Sales Rep: How much time are we talking?

Sarah: Probably 15 hours a week across the team. It's killing us.

Sales Rep: That's painful. What's your timeline?

Sarah: We need something in place by Q3, ideally. Budget isn't a problem—we've
already allocated $30k for this initiative.

Sales Rep: Great. Any other tools you're considering?

Sarah: Yeah, a few. But honestly, the ability to integrate with our existing
Salesforce instance is the biggest factor for us.

Sales Rep: Makes sense. I can definitely help with that. Let's schedule a
technical deep-dive with your IT team. Next week?

Sarah: Perfect. I'll get them on the calendar.
"""

# ============================================================================
# The prompt asks for a specific JSON shape
# ============================================================================
# You tell Claude: "Return ONLY valid JSON with these fields..."
# Claude responds with JSON (only JSON, no explanation).

extraction_prompt = f"""Extract lead information from this sales call transcript.
Return ONLY valid JSON (no explanation) with these fields:

{{
  "prospect_name": "string",
  "company": "string (infer if not stated)",
  "pain_point": "string (what problem do they have?)",
  "time_to_solve_hours_per_week": "number",
  "budget": "string or number (what they have to spend)",
  "timeline": "string (when do they need it?)",
  "must_have_features": ["array of strings"],
  "buying_intent": "hot / warm / cold (based on signals)",
  "next_step": "string (what's the next action?)"
}}

Transcript:
{transcript}
"""

# Send the request
response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=500,
    messages=[
        {
            "role": "user",
            "content": extraction_prompt,
        }
    ],
)

# Extract the response
json_string = response.content[0].text

# ============================================================================
# Parse and use the JSON
# ============================================================================
print("=== Raw response from Claude ===")
print(json_string)
print()

# Parse the JSON
# Sometimes Claude wraps JSON in markdown code blocks, so remove them
if json_string.startswith("```"):
    json_string = json_string.replace("```json\n", "").replace("```", "").strip()

try:
    lead_data = json.loads(json_string)
except json.JSONDecodeError as e:
    print(f"ERROR: Claude's response wasn't valid JSON: {e}")
    exit(1)

# ============================================================================
# Use the structured data
# ============================================================================
print("=== Parsed lead data ===")
print(f"Prospect: {lead_data['prospect_name']} ({lead_data['company']})")
print(f"Pain point: {lead_data['pain_point']}")
print(f"Time wasted: {lead_data['time_to_solve_hours_per_week']} hrs/week")
print(f"Budget: ${lead_data['budget']}k")
print(f"Timeline: {lead_data['timeline']}")
print(f"Must-have features: {', '.join(lead_data['must_have_features'])}")
print(f"Buying intent: {lead_data['buying_intent']}")
print(f"Next step: {lead_data['next_step']}")
print()

# ============================================================================
# In a real app, you'd now insert this into a database
# ============================================================================
# Example:
#   db.leads.insert({
#       'name': lead_data['prospect_name'],
#       'company': lead_data['company'],
#       'pain_point': lead_data['pain_point'],
#       'budget': lead_data['budget'],
#       'timeline': lead_data['timeline'],
#       'buying_intent': lead_data['buying_intent'],
#   })

# Or you'd trigger an automation:
#   if lead_data['buying_intent'] == 'hot':
#       send_alert_to_sales_team()
#       schedule_demo_call()

# ============================================================================
# Key learning: Claude → JSON → Your code
# ============================================================================
# 1. Write a prompt that requests JSON in a specific format
# 2. Tell Claude "return ONLY JSON, no explanation"
# 3. Parse the JSON in Python
# 4. Use it: database inserts, API calls, business logic
#
# This is how you make Claude part of your data pipeline.
# The model reads messy human text, extracts clean structured data,
# and your code uses it to make decisions or populate databases.
