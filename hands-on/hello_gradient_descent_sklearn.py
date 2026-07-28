"""Hello, gradient descent - the scikit-learn version (and a surprise).

Why this file: hello_gradient_descent.py did every step by hand - 100+ lines to
learn two numbers. Here's the same answer in two lines. But there's a twist worth
knowing, and most courses skip it:

    the .fit() you're about to call does NOT use gradient descent.

Run it AFTER hello_gradient_descent.py, so you know what's being hidden from you.
Pairs with study-docs/ML_Study_01 (sections 3.4 - 3.7).

Run (needs scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_gradient_descent_sklearn.py
"""

import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor

# ============================================================================
# THE SAME FOUR WEEKS - identical data to the by-hand version
# ============================================================================

# Ad spend per week, in $1,000s. scikit-learn wants the inputs shaped as a
# grid (one row per example, one column per feature) - hence the double brackets.
X = np.array([[1], [2], [3], [4]])

# Weekly sales in $1,000s. The answers. These stay a simple flat list.
y = np.array([5, 7, 8, 11])

# The truth we're checking everyone against (proved by algebra in the study doc).
TRUE_THETA0, TRUE_THETA1 = 3.0, 1.9


print(__doc__.split("Run (needs")[0].strip())

# ============================================================================
# WAY 1 - LinearRegression: the two-liner everyone reaches for
# ============================================================================
print("\n" + "=" * 78)
print("WAY 1: LinearRegression - the two lines that replace our 100")
print("=" * 78)

# Create the model. No settings, no learning rate, no iteration count. Nothing.
model = LinearRegression()

# Learn from the examples. This one call replaces our entire hand-written loop.
model.fit(X, y)

# Pull out the two knobs it found. Same two numbers we spent 1,035 rounds hunting.
print(f"  theta0 (starting value) : {model.intercept_:.4f}")
print(f"  theta1 (rate/slope)     : {model.coef_[0]:.4f}")
print(f"  the line               : sales = {model.intercept_:.2f} + {model.coef_[0]:.2f} * spend")

# Ask it to predict a week we never showed it: what if we spend $2,500?
print(f"\n  Predict $2.5k of ad spend -> ${model.predict([[2.5]])[0]:.2f}k in sales")

print("\n  Two lines. Same answer. So why did we write 100 lines by hand?")
print("  Because of what just happened underneath - which is NOT what you think.")

# ============================================================================
# THE SURPRISE - .fit() didn't walk downhill at all
# ============================================================================
print("\n" + "=" * 78)
print("THE SURPRISE: LinearRegression does NOT use gradient descent")
print("=" * 78)

# Notice how exact that answer was. Suspiciously exact.
print(f"  It found theta0 = {model.intercept_:.10f}")
print(f"           theta1 = {model.coef_[0]:.10f}")
print(f"  The true answer:  {TRUE_THETA0} and {TRUE_THETA1}")
print()
print("  That is EXACT - not 2.9991, not 1.9003. Exact to ten decimal places.")
print("  No amount of walking downhill lands on a number that cleanly.")
print()
print("  Here's why: LinearRegression doesn't iterate at all. It solves the")
print("  algebra directly - the same closed_form() formula we wrote by hand.")
print("  There's no loop, no learning rate, no convergence. It's one calculation.")
print()
print("  So when a tutorial says '.fit() runs gradient descent' - for THIS model,")
print("  that's simply false. Linear regression is one of the rare problems easy")
print("  enough to solve exactly, so scikit-learn does the smart thing and cheats.")

# ============================================================================
# WAY 2 - SGDRegressor: the one that ACTUALLY does gradient descent
# ============================================================================
print("\n" + "=" * 78)
print("WAY 2: SGDRegressor - this one really does walk downhill")
print("=" * 78)

# SGD = Stochastic Gradient Descent. This model genuinely takes steps downhill,
# exactly like our hand-written loop - but using ONE random row per step
# instead of all four (that's what the "stochastic" means).
sgd = SGDRegressor(
    learning_rate="constant",  # keep the step size fixed, like our ALPHA
    eta0=0.01,                 # <- this IS our ALPHA. "eta" is the Greek letter.
    max_iter=1000,             # <- this IS our MAX_ITERS (the safety cap)
    tol=None,                  # <- our TOLERANCE. None = "never stop early, use the cap"
    penalty=None,              # turn off extras we haven't learned yet (Ridge/Lasso)
    random_state=0,            # fix the randomness so you get the same numbers I did
)

