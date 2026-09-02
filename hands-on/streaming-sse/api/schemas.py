"""The typed contract at the API seam.

Every request declares *what kind of work* it is (`task`) and *how sensitive the
data is* (`sensitivity`) — NEVER a model id. The router turns those two into a
concrete model + provider. This is the "parse, don't validate at the boundary"
discipline: if a request reaches a handler, these fields are already valid, so
the handler never re-checks them.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    # The conversation so far. Each item is {"role": "...", "content": "..."}.
    messages: list[dict]

    # Router inputs. The caller tags the TASK; the router picks the MODEL.
    # Defaults match the "chat" route.
    task: str = "chat"              # -> router tier   (chat -> mid -> a mid model)
    sensitivity: str = "internal"  # -> provider guardrail (confidential/restricted never hit a vendor API)

    # Optional cost-attribution / provenance tag (e.g. which app or team called).
    tenant: str | None = Field(default=None)
