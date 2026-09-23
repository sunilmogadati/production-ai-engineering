# Walkthrough — what every file and line actually does

**Read this before teaching. ~15 minutes, cold.**

`BUILD.md` makes the *argument* — why routing often loses. This makes no argument. It explains the
mechanics, line by line, and pre-answers the questions people ask. If you can read this once and
then talk through the code without opening it, it has done its job.

---

## The one thing to understand first

Every step in this build makes **the same API call**. One function:

```python
client.messages.create(model=..., max_tokens=..., system=..., messages=[...])
```

That is the whole SDK surface used here. The steps differ in *which model*, *what prompt*, and
*what they measure* — never in mechanism. If you can explain that one call, you can explain all five.

### The four arguments

| Argument | What it is |
|---|---|
| `model` | which model, as a string. Choosing this string *is* the build. |
| `max_tokens` | a hard ceiling on **output** tokens. Not a target — the model stops when done. |
| `system` | standing instructions: how to behave. Sent once, applies to the whole exchange. |
| `messages` | the conversation itself: what you are actually asking. |

### `max_tokens`, properly

- **Output only.** Your input is priced separately and is not capped by this.
- **A ceiling, not a target.** Ask for 1000 and get an 80-token answer, you pay for 80. Over-provisioning is nearly free.
- **Required on every call.**
- **When it is hit, the reply is cut off mid-sentence** and `stop_reason` comes back as `"max_tokens"` instead of `"end_turn"`. *That* is why Build 02 cares about `stop_reason` — a loop that ignores it hands a truncated half-answer to a user.
- **It is a budget decision, not a lookup.** A one-word classification wants 16. A long analysis wants thousands. Step 01 uses 16 deliberately.

**"Can it be dynamic?"** — a question you *will* get. Yes: you compute it in your own code before the call, e.g. by task type or input length. What it cannot be is changed by the model mid-generation. There is also a separate beta feature that gives the model a budget it can *see* and pace itself against — different mechanism, later build, not needed here.

### `messages` and `role`

```python
messages=[{"role": "user", "content": "..."}]
```

A conversation is a **list**, and every entry says who is speaking:

| role | who |
|---|---|
| `user` | you — the questions |
| `assistant` | the model — its replies |
| `system` | standing instructions (passed as the separate `system=` argument) |

One turn here, so the list has one entry. In a multi-turn exchange you append the model's reply as
`assistant` and your next question as `user`, and send the whole list again — the API remembers
nothing between calls. **That statelessness is what makes Build 02's loop necessary.**

`system` vs `user`: system is *how to behave*, user is *what you are asking*. Same call, two jobs.

### The response is a **list of typed blocks**, not a string

This surprises everyone, including experienced engineers.

```python
answer = "".join(b.text for b in response.content if b.type == "text")
```

`response.content` is a list. Each item has a `.type`:

| `.type` | holds | has `.text`? |
|---|---|---|
| `text` | the words of the answer | **yes** |
| `thinking` | internal reasoning, when enabled | no |
| `tool_use` | a request to call a tool | no |

So `response.content[0].text` will eventually crash on a `thinking` or `tool_use` block. The filter
`if b.type == "text"` is the guard. Write it defensively now and the same line survives Build 02,
where tool_use blocks genuinely appear.

### `response.usage` — where cost comes from

```python
usage.input_tokens, usage.output_tokens
```

What the API says it **actually consumed**. Not an estimate. Every cost figure in this build
multiplies those two numbers by a published rate. That is the entire "cost is arithmetic" claim.

---

## `_shared.py` — and why it exists

**Read this section before students ask why step 01 looks different from build 00's hello world.**
They will, because it does.

`_shared.py` is **a file in this folder, not a package.** `from _shared import ...` loads it from
disk next door. It still does `import anthropic` underneath — the same SDK, the same
`messages.create()`. Nothing new.

It holds five things:

| Name | What it is |
|---|---|
| `OPUS` / `SONNET` / `HAIKU` | the three model-id strings |
| `RATES` | dollars per million tokens, per model |
| `client()` | `anthropic.Anthropic()`, with a readable error if the key is missing |
| `cost_usd()` | tokens × rate ÷ 1,000,000 |
| `call()` | **the `messages.create()` call**, wrapped in a timer, returning a `Result` |
| `Result` | a small record: model, text, seconds, tokens, cost |

**`call()` is not a different API. It is `messages.create()` plus a stopwatch plus the cost maths.**
Line them up:

| Build 00, written out | Build 01, via the helper |
|---|---|
| `anthropic.Anthropic()` | `client()` |
| `client.messages.create(...)` | inside `call()` |
| the `b.type == "text"` join | inside `call()` |
| cost arithmetic | `cost_usd()` |

**Say this aloud in class:** *"Same call you saw yesterday. It moved into a helper so each step can
be about one idea instead of re-typing the plumbing."*

