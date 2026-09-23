# RUN — every program, in order

One page. Start at the top, work down. **~10 minutes for all of it, a few cents in API spend.**

---

## Once: set up

```bash
git clone https://github.com/sunilmogadati/production-ai-engineering.git
cd production-ai-engineering

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install anthropic
```

Your prompt shows `(.venv)`. That is how you know it worked.

**Your API key** — get one at [console.anthropic.com](https://console.anthropic.com) → API Keys, and
set a spend cap while you are there:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
echo "key set: ${ANTHROPIC_API_KEY:+yes}"
```

That lasts for this terminal window. Permanent: add the `export` line to `~/.zshrc`.

> **New terminal later?** `cd` to the repo and run `source .venv/bin/activate` again, and re-export
> the key if you did not put it in `~/.zshrc`. Those two are the cause of nearly every "it worked
> yesterday".

---

## Build 00 — Foundations · 2 programs

**Does the setup work?**

```bash
cd builds/00-foundations/steps
python3 01_hello.py
```

Expect: a model id, a two-sentence answer, token counts, cost around $0.0001.

**Optional — the same thing in TypeScript.** Only if you want to see that the pattern is not the
syntax. Needs Node via nvm (see `builds/00-foundations/SETUP.md` §2):

```bash
nvm use && npm install && npx tsx 01_hello.ts
```

---

## Build 01 — Model Selection · 7 programs

```bash
cd ../../01-model-routing
```

**First, the one that needs no API key.** Pure arithmetic over published rates:

```bash
python3 src/bench.py
```

Expect: seven configurations with totals. **Look for the row where `opus only @ low` sits *below* the
router** — that is the finding.

**Then the five steps:**

```bash
cd steps
python3 01_one_call.py       # one call, and reading its cost off response.usage
python3 02_three_tiers.py    # each tier on its matched task, then all three on one task
python3 03_effort.py         # the lever inside ONE model -- the point of the build
python3 04_route.py          # a router that reports the rule behind every decision
python3 05_price_first.py    # counting tokens to price a workload before spending
```

**Regenerate the task set** (optional — proves it is reproducible):

```bash
cd ../data && python3 generate.py     # rewrites tasks.json byte-identically
```

**Run the tests** (no key needed):

```bash
cd .. && uv run --with pytest python -m pytest tests/ -q     # expect 26 passed
```

No `uv`? `pip install pytest && python3 -m pytest tests/ -q`

---

## Build 02 — The Agent Loop · 5 programs

```bash
cd ../02-agent-loop/steps

python3 01_single_turn.py    # the model asks for a tool and STOPS. Nobody runs it.
python3 02_stop_reason.py    # the terminal values, provoked deliberately
python3 03_the_loop.py       # the minimal agent, ~20 lines
python3 04_bounded.py        # the three bounds -- one is set low so you watch it trip
python3 05_failures.py       # a tool broken on purpose, reported honestly
```

`04_bounded.py` stops early by design. To see it finish: `python3 04_bounded.py --full`

---

## The 7 files you never run directly

Imported by the programs above. Read them, edit them, but do not execute them:

| File | What it holds |
|---|---|
| `01-model-routing/steps/_shared.py` | the client, cost maths, the `call()` wrapper |
| `01-model-routing/steps/incidents.py` | three synthetic incidents at three difficulties |
| `01-model-routing/src/pricing.py` | the dated rate table and cost arithmetic |
| `01-model-routing/src/policy.py` | the routing rules, as editable data |
| `01-model-routing/src/router.py` | the decision, its rule id, and its cost |
| `01-model-routing/src/tasks.py` | loads and validates the task set |
| `02-agent-loop/steps/_tools.py` | three synthetic tools and their schemas |

**`policy.py` is the one to edit.** Change the rules, re-run `04_route.py`, and watch the routing
change with no other code touched. That is the point of a policy being data.

---

## Running in the browser instead

No install at all — [open the notebook in Colab](https://colab.research.google.com/github/sunilmogadati/production-ai-engineering/blob/main/notebooks/hello_model_selection.ipynb).
Put your key in Colab Secrets (🔑 in the sidebar, name it `ANTHROPIC_API_KEY`, switch on Notebook
access).

---

## If the venv misbehaves

The single most common failure, and it does not look like what it is: **`pip` and `python` serving
different interpreters.** You install a package successfully, then the very next command says it is
not installed.

It happens when a venv is created **while another venv is active**, or when a `pyenv` shim resolves
`python3` to a different version than the one recorded in `pyvenv.cfg`. The venv ends up with two
`lib/pythonX.Y/site-packages` trees — `pip` writes to one, `python` reads the other.

**Check in one line:**

```bash
python3 -c "import sys, os; print(sys.executable); print(os.environ.get('VIRTUAL_ENV'))"
```

Those two paths must agree. If `sys.executable` is not inside your `VIRTUAL_ENV`, the venv is broken.

**Rebuild it properly** — from outside every venv, with an explicit interpreter:

```bash
deactivate                    # repeat until no (venv) prefix is left on your prompt
rm -rf .venv
$(brew --prefix)/bin/python3.12 -m venv .venv      # any python3.10+ you trust
source .venv/bin/activate
pip install anthropic
python3 -c "import anthropic; print(anthropic.__version__)"
```

Two rules that prevent it recurring: **never run `python -m venv` with a venv already active**, and
**name the interpreter explicitly** rather than relying on whatever `python3` resolves to.

> On macOS, `/usr/bin/python3` is the system Python and is usually too old (3.9). Use Homebrew's or
> python.org's.

## When something breaks

| Symptom | Cause |
|---|---|
| `ANTHROPIC_API_KEY is not set` | New terminal, or the export never ran. Re-export it. |
| `ModuleNotFoundError: anthropic` | The venv is not active. `source .venv/bin/activate` from the repo root. |
| `ModuleNotFoundError: _shared` / `pricing` | Run from inside the folder that holds the file — `cd steps` or `cd src` first. |
| `404 model not found` | A model id was edited. The ids here are complete as written; no date suffix. |
| `401` | Key wrong, revoked, or carrying a stray space. Re-copy from the Console. |
| Bench totals differ from the docs | `tasks.json` was regenerated with a changed generator, or the rates were edited. Both are visible in `results/offline.json`. |
| `command not found: nvm` | It is a shell function, not a binary. `command -v nvm`, and reopen the terminal. |

---

## What each build's doc explains

| | Doc | Runs without a key? |
|---|---|---|
| 00 | [Foundations](builds/00-foundations/BUILD.md) — what a harness is, why Claude-native | n/a |
| 01 | [Model Selection](builds/01-model-routing/BUILD.md) — the bench, and why routing lost | **yes**, `src/bench.py` |
| 02 | [The Agent Loop](builds/02-agent-loop/BUILD.md) — who decides when to stop | no |
