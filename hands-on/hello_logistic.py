"""Hello, logistic regression: learn yes/no from examples.

Why this file: instead of writing the rule, we show the machine examples
of what happened, and IT finds the pattern. This is all "training" means.

Same objective features as hello_rules.py:
- buying_keywords: buying words counted in the call transcript
- prior_purchases: completed orders, from order history

Watch Meera: hello_rules.py called her cold. The model gets her right,
because the examples taught it that loyal customers buy.

Run (needs: pip install -r requirements-ml.txt):

    ./venv/bin/python hello_logistic.py
"""

from sklearn.linear_model import LogisticRegression

# Each example: [buying_keywords, prior_purchases] -> did they buy? (1 = yes)
past_customers = [[9, 0], [7, 1], [1, 3], [2, 4], [2, 5], [0, 4],
                  [3, 0], [5, 1], [1, 0], [6, 0], [4, 1], [2, 1]]
bought =         [    1,      1,      1,      1,      1,      1,
                      0,      0,      0,      0,      0,      0]

model = LogisticRegression()
model.fit(past_customers, bought)  # <- this is "training". That is it.

# Meera: barely said a buying word (1), but 3 prior purchases.
meera = [[1, 3]]
prediction = model.predict(meera)[0]
probability = model.predict_proba(meera)[0][1]

print(f"Meera -> will she buy? {'YES' if prediction == 1 else 'no'} "
      f"(probability {probability:.0%})")
print()
print("Nobody wrote a threshold. Nobody wrote an elif.")
print("The model learned from 12 examples that loyalty predicts buying.")
print("This is classification: the answer is yes or no.")
