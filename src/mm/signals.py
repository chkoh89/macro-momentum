"""The paper's four macro themes as one-year trends, and the Exhibit 1 sign map."""
import pandas as pd

from .universe import BASE

# Months between the reference period and when the number is public.
PUB_LAG = {"growth": 3, "inflation": 2, "trade": 1, "monetary": 0, "risk": 0}

STALE = 3

# Theme -> variables. Business cycle is the average of growth and inflation.
THEMES = {"business_cycle": ["growth", "inflation"], "trade": ["trade"],
          "monetary": ["monetary"], "risk": ["risk"]}

# Position sign when the variable is RISING. "trade" is measured as currency
# APPRECIATION, so its signs are the reverse of the paper's depreciation column.
SIGNS = {
    "eq":   {"growth": +1, "inflation": -1, "trade": -1, "monetary": -1, "risk": +1},
    "fx":   {"growth": +1, "inflation": +1, "trade": +1, "monetary": +1, "risk": +1},
    "bond": {"growth": -1, "inflation": -1, "trade": +1, "monetary": -1, "risk": -1},
}


def macro_trends(p: dict, eq_excess: pd.DataFrame) -> dict:
    """One-year change in each macro variable, per country, as known at month t.

    growth     12m change in real GDP growth (yoy)   [paper: consensus forecasts]
    inflation  12m change in CPI inflation (yoy)     [paper: consensus forecasts]
    trade      12m % change in the trade-weighted exchange rate
    monetary   12m change in the 3m rate             [paper: 2y yield]
    risk       12m equity excess return
    """
    t = {
        "growth": p["gdp_yoy"].diff(12),
        "inflation": p["cpi_yoy"].diff(12),
        "trade": p["neer"].pct_change(12, fill_method=None),
        "monetary": p["r3m"].diff(12),
        "risk": eq_excess.rolling(12, min_periods=12).sum(),
    }
    # If this month's figure is not out yet, keep the last known one for up to
    # STALE months; after that the country drops out of that signal.
    return {k: v.shift(PUB_LAG[k]).ffill(limit=STALE) for k, v in t.items()}


def asset_signal(trend: pd.DataFrame, asset: str, var: str) -> pd.DataFrame:
    """Signed signal for one asset class. Currencies are a relative asset, so
    their signal is the local trend minus the US trend."""
    s = SIGNS[asset][var] * trend
    if asset == "fx":
        s = s.drop(columns=BASE).sub(s[BASE], axis=0)
    return s
