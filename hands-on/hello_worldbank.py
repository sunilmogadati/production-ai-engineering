"""Hello, real data: linear regression on the World Bank.

Why this file: hello_gradient_descent.py fit a line to 4 made-up points. Same
math - now on REAL data, 210 countries - to answer a real development question:

    does a country's INCOME predict how long its people LIVE?

Pairs with study-docs/ML_Study_01, Part 5.

Data: World Bank, 2021. Bundled as data/world_bank_life_gdp_2021.csv so this
runs OFFLINE (safe to screen-share). Pass --live to re-pull the latest via wbgapi.

Run (needs scikit-learn + pandas: pip install -r requirements-ml.txt):

    python3 hello_worldbank.py
    python3 hello_worldbank.py --live      # refetch the newest data
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_bank_life_gdp_2021.csv")


def adjusted_r2(r2, n, p):
    """R-squared with a penalty for using p features on n samples.

    Formula from ML_Study_01, section 4.2:  1 - (1 - R^2)(N - 1) / (N - P - 1).
    More features (bigger p) shrink the denominator -> pull the score DOWN, unless
    those features earned their keep by raising R^2 enough to cover the penalty.
    """
    return 1 - (1 - r2) * (n - 1) / (n - p - 1)


def load_data():
    """Load the two columns we need: GDP per capita and life expectancy, per country."""
    # Default path: read the bundled snapshot. Reliable, no network, always works.
    if "--live" not in sys.argv and os.path.exists(DATA):
        print(f"(reading bundled data: {os.path.basename(DATA)})")
        return pd.read_csv(DATA)

    # Optional path: pull the latest numbers straight from the World Bank API.
    print("(fetching live from the World Bank via wbgapi...)")
    import wbgapi as wb
    econ = wb.economy.DataFrame()                        # metadata about every economy
    aggregates = set(econ.index[econ["aggregate"] == True])  # "World", "OECD", ... - not countries
    names = econ["name"]
    gdp  = wb.data.DataFrame("NY.GDP.PCAP.CD", time="YR2021")   # income per person, US$
    life = wb.data.DataFrame("SP.DYN.LE00.IN", time="YR2021")   # life expectancy at birth, years
    df = pd.DataFrame({"gdp_per_capita": gdp.iloc[:, 0], "life_expectancy": life.iloc[:, 0]})
    df = df[~df.index.isin(aggregates)].dropna()         # drop the region aggregates + missing rows
    df = df[df.gdp_per_capita > 0]                        # log needs positive numbers
    df.insert(0, "country", df.index.map(names))
    return df.reset_index(drop=True)


# ============================================================================
# 1. Load and look at the raw data
# ============================================================================
df = load_data()

print("\n" + "=" * 74)
print("THE DATA: one row per country (2021)")
print("=" * 74)
print(f"  {len(df)} countries, from poorest to richest:")
poorest = df.loc[df.gdp_per_capita.idxmin()]
richest = df.loc[df.gdp_per_capita.idxmax()]
print(f"    poorest: {poorest.country:<16} ${poorest.gdp_per_capita:>10,.0f}/person   lives {poorest.life_expectancy:.0f} yrs")
print(f"    richest: {richest.country:<16} ${richest.gdp_per_capita:>10,.0f}/person   lives {richest.life_expectancy:.0f} yrs")
print(f"\n  Notice the income range is HUGE - ${poorest.gdp_per_capita:,.0f} to ${richest.gdp_per_capita:,.0f}.")
print("  A few very rich countries stretch the scale, so a raw line would be dominated")
print("  by them. The fix is to model LOG(income), which pulls that long tail in and")
print("  turns the curve into a straight line. (Same log trick as ML_Study_01, section 3.9.)")

# ============================================================================
# 2. Fit the SAME linear regression - just on log(income)
# ============================================================================
X = np.log(df[["gdp_per_capita"]])   # the feature: log of income
y = df["life_expectancy"]            # the target: years of life

model = LinearRegression().fit(X, y)   # the exact model from hello_linear.py
theta0 = model.intercept_
theta1 = model.coef_[0]
r2 = model.score(X, y)

n = len(df)                              # number of countries (samples)
adj = adjusted_r2(r2, n, p=1)            # p = 1 feature (log income)

print("\n" + "=" * 74)
print("THE MODEL: one straight line through 210 countries")
print("=" * 74)
print(f"  life_expectancy = {theta0:.1f} + {theta1:.1f} * ln(GDP per capita)")
print(f"  R-squared          = {r2:.3f}   income explains {r2*100:.0f}% of the variation")
print(f"  Adjusted R-squared = {adj:.3f}   almost identical here - we used only 1 feature,")
print(f"                                  so the penalty is tiny. Its value shows up next.")

# ----------------------------------------------------------------------------
# Why report Adjusted R² at all? Watch what junk features do to each score.
# ----------------------------------------------------------------------------
print("\n" + "=" * 74)
print("ADJUSTED R²: why it exists — add JUNK features and watch")
print("=" * 74)
print("  We bolt on columns of pure RANDOM NOISE - features that CANNOT possibly help -")
print("  refit, and watch the two scores. (We average many random draws so it's the real")
print("  pattern, not one lucky roll.)\n")
rng = np.random.default_rng(0)                       # fixed seed = same demo every run
base_X = np.log(df[["gdp_per_capita"]]).to_numpy()
print(f"  {'model':<32}{'features':>9}{'R²':>9}{'Adj R²':>9}")
print("  " + "-" * 60)
for k in [0, 2, 5, 10]:
    trials = 1 if k == 0 else 80
    r2s, adjs = [], []
    for _ in range(trials):
        Xk = base_X if k == 0 else np.hstack([base_X, rng.standard_normal((n, k))])
        p = Xk.shape[1]
        r2k = LinearRegression().fit(Xk, y).score(Xk, y)
        r2s.append(r2k); adjs.append(adjusted_r2(r2k, n, p))
    tag = "log(GDP) only" if k == 0 else f"log(GDP) + {k} junk cols"
    print(f"  {tag:<32}{1 + k:>9}{np.mean(r2s):>9.3f}{np.mean(adjs):>9.3f}")
print()
print("  R² climbs with EVERY junk column - it's mathematically guaranteed to rise, so")
print("  it simply cannot tell junk from signal. Adjusted R² just sits there: it refuses")
print("  to reward columns that don't earn their keep (a truly useless one even drags it")
print("  down). THAT gap - R² rising while Adjusted R² stalls - is exactly why you rank")
print("  models by Adjusted R², not R². (ML_Study_01 §4.2)")

# ============================================================================
# 3. What does it MEAN? (interpret, don't just report)
# ============================================================================
print("\n" + "=" * 74)
print("WHAT THE DATA SHOWS US")
print("=" * 74)
print(f"  1. Richer -> longer lives. The slope is POSITIVE (+{theta1:.1f}), so more income")
print("     goes with more years. No surprise - but now we've measured it.")
print()
print(f"  2. Income ALONE explains {r2*100:.0f}% of the gap in life expectancy between")
print("     countries. One single number per country, and it captures most of the story.")
print()
doubling = theta1 * np.log(2)
print(f"  3. DIMINISHING RETURNS - the big one. Because we used log(income), every")
print(f"     DOUBLING of income buys the same ~{doubling:.1f} extra years:")
for lo, hi in [(1_000, 2_000), (4_000, 8_000), (50_000, 100_000)]:
    plo = theta0 + theta1 * np.log(lo)
    phi = theta0 + theta1 * np.log(hi)
    print(f"       ${lo:>7,} -> ${hi:>7,}/person : {plo:.1f} -> {phi:.1f} yrs   (+{phi-plo:.1f})")
print("     So the FIRST few thousand dollars of development add years fast; the same")
print("     jump means almost nothing to an already-rich country. Early money saves lives.")
print()
print(f"  4. The other {100-r2*100:.0f}% is NOT income: healthcare, conflict, disease, diet.")
print("     That's why we look at who beats - and misses - their income prediction next.")

# ============================================================================
# 4. Residuals: who lives longer (or shorter) than their income predicts?
# ============================================================================
df = df.copy()
df["predicted"] = model.predict(X)
df["surprise"] = df["life_expectancy"] - df["predicted"]   # + = lives longer than income says

print("\n" + "=" * 74)
print("THE INTERESTING PART: where income does NOT explain it")
print("=" * 74)
print("  Live LONGER than income predicts - strong public health for their income,")
print("  a Soviet-era health legacy, or an income figure that recently collapsed:")
for _, r in df.sort_values("surprise", ascending=False).head(4).iterrows():
    print(f"    {r.country:<24} {r.life_expectancy:.0f} yrs  (income predicts {r.predicted:.0f})  +{r.surprise:.0f}")
print("  Live SHORTER than income predicts - conflict, disease (e.g. HIV), or oil/mineral")
print("  wealth that never reaches ordinary people:")
for _, r in df.sort_values("surprise").head(4).iterrows():
    print(f"    {r.country:<24} {r.life_expectancy:.0f} yrs  (income predicts {r.predicted:.0f})  {r.surprise:.0f}")
print("  (Careful: a big surprise can mean a REAL health story OR a data quirk - e.g. an")
print("   income that just crashed. Figuring out WHICH is what the actual analysis is.)")

# ============================================================================
# 5. Predict a made-up country
# ============================================================================
print("\n" + "=" * 74)
print("USING THE MODEL: predict a country we don't have")
print("=" * 74)
for income in [1_000, 10_000, 50_000]:
    pred = theta0 + theta1 * np.log(income)
    print(f"  A country at ${income:>6,}/person -> predicted life expectancy {pred:.0f} years")

print("\n" + "=" * 74)
print("THE TAKEAWAY")
print("=" * 74)
print("  - Same linear regression as the 4-point toy example, now on 210 real countries.")
print("  - The log turned a curved income->life relationship into a straight line.")
print("  - One feature, R^2 = 0.71: income explains most of it, but not all.")
print("  - CORRELATION, not proof of cause: income doesn't add years directly - it buys")
print("    clean water, doctors, food, and schools, and THOSE add the years.")
print("  - The residuals (who beats their income) are often the real story.")
