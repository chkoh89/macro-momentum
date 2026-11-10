"""Panel loading and monthly excess returns for the three asset classes."""
import pathlib

import pandas as pd

from .universe import BASE

Panel = dict  # field -> DataFrame (month-end index x country)


def load_panel(path="data/panel.csv", market="data/market.csv") -> Panel:
    """FRED macro panel plus, if present, the tradeable price panel. Every
    field is put on one common month-end index so lags and carry-forwards
    behave the same for all of them."""
    df = pd.read_csv(path, parse_dates=["date"])
    p = {f: g.pivot(index="date", columns="country", values="value") for f, g in df.groupby("field")}
    if market and pathlib.Path(market).exists():
        mk = pd.read_csv(market, parse_dates=["date"])
        p |= {k: g.pivot(index="date", columns="country", values="value") for k, g in mk.groupby("kind")}
    lo = min(v.index.min() for v in p.values())
    hi = max(v.index.max() for v in p.values())
    idx = pd.date_range(lo, hi, freq="ME")
    return {k: v.reindex(idx).rename_axis("date") for k, v in p.items()}


def _par_bond_return(y_prev: pd.DataFrame, y_now: pd.DataFrame, n: int = 20):
    """One-month return of a 10y semi-annual par bond bought at y_prev and
    repriced at y_now (yields in decimals). Ignores one month of ageing."""
    c, y = y_prev, y_now
    disc = (1 + y / 2) ** (-n)
    annuity = (1 - disc) / y.where(y.abs() > 1e-9)
    price = (c * annuity).fillna(c * n / 2) + disc
    return price - 1 + c / 12


def cash_rate(p: Panel) -> pd.DataFrame:
    """Monthly cash return earned over month t: last month's 3m rate / 12.
    Gaps and stale ends in the rate series are carried forward."""
    return p["r3m"].ffill().shift(1) / 1200


def asset_returns(p: Panel, source: str | None = None) -> dict:
    """Monthly excess returns over local cash, by asset class.

    source="market" (default when the tradeable panel is loaded)
      eq    index return (month-end close) minus cash: an index future
      bond  government bond ETF total return minus cash
      fx    long local currency vs USD: spot return plus 3m rate differential
    source="fred" (v0, not tradeable; kept for comparison)
      eq    OECD share price index, monthly average, minus cash
      bond  10y par bond repriced off the monthly-average yield, minus cash
      fx    as above
    """
    source = source or ("market" if "px_eq" in p else "fred")
    cash = cash_rate(p)
    if source == "market":
        eq = p["px_eq"].pct_change(fill_method=None)
        bond = p["px_bond"].pct_change(fill_method=None)
    else:
        eq = p["eq"].pct_change(fill_method=None)
        y = p["y10"] / 100
        bond = _par_bond_return(y.shift(1), y).where(y.notna() & y.shift(1).notna())
    eq = eq - cash[eq.columns]
    bond = bond - cash[bond.columns]
    fx = p["fx"].pct_change(fill_method=None)
    fx = fx + cash[fx.columns].sub(cash[BASE], axis=0)
    return {"eq": eq, "bond": bond, "fx": fx}
