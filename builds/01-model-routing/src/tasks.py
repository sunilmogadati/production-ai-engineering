"""Load and validate the synthetic task set."""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "tasks.json"

REQUIRED_FIELDS = {"id", "kind", "complexity", "input_tokens", "output_tokens", "latency_sensitive"}


def load(path: Path | None = None) -> list[dict]:
    """Read the task set, failing loudly on a malformed record.

    Validation is here rather than trusted because a bench that silently skips a
    malformed task reports a total that is quietly wrong -- and looks right.
    """
    path = DATA if path is None else path
    tasks = json.loads(path.read_text(encoding="utf-8"))

    for task in tasks:
        missing = REQUIRED_FIELDS - task.keys()
        if missing:
            raise ValueError(f"task {task.get('id', '<unnamed>')!r} missing {sorted(missing)}")
        if not 1 <= task["complexity"] <= 5:
            raise ValueError(f"task {task['id']!r} has complexity {task['complexity']}, expected 1-5")
    return tasks
