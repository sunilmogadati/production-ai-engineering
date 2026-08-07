"""Hello, clustering methods: Hierarchical, DBSCAN, and the silhouette score.

Why this file: K-Means (Study 09) is fast but forces round clusters, makes you
pick K, and drags outliers into a group. This shows the tools that fix each:
  - SILHOUETTE  -> validate ANY clustering (no labels needed)
  - HIERARCHICAL-> merge into a tree; choose K after
  - DBSCAN      -> density clusters, arbitrary shapes, flags outliers as noise

Mirrors ML_Study_10:
  1. Silhouette sweep  -> pick K on World Bank data, cross-check the elbow
  2. K-Means vs Hierarchical -> same data, compare silhouettes
  3. DBSCAN finds outliers   -> the 'noise' countries K-Means would force into a tier
  4. Shape demo (two moons)  -> DBSCAN cleanly beats K-Means (silhouette proves it)

Run:  python3 hands-on/hello_clustering_methods.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_moons

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_indicators_2021.csv")
FEATS = ["gdp_per_capita", "life_expectancy", "electricity_pct", "basic_water_pct",
         "internet_pct", "fertility_rate", "under5_mortality", "health_spend_pc"]

print(__doc__.split("Run:")[0].strip())
df = pd.read_csv(DATA)
X = StandardScaler().fit_transform(df[FEATS])   # scale first -- distance-based

# ---------------------------------------------------------------------------
# 1. SILHOUETTE SWEEP + ELBOW  -- validate & pick K (no labels)
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("1. VALIDATE CLUSTERING: silhouette sweep vs the elbow (WB data)")
print("=" * 72)
print("   K :  silhouette   WCSS(elbow)")
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    sil = silhouette_score(X, km.labels_)
    print(f"  {k}  :   {sil:.3f}      {km.inertia_:8.1f}")
print("  silhouette runs -1..+1 (higher = cleaner). WCSS falls (elbow = the bend).")
print("  no labels here -- these REPLACE accuracy for clustering.")
print("  NOTE: on this data silhouette peaks at K=2 (the cleanest rich/poor split);")
print("  more clusters (K=4 income tiers) capture finer structure at a lower score.")
print("  Silhouette rewards clean SEPARATION -- which often means FEWER clusters.")

# ---------------------------------------------------------------------------
# 2. K-MEANS vs HIERARCHICAL  -- same data, compare silhouettes
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("2. K-MEANS vs HIERARCHICAL  (K=4, silhouette)")
print("=" * 72)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)
hc = AgglomerativeClustering(n_clusters=4).fit(X)
print(f"  K-Means      silhouette = {silhouette_score(X, km.labels_):.3f}  (fast; scales to big data)")
print(f"  Hierarchical silhouette = {silhouette_score(X, hc.labels_):.3f}  (slow; but gives a dendrogram, no K up front)")

# ---------------------------------------------------------------------------
# 3. DBSCAN FINDS OUTLIERS  -- the 'noise' countries K-Means can't isolate
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("3. DBSCAN  -- density clusters + outliers labelled as NOISE")
print("=" * 72)
db = DBSCAN(eps=1.3, min_samples=4).fit(X)
labels = db.labels_
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
noise = df["country"][labels == -1].tolist()
print(f"  found {n_clusters} dense cluster(s), and {len(noise)} NOISE countries (outliers):")
print("   ", ", ".join(noise))
print("  Honest read: this data is one CONTINUOUS development gradient (not separated")
print("  blobs), so DBSCAN finds one main cluster -- its value here is isolating the")
print("  OUTLIERS as noise. K-Means would have forced every one of these into a tier.")

# ---------------------------------------------------------------------------
# 4. SHAPE DEMO  -- two crescents where DBSCAN beats K-Means
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("4. SHAPE DEMO: two interleaving crescents (silhouette on the TRUE labels)")
print("=" * 72)
Xm, ym = make_moons(n_samples=300, noise=0.06, random_state=0)
km_m = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(Xm)
db_m = DBSCAN(eps=0.2, min_samples=5).fit_predict(Xm)
# agreement with the true crescent labels (Adjusted Rand-free: simple accuracy up to label swap)
def agree(pred, true):
    a = (pred == true).mean()
    return max(a, 1 - a)      # clusters are unlabeled, so allow the swap
print(f"  K-Means matches the true crescents: {agree(km_m, ym):.0%}  (straight cut splits them wrong)")
mask = db_m != -1
print(f"  DBSCAN  matches the true crescents: {agree(db_m[mask], ym[mask]):.0%}  (follows density -> recovers both)")
print(f"  (DBSCAN also flagged {int((db_m==-1).sum())} points as noise.)")

print("\n" + "=" * 72)
print("TAKEAWAY")
print("=" * 72)
print("  - No labels? Validate clustering with the SILHOUETTE score (-1..+1, higher better).")
print("  - HIERARCHICAL: merge into a dendrogram, choose K by cutting it; slow on big data.")
print("  - DBSCAN: density clusters -> arbitrary SHAPES + isolates OUTLIERS as noise.")
print("  - K-Means for scale; hierarchical for the tree; DBSCAN for shapes and noise.")
