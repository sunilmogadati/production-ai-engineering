# ML Study 05 — Naive Bayes: Classifying with Probability

**Covers:** independent vs. dependent events → conditional probability → Bayes' theorem (derived) → turning it into a classifier → the "naive" independence assumption → a full worked example (Play Tennis) → the zero-frequency trap and Laplace smoothing → when to reach for it.
**Goal:** understand a classifier that doesn't do gradient descent at all — it just **counts**. By the end you can build a Naive Bayes prediction by hand from a frequency table, and know exactly why it's the go-to baseline for text and spam.

**Series context:** this is a **classification** algorithm, a sibling to **[ML Study 03 — Logistic Regression](ML_Study_03_Logistic_Regression.html)**. Both answer *yes/no* — but where logistic regression *learns weights* by descending a cost curve, Naive Bayes **fits by counting frequencies in one pass**. No learning rate, no iterations. Runnable companion: **`hands-on/hello_naive_bayes.py`** (reproduces this whole doc's arithmetic, then confirms it with scikit-learn).

---

## Part 1 — The problem: predict a label from clues

> You're handed some **clues** (it's *Sunny* and *Hot*) and asked for a **label** (will they play tennis — *Yes* or *No*?). You have a history of past days with their clues and what happened. Naive Bayes answers by asking: *"Across everything I've seen, which label makes these particular clues most probable?"* — and it computes that with nothing more than fractions.

Naive Bayes is a **probabilistic classifier**. Instead of drawing a boundary (logistic regression) or a tree of rules (decision trees), it estimates **P(label | clues)** for each possible label and picks the biggest. Its reputation rests on one killer application: **text** — spam filters, sentiment, document topic tagging — where every word is a clue and there are thousands of them. It's fast, needs little data, and is almost always the **first baseline** a working engineer tries before anything fancier.

To get there we need three probability ideas, in order: independent vs. dependent events, conditional probability, and Bayes' theorem.

---

## Part 2 — Two kinds of events: independent vs. dependent

**Independent events — rolling a die.** The outcomes are `{1, 2, 3, 4, 5, 6}`, each with probability `P(1) = P(2) = … = 1/6`. Roll again and the odds are *unchanged* — getting a 2 this time tells you **nothing** about the next roll. When one event's outcome doesn't affect another's, they are **independent**.

**Dependent events — a bag of marbles.** A bag holds **3 red** and **2 green** marbles (5 total). Draw one, *keep it out*, then draw again:

- First draw red: `P(Red) = 3/5`.
- Now only **4** marbles remain. So the second draw's odds *changed* because of the first: `P(Green after a red is gone) = 2/4 = 1/2`.

The second event **depends** on the first — the bag is smaller now. These are **dependent events**.

> **Vocab bridge:** this is the same *independent vs. dependent* language from linear regression (**[Study 01 §3.1](ML_Study_01_Linear_Regression.html)**) — but pointing at a different thing. There it meant the *input feature* (independent, $x$) vs. the *predicted output* (dependent, $y$). Here it means whether two *events'* probabilities affect each other. Same words, different context — worth flagging to students so they don't conflate them.

### Conditional probability — "given that…"

For the marbles, the chance of "red **then** green" is:

$$P(\text{Red and Green}) = P(\text{Red}) \times P(\text{Green} \mid \text{Red})$$

That second term, $P(\text{Green} \mid \text{Red})$, reads **"probability of Green *given* Red"** — the probability of green *once red has already happened*. The vertical bar `|` means **"given"**. This is **conditional probability**, and it's the whole engine of what follows.

In general, for any two events A and B:

$$P(A \text{ and } B) = P(A)\times P(B \mid A)$$

---

## Part 3 — Bayes' theorem (derived in three lines)

Here is the one piece of algebra in this doc. Start from a fact that's obviously true — the probability of "A and B" doesn't care which order you say it:

$$P(A \text{ and } B) = P(B \text{ and } A)$$

Now expand **each side** with the conditional-probability rule from Part 2:

