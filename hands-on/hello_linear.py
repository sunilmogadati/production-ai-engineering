"""Hello, linear regression: learn a NUMBER from examples.

Why this file: classification answers yes/no. But the business also asks
"how much?" - and we don't know the formula. The model finds it.

Run (needs: pip install -r requirements-ml.txt):

    ./venv/bin/python hello_linear.py
"""

from sklearn.linear_model import LinearRegression

# Past orders: [budget] -> what the customer actually spent
budgets = [[50], [80], [120], [160], [200], [240]]
spent =   [ 140,  205,   300,   390,   475,   570]

model = LinearRegression()
model.fit(budgets, spent)  # training, again: just "look at the examples"

new_budget = [[100]]
predicted = model.predict(new_budget)[0]

print(f"A customer with a $100 budget will spend about ${predicted:.0f}")
print()
print(f"The formula the model discovered: spend = "
      f"{model.coef_[0]:.2f} * budget + {model.intercept_:.2f}")
print()
print("We never told it that formula - it found the line through the examples.")
print("This is regression: the answer is a number, not a yes/no.")
