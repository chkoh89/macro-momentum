"""Weights and volatility targeting. Everything here uses data up to t only."""
import numpy as np
import pandas as pd

TARGET = 0.10      # annualised volatility target for every portfolio
VOL_WIN = 36       # months, as in the paper's three-year risk model
VOL_MIN = 24
MIN_ASSETS = 4     # fewest markets with a signal for a long-short portfolio


def ann_vol(r, window=VOL_WIN, minp=VOL_MIN):
    return r.rolling(window, min_periods=minp).std() * np.sqrt(12)


def xs_weights(sig: pd.DataFrame, vol: pd.DataFrame) -> pd.DataFrame:
    """Long-short: rank markets on the signal, demean the ranks so the weights
    sum to zero, then divide each by its own volatility."""
    sig = sig.where(vol.notna())
    rk = sig.rank(axis=1)
    w = rk.sub(rk.mean(axis=1), axis=0)
    w = w.div(w.abs().sum(axis=1).replace(0, np.nan), axis=0)
    w.loc[sig.notna().sum(axis=1) < MIN_ASSETS] = np.nan
    return w / vol


def ts_weights(sig: pd.DataFrame, vol: pd.DataFrame) -> pd.DataFrame:
    """Directional: long if the signal is positive, short if negative, each
    market sized to equal volatility."""
    sig = sig.where(vol.notna())
    n = sig.notna().sum(axis=1).replace(0, np.nan)
    return (np.sign(sig) / vol).div(n, axis=0)


def pnl(w: pd.DataFrame, r: pd.DataFrame) -> pd.Series:
    """Weights set at the end of month t earn the return of month t+1."""
    return (w.shift(1) * r[w.columns]).sum(axis=1, min_count=1)


def vol_scale(x: pd.Series, target=TARGET) -> pd.Series:
    """Leverage applied to month t's return: target over the stream's own
    trailing volatility, known at the end of t-1."""
    return (target / ann_vol(x)).shift(1)


def target_vol(x: pd.Series, target=TARGET) -> pd.Series:
    """Scale a return stream to the volatility target using its own trailing
    volatility, lagged one month."""
    return x * vol_scale(x, target)
