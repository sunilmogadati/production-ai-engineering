"""Hello, Naive Bayes: classify by counting, not by gradient descent.

Why this file: logistic regression LEARNED weights by rolling downhill
(hello_logistic.py). Naive Bayes does something completely different -- it
just COUNTS how often each clue went with each label, then multiplies those
fractions together. No learning rate, no iterations. One pass over the data.

This script mirrors ML_Study_05 exactly:
  1. Fit by hand   -> frequency tables + priors from the classic 14-day dataset
  2. Predict       -> (Sunny, Hot)  reproduces  No: 73% / Yes: 27%
  3. The trap      -> (Overcast, Mild) exposes the zero-frequency problem,
                      then Laplace (add-one) smoothing rescues it
  4. Confirm       -> scikit-learn's CategoricalNB agrees

Run it:  python3 hands-on/hello_naive_bayes.py
"""

from collections import Counter

# ---------------------------------------------------------------------------
# The classic "Play Tennis" dataset: 14 days, each with clues + what happened.
# We use two clues (Outlook, Temperature), exactly like the lecture.
# ---------------------------------------------------------------------------
#            (Outlook,    Temperature, PlayTennis)
DATA = [
    ("Sunny",    "Hot",  "No"),
    ("Sunny",    "Hot",  "No"),
    ("Overcast", "Hot",  "Yes"),
    ("Rain",     "Mild", "Yes"),
    ("Rain",     "Cool", "Yes"),
    ("Rain",     "Cool", "No"),
    ("Overcast", "Cool", "Yes"),
    ("Sunny",    "Mild", "No"),
    ("Sunny",    "Cool", "Yes"),
    ("Rain",     "Mild", "Yes"),
    ("Sunny",    "Mild", "Yes"),
    ("Overcast", "Mild", "Yes"),
    ("Overcast", "Hot",  "Yes"),
    ("Rain",     "Mild", "No"),
]

LABELS = ["Yes", "No"]


# ---------------------------------------------------------------------------
# STEP 1 -- "Fit" the model. For Naive Bayes, fitting is just counting.
# ---------------------------------------------------------------------------
def fit(data):
    """Return the counts we need: label totals, and per-feature tallies."""
    label_counts = Counter(row[2] for row in data)              # {Yes: 9, No: 5}
    # outlook_counts[label][value] = how many days had this outlook AND this label
    outlook_counts = {lab: Counter() for lab in LABELS}
    temp_counts = {lab: Counter() for lab in LABELS}
    for outlook, temp, label in data:
        outlook_counts[label][outlook] += 1
        temp_counts[label][temp] += 1
    return label_counts, outlook_counts, temp_counts


def likelihood(count, total, alpha=0.0, n_categories=0):
    """P(feature value | label) = count / total.

    With alpha=1 this becomes Laplace (add-one) smoothing:
        (count + alpha) / (total + alpha * n_categories)
    so nothing is ever exactly zero.
    """
    return (count + alpha) / (total + alpha * n_categories)


def score(outlook, temp, label, counts, alpha=0.0):
    """prior * P(outlook|label) * P(temp|label)  -- the denominator is dropped."""
    label_counts, outlook_counts, temp_counts = counts
    total = sum(label_counts.values())                          # 14
    n_out = len({o for o, _, _ in DATA})                        # 3 outlook categories
    n_temp = len({t for _, t, _ in DATA})                       # 3 temperature categories

    prior = label_counts[label] / total                         # P(Yes)=9/14, P(No)=5/14
    p_out = likelihood(outlook_counts[label][outlook], label_counts[label], alpha, n_out)
    p_temp = likelihood(temp_counts[label][temp], label_counts[label], alpha, n_temp)
    return prior * p_out * p_temp


def predict(outlook, temp, counts, alpha=0.0):
    """Score both labels, normalize to real probabilities, return the winner."""
    raw = {lab: score(outlook, temp, lab, counts, alpha) for lab in LABELS}
    total = sum(raw.values())
    probs = {lab: (raw[lab] / total if total > 0 else 0.0) for lab in LABELS}
    winner = max(probs, key=probs.get)
    return winner, raw, probs


# ---------------------------------------------------------------------------
# Run it
# ---------------------------------------------------------------------------
counts = fit(DATA)
label_counts, outlook_counts, temp_counts = counts
total = sum(label_counts.values())

print("=" * 70)
print("STEP 1 -- FIT BY COUNTING (no gradient descent, one pass)")
print("=" * 70)
print(f"  Priors:  P(Yes) = {label_counts['Yes']}/{total}   "
      f"P(No) = {label_counts['No']}/{total}\n")
