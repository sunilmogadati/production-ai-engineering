# Production AI — The Build Track

Systems you build, run, and defend. Each entry is one folder you clone: the working code, a runbook
that gets you to a result, and a write-up of the judgment behind it — what breaks in production,
what it costs, and the decision you would defend in a design review.

Companion to [CURRICULUM.md](CURRICULUM.md), the four-week Dev → AI Engineer path. That track builds
the foundations. This one builds the systems.

**How to use it:** run the build first, read the write-up second. Every claim in a write-up is backed
by something that ran, and every number is labelled **computed**, **measured**, or **unmeasured** —
so you can tell what was proven from what is still owed a measurement.

---

## Part 0 — Foundations

- **00 — Foundations** — [builds/00-foundations](builds/00-foundations/) — *Ship: a working local
  environment, and a hello-world in both languages.* What harness engineering actually names, the four
  parts of a harness, why this track is Claude-native when you already know LangChain, and what else
  exists. Your own key, your own laptop — no hosted workspace.

## Part A — The harness

The machinery around the model: what it costs, how the loop is controlled, what stays in context.

- **01 — Model Routing** — [builds/01-model-routing](builds/01-model-routing/) — *Ship: a router that
  picks a model per task, and a bench that makes it compete against one model at lower effort.* Price
  a workload before spending anything; find out whether the router earned its place. On the committed
  run, it did not. Start with the
  [build brief](builds/01-model-routing/BUILD.md) and the five
  [steps](builds/01-model-routing/steps/) or the [Colab notebook](notebooks/hello_model_selection.ipynb); the bench runs with no API key.

*Builds 02–07 in progress.*

---

## Part B — Tools over a protocol

*In progress.*

## Part C — Proving it works

*In progress.*

## Part D — Bounded autonomy

*In progress.*

---

**Program:** Production AI Engineering
**Author:** Sunil Mogadati — 25+ years in software development and architecture; US patent holder.
**Community:** [DeliveryMomentum](https://www.skool.com/deliverymomentum)
