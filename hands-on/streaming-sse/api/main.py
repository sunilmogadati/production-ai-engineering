"""Streaming agent — a FastAPI typed-SSE serving tier (teaching demo).

The whole point of this lab: a routed, Python FastAPI tier that streams AGENTIC
LLM output as TYPED Server-Sent Events. A browser (or `curl -N`) consumes the
stream and renders tokens as they arrive instead of waiting for the full answer.

Run:   uvicorn api.main:app --reload   (from hands-on/streaming-sse)
Docs:  http://localhost:8000/docs
"""

import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from .router import stream_agent
from .schemas import ChatRequest

app = FastAPI(title="Streaming Agent — FastAPI typed-SSE serving tier (demo)")


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/v1/chat/stream")
async def chat_stream(req: ChatRequest):
    """Routed, agentic, typed SSE.

    `async def` so the event loop can serve other requests while this one waits
    on the model — the whole reason a streaming tier is async. Note the handler
    itself never picks a model: the router turns (task, sensitivity) into one.
    """
    async def sse():
        async for event in stream_agent(
            task=req.task,
            sensitivity=req.sensitivity,
            input=req.messages,
            ctx={"tenant": req.tenant},
        ):
            # One typed event per SSE frame. `type` in delta|tool_call|tool_result|done.
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
