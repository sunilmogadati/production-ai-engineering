# Steps — the agent loop, one idea at a time

Five standalone programs. Each runs on its own.

| Step | Teaches |
|---|---|
| `01_single_turn.py` | the model answers once and stops — why a loop must exist |
| `02_stop_reason.py` | the four terminal values, provoked deliberately |
| `03_the_loop.py` | the minimal agent, ~20 lines |
| `04_bounded.py` | iterations, cost, wall clock — and one of them tripping |
| `05_failures.py` | a broken tool, `is_error`, and idempotency |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 01_single_turn.py     # then 02, 03, 04, 05
```

`_tools.py` holds three synthetic tools over a fabricated incident. The data is
deliberately **inconsistent** — the service reporting the problem has not deployed in
days, while something it depends on shipped 55 minutes ago. No single tool call reaches
that conclusion, which is what makes the loop earn its existence.

Costs a few cents for all five.
