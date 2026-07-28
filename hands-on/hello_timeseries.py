"""Hello, time series: forecasting the future is NOT the same as fitting the past.

Why this file: every model so far predicted from a RANDOM train/test split. Time
series breaks that rule - the data is ordered in time, and you must train on the
PAST and test on the FUTURE. This file shows the one discipline that matters most
in forecasting, using real World Bank data (World GDP per capita, 1960-2025).

And it delivers a surprise that every forecaster learns the hard way:
    the model that fits the past BEST can be the WORST at predicting the future.

Pairs with study-docs/ML_Study_04 (time series). Builds on ML_Study_01 section 3.9
(the log trick for exponential growth).

Run (needs pandas + scikit-learn: pip install -r requirements-ml.txt):

    python3 hello_timeseries.py
"""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "data", "world_gdp_per_capita_timeseries.csv")

print(__doc__.split("Run (")[0].strip())

# ============================================================================
# 1. The data - one number per year, in order
# ============================================================================
df = pd.read_csv(DATA).sort_values("year").reset_index(drop=True)

print("\n" + "=" * 74)
print("THE DATA: World GDP per capita, one value per year")
print("=" * 74)
print(f"  {df.year.min()} to {df.year.max()}  ({len(df)} years)")
print(f"  started at ${df.gdp_per_capita.iloc[0]:,.0f}  ->  latest ${df.gdp_per_capita.iloc[-1]:,.0f}")

# Year-over-year change exposes the SHOCKS - the years no model can see coming.
df["yoy_pct"] = df.gdp_per_capita.pct_change() * 100
print("  the 3 worst single-year drops (shocks a forecaster can't predict):")
for _, r in df.nsmallest(3, "yoy_pct").iterrows():
    print(f"    {int(r.year)}: {r.yoy_pct:+.1f}%   (e.g. 2009 financial crisis, 2020 COVID)")

# ============================================================================
# 2. THE CARDINAL RULE: split by TIME, never at random
# ============================================================================
print("\n" + "=" * 74)
print("THE ONE RULE THAT MATTERS: train on the PAST, test on the FUTURE")
print("=" * 74)
CUT = 2013
train = df[df.year <= CUT]
test = df[df.year > CUT]
print(f"  train: {train.year.min()}-{train.year.max()} ({len(train)} yrs)   "
      f"test = the FUTURE: {test.year.min()}-{test.year.max()} ({len(test)} yrs)")
print("  We do NOT shuffle. In week 2 a random split was fine; here it would be CHEATING -")
print("  shuffling lets 2024 sneak into training, so the model 'predicts' a future it")
print("  already saw. Real forecasts never get to peek. So: past trains, future tests.")

yr_tr, yr_te = train[["year"]], test[["year"]]
y_te = test.gdp_per_capita.values


def score(pred):
    return mean_absolute_error(y_te, pred), mean_squared_error(y_te, pred) ** 0.5


# ============================================================================
# 3. Three forecasters - including "the one that should win"
# ============================================================================
# (a) NAIVE baseline: predict every future year = the last value we saw. Dumb on
#     purpose. ALWAYS build this first - if a fancy model can't beat it, it's useless.
naive = np.full(len(test), train.gdp_per_capita.iloc[-1])

# (b) LINEAR trend: fit a straight line to (year -> gdp). This IS linear regression,
#     with time as the single feature - the exact model from ML_Study_01.
lin = LinearRegression().fit(yr_tr, train.gdp_per_capita)
lin_pred = lin.predict(yr_te)

# (c) LOG-LINEAR trend: GDP grows roughly exponentially, and ML_Study_01 section 3.9
#     taught that log straightens exponential growth. So this "should" be the best...
logm = LinearRegression().fit(yr_tr, np.log(train.gdp_per_capita))
log_pred = np.exp(logm.predict(yr_te))
growth = (np.exp(logm.coef_[0]) - 1) * 100

print("\n" + "=" * 74)
print("THREE FORECASTS, scored on the held-out FUTURE (lower = better)")
print("=" * 74)
print(f"  {'model':<34}{'MAE':>11}{'RMSE':>12}")
print("  " + "-" * 58)
for name, pred in [("naive (= last value seen)", naive),
                   ("linear trend  (year -> gdp)", lin_pred),
                   (f"log-linear trend ({growth:.1f}%/yr)", log_pred)]:
    mae, rmse = score(pred)
    print(f"  {name:<34}${mae:>9,.0f}   ${rmse:>9,.0f}")

# ============================================================================
# 4. THE SURPRISE
# ============================================================================
print("\n" + "=" * 74)
print("THE SURPRISE: the 'smartest' model is the WORST")
print("=" * 74)
print(f"  The log-linear model fit 1960-2013 beautifully and learned {growth:.1f}% growth/year.")
print("  Extrapolated forward, that compounds into a HUGE overshoot - it confidently")
print("  predicts a boom that never came. Meanwhile the DUMB naive baseline wins.")
print()
print("  The lesson every forecaster learns the hard way:")
print("    * Fitting the PAST well  !=  predicting the FUTURE well.")
print("    * The more aggressively a model extrapolates, the harder it can faceplant.")
print("    * ALWAYS compare against the naive baseline. If you can't beat 'guess last")
print("      value', you don't have a forecast - you have a fancy way to be wrong.")
print("  (The §3.9 log trick is great for DESCRIBING past data - just dangerous when you")
print("   extrapolate it years into the future and assume the growth rate is eternal.)")

# ============================================================================
# 5. Nobody saw the shock coming
# ============================================================================
print("\n" + "=" * 74)
print("AND nobody forecasts a shock")
print("=" * 74)
v2019 = df.loc[df.year == 2019, "gdp_per_capita"].values[0]
v2020 = df.loc[df.year == 2020, "gdp_per_capita"].values[0]
print(f"  2019 -> 2020: ${v2019:,.0f} -> ${v2020:,.0f}  ({(v2020/v2019 - 1)*100:+.1f}%, the COVID drop).")
print("  Every trend model predicted 2020 would keep RISING. It FELL instead. A model")
print("  that learns from history cannot see a pandemic coming - the past didn't")
print("  contain it. Trend models extend the trend; they do not forecast surprises.")

print("\n" + "=" * 74)
print("THE TAKEAWAY")
print("=" * 74)
print("  1. Time series is ORDERED - train on the past, test on the future, never shuffle.")
print("  2. A trend model is just linear regression with TIME as the feature.")
print("  3. Always beat a naive baseline, or you have no forecast.")
print("  4. Fitting the past != predicting the future; extrapolation compounds error.")
print("  5. Real tools go further - ARIMA, Prophet, and (the AI route) RNN/LSTM - but")
print("     none of them can beat these fundamentals, and none can predict a shock.")
