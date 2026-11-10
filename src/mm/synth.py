"""Random panel with the same shape as the real one. For tests only: returns
are pure noise, so any Sharpe ratio it produces is meaningless."""
import numpy as np
import pandas as pd

from .universe import BASE, COUNTRIES


def make_panel(start="2005-01-31", months=262, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=months, freq="ME")
    n = len(COUNTRIES)

    def walk(vol, x0=0.0):
        return pd.DataFrame(x0 + np.cumsum(rng.normal(0, vol, (months, n)), axis=0),
                            index=idx, columns=COUNTRIES)

    gdp = walk(0.6, 2.0)
    gdp.loc[~np.isin(idx.month, [3, 6, 9, 12])] = np.nan   # quarterly, carried forward
    gdp = gdp.ffill(limit=5)
    return {"eq": 100 * np.exp(walk(0.045)), "y10": walk(0.18, 3.0), "r3m": walk(0.10, 2.0),
            "fx": np.exp(walk(0.028)).drop(columns=BASE), "neer": 100 * np.exp(walk(0.015)),
            "cpi_yoy": walk(0.25, 2.0), "gdp_yoy": gdp}