# Same call, same data - but a completely different engine underneath.
sgd.fit(X, y)

print(f"  theta0 : {sgd.intercept_[0]:.4f}   (true answer: {TRUE_THETA0})")
print(f"  theta1 : {sgd.coef_[0]:.4f}   (true answer: {TRUE_THETA1})")
print()
print("  Close - but NOT exact. It walked, so it only got near. Just like ours did.")

# Now the interesting bit: throw 50x more iterations at it and see if that fixes it.
sgd_more = SGDRegressor(learning_rate="constant", eta0=0.01, max_iter=50000,
                        tol=None, penalty=None, random_state=0).fit(X, y)

print(f"\n  Now with 50x more steps (max_iter=50,000):")
print(f"  theta0 : {sgd_more.intercept_[0]:.4f}")
print(f"  theta1 : {sgd_more.coef_[0]:.4f}")
print()
print("  Barely better! 50x the work bought almost nothing. Why?")
print("  Because SGD looks at ONE random row per step, so its slope reading is")
print("  always a bit wrong. It doesn't settle at the bottom - it jitters around")
print("  it forever. More steps = more jittering, not more accuracy.")

# The actual fix isn't more steps - it's smaller steps.
sgd_fine = SGDRegressor(learning_rate="constant", eta0=0.001, max_iter=100000,
                        tol=None, penalty=None, random_state=0).fit(X, y)
print(f"\n  The real fix is a SMALLER step (eta0=0.001), not more steps:")
print(f"  theta0 : {sgd_fine.intercept_[0]:.4f}   theta1 : {sgd_fine.coef_[0]:.4f}")
print("  Tighter jitter -> closer to the bottom. That's the learning rate at work.")

# ============================================================================
# THE SCOREBOARD
# ============================================================================
print("\n" + "=" * 78)
print("SCOREBOARD: three ways to find the same two numbers")
print("=" * 78)
print(f"  {'method':<34} {'theta0':>9} {'theta1':>9}   how it works")
print("  " + "-" * 74)
print(f"  {'our hand-written loop':<34} {2.9991:>9.4f} {1.9003:>9.4f}   batch gradient descent")
print(f"  {'LinearRegression':<34} {model.intercept_:>9.4f} {model.coef_[0]:>9.4f}   exact algebra (NO descent)")
print(f"  {'SGDRegressor':<34} {sgd.intercept_[0]:>9.4f} {sgd.coef_[0]:>9.4f}   stochastic gradient descent")
print(f"  {'the truth (algebra)':<34} {TRUE_THETA0:>9.4f} {TRUE_THETA1:>9.4f}   proved on paper")

# ============================================================================
# WHAT EVERY SETTING MEANS - the payoff for having done it by hand
# ============================================================================
print("\n" + "=" * 78)
print("THE PAYOFF: you now know what every one of these knobs means")
print("=" * 78)
print("  our hand-written code        scikit-learn        what it is")
print("  " + "-" * 74)
print("  ALPHA = 0.05            ->   eta0=0.05           how big a step downhill")
print("  MAX_ITERS = 3000        ->   max_iter=3000       the safety cap")
print("  TOLERANCE = 1e-9        ->   tol=1e-9            'close enough, stop'")
print("  our whole train() loop   ->   .fit()              the loop itself")
print("  (not covered yet)       ->   penalty='l2'        Ridge - next study doc")
print()
print("  Those aren't magic words in a tutorial anymore. You wrote each one.")

print("\n" + "=" * 78)
print("THE TAKEAWAY")
print("=" * 78)
print("  1. In real work you call .fit(). Nobody hand-writes the loop.")
print("  2. But .fit() is not one thing: LinearRegression solves the algebra exactly,")
print("     SGDRegressor actually walks downhill. Same call, different engines.")
print("  3. Exact algebra only exists for easy problems. Every neural network on")
print("     earth has no such shortcut - which is why gradient descent is THE")
print("     algorithm of modern AI, and why we hand-wrote it first.")
print("  4. When SGD gives a mediocre answer, more iterations may not help.")
print("     Look at the learning rate. You know that because you watched it happen.")
