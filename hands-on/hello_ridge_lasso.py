"""Hello, Ridge & Lasso: two one-line fixes for overfitting.

Why this file: hello_gradient_descent.py showed how a model LEARNS. This one shows
what goes wrong when it learns TOO well (overfitting), and the two tiny changes to
the cost function that fix it:

    Ridge  (L2)  = usual cost + lambda * (sum of slopes SQUARED)   -> shrinks slopes
    Lasso  (L1)  = usual cost + lambda * (sum of |slopes|)         -> DELETES junk features

Pairs with study-docs/ML_Study_02. Two parts:
    Part A - overfitting, and how Ridge rescues it
    Part B - Lasso's superpower: automatic feature selection

Run (needs scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_ridge_lasso.py
"""

import warnings
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.exceptions import ConvergenceWarning

# Lasso prints a "didn't fully converge" note on tiny datasets - harmless here, so hush it.
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# A fixed random stream so you get the exact numbers described in the comments.
rng = np.random.default_rng(0)


print(__doc__.split("Run (needs")[0].strip())

# ============================================================================
# PART A - Overfitting, and how Ridge rescues it
# ============================================================================
print("\n" + "=" * 78)
print("PART A: a model that learns TOO well")
print("=" * 78)

# The TRUE relationship we're trying to learn (a gentle wave). In real life you
# never know this - here we do, so we can grade the models honestly.
def true_relationship(x):
    return np.sin(2 * np.pi * x) * 0.8 + x

# TRAINING data: just 18 points, and a little measurement noise on top of the truth.
x_train = np.sort(rng.uniform(0, 1, 18))
y_train = true_relationship(x_train) + rng.normal(0, 0.15, 18)

# TEST data: a big, clean set of 400 points straight from the true curve. This is
# the "new data the model will face" - and being large + clean makes the score stable.
x_test = np.linspace(0, 1, 400)
y_test = true_relationship(x_test)

# We deliberately hand the model a VERY flexible shape: a degree-12 polynomial.
# (That's 12 knobs - way more than 18 points need. Flexibility is what lets it overfit.)
# StandardScaler just rescales the features so training behaves - see ML_Study_02 Part 6.
def make_model(regularizer):
    return make_pipeline(PolynomialFeatures(12), StandardScaler(), regularizer)

print("\nSame flexible (degree-12) model, different amounts of Ridge regularization (λ):\n")
print(f"  {'λ (alpha)':<14}{'train R²':>10}{'test R²':>10}   verdict")
print("  " + "-" * 62)

# alpha is scikit-learn's name for lambda. We sweep it from 0 (none) upward.
sweep = [(0.0, "no penalty  -> OVERFIT (memorized the noise)"),
         (1e-4, "a touch     -> GENERALIZED  <-- the sweet spot"),
         (1e-1, "more        -> starting to underfit"),
         (1.0, "a lot       -> underfitting"),
         (100.0, "way too much-> flat = UNDERFIT")]

for alpha, verdict in sweep:
    # alpha=0 means "no penalty at all", which is plain LinearRegression.
    reg = LinearRegression() if alpha == 0 else Ridge(alpha=alpha)
    model = make_model(reg).fit(x_train.reshape(-1, 1), y_train)
    tr = model.score(x_train.reshape(-1, 1), y_train)   # how well it fits TRAINING data
    te = model.score(x_test.reshape(-1, 1), y_test)     # how well it does on NEW data
    print(f"  {alpha:<14g}{tr:>10.3f}{te:>10.3f}   {verdict}")

print("""
  Read the two columns:
   - With NO penalty (top row), training R² is near-perfect but test R² is NEGATIVE
     - the model does WORSE on new data than just guessing the average. Classic overfit.
   - A TINY bit of Ridge flips test R² from about -0.1 to about 0.98. One knob. Huge.
   - Keep turning λ up and it over-corrects: the model goes flat and UNDERFITS.
  That U-shape - overfit on the left, underfit on the right, sweet spot in the middle -
  is the whole reason λ has to be tuned, not guessed.""")

