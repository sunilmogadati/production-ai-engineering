# Streaming Agent — a FastAPI typed-SSE serving tier

A minimal, runnable FastAPI tier that streams **agentic** LLM output as **typed
Server-Sent Events (SSE)**, routed by `task` + `sensitivity`. It's the smallest
thing that shows the whole "AI serving tier" architecture decision at once.

> The thesis, in one line: *the caller says what it wants and how private it is;
> the router picks the model; the stream is typed so an agent's tool calls survive
> on the wire.*

Pairs with the study docs: **`study-docs/ML_Study_12_Serving_Models_FastAPI.md`**
(train-time vs serve-time, the feature contract, the `main0 -> main4` ladder) and
the LangChain/agent notes in the 13-series.

## Run (zero API keys)

```bash
cd hands-on/streaming-sse
python3 -m venv .venv && ./.venv/bin/pip install "fastapi[standard]"
./.venv/bin/uvicorn api.main:app --reload
# open http://localhost:8000/docs
```

The default run needs **no key** — a fake agent loop streams the typed events so
the demo is guaranteed to work live. To stream **real Claude tokens** instead:
`pip install anthropic`, `export ANTHROPIC_API_KEY=...`, restart. (The real path
is single-call streaming; a production build would wire a full agent loop so real
`tool_call`/`tool_result` frames flow too.)

## The demo that shows the whole architecture

```bash
curl -sN -X POST http://localhost:8000/v1/chat/stream \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"why has order A-1042 not shipped?"}],
       "task":"chat","sensitivity":"internal","tenant":"demo"}'
```

You'll see typed frames arrive one at a time:

```
data: {"type":"delta","text":"Looking "} ...
data: {"type":"tool_call","name":"lookup_order","input":{"order":"A-1042"}}
data: {"type":"tool_result","name":"lookup_order","output":{"shipped":false,...}}
data: {"type":"delta","text":"Found "} ...
data: {"type":"done","model":"claude-sonnet-4-6","tier":"mid"}
```

## Teaching beats

1. **`async def` + `StreamingResponse` = the payoff.** `curl -sN` shows words
   appear one at a time instead of a 20-second spinner. That difference *is*
   FastAPI's async streaming.
2. **The typed contract at the door.** `ChatRequest` (Pydantic) validates
   `task`/`sensitivity` before the handler runs — a bad body is a `422`, never a
   crash deep inside. ("Parse, don't validate at the boundary.")
3. **The caller never picks a model.** It passes `task="chat"` +
   `sensitivity="internal"`; the router returns `sonnet-4-6`/`mid` on the `done`
   frame. Change `task` to `synthesize` -> watch it resolve to `opus-4-8`.
4. **Why the stream lives in your Python tier.** Set `sensitivity="confidential"`
   — the provider guardrail forbids a vendor API and forces Bedrock/local. The
   stream *has* to live where the router and the data-residency rule live, not in
   a thin edge proxy.
5. **Typed events, not bare text.** The `tool_call`/`tool_result` frames are why
   the wire format carries a `type` from day one — an agentic chat needs it, and
   plain text-only SSE would have to be re-cut once tools arrive.
6. **Budget is post-hoc for streams.** Cost/model land on the `done` frame, not
   before — a stream's cost is known only when it ends.

## Layout

```
streaming-sse/
  api/
    main.py      # FastAPI app: /v1/chat/stream (typed SSE), /healthz
    router.py    # the model router: task+sensitivity -> (tier, model); fake + real paths
    schemas.py   # ChatRequest — the typed contract at the seam
  requirements.txt
```

Deploy note: a streaming endpoint needs a **container (Fargate/ECS) or a Lambda
Function URL with response streaming** — **not** API Gateway + a buffering
adapter, which holds the whole body and breaks SSE.
