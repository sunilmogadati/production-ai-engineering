# The Production AI Path — Dev → AI Engineer

For experienced engineers crossing from traditional software into AI. Four weeks, foundations to
production — taught from the delivery side, where the through-line is judgment:
**problem → pattern → architecture → the decision you'd defend in production.**

Each item links to a worked study-doc (plain English first, then the math and the code). Read in order,
or jump to what you're shipping this week.

---

## Week 1 — Classical ML foundations (the ground floor)

The models that still run most of production. Learn what each one is *for*, and when it's the right call.

- **The map: Dev → AI Engineer (start here)** — [ML_Study_00](study-docs/ML_Study_00_ML_Foundations.md)
- **Predict a number** — Linear Regression — [01](study-docs/ML_Study_01_Linear_Regression.md)
- **Stop a model from memorizing** — Overfitting, Ridge & Lasso — [02](study-docs/ML_Study_02_Overfitting_Ridge_Lasso.md)
- **Predict yes / no** — Logistic Regression — [03](study-docs/ML_Study_03_Logistic_Regression.md)
- **Forecast over time** — Time Series — [04](study-docs/ML_Study_04_Time_Series.md)
- **Fast text classification** — Naïve Bayes — [05](study-docs/ML_Study_05_Naive_Bayes.md)
- **Predict by nearest example** — KNN — [06](study-docs/ML_Study_06_KNN.md)
- **Decisions you can read** — Decision Trees — [07](study-docs/ML_Study_07_Decision_Trees.md)
- **Combine weak models into a strong one** — Ensembles — [08](study-docs/ML_Study_08_Ensemble_Techniques.md)
- **Find groups without labels** — K-Means — [09](study-docs/ML_Study_09_KMeans_Clustering.md)
- **Density-based clustering** — Hierarchical / DBSCAN — [10](study-docs/ML_Study_10_Hierarchical_DBSCAN_Silhouette.md)
- **The competition winner** — XGBoost — [11](study-docs/ML_Study_11_XGBoost.md)
- **Trust your data before your model** — Data Quality & Anomaly Detection — [21](study-docs/ML_Study_21_Data_Quality_Anomaly_Detection.md)

## Week 2 — Deep learning & modern AI

When a neural net earns its keep — and the ideas underneath today's LLMs.

- **When to reach for a neural net** — Deep Learning — [14](study-docs/ML_Study_14_Deep_Learning.md)
- **See images** — CNNs & computer vision — [15](study-docs/ML_Study_15_CNNs_Computer_Vision.md)
- **Model sequences** — RNNs & LSTMs — [16](study-docs/ML_Study_16_RNN_LSTM_Sequences.md)
- **The idea behind LLMs** — Embeddings & Transformers — [17](study-docs/ML_Study_17_Embeddings_and_Transformers.md)
- **Build it in code** — PyTorch — [18](study-docs/ML_Study_18_PyTorch.md)
- **The whole board** — Modern AI, the big picture — [20](study-docs/ML_Study_20_Modern_AI_Big_Picture.md)

## Week 3 — Applied AI engineering (LLMs, RAG, agents)

Turning a model into a system: retrieval, tools, memory, and the guardrails that keep it honest.

- **Your first agent** — LangChain — [13](study-docs/ML_Study_13_LangChain_Agents.md)
- **Orchestrate agents** — LangGraph — [13a](study-docs/ML_Study_13a_LangGraph.md)
- **Give agents tools** — MCP — [13b](study-docs/ML_Study_13b_MCP.md)
- **Ground answers in your data** — RAG — [13c](study-docs/ML_Study_13c_RAG.md)
- **RAG without a vector DB** — Vectorless RAG — [13d](study-docs/ML_Study_13d_Vectorless_RAG.md)
- **Agents that plan** — Deep Agents — [13e](study-docs/ML_Study_13e_Deep_Agents.md)
- **Codify what the model must never do** — Guardrails — [13f](study-docs/ML_Study_13f_Guardrails.md)
- **Stop shipping on vibes** — Evaluation — [13g](study-docs/ML_Study_13g_LLM_Evaluation.md)
- **One door to every model** — LLM Gateways — [13h](study-docs/ML_Study_13h_LLM_Gateways.md)

## Week 4 — Serving, deployment & the capstone

Make it something a team can run — then prove it on one real system.

- **Turn a notebook into a service** — Serving with FastAPI — [12](study-docs/ML_Study_12_Serving_Models_FastAPI.md)
- **Ship it and run it** — Cloud, MLOps & Security — [19](study-docs/ML_Study_19_Deploying_AI_Cloud_MLOps_Security.md)
- **The capstone** — an end-to-end system on real data, deployed on AWS — [wb-health-monitor](https://github.com/sunilmogadati/wb-health-monitor)

---

*The tools are the easy part now. Which fix is right, and making it hold in production — that's the job.*
