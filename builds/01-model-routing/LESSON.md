# Lesson 01 — Choosing a Model: The Decision That Outlives the Model List

**Covers:** the three tiers and the three dimensions they trade off (**intelligence · speed · cost**) → matching a model to a task → **smart routing**, the optimisation everyone reaches for first → the four things a price table leaves out (**effort**, **model-scoped caches**, **the classifier's own bill**, **cost per *completed* task**) → a router that reports the rule behind every decision → what a bench says when you actually measure it.

**Goal:** stop treating model selection as a lookup against a price table. By the end you can price a workload before spending anything, you know which lever to pull *first*, and you can defend the choice in a design review — including the case for not routing at all.

**Series context:** first lesson of the Build Track. Pairs with the runnable build in this folder: five steps in [`steps/`](steps/) you run live, and a bench in [`src/`](src/) that runs with **no API key at all**.

---

## Part 1 — The problem: the model list is already out of date

Here is the table every introduction to a model family ends with.

| Tier | Model | Input $/MTok | Output $/MTok | Context |
|---|---|---|---|---|
| Large | `claude-opus-5` | $5.00 | $25.00 | 1M |
| Mid | `claude-sonnet-5` | $2.00 | $10.00 | 1M |
| Small | `claude-haiku-4-5` | $1.00 | $5.00 | 200K |

*Rates verified 2026-09-16.*

Three tiers, priced in order. And the conclusion that follows feels obvious: most work is easy, the small tier is a fifth the price, so classify each request and send the easy ones down.

**Start with the uncomfortable part.** That table will be wrong within months. Model families ship on a cadence measured in weeks — names change, prices move, and the relationship between tiers changes with them. A course, a blog post, or a doc built on a *specific list of models* has a shelf life, and anything you memorised about which model is "the fast one" expires with it.

So we are not going to teach the table. We are going to teach the **decision procedure**, which does not expire — and then run it against today's table.

> **The one-line frame:** the model list is a fact with an expiry date. The **way you choose** is the part worth learning, because it survives the next release.

---

## Part 2 — The three dimensions, and the one that lies

Every model is described on three axes:

- **Intelligence** — how well it handles reasoning, nuance, and multi-step problems.
- **Speed** — latency. How long the user waits.
- **Cost** — dollars per million tokens, in and out.

Two of those are honest. **Cost is not a dimension — it is four line items**, and a price table shows you one of them.

```mermaid
flowchart TB
    Q["What does this request cost?"]
    Q --> A["1. Tokens x rate<br/>the only line in the price table"]
    Q --> B["2. Cache: warm or cold<br/>a repeated prefix bills ~0.1x when warm<br/>caches are scoped to ONE model"]
    Q --> C["3. The routing decision<br/>a model call of its own,<br/>charged on every request"]
    Q --> D["4. Retries and escalation<br/>a failed cheap call still bills,<br/>then a stronger model bills again"]
    A --> T["What you are actually billed"]
    B --> T
    C --> T
    D --> T
```

Lines 2, 3 and 4 appear in no tier table anywhere. They are also the three that decide whether routing is worth doing — which is why the obvious optimisation so often disappoints.

> **The one-line frame:** a price table tells you what a **token** costs. It does not tell you what the **work** costs, and those two numbers rank your options differently.

---

## Part 3 — The claim, and how to test it

You will read everywhere — vendor docs, courses, conference talks — that routing simple work to a small model saves **80% or more**.

That number is not a lie. It is achievable. It requires three conditions to hold at once:

1. Almost all of your traffic is genuinely trivial.
2. There is little or no repeated prefix, so splitting the cache costs nothing.
3. The small tier almost never fails, so almost nothing escalates.

Break any one of them and the number collapses. **80% is a property of a workload, not a fact about routing.** Someone measured it on theirs. The engineering question is what it is on yours.

So we measure. `src/bench.py` in this folder prices 200 synthetic tasks across seven configurations, offline, from published rates. Here is what it produced:

| Configuration | Models | Calls | Classifier | Escalations | **Total** |
|---|---|---|---|---|---|
| router (policy cascade) | 3 | $18.87 | $0.05 | $1.53 | **$20.44** |
| opus only @ high effort | 1 | $20.13 | — | $1.48 | **$21.61** |
| **opus only @ low effort** | 1 | $18.50 | — | $1.39 | **$19.89** |
| **sonnet only @ high** | 1 | $8.05 | — | $4.12 | **$12.18** |
| haiku only @ high | 2 | $7.77 | — | $7.39 | **$15.16** |
| router, cache reuse off | 3 | $20.28 | $0.05 | $1.65 | **$21.98** |

Four readings, and the first one is the lesson:

**1. The router saved 5.4% — and lost to one model at lower effort.** Against the naive full-effort baseline it wins. Against the *same model with one parameter changed*, it is 2.8% more expensive, and that configuration saves 8.0% on its own. One model, one cache, no classifier, no second failure mode, and a better number.

**2. The cache split cost more than routing saved.** Turn cache reuse off and the router's bill rises $1.53 — **7.5%**. It was built to capture 5.4%. The mechanism it defeats itself with is larger than the one it exploits.

**3. The cheapest tokens produced an expensive outcome.** Haiku has the lowest rate of the three. **48.7% of its bill is escalation** — work it attempted, failed, and handed upward, having already been paid for.

**4. The genuinely cheapest option was the least sophisticated.** One mid-tier model, no routing logic at all: **43.7% below** the naive baseline.

> **The one-line frame:** the 80% claim and our 5.4% are both true, of different workloads. **Measure the simple fix before you build the sophisticated one.**

---

## Part 4 — The procedure

This is the part that survives the next model release.

```mermaid
flowchart TD
    S["A workload to serve"] --> P["1. PRICE IT<br/>count tokens, multiply by rates<br/>free, instant, no API call"]
    P --> B["2. BASELINE<br/>strongest model, reduced effort<br/>one model, one cache"]
    B --> M{"3. Does it meet<br/>quality and latency?"}
    M -->|yes| DONE["Ship it.<br/>You are done."]
    M -->|no| E["4. Raise effort, or move a tier"]
    E --> R{"5. Still not there,<br/>and volume is large?"}
    R -->|no| DONE
    R -->|yes| C["6. NOW consider routing<br/>price the cache split<br/>price the classifier<br/>count escalations"]
    C --> V{"7. Does it beat<br/>step 2 by enough<br/>to justify two systems?"}
    V -->|no| DONE
    V -->|yes| SHIP["Route — and make every<br/>decision report its rule"]
```

Step 2 is where most teams go wrong, by skipping it. They compare routing against the *naive* default — strongest model, full effort — which is a baseline nobody should be running. Beating it proves very little.

Two hard constraints sit outside the procedure and override it:

- **Context window.** A model that cannot hold the input is not a cheaper option; it is a different failure. Check fit before cost.
- **Latency.** If the large tier cannot meet your response budget, routing buys you *time*, not money — a completely different justification, and a legitimate one.

> **The one-line frame:** price it, baseline one model at reduced effort, and make routing **earn its place** against that — not against a default nobody should be running.

---

## Part 5 — The decision you would defend

A design review asks: *why is there no router?* "Routers are overrated" is not an answer. This is:

1. **We measured the one-model baseline first** — strongest model at reduced effort, on our traffic.
2. **We priced the cache split.** Our shared prefix is *N* tokens on every request; splitting it across three models costs *X* a month against a projected routing saving of *Y*.
3. **We counted escalations, not calls.** Cost per completed task, with failed cheap calls charged twice.
4. **We know what we have not measured**, and we said so rather than quoting a plausible number.

And the conditions under which the answer flips, stated in advance — because a decision with no reversal condition is just a belief:

- A **large, genuinely trivial** share of traffic, with low escalation.
- A **small or absent shared prefix**, which removes the cache penalty.
- A **latency requirement** the large tier cannot meet.

> **The one-line frame:** the defensible position is not a verdict on routing — it is **the baseline you measured, the mechanism you priced, and the condition under which you would change your mind.**

---

## Run it

Five steps, one idea each — see [`steps/README.md`](steps/README.md):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd steps
python3 01_one_call.py      # one call, and what it cost
python3 02_three_tiers.py   # same work, three tiers
python3 03_effort.py        # the lever inside one model
python3 04_route.py         # a router that reports its rule
python3 05_price_first.py   # price before you spend
```

No key? The full bench runs offline — cost is arithmetic:

```bash
cd src && python3 bench.py
```

The deeper write-up, including how the bench models cache warmth and escalation, is in [README.md](README.md).

---

## Quick reference / glossary

| Term | Meaning |
|---|---|
| **effort** | request-level control trading thoroughness against spend *within one model* — the lever to try before a second model |
| **prompt cache** | a warm copy of a repeated prefix, billed ~0.1× on read, ~1.25× to write — **scoped to one model** |
| **cache affinity** | routing for locality because a miss costs more than the cheaper rate saves |
| **classifier tax** | the cost of deciding where to route, charged on every request including ones headed for the expensive tier |
| **escalation** | a failed cheap call handed upward; the task pays for both |
| **cost per completed task** | total spend ÷ tasks *finished* — the only unit that survives retries |
| **context window** | a hard constraint, never a preference |
| `response.usage` | what the call actually consumed — the only honest basis for a cost figure |
| `count_tokens` | prices the input side *before* you spend anything |

---

*Lesson 01 — the model list expires; the decision procedure does not. Cost is not one number but four: tokens × rate, cache warmth, the routing decision itself, and escalation — and a price table shows you only the first. So price the workload before spending (arithmetic, free), baseline the strongest model at reduced effort (one model, one cache, one failure mode), and make routing earn its place against **that** rather than against a default nobody should run. On our bench the router beat the naive baseline by 5.4% and **lost to the same model at low effort**, while the cache split it caused cost 7.5% — more than routing saved. The widely-quoted 80% saving is real on some workload; it is a property of that workload, not of routing. Measure yours. And make every routing decision carry the rule that produced it, so a reviewer argues with the policy instead of the outcome.*
