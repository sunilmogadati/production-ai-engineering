# Prompt Engineering: Progressive Teaching Series

Build from hello world to production patterns. Each script is standalone and teaches one concept.

## Completed Scripts

### **prompt01_hello_world.py**
**Concepts:** API client, basic request-response  
**What you learn:**
- Import `Anthropic` and create a client
- Call `client.messages.create()` with model, max_tokens, messages
- Extract response text from `response.content[0].text`

**Key insight:** Every API call is `request → response → parse`. Nothing hidden.

**Time:** 5 min | **Lines:** ~60 | **Dependencies:** `anthropic` SDK

---

### **prompt02_conversation.py**
**Concepts:** Multi-turn conversation, message history  
**What you learn:**
- Claude has NO memory. You manage a `messages` list.
- Each turn: append user message → send full history → append Claude's response
- Context is carried by YOU, not the model

**Key insight:** History management is your responsibility. Reset it, and Claude thinks it's a new conversation.

**Time:** 5 min | **Lines:** ~80 | **Dependencies:** `anthropic` SDK

---

### **prompt03_system_prompt.py**
**Concepts:** System prompts (role/persona/instructions)  
**What you learn:**
- `system=` parameter tells Claude its role BEFORE the conversation
- Same user question + different system prompts = completely different answers
- System prompt is the standing instruction for the whole conversation

**Key insight:** The system prompt is where you shape behavior. Use it for role, tone, constraints.

**Teaching moment:** Run this 3 times with different personas (sales coach, comedian, teacher) on the SAME question. Watch the answers change.

**Time:** 5 min | **Lines:** ~100 | **Dependencies:** `anthropic` SDK

---

### **prompt04_structured_output.py**
**Concepts:** JSON extraction, parsing, integration  
**What you learn:**
- Tell Claude: "Return ONLY JSON with these fields..."
- Claude outputs JSON (deterministic, structured)
- Parse it in Python and use it (database, API calls, business logic)

**Key insight:** This is how you make Claude part of your data pipeline. Messy input → clean JSON output → your code.

**Real-world example:** Extract lead info from sales call transcripts → insert into CRM.

**Time:** 10 min | **Lines:** ~130 | **Dependencies:** `anthropic` SDK

---

### **prompt05_temperature.py**
**Concepts:** Temperature, sampling, randomness  
**What you learn:**
- `temperature=0`: deterministic (same answer every run)
- `temperature=1`: balanced and creative
- `temperature=2`: wild and unpredictable
- Temperature=0 for facts/code, temperature=1+ for creativity

**Key insight:** Temperature controls randomness. High temperature = brainstorming, low = fact extraction.

**Teaching moment:** Run the same tagline prompt 3 times at each temperature level. Watch how temp=0 repeats, but temp=2 varies wildly.

**Time:** 5 min | **Lines:** ~100 | **Dependencies:** `anthropic` SDK

---

## Planned (Next in the Series)

### **prompt06_streaming.py**
**Concepts:** Real-time responses, streaming  
**What you learn:**
- Instead of waiting for a full response, stream tokens one at a time
- User sees text appearing (like ChatGPT)
- Useful for long responses or responsive UIs

**Example:** A FastAPI endpoint that streams Claude's response to a frontend

---

### **prompt07_token_counting.py**
**Concepts:** Measure cost before you pay  
**What you learn:**
- `model.count_tokens()` tells you how many tokens a message will cost
- Tokens ≈ words (roughly 4 chars per token)
- Use this to estimate costs or enforce limits

**Example:** Before sending a 50-page PDF to Claude, count tokens and warn if it'll cost $X

---

### **prompt08_few_shot.py**
**Concepts:** Few-shot prompting, examples  
**What you learn:**
- Show Claude examples of what you want (input → output pairs)
- Claude learns from examples and mimics the pattern
- Better than writing complex instructions

**Example:** 
```
Extract product features:
Product: "iPhone 15"
Features: ["A17 Pro chip", "Dynamic Island", "USB-C"]

Product: "Galaxy S24"
Features: [?]  ← Claude fills this in based on the pattern
```

---

### **prompt09_chain_of_thought.py**
**Concepts:** Let Claude think step-by-step  
**What you learn:**
- Asking Claude to "think step-by-step" often improves accuracy
- Claude can reason through complex problems if asked
- Useful for math, logic, analysis

**Example:** "Solve this step-by-step" vs. "Solve this"

---

### **prompt10_vision.py**
**Concepts:** Analyze images (if using vision models)  
**What you learn:**
- Pass images to Claude and ask questions about them
- Useful for receipts, screenshots, diagrams, charts
- Different model: `claude-3-5-sonnet` supports vision

