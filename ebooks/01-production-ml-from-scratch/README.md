# eBook 01 — Production ML, From Scratch

**Working title:** *Production Machine Learning, From Scratch*
**Subtitle:** *Classical ML, one algorithm at a time — on real public data, and served as an API.*

This eBook is **assembled from existing study-docs** (`../../study-docs/ML_Study_*`) plus new
connective tissue. It is a packaging effort, not a rewrite: the chapters already exist and are
screen-share-clean; this folder adds the front matter, the ordering, the running example, and the build.

---

## Who it's for
Working software engineers (especially backend/Java) who want to *actually understand* classical
machine learning — not memorize APIs — and see it built and shipped the way production software is built.

## The spine
One dataset threads the whole book: **a world & countries data platform** built on **public data from
international organizations** (World Bank first; framed to extend to IMF / OECD / UN / WHO). Every
algorithm is learned on the same evolving, real dataset, and the book ends by **serving a trained model
as an API** — the bridge from "notebook" to "production."

## Table of contents (chapter → source study-doc + notebook)

| Ch | Title | Source doc | Companion notebook |
|----|-------|-----------|--------------------|
| — | **Introduction** (new) | `00-introduction.md` | — |
| 0 | ML Foundations: the Landscape | `ML_Study_00_ML_Foundations.md` | `World_Bank_Data_Foundations.ipynb`, `hello_worldbank.ipynb` |
| 1 | Linear Regression | `ML_Study_01_Linear_Regression.md` | `Gradient_Descent_From_Scratch_COLAB.ipynb`, `hello_preprocessing_worldbank.ipynb` |
| 2 | Overfitting, and the Fix: Ridge & Lasso | `ML_Study_02_Overfitting_Ridge_Lasso.md` | — |
| 3 | Logistic Regression: the Classifier | `ML_Study_03_Logistic_Regression.md` | `hello_logistic.ipynb` |
| 4 | Time Series: Forecasting the Future | `ML_Study_04_Time_Series.md` | — |
| 5 | Naive Bayes | `ML_Study_05_Naive_Bayes.md` | `hello_naive_bayes.ipynb` |
| 6 | K-Nearest Neighbors | `ML_Study_06_KNN.md` | `hello_knn.ipynb` |
| 7 | Decision Trees | `ML_Study_07_Decision_Trees.md` | `hello_decision_tree.ipynb` |
| 8 | Ensemble Techniques | `ML_Study_08_Ensemble_Techniques.md` | `hello_ensembles.ipynb` |
| 9 | K-Means Clustering | `ML_Study_09_KMeans_Clustering.md` | `hello_kmeans_income.ipynb` |
| 10 | More Clustering: Hierarchical, DBSCAN & Silhouette | `ML_Study_10_Hierarchical_DBSCAN_Silhouette.md` | `hello_clustering_methods.ipynb` |
| 11 | XGBoost: Under the Hood | `ML_Study_11_XGBoost.md` | `hello_xgboost.ipynb` |
| 12 | Data Quality & Anomaly Detection | `ML_Study_21_Data_Quality_Anomaly_Detection.md` | — |
| 13 | Serving a Model: From File to API | `ML_Study_12_Serving_Models_FastAPI.md` | — |

**Note on ordering:** the book renumbers for narrative flow — Study 21 (Data Quality) becomes Ch 12 and
Study 12 (Serving) becomes the closing Ch 13, so the arc reads *landscape → algorithms → clean the data
→ ship it*. Source filenames are unchanged; only the eBook's chapter order differs.

*Deep Learning (Studies 14–18) and LLM Apps & Agents (13/13a/13b, 19, 20) are **eBooks #2 and #3** — out
of scope here. See `../../../production-ai-engineering-instructor/planning/PRODUCT_ROADMAP.md`.*

## Build plan
1. **Introduction** — written (`00-introduction.md`). ✅
2. **Reframe pass** — light edit across the 13 source chapters so the World Bank example reads as the
   broader "world/countries data platform." (Content already WB-based; this is framing, not rework.)
3. **Part intros** (optional, thin) — 3 parts: *Foundations & Regression* (0–2), *Classifiers &
   Clustering* (3–11), *Production* (12–13).
4. **Assemble + build** — concatenate chapters per the TOC and run the existing `study-docs/render.py`
   pipeline (extended to accept a chapter list) → one self-contained HTML, then PDF.
5. **Fence check** — confirm screen-share-clean, no third-party attributions, no client data.

## Definition of done
A single distributable file (HTML + PDF), 14 chapters in order, one consistent running example,
front matter complete, fence-compliant. Distribution (free lead-magnet vs. low-ticket) decided at ship.