$$P(A)\times P(B \mid A) = P(B)\times P(A \mid B)$$

Divide both sides by $P(A)$ and you have **Bayes' theorem**:

$$\boxed{\;P(B \mid A) = \dfrac{P(B)\times P(A \mid B)}{P(A)}\;}$$

📖 **Read it aloud:** *"probability of B given A equals probability of B, times probability of A given B, divided by probability of A."*

**Why this is magic:** it lets you **flip a conditional**. Often you *can't* directly measure the thing you want, `P(B | A)`, but you *can* easily count the reverse, `P(A | B)`, from past data. Bayes' theorem trades the one you have for the one you want. **That flip is the crux of Naive Bayes.**

---

## Part 4 — From Bayes' theorem to a classifier

Rename the pieces for machine learning. Our clues are features $x_1, x_2, \ldots, x_n$ (the **independent features**), and $y$ is the label we want (the **dependent/output feature**, e.g. Yes/No). Plug them into Bayes' theorem:

$$P(y \mid x_1, x_2, \ldots, x_n) = \dfrac{P(y)\;\times\;P(x_1, x_2, \ldots, x_n \mid y)}{P(x_1, x_2, \ldots, x_n)}$$

Read the three parts:

- **$P(y)$ — the prior.** How common is this label overall, *before* looking at any clue? (e.g. "people played on 9 of 14 days.")
- **$P(x_1,\ldots,x_n \mid y)$ — the likelihood.** If the label were $y$, how likely are *these* clues?
- **$P(x_1,\ldots,x_n)$ — the evidence (denominator).** How common are these clues in general?

**The first simplification — drop the denominator.** We compute this for *every* label (Yes and No) using the **same** clues, so the denominator $P(x_1,\ldots,x_n)$ is **identical in every case** — a constant. Since we only care *which label is bigger*, a shared constant can't change the winner, so we **ignore it**:

$$P(y \mid x_1,\ldots,x_n) \;\propto\; P(y)\times P(x_1,\ldots,x_n \mid y)$$

(The `∝` means "proportional to" — equal except for that constant we dropped. We put it back at the very end by *normalizing*, Part 7.)

---

## Part 5 — The "naive" assumption (this is where the name comes from)

The likelihood $P(x_1, x_2, \ldots, x_n \mid y)$ is still hard — it's the probability of a *whole specific combination* of clues occurring together, and you'd rarely have enough data to count every combination.

So Naive Bayes makes one **bold, deliberately-too-simple assumption**: it pretends all the features are **independent of each other** (given the label). That's the "naive" part — in reality *Sunny* and *Hot* are correlated, but we pretend they aren't. Under that pretense, the probability of the combination becomes just the **product** of each clue on its own:

$$P(x_1,\ldots,x_n \mid y) \approx P(x_1 \mid y)\times P(x_2 \mid y)\times \cdots \times P(x_n \mid y)$$

Putting it together:

$$\underbrace{P(y \mid x_1,\ldots,x_n)}_{\text{what we want}} \;\propto\; \underbrace{P(y)\times \prod_{j=1}^{n} P(x_j \mid y)}_{\text{the \textbf{score} — we compute this}}$$

📖 **In words:** *"prior times the product of each clue's likelihood."* Every term on the right is just a **fraction you count from the data**. That's the whole algorithm.

**What "score for each label" means.** A **label** is one possible answer — here just two, **Yes** and **No**. The **score** is that right-hand number, $P(y)\times\prod_j P(x_j\mid y)$, worked out **once for each label**. So for the clues (Sunny, Hot) you compute *two* scores:

- **score(Yes)** $= P(\text{Yes})\times P(\text{Sunny}\mid\text{Yes})\times P(\text{Hot}\mid\text{Yes})$
- **score(No)** $= P(\text{No})\times P(\text{Sunny}\mid\text{No})\times P(\text{Hot}\mid\text{No})$

Then you **pick the label with the bigger score** — that's the prediction. (Part 6 gets score(Yes) ≈ 0.031 and score(No) ≈ 0.085, so **No** wins.)

