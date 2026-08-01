"""Hello, K-Nearest Neighbors: classify (and predict) by your closest neighbors.

Why this file: KNN is the most intuitive algorithm in ML -- "you are the company
you keep." It does NO training. To label a new country it just finds the K most
SIMILAR countries it already knows, and goes with the crowd.

This mirrors ML_Study_06 on real World Bank data:
  1. Classify   -> guess a country's income group from its 5 nearest neighbors
  2. Scaling    -> prove KNN is broken without feature scaling, fixed with it
  3. Tune K     -> sweep K=1..25, find the error-rate elbow
  4. Regress    -> predict life expectancy by AVERAGING the nearest neighbors

Run:  python3 hands-on/hello_knn.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, r2_score

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
# Human-development signals, on deliberately DIFFERENT scales (fertility ~1-7 vs
# health_spend ~10-10,000) -- so we can show why scaling matters for a distance model.
FEATS = ["life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality", "health_spend_pc"]

print(__doc__.split("Run:")[0].strip())

df = pd.read_csv(DATA)
X, y = df[FEATS], df["income_group"]
Xtr, Xte, ytr, yte, ctr, cte = train_test_split(
    X, y, df["country"], test_size=0.3, random_state=42, stratify=y)

# ---------------------------------------------------------------------------
# 1. CLASSIFY -- who are a country's 5 nearest neighbors, and how do they vote?
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("1. CLASSIFY BY NEIGHBORS  -- 'a country is like the company it keeps'")
print("=" * 72)
scaler = StandardScaler().fit(Xtr)
knn = KNeighborsClassifier(n_neighbors=5).fit(scaler.transform(Xtr), ytr)

# Pick one test country and show WHO its neighbors are (the whole intuition).
i = 3
country = cte.iloc[i]
dist, idx = knn.kneighbors(scaler.transform(Xte.iloc[[i]]), n_neighbors=5)
neigh = pd.DataFrame({"neighbor": ctr.iloc[idx[0]].values,
                      "income_group": ytr.iloc[idx[0]].values,
                      "distance": dist[0].round(2)})
print(f"\nNew country to classify: {country}  (actual: {yte.iloc[i]})")
print("Its 5 nearest neighbors (in scaled feature space):")
print(neigh.to_string(index=False))
vote = neigh["income_group"].value_counts()
print(f"\nMajority vote -> {vote.idxmax()}  ({vote.max()} of 5 neighbors)")
print(f"KNN predicts: {knn.predict(scaler.transform(Xte.iloc[[i]]))[0]}")

# ---------------------------------------------------------------------------
# 2. TUNE K -- small K overfits, large K underfits; find the elbow
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("2. CHOOSING K  -- sweep K and read the error rate")
print("=" * 72)
Xs = StandardScaler().fit_transform(X)
rows = []
for k in range(1, 26):
    acc = cross_val_score(KNeighborsClassifier(n_neighbors=k), Xs, y, cv=5).mean()
    rows.append((k, 1 - acc))
best_k, best_err = min(rows, key=lambda r: r[1])
print("   K :  error rate   (5-fold cross-validation)")
for k, err in rows:
    if k <= 3 or k % 5 == 0 or k == best_k:
        star = "  <-- best" if k == best_k else ""
        print(f"  {k:2} :   {err:.3f}{star}")
print(f"\n  Best K = {best_k}  (error {best_err:.3f}). K=1 overfits (twitchy);")
print("  large K underfits (washes out local detail). The elbow is the sweet spot.")

# ---------------------------------------------------------------------------
# 3. REGRESSION + WHY SCALING MATTERS -- predict life expectancy from neighbors
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("3. KNN REGRESSION + WHY SCALING MATTERS")
print("=" * 72)
# gdp_per_capita (huge, ~300-100,000) sits next to small predictors (fertility ~1-7).
# Here GDP is NOT the strongest signal for life expectancy, so letting it dominate
# the distance HURTS -- and scaling fixes it. (Contrast: for INCOME, the huge $-feature
# IS the definition, so scaling can even look worse -- you can't count on that luck,
# so the rule stands: always scale a distance model.)
RFEATS = ["under5_mortality", "fertility_rate", "internet_pct", "gdp_per_capita"]
Xr, yr = df[RFEATS], df["life_expectancy"]
Xrtr, Xrte, yrtr, yrte, crtr, crte = train_test_split(
    Xr, yr, df["country"], test_size=0.3, random_state=42)

raw_reg = KNeighborsRegressor(n_neighbors=5).fit(Xrtr, yrtr)                       # NO scaling
r2_raw = r2_score(yrte, raw_reg.predict(Xrte))
reg = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5)).fit(Xrtr, yrtr)
r2_scaled = r2_score(yrte, reg.predict(Xrte))
print(f"  feature ranges:  fertility_rate ~1-7   vs   gdp_per_capita ~300-100,000")
print(f"  KNN WITHOUT scaling : R^2 = {r2_raw:.2f}   (GDP swamps the distance)")
print(f"  KNN WITH StandardScaler: R^2 = {r2_scaled:.2f}   (every feature counts fairly)")
print("  --> always scale a distance model. This is the #1 KNN mistake.\n")

j = 0
pred = reg.predict(Xrte.iloc[[j]])[0]
print(f"  Example -- life expectancy = average of the 5 nearest countries:")
print(f"  {crte.iloc[j]}: predicted {pred:.1f} yrs vs actual {yrte.iloc[j]:.1f} yrs")
print("  Classification VOTES; regression AVERAGES -- that's the only difference.")

print("\n" + "=" * 72)
print("TAKEAWAY")
print("=" * 72)
print("  - KNN does no training -- it stores the data and computes distances at predict time.")
print("  - Classify = majority vote of K nearest; regress = average of K nearest.")
print("  - SCALE your features first, always -- distance is meaningless otherwise.")
print("  - K is the bias-variance dial: small overfits, large underfits; sweep to find it.")
print("  - Weak against outliers, imbalance, and high dimensions -- know before you use it.")
