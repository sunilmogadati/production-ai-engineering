"""Hello, decision tree: the machine writes the elifs.

Why this file: the bridge between Session 3's two worlds.
A decision tree IS a rule engine - but the machine wrote the rules
by learning them from examples, instead of a developer guessing.

Same 12 examples as hello_logistic.py. Look at what it prints:
readable rules - and the FIRST split it chose is prior_purchases,
the signal our hand-written rule in hello_rules.py never looked at.

Run (needs: pip install -r requirements-ml.txt):

    ./venv/bin/python hello_tree.py
"""

from sklearn.tree import DecisionTreeClassifier, export_text

# Each example: [buying_keywords, prior_purchases] -> did they buy? (1 = yes)
past_customers = [[9, 0], [7, 1], [1, 3], [2, 4], [2, 5], [0, 4],
                  [3, 0], [5, 1], [1, 0], [6, 0], [4, 1], [2, 1]]
bought =         [    1,      1,      1,      1,      1,      1,
                      0,      0,      0,      0,      0,      0]

model = DecisionTreeClassifier(max_depth=2, random_state=42)
model.fit(past_customers, bought)

print("The rules the machine wrote (read top to bottom, like elifs):")
print(export_text(model, feature_names=["buying_keywords", "prior_purchases"]))

meera = [[1, 3]]
prediction = model.predict(meera)[0]
print(f"Meera (1 buying keyword, 3 prior purchases) -> {'buys' if prediction else 'does not buy'}")
print()
print("It chose prior_purchases as its FIRST question, all by itself.")
print("Our hand-written rule in hello_rules.py never looked at loyalty -")
print("the tree learned that it is the strongest signal in the data.")
