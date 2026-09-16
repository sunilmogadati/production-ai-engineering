# Runbook — Build 01, Model Routing

Everything below runs **offline**. No API key, no credentials, no network. The one command that
would spend money is behind an explicit flag and is called out at the bottom.

## Prerequisites

- Python **3.10 or newer** (`python3 --version`)
- [`uv`](https://docs.astral.sh/uv/) — optional, but it is how the test command below runs without
  installing anything into your system Python

Nothing else. The offline path uses only the standard library.

## Install

```bash
cd builds/01-model-routing
```

That is the whole install. There are no runtime dependencies for the offline path.

## Run the bench

```bash
cd src && python3 bench.py
```

**Expected output** — a table of seven configurations with a total and a per-task cost for each,
followed by the labelling notice:

```
  200 tasks | rates taken 2026-09-16 | mode: offline
  configuration                     models     calls   classif  escalate      TOTAL   per task
  --------------------------------------------------------------------------------------------
  router (policy-based cascade)          3    18.867     0.052     1.525     20.444    0.10222
  opus only @ high                       1    20.132     0.000     1.483     21.615    0.10807
  ...
  Cost figures above are COMPUTED from published rates, under the ASSUMED
  effort and retry inputs printed in the JSON report. Latency and quality are
  UNMEASURED until a live run.
```

It also writes the full report, including every routing decision and the assumptions the totals
rest on, to `results/offline.json`.

**What to look at first:** compare the `router` row against `opus only @ low`. On the committed run
the router is the *more* expensive of the two. That is the finding, not a bug.

## Run the tests

```bash
uv run --with pytest python -m pytest tests/ -q
```

Expected: **26 passed**. The suite makes no network calls and needs no key.

If you would rather not use `uv`: `pip install pytest && python3 -m pytest tests/ -q`.

## Regenerate the task set

```bash
cd data && python3 generate.py
```

The generator is seeded, so this reproduces the committed `tasks.json` exactly. If it does not, the
generator changed and every committed figure is stale.

## Change the routing policy

Edit the rule list in `src/policy.py` and re-run the bench. No code outside that file needs to
change — that is the point of the policy being data. Two things to try:

- Delete the terminal rule (`R5-default-hard`) and watch the router refuse to route rather than
  quietly defaulting.
- Move `R2-latency-first` below `R3-trivial` and see the ordering change the outcome.

## The live run (spends money)

```bash
export ANTHROPIC_API_KEY=...        # or use an `ant auth login` profile
cd src && python3 bench.py --live
```

**Not yet implemented, deliberately.** The flag exists, checks for a credential, and then exits
saying so. It is scaffolded rather than stubbed with invented numbers, because the figures it would
produce — latency, and the real retry rates per tier — are exactly the ones this build refuses to
guess at. They are marked `UNMEASURED` throughout until this command produces them.

When you implement it against your own workload, it should write `results/live.json` and the doc's
`ASSUMED` inputs should be replaced with what you measured.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `ModuleNotFoundError: pricing` | Run the bench from inside `src/`, or add `src/` to `PYTHONPATH`. |
| `KeyError: unknown model id` | A model identifier was edited and carries a date suffix. The identifiers in `src/pricing.py` are complete as written. |
| Totals differ from the table above | `data/tasks.json` was regenerated with a changed generator, or the rates in `src/pricing.py` were edited. Both are visible in `results/offline.json`. |
