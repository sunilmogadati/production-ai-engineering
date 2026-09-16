"""Generate the synthetic task set.

Synthetic and deterministic, for two reasons. The obvious one is that no real
workload belongs in a public repository. The less obvious one is that a bench whose
inputs change between runs cannot tell a routing improvement from a different
question, and the first thing anyone does with a bench is run it twice.

Re-running this script reproduces tasks.json byte for byte.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 20260916
HERE = Path(__file__).parent

# A workload shape: what kind of work it is, how hard, how big, and how fast it must
# answer. The mix is deliberately weighted toward easy work, because real workloads
# are -- which is exactly why routing looks so attractive before it is measured.
SHAPES = [
    # (kind,               complexity, in_lo,  in_hi,  out_lo, out_hi, latency, weight)
    ("sentiment-tag",               1,    300,    900,     20,     60,   True,     22),
    ("field-extraction",            2,    800,   2_500,     80,    240,  False,    20),
    ("ticket-triage",               2,    600,   1_800,     60,    180,  True,     14),
    ("summarize-thread",            3,  3_000,  12_000,    250,    700,  False,    16),
    ("policy-question",             3,  2_000,   8_000,    300,    900,  False,    12),
    ("contract-analysis",           4, 20_000,  90_000,    800,  2_500,  False,     9),
    ("incident-root-cause",         5, 40_000, 180_000,  1_500,  5_000,  False,     5),
    ("whole-repo-review",           5, 210_000, 600_000, 2_000,  6_000,  False,     2),
]

N_TASKS = 200


def generate() -> list[dict]:
    rng = random.Random(SEED)
    population = [s for s in SHAPES for _ in range(s[-1])]

    tasks = []
    for i in range(N_TASKS):
        kind, complexity, in_lo, in_hi, out_lo, out_hi, latency, _ = rng.choice(population)
        tasks.append(
            {
                "id": f"T{i:03d}",
                "kind": kind,
                # Ground-truth complexity. Offline runs read it directly; the live
                # path has a classifier infer it, which is where classifier error
                # (and its cost) enters the picture.
                "complexity": complexity,
                "input_tokens": rng.randint(in_lo, in_hi),
                "output_tokens": rng.randint(out_lo, out_hi),
                "latency_sensitive": latency,
            }
        )
    return tasks


if __name__ == "__main__":
    tasks = generate()
    out = HERE / "tasks.json"
    out.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(tasks)} tasks to {out}")