Why "score" and not "probability"? Because we **dropped the denominator** in Part 4 (`∝`, not `=`), these two numbers are only *proportional* to the true probabilities — they won't add up to 1 on their own. They're perfectly good for **ranking** the labels (all we need to pick a winner), and Part 7 rescales them back into real percentages by normalizing. Think of a score as an **un-normalized probability** — a comparable number, not yet a true probability.

> **Why "naive" still works:** the independence assumption is usually *false*, yet the classifier is often excellent. Reason: we don't need the *probabilities* to be accurate — we only need the **Yes score to beat the No score in the right direction**. The errors from the naive assumption tend to hit both scores similarly and wash out in the comparison.

---

## Part 6 — Full worked example: will they play tennis?

The classic 14-day dataset (Outlook, Temperature, Humidity, Wind → PlayTennis). This is the raw data every count below comes from — **PlayTennis** is the label (a binary classification, Yes/No); the other four columns are the clues:

| Day | Outlook | Temperature | Humidity | Wind | **PlayTennis** |
|:---:|---|---|---|---|:---:|
| D1 | Sunny | Hot | High | Weak | **No** |
| D2 | Sunny | Hot | High | Strong | **No** |
| D3 | Overcast | Hot | High | Weak | **Yes** |
| D4 | Rain | Mild | High | Weak | **Yes** |
| D5 | Rain | Cool | Normal | Weak | **Yes** |
| D6 | Rain | Cool | Normal | Strong | **No** |
| D7 | Overcast | Cool | Normal | Strong | **Yes** |
| D8 | Sunny | Mild | High | Weak | **No** |
| D9 | Sunny | Cool | Normal | Weak | **Yes** |
| D10 | Rain | Mild | Normal | Weak | **Yes** |
| D11 | Sunny | Mild | Normal | Strong | **Yes** |
| D12 | Overcast | Mild | High | Strong | **Yes** |
| D13 | Overcast | Hot | Normal | Weak | **Yes** |
| D14 | Rain | Mild | High | Strong | **No** |

We'll use just **Outlook** and **Temperature** as clues (Humidity and Wind are left as an exercise — the method is identical). First, **fit by counting** — build a frequency table per feature by tallying the label column above. Totals: **9 Yes, 5 No** out of 14 days.

*(How to read the Outlook table below: of the 5 Sunny days, 2 were Yes and 3 were No — so P(Sunny|Yes) = 2/9 counts against the 9 total Yes days, and P(Sunny|No) = 3/5 against the 5 total No days.)*

**Priors** (before any clue):

$$P(\text{Yes}) = \tfrac{9}{14}, \qquad P(\text{No}) = \tfrac{5}{14}$$

**Feature 1 — Outlook:**

| Outlook | Yes | No | P(·\|Yes) | P(·\|No) |
|---|:---:|:---:|:---:|:---:|
| Sunny | 2 | 3 | 2/9 | 3/5 |
| Overcast | 4 | **0** | 4/9 | **0/5** |
| Rain | 3 | 2 | 3/9 | 2/5 |
| **Total** | **9** | **5** | | |

**Feature 2 — Temperature:**

| Temp | Yes | No | P(·\|Yes) | P(·\|No) |
|---|:---:|:---:|:---:|:---:|
| Hot | 2 | 2 | 2/9 | 2/5 |
| Mild | 4 | 2 | 4/9 | 2/5 |
| Cool | 3 | 1 | 3/9 | 1/5 |
| **Total** | **9** | **5** | | |

### Predict a new day: (Sunny, Hot)

Score each label with `prior × likelihoods` (denominator dropped):

$$P(\text{Yes} \mid \text{Sunny, Hot}) \propto P(\text{Yes})\cdot P(\text{Sunny}\mid\text{Yes})\cdot P(\text{Hot}\mid\text{Yes}) = \tfrac{9}{14}\cdot\tfrac{2}{9}\cdot\tfrac{2}{9} = \tfrac{2}{63} \approx \mathbf{0.031}$$

