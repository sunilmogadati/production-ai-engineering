"""Hello, non-linear data: straighten the curve, then use linear regression.

Why this file: linear regression only draws straight lines. But lots of real
relationships are curved. The trick (ML_Study_01 section 3.9): if you can NAME the
shape, you can often TRANSFORM a variable so it becomes straight - then plain linear
regression works. This program shows four shapes on real data and does exactly that.

    (1) Logarithmic  income -> life expectancy   REAL World Bank data  -> log the x
    (2) Exponential  compound interest (math)                         -> log the y
    (3) Polynomial   fertilizer -> crop yield   (illustrative)        -> add x^2 feature
    (4) S-curve      world internet %           REAL World Bank data  -> LOGIT (not log!)

It pulls the World Bank numbers LIVE from the public REST API, so you also see how to
get real data. Needs internet.

Run:

    python3 hello_nonlinear_transforms.py
"""

import json
import ssl
import urllib.request
import numpy as np
import matplotlib.pyplot as plt

# The World Bank's open data API. No key needed - it's public.
WB = "https://api.worldbank.org/v2"
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE   # some corporate networks need this; fine for public data


def wb_indicator(indicator, economies="all", date="2021"):
    """Fetch one World Bank indicator. Returns {country_code: value}."""
    url = f"{WB}/country/{economies}/indicator/{indicator}?date={date}&format=json&per_page=500"
    with urllib.request.urlopen(url, timeout=90, context=_ctx) as r:
        payload = json.loads(r.read().decode())
    # The API returns [metadata, rows]; keep rows that actually have a value.
    return {row["countryiso3code"]: row["value"] for row in payload[1] if row["value"] is not None}


def r_squared(x, y):
    """Fit a straight line y = b0 + b1*x and return (R^2, b0, b1). R^2 = how straight it is."""
    b1, b0 = np.polyfit(x, y, 1)
    y_hat = b0 + b1 * x
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1 - ss_res / ss_tot, b0, b1


print(__doc__.split("Run:")[0].strip())

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# ============================================================================
# (1) LOGARITHMIC - the Preston curve (REAL World Bank data)
# ============================================================================
print("\n" + "=" * 74)
print("(1) LOGARITHMIC: income -> life expectancy  (real World Bank data, 2021)")
print("=" * 74)
try:
    gdp = wb_indicator("NY.GDP.PCAP.CD")     # GDP per capita, US$
    life = wb_indicator("SP.DYN.LE00.IN")    # life expectancy at birth, years
    # keep only countries that have BOTH numbers
    codes = [c for c in gdp if c in life and gdp[c] and life[c]]
    g = np.array([gdp[c] for c in codes])
    L = np.array([life[c] for c in codes])

    r_raw, _, _ = r_squared(g, L)                 # straight line on RAW income
    r_log, b0, b1 = r_squared(np.log(g), L)       # straight line on LOG income
    print(f"  {len(codes)} countries")
    print(f"  straight line on RAW income      : R² = {r_raw:.3f}   (misses the curve)")
    print(f"  straight line on ln(income)      : R² = {r_log:.3f}   <- much straighter")
    print(f"  learned line: life_exp = {b0:.1f} + {b1:.1f} * ln(GDP per capita)")
    print("  Meaning: every time income MULTIPLIES by e (~2.7x), life expectancy")
    print(f"           adds about {b1:.1f} years. Diminishing returns, made linear.")

    ax = axes[0, 0]
    ax.scatter(np.log(g), L, s=12, alpha=0.5)
    xs = np.linspace(np.log(g).min(), np.log(g).max(), 100)
    ax.plot(xs, b0 + b1 * xs, "g-", lw=2)
    ax.set_title(f"(1) log(income) -> life expectancy  (R²={r_log:.2f})")
    ax.set_xlabel("ln(GDP per capita)"); ax.set_ylabel("life expectancy")
except Exception as e:
    print(f"  (could not fetch World Bank data - are you online? {e})")

# ============================================================================
# (2) EXPONENTIAL - compound interest (pure math, always clean)
# ============================================================================
print("\n" + "=" * 74)
print("(2) EXPONENTIAL: $10,000 at 8%/yr  (compound-interest math)")
print("=" * 74)
year = np.arange(0, 41)
amount = 10000 * 1.08 ** year                 # A = P*(1+r)^t
r_raw, _, _ = r_squared(year, amount)
r_log, c0, c1 = r_squared(year, np.log(amount))
print(f"  straight line on RAW amount      : R² = {r_raw:.3f}   (curves upward)")
print(f"  straight line on ln(amount)      : R² = {r_log:.3f}   <- perfectly straight")
print(f"  slope of ln(amount) = {c1:.4f}/yr  ->  growth rate = e^{c1:.4f} - 1 = {np.exp(c1)-1:.1%}")
print("  We RECOVERED the 8% rate from the straightened line. That's the payoff.")
ax = axes[0, 1]
ax.scatter(year, np.log(amount), s=15)
ax.plot(year, c0 + c1 * year, "g-", lw=2)
ax.set_title(f"(2) year -> ln(amount)  (R²={r_log:.2f})")
ax.set_xlabel("year"); ax.set_ylabel("ln(amount)")

