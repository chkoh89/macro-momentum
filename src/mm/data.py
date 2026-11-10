"""Panel loading and monthly excess returns for the three asset classes."""
import numpy as np
import pandas as pd

from .universe import BASE

Panel = dict  # field -> DataFrame (month-end index x country)


def load_panel(path="data/panel.csv") -> Panel:
    df = pd.read_csv(path, parse_dates=["date"])
    return {f: g.pivot(index="date", columns="country", values="value").sort_index()
            for f, g in df.groupby("field")}


def _par_bond_return(y_prev: pd.DataFrame, y_now: pd.DataFrame, n: int = 20):
    """One-month return of a 10y semi-annual par bond bought at y_prev and
    repriced at y_now (yields in decimals). Ignores one month of ageing."""
    c, y = y_prev, y_now
    disc = (1 + y / 2) ** (-n)
    annuity = (1 - disc) / y.where(y.abs() > 1e-9)
    price = (c * annuity).fillna(c * n / 2) + disc
    return price - 1 + c / 12


def asset_returns(p: Panel) -> dict:
    """Monthly excess returns over the local 3m rate, by asset class.

    eq    price index return minus cash (no dividends: understates level,
          immaterial for long-short signals)
    bond  10y par bond repriced off the yield change, minus cash
    fx    long local currency vs USD: spot return plus the 3m rate differential
    """
    cash = p["r3m"].shift(1) / 1200
    eq = p["eq"].pct_change(fill_method=None) - cash
    y = p["y10"] / 100
    bond = _par_bond_return(y.shift(1), y).where(y.notna() & y.shift(1).notna()) - cash
    fx = p["fx"].pct_change(fill_method=None)
    fx = fx + cash[fx.columns].sub(cash[BASE], axis=0)
    return {"eq": eq, "bond": bond, "fx": fx}
