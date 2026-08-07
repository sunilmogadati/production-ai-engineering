"""Hello, Ensembles: many models beat one.

Why this file: every algorithm so far used ONE model. Ensembles combine MANY --
and that's why Random Forest and boosting win on tabular data. Two families:
  - BAGGING  (parallel, vote/average)  -> Random Forest
  - BOOSTING (sequential, fix the last one's mistakes) -> AdaBoost, Gradient Boosting

Mirrors ML_Study_08 on real World Bank data:
  1. One tree vs the ensembles  -> RF / AdaBoost / GradientBoosting on held-out data
  2. Bagging cuts variance       -> the single tree's train>>test gap vs the forest's
  3. Random Forest regressor     -> predict life expectancy + feature importances
  4. No scaling needed for trees -> same score scaled or not (contrast KNN)

Run:  python3 hands-on/hello_ensembles.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                              AdaBoostClassifier, GradientBoostingClassifier)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
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
# 1. ONE TREE vs THE ENSEMBLES  (held-out test accuracy)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("1. ONE MODEL vs MANY  (held-out test accuracy)")
print("=" * 72)
models = {
    "Single decision tree (overfits)": DecisionTreeClassifier(random_state=0),
    "Random Forest  (BAGGING, 200)  ": RandomForestClassifier(n_estimators=200, random_state=0),
    "AdaBoost       (BOOSTING, stumps)": AdaBoostClassifier(n_estimators=200, random_state=0),
    "Gradient Boosting (BOOSTING)    ": GradientBoostingClassifier(random_state=0),
}
for name, m in models.items():
    m.fit(Xtr, ytr)
    print(f"  {name}: {accuracy_score(yte, m.predict(Xte)):.0%}")
print("  --> Random Forest & Gradient Boosting clearly beat the lone tree.")
print("      AdaBoost UNDERperforms here -- an honest lesson: an ensemble isn't")
print("      automatically better. AdaBoost's shallow STUMPS are built for BINARY")
print("      problems and struggle on this 4-class task. Base learner + problem matter.")

# ---------------------------------------------------------------------------
# 2. BAGGING CUTS VARIANCE  (train vs test gap)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("2. BAGGING CUTS VARIANCE  (train vs test -- the overfitting gap)")
print("=" * 72)
tree = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)
forest = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
print(f"  Single tree : train {accuracy_score(ytr,tree.predict(Xtr)):.0%}"
      f"  test {accuracy_score(yte,tree.predict(Xte)):.0%}   <- big gap = HIGH variance")
print(f"  Random Forest: train {accuracy_score(ytr,forest.predict(Xtr)):.0%}"
      f"  test {accuracy_score(yte,forest.predict(Xte)):.0%}   <- gap closed = LOW variance")
print("  same low bias, but voting many trees averaged the variance away.")

# ---------------------------------------------------------------------------
# 3. RANDOM FOREST REGRESSOR + feature importances
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("3. RANDOM FOREST REGRESSOR  -- predict life expectancy")
print("=" * 72)
RF = ["electricity_pct", "basic_water_pct", "internet_pct", "fertility_rate", "under5_mortality"]
Xr, yr = df[RF], df["life_expectancy"]
Xrtr, Xrte, yrtr, yrte = train_test_split(Xr, yr, test_size=0.3, random_state=42)
reg = RandomForestRegressor(n_estimators=200, random_state=0).fit(Xrtr, yrtr)
print(f"  R^2 on held-out countries = {r2_score(yrte, reg.predict(Xrte)):.2f}")
imp = sorted(zip(RF, reg.feature_importances_), key=lambda t: -t[1])
print("  feature importances (which indicators the forest leans on):")
for f, v in imp:
    print(f"    {f:20} {v:.3f}")

# ---------------------------------------------------------------------------
# 4. NO SCALING NEEDED FOR TREES  (contrast KNN, which needs it)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("4. TREES NEED NO FEATURE SCALING  (a common interview question)")
print("=" * 72)
raw = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
scaled = make_pipeline(StandardScaler(),
                       RandomForestClassifier(n_estimators=200, random_state=0)).fit(Xtr, ytr)
print(f"  Random Forest, RAW features   : {accuracy_score(yte, raw.predict(Xte)):.0%}")
print(f"  Random Forest, SCALED features: {accuracy_score(yte, scaled.predict(Xte)):.0%}")
print("  ~same: trees split by threshold, so rescaling doesn't change the split.")
print("  (KNN, by contrast, is distance-based and REQUIRES scaling -- Study 06.)")

print("\n" + "=" * 72)
print("TAKEAWAY")
print("=" * 72)
print("  - Ensembles combine MANY models and beat any single one.")
print("  - BAGGING (Random Forest): parallel trees, vote/average -> cuts variance.")
print("  - BOOSTING (AdaBoost/GradientBoosting): sequential weak learners fix the")
print("    last one's mistakes -> cuts bias, usually the highest score (tune it).")
print("  - Trees/forests need NO scaling and shrug off outliers; KNN needs both.")
print("  - On tabular data, start with Random Forest; reach for XGBoost to win.")
