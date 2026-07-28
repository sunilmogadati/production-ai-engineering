"""Hello, logistic regression — the FULL story: predict + evaluate a classifier.

Why this file: hello_logistic.py shows the model in 3 lines. This one shows the
half that matters in production - how you EVALUATE a yes/no model: the confusion
matrix, precision, recall, and F1 (ML_Study_03, Parts 6-9).

The task is the study doc's own example, on real World Bank data:
    "Is this a HIGH-INCOME country?"  (yes / no)
...predicted from DEVELOPMENT indicators alone (life expectancy, electricity,
internet, sanitation, fertility, child mortality) - NOT from income itself.
That gap is what makes it interesting: some countries fool the model.

Pairs with study-docs/ML_Study_03 (Logistic Regression).
Data: World Bank 2021 (bundled offline). 168 countries.

Run (needs pandas + scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_logistic_worldbank.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
# development indicators only - deliberately EXCLUDE gdp/health-spend ($ measures),
# so the model must predict the income TIER from human-development signals.
FEATS = ["life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality"]

print(__doc__.split("Run (")[0].strip())

df = pd.read_csv(DATA)
df["is_high_income"] = (df.income_group == "HIC").astype(int)   # 1 = High-Income, 0 = not

print("\n" + "=" * 72)
print("THE TASK: predict 'High-Income?' (yes/no) from development indicators")
print("=" * 72)
print(f"  {len(df)} countries  |  High-Income: {df.is_high_income.sum()}  |  not: {(df.is_high_income==0).sum()}")

# Split by TIME? No - this is cross-section, so a random split is fine (stratified
# to keep both classes in the test set). Standardize: logistic regression likes it.
X = StandardScaler().fit_transform(df[FEATS])
y = df.is_high_income.values
Xtr, Xte, ytr, yte, idx_tr, idx_te = train_test_split(
    X, y, df.index, test_size=0.30, random_state=42, stratify=y)

model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)   # training = one call
ypred = model.predict(Xte)                                # yes/no on the held-out countries

# ----------------------------------------------------------------------------
# EVALUATE - this is the Part 7-9 material, on real predictions
# ----------------------------------------------------------------------------
tn, fp, fn, tp = confusion_matrix(yte, ypred).ravel()
print("\n" + "=" * 72)
print("THE CONFUSION MATRIX (on the held-out test countries)")
print("=" * 72)
print(f"                          Predicted HIGH   Predicted NOT")
print(f"   Actual HIGH-income        TP = {tp:<3}         FN = {fn:<3}  <- misses")
print(f"   Actual NOT high-income    FP = {fp:<3}         TN = {tn:<3}")
print(f"                             ^ false alarms")

print("\n" + "=" * 72)
print("THE METRICS (why one number is never enough)")
print("=" * 72)
print(f"   Accuracy  = (TP+TN)/all      = {accuracy_score(yte, ypred):.0%}")
print(f"   Precision = TP/(TP+FP)       = {precision_score(yte, ypred):.0%}   of the countries we CALLED high-income, this % really were")
print(f"   Recall    = TP/(TP+FN)       = {recall_score(yte, ypred):.0%}   of the ACTUAL high-income countries, we caught this %")
print(f"   F1        = harmonic mean    = {f1_score(yte, ypred):.0%}   one number, only high if BOTH are")

# ----------------------------------------------------------------------------
# The interesting part: WHO fooled the model?
# ----------------------------------------------------------------------------
te = df.loc[idx_te].copy()
te["pred"] = ypred
misses = te[(te.is_high_income == 1) & (te.pred == 0)]      # false negatives
alarms = te[(te.is_high_income == 0) & (te.pred == 1)]      # false positives
print("\n" + "=" * 72)
print("WHO THE MODEL GOT WRONG (the errors have a story)")
print("=" * 72)
if len(misses):
    print("  MISSED high-income countries (FN) - officially rich, but human-development")
    print("  indicators (life expectancy, internet, sanitation) look mid-tier:")
    for _, r in misses.iterrows():
        print(f"    {r.country:<22} GDP ${r.gdp_per_capita:>8,.0f}")
if len(alarms):
    print("  FALSE ALARMS (FP) - not officially HIC, but development looks it:")
    for _, r in alarms.iterrows():
        print(f"    {r.country:<22} GDP ${r.gdp_per_capita:>8,.0f}")

# a single probability example, like hello_logistic.py
one = te.iloc[0]
prob = model.predict_proba(Xte[0:1])[0][1]
print(f"\n  Example - {one.country}: model says High-Income with probability {prob:.0%} "
      f"({'correct' if (prob>=.5)==bool(one.is_high_income) else 'wrong'})")

print("\n" + "=" * 72)
print("THE TAKEAWAY")
print("=" * 72)
print("  1. Training a classifier is one .fit() call - EVALUATING it is the real skill.")
print("  2. Accuracy alone hides the errors; the confusion matrix shows all four outcomes.")
print("  3. Precision (false alarms) vs recall (misses) - which matters depends on the cost.")
print("  4. The mistakes tell a story: oil/finance economies are rich but 'look' mid-tier.")
print("  5. Real use: this IS how aid is targeted - classify who's poor, then act (Togo, Nature 2022).")