$$P(\text{No} \mid \text{Sunny, Hot}) \propto P(\text{No})\cdot P(\text{Sunny}\mid\text{No})\cdot P(\text{Hot}\mid\text{No}) = \tfrac{5}{14}\cdot\tfrac{3}{5}\cdot\tfrac{2}{5} = \tfrac{3}{35} \approx \mathbf{0.085}$$

`No (0.085)` beats `Yes (0.031)`, so the prediction is **No** — on a sunny, hot day, they don't play.

---

## Part 7 — Normalization: turning scores into probabilities

The two scores (0.031 and 0.085) don't add to 1 — because we threw away the denominator. To recover real, reportable probabilities, **normalize**: divide each by their sum (this is exactly the constant denominator, reconstructed):

$$P(\text{Yes}) = \frac{0.031}{0.031 + 0.085} = \frac{0.031}{0.116} \approx 0.27 = \mathbf{27\%}$$

$$P(\text{No}) = \frac{0.085}{0.116} \approx 0.73 = \mathbf{73\%} \quad(\text{or simply } 1 - 0.27)$$

**Decision rule** (same 0.5 threshold as logistic regression, Study 03): 73% ≥ 50% → predict **No**. Same winner as before — normalizing never changes *which* label wins; it just makes the number honest to report.

---

## Part 8 — Your turn (and the trap hiding in it): (Overcast, Mild)

As an exercise, predict for **(Overcast, Mild)**. Set it up the same way:

$$P(\text{Yes} \mid \cdots) \propto \tfrac{9}{14}\cdot\underbrace{\tfrac{4}{9}}_{\text{Overcast}\mid\text{Yes}}\cdot\underbrace{\tfrac{4}{9}}_{\text{Mild}\mid\text{Yes}} = \tfrac{9}{14}\cdot\tfrac{16}{81}\approx \mathbf{0.127}$$

$$P(\text{No} \mid \cdots) \propto \tfrac{5}{14}\cdot\underbrace{\tfrac{0}{5}}_{\text{Overcast}\mid\text{No}}\cdot\underbrace{\tfrac{2}{5}}_{\text{Mild}\mid\text{No}} = \mathbf{0}$$

Prediction: **Yes** (in fact 100% after normalizing). But look *why* the No score is exactly **0**.

> ### ⚠️ The zero-frequency problem
> In all 14 days, **Overcast never once came with "No"** — that cell is `0`. So `P(Overcast | No) = 0/5 = 0`, and since the scores are a **product**, that single zero **annihilates the entire No score** — even though *Mild* had decent support for No. One unseen combination silently vetoed a whole label. In a spam filter with thousands of words, this happens constantly: any word never seen in a "spam" email would zero out the spam probability entirely.
>
> **The fix — Laplace (add-one) smoothing.** Add a small count (usually **1**) to *every* tally so nothing is ever exactly zero:
> $$P(x_j \mid y) = \frac{\text{count}(x_j, y) + 1}{\text{count}(y) + k}$$
> where $k$ = number of categories for that feature. Now `P(Overcast | No) = (0+1)/(5+3) = 1/8`, small but non-zero — the label survives to be judged on its other evidence. **scikit-learn does this by default** (`alpha=1.0`), which is why its numbers differ slightly from the bare-hands arithmetic above. The companion lab shows both.

---

## Part 9 — Judgment: when to reach for Naive Bayes

**Reach for it when:**
- **Text / high-dimensional categorical data** — spam, sentiment, topic tagging. This is its home turf; thousands of word-features, and the independence assumption (word order ignored, "bag of words") is good enough.
- **You need a fast, strong baseline.** It trains in a single counting pass — no iterations, no tuning a learning rate. Always worth running first to set the bar.
- **Little training data.** It estimates few parameters (just per-feature frequencies), so it holds up when data is scarce and fancier models would overfit.
- **You need speed at prediction time** — a handful of multiplications per class.

