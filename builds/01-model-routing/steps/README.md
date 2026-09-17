# Steps — model selection, one idea at a time

Five standalone programs. Each runs on its own and teaches one thing. Start at 01, or
start wherever the idea you want is.

| Step | Teaches | Needs a key |
|---|---|---|
| `01_one_call.py` | one request, and reading what it cost from `response.usage` | yes |
| `02_three_tiers.py` | the same work on three tiers — price gap vs. answer gap | yes |
| `03_effort.py` | `effort` — the lever *inside* one model, before you add a second | yes |
| `04_route.py` | a router that reports its rule, and the classifier's own bill | yes |
| `05_price_first.py` | counting tokens to price a workload *before* spending | yes |

```bash
python3 -m venv ../.venv && source ../.venv/bin/activate
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python3 01_one_call.py        # then 02, 03, 04, 05
```

Or with `uv`, which needs no venv of your own:
`uv run --with anthropic python 01_one_call.py`

No API key? `../src/bench.py` runs the full comparison offline — cost is arithmetic.

`incidents.py` holds three synthetic production incidents at genuinely different
difficulties. `_shared.py` is the small amount of plumbing the steps share, so each step
can be about one idea.