---

## Teaching Philosophy

**Each script:**
- ✅ Runs standalone (can understand it without reading others)
- ✅ Has one main concept (not a grab-bag of ideas)
- ✅ Takes ~5 min to run and understand
- ✅ Has extensive comments (teaching code, not production code)
- ✅ Shows the concept, then the teaching moment

**Order matters:**
1. Start with hello world (just "make it work")
2. Add conversation (the API is stateless; YOU manage state)
3. Add system prompts (shape behavior)
4. Add structure (JSON extraction; integration with your app)
5. Add sophistication (temperature, streaming, token counting, reasoning)

**Progression pattern:**
- `prompt01-05`: Core concepts (everyone needs these)
- `prompt06-10`: Production patterns (add as needed for your use case)

## How to Use in Your Cohort

### **Session Plan**
Each teaching session covers 1-2 scripts:

**Week 1: Foundations**
- Day 1: `prompt01` + `prompt02` (5+5 min each)
- Day 2: `prompt03` + `prompt04` (5+10 min each)
- Day 3: `prompt05` (5 min) + live demo/Q&A

**Week 2: Integration**
- Day 1: `prompt06` (streaming) + live coding: build a FastAPI endpoint
- Day 2: `prompt07` (token counting) + cost estimation exercise
- Day 3: Q&A + practice prompts

**Week 3+: Application**
- Students apply concepts to their own projects
- Few-shot, chain-of-thought, vision as needed

### **Teaching Moments**
- Pause after each script and ask: "What would happen if we...?"
  - "What if we don't include the history in prompt02?"
  - "What if we change the system prompt in prompt03?"
  - "What if temperature was 0 in prompt05?"
- Have students modify and re-run. Learning by breaking things.

### **Live Coding**
After `prompt05`, live-code `prompt06` (streaming) together:
1. Start with `prompt01` (hello world)
2. Add streaming: `with client.messages.stream(...) as stream:`
3. Print tokens as they arrive: `for text in stream.text_stream: print(text, end='', flush=True)`
4. Compare: blocking vs. streaming

## Integration with Your ML + FastAPI Course

**Connection points:**

- **prompt04** (JSON extraction) → feeds into `serve.py` as enriched lead data
  - Sales call transcript → Claude extracts JSON → inserted into prospect record
  - `POST /api/enrich` endpoint takes transcript, returns structured data

- **prompt06** (streaming) → create `GET /api/chat/stream` endpoint
  - Real-time coaching advice via streaming
  - User asks a question → Claude streams back response

- **prompt07** (token counting) → cost tracking dashboard
  - Each request logs tokens used
  - Dashboard shows cost per prospect, cost per conversation

- **Full app** (End of series): "Prospect Coach"
  - User picks a hot lead (from ML scoring)
  - Clicks "Prepare for Call" → streams a suggested script (prompt03 + prompt06)
  - After the call, pastes transcript → Claude extracts notes (prompt04)
  - Suggested next action, follow-up tasks, etc.

## Files Reference

```
fastapi-hello/
├── prompt01_hello_world.py        ← Start here
├── prompt02_conversation.py
├── prompt03_system_prompt.py
├── prompt04_structured_output.py
├── prompt05_temperature.py
├── PROMPT_PROGRESSION.md          ← This file
├── serve.py                        ← FastAPI app (unchanged from ML unit)
└── static/
    ├── index.html                 ← Prospect dashboard
    └── step6.html                 ← Transcript analysis demo
```

## Running Them

```bash
cd /Users/sunilmogadati/Downloads/fastapi-hello

# Make sure you have the SDK
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run each script
python prompt01_hello_world.py
python prompt02_conversation.py
python prompt03_system_prompt.py  # Run 3 times—notice personas change the answer
python prompt04_structured_output.py
python prompt05_temperature.py    # Run 3 times at each temperature—notice randomness
```

## Key Takeaways (Teach These)

1. **The API is simple:** request → response. Everything else is you managing state.
2. **System prompt is powerful:** same user input + different system prompts = night-and-day differences.
3. **Structure matters:** tell Claude what JSON shape you want, and parse it in your code.
4. **Temperature is control:** low for facts, high for creativity.
5. **Integration is the win:** Claude's output becomes your code's input (database, API call, next decision).

---

## Next Steps After prompt05

- Have students pick a use case (sales, support, content, code review)
- Build a one-prompt solution (hello world + system prompt for their case)
- Then add streaming (prompt06)
- Then add token counting (prompt07)
- Then put it in a FastAPI endpoint
- Then wire it to the prospect dashboard

This progression mirrors the ML cohort: simple to integrated.