**Be cautious when:**
- **Features are strongly correlated.** The naive assumption breaks; probabilities get badly miscalibrated (the *ranking* often survives, but don't trust the 73%-type numbers as true confidence).
- **You need well-calibrated probabilities**, not just the winning label — reach for logistic regression instead.
- **Relationships are genuinely interactive** ("this *only* matters when combined with that") — Naive Bayes is blind to interactions by construction; a tree or gradient-boosted model will beat it.

**The three flavors** (pick by what your features look like):

| Variant | Use when features are… | Example |
|---|---|---|
| **Multinomial NB** | counts / frequencies | word counts in a document (spam) |
| **Bernoulli NB** | binary present/absent | did the word appear? yes/no |
| **Gaussian NB** | continuous numbers | height, income — assumes a bell curve per class |

*Our Play-Tennis features are plain categories, so the lab uses scikit-learn's `CategoricalNB`.*

---

## Companion lab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sunilmogadati/production-ai-engineering/blob/main/notebooks/hello_naive_bayes.ipynb) &nbsp; *(one-time GitHub sign-in; you're a collaborator on the repo)*

**`hands-on/hello_naive_bayes.py`** (and the Colab notebook above) does three things, in order:
1. **Fits by hand** — builds the exact frequency tables above and reproduces `Sunny,Hot → No (27% / 73%)` from raw counts, so you can see there's no magic, only fractions.
2. **Solves the assignment** — computes `(Overcast, Mild)` and demonstrates the zero-frequency annihilation, then shows Laplace smoothing rescuing the No score.
3. **Confirms with scikit-learn** — trains `CategoricalNB` on the same 14 rows and shows it agrees (with smoothing on by default).

---

## Quick Reference — say it in plain words (then the term)

| Plain words | The term |
|---|---|
| "Does one event's outcome change the other's odds?" | independent vs. dependent events |
| "Probability of B, *given* A already happened." | conditional probability, $P(B\mid A)$ |
| "Flip a conditional you can't measure into one you can count." | Bayes' theorem |
| "How common is this label before seeing clues?" | prior, $P(y)$ |
| "If the label were y, how likely are these clues?" | likelihood, $P(x\mid y)$ |
| "Pretend all clues are independent, so just multiply them." | the **naive** assumption |
| "The bottom of Bayes is the same for every label, so drop it." | dropping the (constant) evidence |
| "Turn the raw scores back into percentages that sum to 1." | normalization |
| "Add 1 to every count so nothing is ever zero." | Laplace / add-one smoothing |

## Glossary (jargon → plain English)

| Term | Plain English |
|---|---|
| Naive Bayes | a classifier that picks the label making your clues most probable, via Bayes' theorem + a pretend-independence shortcut |
| Bayes' theorem | $P(B\mid A) = P(B)\,P(A\mid B)/P(A)$ — flips a conditional probability |
| Prior | the base rate of a label before seeing any feature |
| Likelihood | probability of a feature value given a label |
| Posterior | $P(\text{label}\mid\text{clues})$ — what we ultimately want |
| Naive (independence) assumption | pretend features don't affect each other, so the joint likelihood is a product |
| Zero-frequency problem | an unseen feature/label combo makes one count 0, zeroing the whole product |
| Laplace smoothing | add a small constant to every count so no probability is ever exactly 0 |
| Multinomial / Bernoulli / Gaussian NB | variants for count / binary / continuous features |

---
**◄ Previous: [ML Study 03 — Logistic Regression](ML_Study_03_Logistic_Regression.html)**  ·  **Related → [ML Study 01 — Linear Regression](ML_Study_01_Linear_Regression.html)** (independent vs. dependent variables)

*ML Study 05 — Naive Bayes: independent/dependent events → conditional probability → Bayes' theorem → the naive product → Play-Tennis worked example → the zero-frequency trap. A counting classifier: no gradient descent, one pass over the data. Companion lab: `hands-on/hello_naive_bayes.py`.*