# ============================================================================
# (3) POLYNOMIAL - the sweet spot (illustrative; add x^2 as a feature)
# ============================================================================
print("\n" + "=" * 74)
print("(3) POLYNOMIAL: fertilizer -> crop yield  (inverted-U, illustrative)")
print("=" * 74)
fert = np.array([0, 50, 100, 150, 200, 250.0])
yld = np.array([2.0, 4.5, 6.0, 6.5, 6.0, 5.0])
r_line, _, _ = r_squared(fert, yld)
coef = np.polyfit(fert, yld, 2)               # fit  y = a*x^2 + b*x + c  (add the x^2 feature)
y_hat = np.polyval(coef, fert)
r_poly = 1 - np.sum((yld - y_hat) ** 2) / np.sum((yld - yld.mean()) ** 2)
print(f"  straight line                    : R² = {r_line:.3f}   (can't fit a hump)")
print(f"  add a fertilizer^2 feature       : R² = {r_poly:.3f}   <- the parabola fits")
print("  Key: this is NOT an axis transform. We added a feature (x^2). The model is")
print("  still LINEAR in its coefficients - it just now has a curved shape available.")
ax = axes[1, 0]
ax.scatter(fert, yld, s=40)
fs = np.linspace(0, 250, 100)
ax.plot(fs, np.polyval(coef, fs), "g-", lw=2)
ax.set_title(f"(3) fertilizer + fertilizer^2 -> yield  (R²={r_poly:.2f})")
ax.set_xlabel("fertilizer (kg N/ha)"); ax.set_ylabel("yield (t/ha)")

# ============================================================================
# (4) S-CURVE - the twist: LOGIT straightens it, a plain log does NOT
# ============================================================================
print("\n" + "=" * 74)
print("(4) S-CURVE: world internet %  (real World Bank data) - needs the LOGIT")
print("=" * 74)
try:
    # One economy (WLD = the world) over many years, so we key by DATE, not country.
    url = f"{WB}/country/WLD/indicator/IT.NET.USER.ZS?date=2005:2021&format=json&per_page=100"
    with urllib.request.urlopen(url, timeout=90, context=_ctx) as r:
        rows = json.loads(r.read().decode())[1]
    pts = sorted((int(d["date"]), d["value"]) for d in rows if d["value"] is not None)
    yr = np.array([p[0] for p in pts])
    p = np.array([p[1] for p in pts]) / 100.0      # convert % to a fraction 0..1

    r_raw, _, _ = r_squared(yr, p * 100)
    r_log, _, _ = r_squared(yr, np.log(p * 100))   # PLAIN log - does it work?
    logit = np.log(p / (1 - p))                    # the log-ODDS
    r_logit, d0, d1 = r_squared(yr, logit)         # LOGIT - does it work?
    print(f"  straight line on RAW %           : R² = {r_raw:.3f}")
    print(f"  straight line on ln(%)           : R² = {r_log:.3f}   <- plain log does NOT help")
    print(f"  straight line on LOGIT ln(p/1-p) : R² = {r_logit:.3f}   <- THIS straightens the S")
    print("  The S-curve has a floor AND a ceiling, so a plain log (which shoots past")
    print("  100%) can't straighten it. The logit can - and the logit IS logistic")
    print("  regression, coming up in ML_Study_03.")
    ax = axes[1, 1]
    ax.scatter(yr, logit, s=25)
    ax.plot(yr, d0 + d1 * yr, "g-", lw=2)
    ax.set_title(f"(4) year -> LOGIT(% online)  (R²={r_logit:.2f})")
    ax.set_xlabel("year"); ax.set_ylabel("logit(% online)")
except Exception as e:
    print(f"  (could not fetch World Bank data - are you online? {e})")

# ============================================================================
print("\n" + "=" * 74)
print("THE TAKEAWAY")
print("=" * 74)
print("  - Linear regression draws straight lines. Curved data needs a straightening step.")
print("  - Name the shape -> pick the transform:")
print("      exponential -> log the y      logarithmic -> log the x")
print("      power law   -> log both       polynomial  -> add x^2, x^3 features")
print("      S-curve     -> LOGIT (a DIFFERENT transform) -> logistic regression")
print("  - Always CHECK the data: 'population is exponential' is often false in practice.")

out = "nonlinear_transforms.png"
fig.suptitle("Four non-linear relationships, each straightened by the right transform", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(out, dpi=110)
print(f"\n  Saved the 4-panel figure to: hands-on/{out}")
print("  (uncomment plt.show() at the bottom to open it interactively)")
# plt.show()
