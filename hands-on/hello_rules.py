"""Hello, rules: the smallest possible "smart" decision.

Why this file: intelligence can start as an if/else. No data, no training,
no dependencies - instantly explainable. This is where every real system starts.

Features must be OBJECTIVE - things we can actually observe:
  - buying_keywords : how many buying words ("order", "buy", "price") appeared
                      in the call transcript. Countable.
  - prior_purchases : completed orders, from the order history table. A fact.
No "gut feeling" scores: a subjective feature is a model hiding in a field.

(Same signal, two altitudes: the ML tier - ml01_generate_synthetic_data.py -
 calls buying_keywords by its productionized name, intent_signal, on a 0-100
 scale. Same idea, computed upstream from the transcript.)

But watch Meera: the rule can only see what we told it to look at.

Run it (no server, no pip install needed):

    ./venv/bin/python hello_rules.py
"""


def score(buying_keywords: int) -> str:
    """Our whole 'model': three if/elifs over ONE feature."""
    if buying_keywords >= 6:
        return "hot"
    if buying_keywords >= 3:
        return "warm"
    return "cold"


# Each row: (name, buying_keywords, prior_purchases, what actually happened).
# The rule above only ever looks at buying_keywords - prior_purchases is here
# so you can see the column it is BLIND to.
customers = [
    ("John",  7, 0, "bought"),        # loud buyer      -> rule right
    ("Rahul", 0, 0, "did not buy"),   # silent and new  -> rule right
    ("Meera", 1, 3, "bought"),        # quiet but loyal -> rule MISSES her
]

for name, buying_keywords, prior_purchases, outcome in customers:
    decision = score(buying_keywords)
    chased = decision != "cold"                 # we follow up on hot/warm, skip cold
    correct = chased == (outcome == "bought")
    verdict = "correct" if correct else "WRONG"
    print(f"{name:<6} buying_keywords={buying_keywords} prior_purchases={prior_purchases}  "
          f"->  rule says {decision:<4} | actually {outcome:<12} [{verdict}]")

print()
print("Meera bought 3 times before. Loyal customers don't announce themselves -")
print("they just order. Our rule never looks at prior_purchases, so it calls her")
print("cold and we lose the sale. We could bolt on an elif for prior_purchases,")
print("but then the next miss needs another elif, and the next. A hand-written")
print("rule can only ever see the columns we thought to write down.")
print("Next (hello_logistic.py): let a model read the examples and find the pattern.")
