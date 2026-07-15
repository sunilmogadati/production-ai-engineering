"""Hello, model persistence: the model is a FILE.

Why this file: in hello_logistic.py the trained model lived in memory -
when the script ended, it died. Every prediction meant retraining.

Real systems train ONCE, save the model to disk, and load it anywhere:
another script, another server, an API endpoint. The file is the handoff.

Run (needs: pip install -r requirements-ml.txt):

    ./venv/bin/python hello_save_load.py
"""

from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression

# Same 12 examples as hello_logistic.py:
# [buying_keywords, prior_purchases] -> did they buy?
past_customers = [[9, 0], [7, 1], [1, 3], [2, 4], [2, 5], [0, 4],
                  [3, 0], [5, 1], [1, 0], [6, 0], [4, 1], [2, 1]]
bought =         [    1,      1,      1,      1,      1,      1,
                      0,      0,      0,      0,      0,      0]

# --- TRAIN TIME (happens once, occasionally) ---
model = LogisticRegression()
model.fit(past_customers, bought)

Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/hello_model.joblib")
print("Trained and saved to models/hello_model.joblib - the model is now a file.")

del model  # gone from memory. Pretend the training program just exited.

# --- PREDICT TIME (happens anywhere, any time later) ---
loaded = joblib.load("models/hello_model.joblib")
meera = [[1, 3]]  # 1 buying keyword, 3 prior purchases
print(f"Loaded the file. Meera -> {'buys' if loaded.predict(meera)[0] else 'does not buy'}")
print()
print("No retraining. The .joblib file is the handoff between the world")
print("that TRAINS the model and the world that USES it - next: an API.")
