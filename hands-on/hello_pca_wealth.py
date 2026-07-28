"""Hello, PCA: squeeze 8 development indicators into ONE wealth score.

Why this file: sometimes you have many correlated columns (GDP, life expectancy,
electricity, internet, ...) and want a SINGLE number that ranks countries by
wealth - with no "income" column to lean on. PCA does exactly that, and it's not
a toy: this is literally how the Demographic and Health Surveys (DHS) Wealth Index
is built and used to target aid across 90+ countries.

Pairs with the World Bank data thread (instructor teaching notes) and ML_Study_00.
Data: World Bank, 2021 (bundled offline). 168 countries, 8 indicators.

Run (needs pandas + scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_pca_wealth.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
FEATS = ["gdp_per_capita", "life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality", "health_spend_pc"]

print(__doc__.split("Run (")[0].strip())

df = pd.read_csv(DATA)

print("\n" + "=" * 74)
print("THE PROBLEM: 8 columns, and we want ONE wealth number per country")
print("=" * 74)
print(f"  {len(df)} countries, each with these 8 indicators:")
print("   ", ", ".join(FEATS))
print("  They're all correlated (rich countries score high on most). Can we collapse")
print("  them into a single 'wealth axis' without just picking GDP and ignoring the rest?")

# ----------------------------------------------------------------------------
# Standardize first - PCA is scale-sensitive. GDP is in thousands, fertility is
# ~1-7; without scaling, GDP's big numbers would drown everything else out.
# ----------------------------------------------------------------------------
X = StandardScaler().fit_transform(df[FEATS])

# PCA: find the single direction that captures the most variation across all 8.
pca = PCA().fit(X)
pc1 = pca.transform(X)[:, 0]

# PCA's sign is arbitrary; orient it so HIGHER = WEALTHIER (align with GDP).
if np.corrcoef(pc1, df.gdp_per_capita)[0, 1] < 0:
    pc1 = -pc1
    loadings = -pca.components_[0]
else:
    loadings = pca.components_[0]
df["wealth_score"] = pc1

print("\n" + "=" * 74)
print("PCA: one direction that captures the most information")
print("=" * 74)
print(f"  PC1 alone explains {pca.explained_variance_ratio_[0]*100:.0f}% of ALL the variation across 8 indicators.")
print(f"  (PC1 + PC2 together: {pca.explained_variance_ratio_[:2].sum()*100:.0f}%.)")
print("  So a SINGLE number keeps most of what the 8 columns were telling us.")

print("\n  What the wealth axis is made of (PC1 loadings - which way each indicator points):")
for f, w in sorted(zip(FEATS, loadings), key=lambda t: -t[1]):
    bar = ("+" if w >= 0 else "-") * max(1, int(abs(w) * 20))
    print(f"    {f:<18} {w:+.2f}  {bar}")
print("  Reads exactly like 'development': electricity/internet/life-expectancy push")
print("  wealth UP; fertility and child mortality push it DOWN. PCA found that unaided.")

# ----------------------------------------------------------------------------
# The score ranks countries.
# ----------------------------------------------------------------------------
ranked = df.sort_values("wealth_score", ascending=False)
print("\n" + "=" * 74)
print("THE RESULT: one score, and it ranks the world")
print("=" * 74)
print("  richest by our PCA score:")
for _, r in ranked.head(5).iterrows():
    print(f"    {r.country:<20} score {r.wealth_score:+.2f}   ({r.income_group})")
print("  poorest by our PCA score:")
for _, r in ranked.tail(5).iterrows():
    print(f"    {r.country:<20} score {r.wealth_score:+.2f}   ({r.income_group})")

# Does the score agree with the World Bank's OFFICIAL income tiers?
rank = {"LIC": 0, "LMC": 1, "UMC": 2, "HIC": 3}
corr = abs(np.corrcoef(df.wealth_score, df.income_group.map(rank))[0, 1])
print(f"\n  Our PCA score's correlation with the OFFICIAL income tiers: {corr:.2f}")
print("  We never showed PCA the income groups - it reconstructed the wealth ordering")
print("  from the raw indicators alone.")

print("\n" + "=" * 74)
print("THE REVEAL: this is a real tool, doing a real job")
print("=" * 74)
print("  8 messy indicators -> 1 clean wealth score that ranks every country, with NO")
print("  income figure required. That last part is the whole point: in the poorest")
print("  countries you often CAN'T measure income - but you CAN ask 'do you own a")
print("  fridge / have electricity / piped water?'")
print()
print("  This IS the DHS Wealth Index: PCA on household assets (Filmer & Pritchett,")
print("  late 1990s), now the standard wealth measure across 90+ countries' health")
print("  surveys - used to decide who gets targeted by health and social programs.")

print("\n" + "=" * 74)
print("THE TAKEAWAY")
print("=" * 74)
print("  1. PCA collapses many correlated columns into a few that keep most of the info.")
print("  2. ALWAYS standardize first - PCA is scale-sensitive.")
print("  3. PC1's loadings are interpretable - here it's literally a 'development axis'.")
print("  4. The sign is arbitrary; orient it so higher = the direction you care about.")
print("  5. Real use: the DHS Wealth Index ranks households for aid targeting this exact way.")
