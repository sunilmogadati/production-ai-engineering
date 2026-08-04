"""Hello, Decision Trees: the one model you can actually read.

Why this file: a decision tree is a nested if/else the MACHINE builds itself -
a flowchart of yes/no questions. Unlike KNN or linear models, you can print it
out and read exactly why it decided what it decided.

Mirrors ML_Study_07 on real World Bank data:
  1. Classify income group  -> and PRINT the tree's rules (the readable flowchart)
  2. Entropy vs Gini         -> compute both on a node by hand, confirm vs sklearn
  3. Overfit -> prune        -> unbounded tree memorizes; max_depth closes the gap
  4. Regressor               -> predict life expectancy; leaf = mean of its rows
  5. One tree vs a forest    -> a Random Forest beats the single tree on held-out data

Run:  python3 hands-on/hello_decision_tree.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, r2_score

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
FEATS = ["life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality", "health_spend_pc"]

print(__doc__.split("Run:")[0].strip())
df = pd.read_csv(DATA)
X, y = df[FEATS], df["income_group"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# ---------------------------------------------------------------------------
# 1. CLASSIFY + PRINT THE RULES  -- a tree IS a flowchart you can read
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("1. A READABLE MODEL  -- the tree's actual if/else rules (max_depth=3)")
print("=" * 72)
clf = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)
print(export_text(clf, feature_names=FEATS).rstrip())
print(f"\n  test accuracy = {accuracy_score(yte, clf.predict(Xte)):.0%}")
print("  ^ no other model lets you read the decision path like this.")

# ---------------------------------------------------------------------------
# 2. ENTROPY vs GINI  -- measure a node's 'mixed-ness' two ways
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("2. PURITY: ENTROPY vs GINI  (by hand, then confirm the idea)")
print("=" * 72)
def entropy(pos, neg):
    tot = pos + neg
    ps = [c / tot for c in (pos, neg) if c > 0]
    return abs(-sum(p * np.log2(p) for p in ps))   # abs() avoids a cosmetic -0.000
def gini(pos, neg):
    tot = pos + neg
    return 1 - sum((c / tot) ** 2 for c in (pos, neg))
for label, pos, neg in [("pure   (4 Yes, 0 No)", 4, 0),
                        ("mixed  (3 Yes, 3 No)", 3, 3),
                        ("skewed (7 Yes, 2 No)", 7, 2)]:
    print(f"  {label}:  entropy = {entropy(pos,neg):.3f}   gini = {gini(pos,neg):.3f}")
print("  entropy runs 0->1, gini runs 0->0.5; both are 0 when pure. Gini is faster (no log).")

# ---------------------------------------------------------------------------
# 3. OVERFIT -> PRUNE  -- an unbounded tree memorizes the training data
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("3. OVERFITTING & PRUNING  -- max_depth is the tree's bias-variance dial")
print("=" * 72)
full = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)             # no limit
print(f"  Unbounded tree : train {accuracy_score(ytr, full.predict(Xtr)):.0%}"
      f"  vs  test {accuracy_score(yte, full.predict(Xte)):.0%}   <- big gap = overfit")
for d in (2, 3, 5):
    p = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
    print(f"  max_depth={d}     : train {accuracy_score(ytr,p.predict(Xtr)):.0%}"
          f"  vs  test {accuracy_score(yte,p.predict(Xte)):.0%}")
print("  pruning (a shallower tree) sacrifices train accuracy to GENERALIZE better.")

# ---------------------------------------------------------------------------
# 4. REGRESSOR  -- leaf outputs the MEAN; splits judged by MSE
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("4. DECISION TREE REGRESSOR  -- predict life expectancy (leaf = mean)")
print("=" * 72)
RF = ["electricity_pct", "basic_water_pct", "internet_pct", "fertility_rate", "under5_mortality"]
Xr, yr = df[RF], df["life_expectancy"]
Xrtr, Xrte, yrtr, yrte = train_test_split(Xr, yr, test_size=0.3, random_state=42)
reg = DecisionTreeRegressor(max_depth=3, random_state=0).fit(Xrtr, yrtr)
print(f"  R^2 on held-out countries = {r2_score(yrte, reg.predict(Xrte)):.2f}")
print("  the prediction for any country = the AVERAGE life expectancy of the")
print("  training countries that land in the same leaf. (Classifier votes; regressor averages.)")

# ---------------------------------------------------------------------------
# 5. ONE TREE vs A FOREST  -- many varied trees vote -> steadier
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("5. ONE TREE vs A RANDOM FOREST  (held-out test set)")
print("=" * 72)
one_tree = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)             # the naive single (overfit) tree
forest = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
print(f"  single (unpruned) tree : test accuracy = {accuracy_score(yte, one_tree.predict(Xte)):.0%}"
      f"   <- overfit (was 100% on train)")
print(f"  random forest (200)    : test accuracy = {accuracy_score(yte, forest.predict(Xte)):.0%}"
      f"   <- many varied trees vote -> errors cancel")
print("  the forest recovers the accuracy the single overfit tree lost. You trade")
print("  the single tree's readability for a real jump in accuracy and stability.")

print("\n" + "=" * 72)
print("TAKEAWAY")
print("=" * 72)
print("  - A tree is a nested if/else the machine builds -- and you can READ it.")
print("  - It splits on the feature with the highest INFORMATION GAIN (purest children).")
print("  - Purity = entropy (0-1) or gini (0-0.5); gini is the faster default.")
print("  - Regressor: leaf = mean, splits judged by MSE instead of gini/entropy.")
print("  - One tree overfits -> prune it (max_depth) or grow a RANDOM FOREST.")
