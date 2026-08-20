# ML Study 21 — Data Quality & Anomaly Detection

**Covers:** why data quality is the real job → the method ladder (schema → statistical → distributional → time-series → multivariate → cross-source) → the false-positive trap (why one method can't fit every feature) → filter vs. halt (the tripwire) → the production tools.
**Goal:** learn to catch bad data **without relying on domain intuition** — and to know when a "detected anomaly" is a real error versus a legitimate value your method mis-flagged.

**Series context:** the twin of **[ML Study 04 — Time Series](ML_Study_04_Time_Series.html)** (a forecast's residual *is* an anomaly detector). Every example here is real — caught while building the World Bank capstone.

---

## Part 1 — The real job: garbage in, garbage out

> Every model you've built assumes the data is trustworthy. It usually isn't. **Public, authoritative sources contain real errors** — and a model trained on them fails silently, which is the worst kind of failure: no crash, just quietly wrong answers.

**The case that started it.** Building the capstone, a data-quality check halted training on one value: **Central African Republic, 2022, life expectancy = 18.818 years.** Impossible — a newborn dying before 19. We traced it: the World Bank's own API returns it (our pipeline was faithful), and the whole series *sawtoothed* — 51.9 → 45.2 → 52.3 → **31.5** → 50.6 → **40.3** → **18.8**. An independent source (the WHO) showed CAR at a smooth ~52 throughout. **Verdict: a real World Bank data error**, and the model had been training on it.

The lesson isn't "the World Bank is bad." It's that **validation is not optional** — you defend against the source, you don't trust it.

---

## Part 2 — The method ladder (cheapest → most general)

You climb this ladder until the bad data is caught. Each rung needs *less* domain knowledge than the one before.

| Rung | Method | Catches | Needs |
|---|---|---|---|
| 1. **Schema / contract** | types, allowed values, not-null, **hand-set ranges** | wrong type, `NULL`, out-of-bounds | you to know the bounds |
| 2. **Statistical (univariate)** | **robust z-score** (median + MAD), IQR / Tukey fences | values far from the column's bulk | *nothing* — pure stats |
| 3. **Time-series (self-history)** | **year-over-year volatility** vs the series' own history | a value that jumps implausibly | ordering (time) |
| 4. **Distributional drift** | PSI, KL-divergence, KS-test vs a reference batch | "this new pull looks different" | a reference |
| 5. **Multivariate** | Isolation Forest, LOF, Mahalanobis, autoencoder error | rows jointly implausible across features | — |
| 6. **Cross-source reconciliation** | compare to an independent source | source-specific errors | a second source |

**The two that need no intuition (rungs 2–3) are the workhorses.** Robust z-score flags "far from the bulk"; year-over-year volatility flags "broke its own pattern." Run on the real data with **zero hand-set ranges**, they caught every corrupted CAR/SSD cell — *and* surfaced Botswana 2022, a jump no human had flagged.

> **Robust z, in one line:** `z = 0.6745 · (x − median) / MAD`, where `MAD = median(|x − median|)`. Uses the median (not the mean) so a few outliers don't poison the yardstick they're measured against.

---

## Part 3 — The false-positive trap (method choice per feature)

> Here's the catch that makes this a *skill*, not a checkbox. When we ran robust-z on **every** column, it flagged **Botswana and Gabon's GDP-per-capita** as anomalies. They're not errors — those are just **genuinely richer countries.**

GDP-per-capita across Sub-Saharan Africa is heavily **right-skewed** (most countries poor, a few much richer). Robust-z assumes a roughly **unimodal** spread, so it treats a legitimately high-income country as an outlier. A **false positive** — and a costly one: it tripped the pipeline's safety halt on good data.

**The rule:** *the method must fit the feature's distribution.*
- **Bounded / unimodal** features (life expectancy, fertility rate) → robust-z is right.
- **Skewed *level* variables** (GDP, income, population) → robust-z false-positives. Use a **log transform first**, or rely on **year-over-year change** (a country's own GDP shouldn't leap 10× — but its *level* being high is fine), or exclude it from population outlier detection.

We also caught **Seychelles' life expectancy of 77** by robust-z — again real, just a high-income outlier in a low-income group. **A detector finds *candidates*; a human or a second source confirms.** Never auto-delete on a flag alone.

**🎯 Say it clearly — "Robust-z flagged your richest country. Is it an anomaly?"** *"Probably not — it's a false positive. Robust-z assumes a unimodal spread, and income is skewed, so a genuinely rich entity looks like an outlier. For skewed level variables, log-transform first or use year-over-year change instead. Statistical flags are candidates to review, not verdicts."*

---

## Part 4 — What to do with a flag: filter vs. halt (the tripwire)

Finding bad data is half the job; the other half is **responding proportionally.**

- **A few bad rows** (isolated source noise) → **filter** them out (treat like missing values) and train on the clean remainder.
- **Many bad rows** (a systemic break — the source changed schema, a join broke) → **halt** the pipeline. Don't quietly train on a broken pull.

The switch between them is a **tripwire**: *halt only if the flagged fraction exceeds a threshold* (e.g. 5%). In the capstone, the gate flagged **7 of 357 country-years (2%)** → filtered them and proceeded. Training on the clean 350 rows, the model's error **dropped from RMSE 3.27 to 2.72** — cleaning the data *improved the model*. That's the payoff: not just safety, but accuracy.

**Where the gate lives:** as early as possible — validate on ingest / before the mart is built, so bad data never propagates downstream. "Shift left."

---

## Part 5 — The production tools (don't hand-roll it)

You built the detectors by hand to *understand* them. In production, use a framework:

- **Great Expectations** — declarative "expectations" (`expect_column_values_to_be_between`, `...to_not_be_null`), with data docs and a validation report. The industry default.
- **Pandera** — lightweight schema + statistical checks for pandas/Polars, great inside Python pipelines.
- **dbt tests** — `not_null`, `unique`, `accepted_values`, `relationships`, plus custom SQL tests, run as part of the transform.
- **Evidently AI** — drift and data-quality monitoring over time, dashboards included (rung 4).

All of them encode the same ladder — you just declare the checks instead of writing the loop.

---

## Quick Reference — say it in plain words
| Question | Plain-English answer |
|---|---|
| **Why validate authoritative data?** | "Because even the World Bank ships real errors. A model trained on them fails silently — the worst failure." |
| **How to catch a bad value with no intuition?** | "Robust z-score (far from the column's bulk) and year-over-year volatility (broke its own pattern). Both are domain-agnostic." |
| **Why not robust-z on everything?** | "It assumes a unimodal spread. On skewed level variables like GDP it false-positives on genuinely rich/poor entities. Log-transform or use relative change instead." |
| **A detector flagged a row — delete it?** | "No. A flag is a candidate, not a verdict. Confirm with a human or an independent source first." |
| **Filter or halt?** | "Filter isolated bad rows; halt if the flagged fraction is large (a tripwire). Proportional response." |
| **Production tools?** | "Great Expectations, Pandera, dbt tests, Evidently — declare the checks instead of coding the loop." |
| **Did cleaning help the model?** | "Yes — dropping 7 corrupted rows cut the error from 3.27 to 2.72. Clean data *is* model performance." |

---
*ML Study 21 — Data Quality & Anomaly Detection. The other half of [ML Study 04](ML_Study_04_Time_Series.html): forecasting predicts the next point; anomaly detection asks whether this one is real.*
