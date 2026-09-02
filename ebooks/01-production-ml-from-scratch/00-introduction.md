# Production Machine Learning, From Scratch

*Classical ML, one algorithm at a time — on real public data, and served as an API.*

---

## Why this book exists

Most machine-learning material fails working engineers in one of two ways. Either it's a wall of
mathematics with no code you'd ship, or it's a stack of `model.fit()` calls with no idea of what's
happening underneath. The first makes you feel unqualified; the second makes you dangerous — you can
call the library but you can't tell when it's lying to you.

This book takes a third path, the one a senior engineer actually needs: **understand each algorithm
well enough to reason about it, build it on real data, and ship it like production software.** Not
research-grade proofs. Not toy datasets. The working knowledge that lets you look at a model's output
and say *"that number is wrong, and here's why."*

If you've written software for a living — especially backend or enterprise systems — you already have
the hard part: you think in systems, contracts, and failure modes. Machine learning is not a different
universe. It's a new kind of component with new failure modes, and this book teaches it as exactly
that.

## How each chapter works

Every chapter follows the same four moves, because that's how an experienced engineer actually learns a
new technique:

1. **The problem** — what real question forces this algorithm into existence. We never start with the
   math; we start with the itch it scratches.
2. **The pattern underneath** — the computer-science idea doing the work (a distance, a probability, a
   split, a gradient step). Once you see the pattern, the API stops being magic.
3. **The architecture** — how it fits a real pipeline: the data going in, the contract coming out,
   where it breaks.
4. **The judgment** — when to reach for it, when *not* to, and how to read its output like a
   diagnostician. This is the part libraries can't give you and the part that makes you valuable.

You'll see this rhythm in every chapter. It's deliberate. By chapter three you'll be anticipating it,
and that anticipation *is* the mental model forming.

## The running example: a world & countries data platform

One dataset threads the entire book. Rather than a new toy problem each chapter, we build up a single,
real one: **a data platform for world and country indicators**, sourced from **public international
organizations** — the World Bank to start, with the shape to extend to the IMF, OECD, UN, and WHO.

This choice is not decoration. It does three things a scatter of toy datasets can't:

- **It's real and public.** Every number traces to an open source. No synthetic hand-waving, no data
  you're not allowed to look at. You can run all of it yourself.
- **It compounds.** The regression you fit in Chapter 1 uses features you'll cluster in Chapter 9 and
  serve in Chapter 13. The dataset grows with your skill, the way a real project does.
- **It's honest about what ML can and can't claim.** Country data forces the questions that matter in
  production — *is this association or causation? what does a residual actually mean? who gets hurt if
  we're wrong?* We answer those in-line, not in an appendix.

By the last chapter, the same platform that taught you linear regression is **serving a trained model
behind a FastAPI endpoint** — the bridge every engineer needs and most books skip: from a model in a
notebook to a model other systems can call.

## How to read it

- **In order, the first time.** The chapters build; the running example accumulates. Later chapters
  assume the vocabulary earlier ones establish.
- **Run the notebooks.** Each chapter names a companion `hello_*` notebook. Reading about gradient
  descent is fine; watching it converge on real data is when it clicks. The book is written so the
  notebooks are the lab, not an afterthought.
- **As a reference, later.** Once you've read it through, each chapter stands alone as the thing you
  come back to when you need to remember *why* Ridge beats plain regression, or when DBSCAN earns its
  keep over K-Means.

## What this book is not

It's not a deep-learning book (that's the next one), and it's not an LLM/agents book (the one after).
It's the **foundation** — the classical models that still run most of the world's production ML, that
you must understand before neural networks make sense, and that are very often the *right* answer when a
team reaches for something fancier than the problem needs.

Good judgment about the simple models is what separates engineers who *use* ML from engineers who can
be *trusted* with it. That judgment is what we're here to build.

Let's start with the landscape.

---

*Next: **Chapter 0 — ML Foundations: the Landscape.***