print("  Outlook frequency table:")
print(f"  {'':10}{'Yes':>5}{'No':>5}{'P(.|Yes)':>12}{'P(.|No)':>12}")
for val in ["Sunny", "Overcast", "Rain"]:
    y, n = outlook_counts['Yes'][val], outlook_counts['No'][val]
    print(f"  {val:10}{y:>5}{n:>5}{y/9:>12.3f}{n/5:>12.3f}")
print("\n  Temperature frequency table:")
print(f"  {'':10}{'Yes':>5}{'No':>5}{'P(.|Yes)':>12}{'P(.|No)':>12}")
for val in ["Hot", "Mild", "Cool"]:
    y, n = temp_counts['Yes'][val], temp_counts['No'][val]
    print(f"  {val:10}{y:>5}{n:>5}{y/9:>12.3f}{n/5:>12.3f}")

print("\n" + "=" * 70)
print("STEP 2 -- PREDICT (Sunny, Hot)   [matches ML_Study_05 Part 6-7]")
print("=" * 70)
winner, raw, probs = predict("Sunny", "Hot", counts, alpha=0.0)
print(f"  raw score Yes = {raw['Yes']:.3f}   (= 9/14 * 2/9 * 2/9 = 2/63)")
print(f"  raw score No  = {raw['No']:.3f}   (= 5/14 * 3/5 * 2/5 = 3/35)")
print(f"  normalized -> Yes: {probs['Yes']*100:.0f}%   No: {probs['No']*100:.0f}%")
print(f"  PREDICTION: {winner}   (sunny + hot -> don't play)")

print("\n" + "=" * 70)
print("STEP 3 -- THE ASSIGNMENT (Overcast, Mild)  AND THE ZERO-FREQUENCY TRAP")
print("=" * 70)
winner, raw, probs = predict("Overcast", "Mild", counts, alpha=0.0)
print(f"  raw score Yes = {raw['Yes']:.3f}   (= 9/14 * 4/9 * 4/9)")
print(f"  raw score No  = {raw['No']:.3f}   <-- EXACTLY ZERO")
print("  Why zero? Overcast NEVER occurred with 'No' in 14 days -> P(Overcast|No)=0/5,")
print("  and one zero in a product annihilates the whole label, ignoring Mild's support.")
print(f"  PREDICTION (no smoothing): {winner}\n")

winner_s, raw_s, probs_s = predict("Overcast", "Mild", counts, alpha=1.0)
print("  With Laplace (add-one) smoothing -- nothing is ever exactly zero:")
print(f"    P(Overcast|No) becomes (0+1)/(5+3) = {1/8:.3f}, not 0")
print(f"    normalized -> Yes: {probs_s['Yes']*100:.0f}%   No: {probs_s['No']*100:.0f}%")
print(f"    PREDICTION (smoothed): {winner_s}  (still Yes -- overcast strongly means play)")

print("\n" + "=" * 70)
print("STEP 4 -- CONFIRM WITH scikit-learn (CategoricalNB)")
print("=" * 70)
try:
    from sklearn.naive_bayes import CategoricalNB
    from sklearn.preprocessing import OrdinalEncoder
    import numpy as np

    X_raw = [[o, t] for o, t, _ in DATA]
    y_raw = [lab for _, _, lab in DATA]
    enc = OrdinalEncoder()
    X = enc.fit_transform(X_raw)
    # sklearn applies Laplace smoothing by default (alpha=1.0)
    model = CategoricalNB(alpha=1.0)
    model.fit(X, y_raw)

    for clue in [["Sunny", "Hot"], ["Overcast", "Mild"]]:
        xq = enc.transform([clue])
        pred = model.predict(xq)[0]
        proba = dict(zip(model.classes_, model.predict_proba(xq)[0]))
        pretty = "  ".join(f"{lab}:{p*100:.0f}%" for lab, p in proba.items())
        print(f"  {tuple(clue)!s:24} -> {pred:4}   ({pretty})")
    print("\n  sklearn agrees on the winners. Its exact %s differ from Step 2 because")
    print("  it smooths by default -- the same fix we did by hand in Step 3.")
except ImportError:
    print("  scikit-learn not installed -- skip. The hand-built model above IS the algorithm.")

print("\n" + "=" * 70)
print("TAKEAWAY")
print("=" * 70)
print("  - Naive Bayes 'trains' by counting frequencies once -- no iterations.")
print("  - It picks the label that makes your clues most probable (Bayes' theorem).")
print("  - 'Naive' = it pretends the clues are independent, so it just multiplies them.")
print("  - Watch for the zero-frequency trap; Laplace smoothing is the standard fix.")
print("  - It's the classic fast baseline for text/spam -- try it before anything fancier.")
