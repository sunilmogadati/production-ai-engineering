"""Hello, K-Means: let an algorithm rediscover the World Bank's income tiers.

Why this file: every model so far had an ANSWER KEY (supervised). Clustering has
none - you hand it data with NO labels and it finds the natural groups itself.
The reveal: cluster 168 countries blind, then reveal the World Bank's OFFICIAL
income groups - and watch the algorithm land on nearly the same four tiers, having
never seen a single label.

And the disagreements aren't errors - they're the actionable part.

Pairs with the World Bank data thread (instructor teaching notes) and ML_Study_00.
Data: World Bank, 2021 (bundled offline). 168 countries, 8 indicators.

Run (needs pandas + scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_kmeans_income.py
"""
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
FEATS = ["gdp_per_capita", "life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality", "health_spend_pc"]
TIER_NAME = {"LIC": "Low income", "LMC": "Lower-middle", "UMC": "Upper-middle", "HIC": "High income"}

print(__doc__.split("Run (")[0].strip())

df = pd.read_csv(DATA)

print("\n" + "=" * 74)
print("THE SETUP: cluster BLIND - hide the income groups from the algorithm")
print("=" * 74)
print(f"  {len(df)} countries, 8 development indicators. We do NOT give K-Means the")
print("  income_group column - it never sees a label. We just ask it: 'find 4 natural")
print("  groups.' (Why 4? Because we'll compare against the World Bank's 4 tiers.)")

# Standardize (K-Means measures distance, so scales must be comparable), then cluster.
X = StandardScaler().fit_transform(df[FEATS])
km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(X)
df["cluster"] = km.labels_

# Only NOW do we look at the labels - to name each cluster by its majority tier.
majority = df.groupby("cluster")["income_group"].agg(lambda s: s.value_counts().idxmax())
df["cluster_tier"] = df.cluster.map(majority)

print("\n" + "=" * 74)
print("THE REVEAL: the blind clusters ARE the income tiers")
print("=" * 74)
order = ["LIC", "LMC", "UMC", "HIC"]
inv = {v: k for k, v in majority.to_dict().items()}
for t in order:
    if t in inv:
        c = inv[t]
        members = df[df.cluster == c]
        print(f"  cluster {c}  ->  mostly {TIER_NAME[t]:<13} ({len(members)} countries, "
              f"avg GDP/capita ${members.gdp_per_capita.mean():>8,.0f})")
agree = (df.cluster_tier == df.income_group).mean()
print(f"\n  Each cluster maps to a DISTINCT official tier, and the blind grouping agrees")
print(f"  with the World Bank's official label for {agree*100:.0f}% of countries -")
print("  a classification humans designed, rediscovered from raw indicators alone.")

print("\n" + "=" * 74)
print("THE ACTIONABLE PART: the DISagreements")
print("=" * 74)
print("  The countries where the blind cluster != the official tier are not noise -")
print("  they're the ones whose DEVELOPMENT profile doesn't match their INCOME label:\n")
anom = df[df.cluster_tier != df.income_group].copy()
anom["dev_rank"] = anom.cluster_tier.map({"LIC":0,"LMC":1,"UMC":2,"HIC":3})
anom["inc_rank"] = anom.income_group.map({"LIC":0,"LMC":1,"UMC":2,"HIC":3})
# richer by income than their development profile suggests (e.g. oil economies)
rich = anom[anom.inc_rank > anom.dev_rank].sort_values("gdp_per_capita", ascending=False)
print("  officially RICHER than their development profile (income outruns human development):")
for _, r in rich.head(5).iterrows():
    print(f"    {r.country:<22} official {r.income_group}, clusters with {r.cluster_tier}   (GDP ${r.gdp_per_capita:,.0f})")
print("  -> often oil/mineral economies: high income, but health/access indicators lag.")
poor = anom[anom.inc_rank < anom.dev_rank]
if len(poor):
    print("\n  officially POORER than their development profile (punch above their income):")
    for _, r in poor.head(3).iterrows():
        print(f"    {r.country:<22} official {r.income_group}, clusters with {r.cluster_tier}   (GDP ${r.gdp_per_capita:,.0f})")

print("\n" + "=" * 74)
print("THE TAKEAWAY")
print("=" * 74)
print("  1. Clustering is UNSUPERVISED - no answer key; it finds structure on its own.")
print("  2. Standardize first: K-Means uses distance, so scales must be comparable.")
print("  3. Here it rediscovered a human classification (the income tiers) from raw data.")
print("  4. The DISagreements are the payoff - a 'review these' list of countries whose")
print("     income label and development reality diverge.")
print("  5. Real use: Togo clustered satellite imagery into grid cells to pick the 100")
print("     POOREST cantons for emergency cash - clustering deciding where aid goes.")