# ---- How do you FIND that sweet spot? Cross-validation. ----
print("  " + "-" * 62)
print("  HOW TO PICK λ: try many values, keep the one that scores best on held-out")
print("  data. That's cross-validation. Here's the by-hand version:\n")

candidates = [0.0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
scored = []
for alpha in candidates:
    reg = LinearRegression() if alpha == 0 else Ridge(alpha=alpha)
    model = make_model(reg).fit(x_train.reshape(-1, 1), y_train)
    scored.append((alpha, model.score(x_test.reshape(-1, 1), y_test)))
best_alpha, best_score = max(scored, key=lambda t: t[1])
print(f"    best λ = {best_alpha:g}  (test R² = {best_score:.3f})")
print("    scikit-learn automates this exact search with RidgeCV / LassoCV.")

# ============================================================================
# PART B - Lasso's superpower: feature selection
# ============================================================================
print("\n" + "=" * 78)
print("PART B: Lasso deletes the junk features (feature selection)")
print("=" * 78)

# Build data with 100 rows and 25 features - but only the FIRST FIVE actually matter.
# The other 20 are pure noise ("junk"): their true effect on the answer is exactly zero.
n = 100
X = rng.normal(0, 1, (n, 25))
true_coef = np.array([5.0, -4.0, 3.0, -2.0, 1.0] + [0.0] * 20)   # 5 real, 20 junk
y = X @ true_coef + rng.normal(0, 1.0, n)

# Split into train / test the simple way.
Xtr, Xte, ytr, yte = X[:70], X[70:], y[:70], y[70:]

print("\n  25 features: 5 real, 20 pure junk. Which model figures that out?\n")
print(f"  {'model':<20}{'test R²':>9}{'features used':>16}")
print("  " + "-" * 50)

results = {}
for name, m in [("LinearRegression", LinearRegression()),
                ("Ridge(λ=1)", Ridge(alpha=1.0)),
                ("Lasso(λ=0.1)", Lasso(alpha=0.1, max_iter=50000))]:
    m.fit(Xtr, ytr)
    used = int(np.sum(np.abs(m.coef_) > 0.01))       # how many coefficients are non-zero
    results[name] = m
    print(f"  {name:<20}{m.score(Xte, yte):>9.3f}{used:>13} / 25")

print("""
  All three get about the same test score - but look at 'features used':
  LinearRegression and Ridge keep essentially all 25 (every junk feature keeps a
  small non-zero coefficient). Lasso threw most of the junk OUT - it zeroed those
  coefficients, so those features are simply gone. Same accuracy, a far SIMPLER model.""")

lasso = results["Lasso(λ=0.1)"]
print("  Lasso's coefficients:")
print("    real features (x1..x5):", np.round(lasso.coef_[:5], 2), " <- kept, close to the true [5,-4,3,-2,1]")
print("    junk features (x6..x25):", np.round(lasso.coef_[5:], 2))
print(f"    -> {int(np.sum(lasso.coef_[5:] == 0))}/20 junk features driven to EXACTLY zero.")

print("""
  Why does Lasso zero them but Ridge doesn't? Ridge's pull fades as a coefficient
  shrinks (it coasts near zero); Lasso's pull is constant all the way down, so it
  shoves right through to exactly zero. That's L1 vs L2 in one sentence.""")

# ============================================================================
# THE TAKEAWAY
# ============================================================================
print("\n" + "=" * 78)
print("THE TAKEAWAY")
print("=" * 78)
print("  1. Overfitting = great on training, bad on new data. A flexible model")
print("     memorizes the noise. Watch for a big train-vs-test gap.")
print("  2. Ridge (L2) and Lasso (L1) both fix it by fining big coefficients -")
print("     one extra term on the cost function. They shrink the model toward simple.")
print("  3. λ (alpha) is a DIAL: too small = still overfit, too big = underfit.")
print("     Tune it with cross-validation (RidgeCV / LassoCV).")
print("  4. Bonus for Lasso: it zeros useless coefficients outright = feature selection.")
print("  5. In real code this is two lines: `Ridge(alpha=...).fit(X, y)`. But now you")
print("     know exactly what that one line is doing, and why.")