> **Honest note for you, not the room:** this helper is a cost. It makes the steps short and the
> comparison clean, and it hides the API call that is the point of the lesson. Build 00 is
> self-contained for exactly that reason. If a student is confused, open `_shared.py` and show them
> `call()` — it is fifteen lines, and the confusion ends immediately.

`incidents.py` is three synthetic production incidents at genuinely different difficulties. The
difficulty gap **is** the experiment — if all three were easy, every model would look identical and
there would be nothing to decide.

---

## Step by step

### `01_one_call.py` — the baseline

One Haiku call on the easy incident. `max_tokens=16`, because the system prompt demands exactly one
word — a live example of sizing the ceiling to the task.

**Prints:** the answer, then latency, tokens, cost.
**The point:** cost comes off `response.usage`. You are never guessing.

**"Isn't this the same as `01_hello.py`?"** — Mechanically yes, and say so plainly. The differences
are deliberate: this one uses a task with a **checkable right answer** (severity classification), so
models can be compared fairly — you cannot compare "explain something" across tiers. And it captures
**latency**, which build 00 ignored, because choosing a model trades cost against speed.

*`01_hello.py` proves the pipe works. `01_one_call.py` is the control in an experiment.*

### `02_three_tiers.py` — the method lesson

Two halves, and **the order is the whole point.**

**Part A** gives each tier the work the tier table says it is for: one-word triage → Haiku,
structured analysis → Sonnet, multi-cause investigation → Opus. All three look good.

**It is not a comparison.** Two things moved at once — the task *and* the model — so nothing is
isolated. It looks like evidence and proves nothing.

**Part B** holds the incident fixed and moves only the model. *Now* it is a comparison. It prints
the cost spread and the latency spread.

**Teach the difference explicitly.** Part A is the flattering benchmark everyone reaches for; Part B
is the controlled one. That distinction is worth more to a senior engineer than anything about
model tiers.

This is also the **only place in the build with real latency numbers.** Cost is arithmetic and the
offline bench computes it for free; time must be measured.

### `03_effort.py` — the turn

One model — Opus — at `effort` low, medium, high. Same prompt, same incident.

`effort` trades thoroughness against token spend **inside one model**. Thinking tokens bill as
output, so lower effort costs less.

**This is what the session exists for.** The saving arrives with **no router, no classifier, no
second model, no second cache.** One parameter.

Set it up before you run it: *"There is an option that tier table never mentions."* Then run it, and
leave silence.

*Note: not every tier accepts `effort` — the small tier rejects it. That is why this step uses Opus.*

### `04_route.py` — routing, with its reasoning visible

Classify the incident (a cheap model call), pick a tier from a policy, run it.

Two details that are the actual lesson:

1. **The classifier is itself a model call** — priced, and charged on **every** request, including
   the ones that route to the expensive model anyway. The step prints it as its own line. Never fold
   it into the routed call.
2. **Every decision reports the rule that made it.** A bare model name is an instruction; a model
   name plus its rule is an *argument*, and an argument can be reviewed by the person whose budget
   it is — someone who will never open the source.

`POLICY` is a **list of dicts** — data, not code. First match wins, so ordering is part of the
policy. **This is the file to edit live:** change a rule, re-run, watch routing change with nothing
else touched.

### `05_price_first.py` — the assignment

Uses `count_tokens` to price the **input** side before any generation happens. Free, instant, no
guessing. For long-context work the input dominates, so a 200,000-token document sent to the wrong
tier is a decision you can evaluate *before* making it.

Only the output side needs measuring, because only the model decides that.

---

## Questions you will get, with answers

**"Why is output 5× the price of input?"** Generation is the expensive operation; reading is cheap.
It is why `max_tokens` matters for cost and why `effort` (which moves output tokens) is such a
strong lever.

**"Why did you set `max_tokens=16`?"** The prompt demands one word. Sizing the ceiling to the task
is the habit; it also caps worst-case spend on a runaway input.

**"Does the model remember the last call?"** No. The API is stateless. You resend the whole
conversation every time — which is why a long agent loop gets more expensive each turn.

**"Can I use a different model mid-conversation?"** Yes, you hold the history. But the cache goes
cold (caches are per-model), thinking blocks get dropped, and window sizes differ. Portable, not free.

**"Is caching automatic?"** No — opt-in, via a `cache_control` breakpoint. Covered in `BUILD.md`.

**"Where does the routing happen — is it an API feature?"** There is none. The API takes a `model`
string per request; choosing it is your application code. `04_route.py` *is* the router.

---

## Before you teach: 10-minute prep

1. Run `python3 check_env.py` from the repo root.
2. Run `src/bench.py` — no key needed. Put the numbers on screen.
3. Run steps 01, 02, 03. Watch the effort numbers yourself before the room does.
4. Re-read the three lines above marked **the point** — one per step.
5. Open `_shared.py` and look at `call()`. Fifteen lines. It is the answer to the commonest question.

You do not need to have read `BUILD.md` end to end to teach the steps. Read Part 3's findings table
and Part 5. The rest is the write-up students read afterwards.
