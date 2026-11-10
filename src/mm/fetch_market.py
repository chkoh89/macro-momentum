"""Download the tradeable series in instruments.py from Yahoo Finance.

    python -m mm.fetch_market [--start 2008-01-01] [--out data]

Writes
  data/market.csv            long: date (month-end), kind, country, ticker, value
  data/market_coverage.csv   first/last month and count per ticker
Prices are adjusted closes (splits and distributions reinvested), so ETF series
are total-return levels.
"""
import argparse
import pathlib
import sys
import time

import numpy as np
import pandas as pd

from .instruments import BOND, EQ_REF, EQUITY, FX


def fix_units(s: pd.Series) -> pd.Series:
    """Undo 100x jumps (pence vs pounds quoting on some London tickers)."""
    r = s / s.shift(1)
    step = pd.Series(0.0, index=s.index)
    step[(r > 80) & (r < 125)] = -2.0
    step[(r > 1 / 125) & (r < 1 / 80)] = 2.0
    return s * 10 ** step.cumsum()


def month_end(s: pd.Series) -> pd.Series:
    """Last close of each month; an unfinished current month is dropped."""
    m = s.resample("ME").last().dropna()
    return m[m.index <= s.index[-1] + pd.offsets.BDay(2)]


def yahoo(ticker: str, start: str, retries: int = 3):
    import yfinance as yf
    for k in range(retries):
        try:
            h = yf.Ticker(ticker).history(start=start, auto_adjust=True)
            if len(h):
                s = h["Close"].dropna()
                s.index = pd.DatetimeIndex(s.index.tz_localize(None)).normalize()
                return s[s > 0]
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2 + 2 * k)
    return None


def build(start: str, out: pathlib.Path):
    jobs = [("px_eq", c, t[0], False) for c, t in EQUITY.items()]
    jobs += [("px_bond", c, t[0], False) for c, t in BOND.items()]
    jobs += [("px_fx_yahoo", c, t[1], t[2]) for c, t in FX.items()]
    jobs += [("px_eq_ref", c, t, False) for c, t in EQ_REF.items()]
    rows, cov, failed = [], [], []
    for kind, c, ticker, invert in jobs:
        s = yahoo(ticker, start)
        if s is None or len(s) < 30:
            failed.append(ticker)
            cov.append([kind, c, ticker, "", "", 0, np.nan])
            continue
        s = fix_units(s)
        m = month_end(1 / s if invert else s)
        rows.append(pd.DataFrame({"date": m.index, "kind": kind, "country": c,
                                  "ticker": ticker, "value": m.to_numpy()}))
        cov.append([kind, c, ticker, f"{m.index[0]:%Y-%m}", f"{m.index[-1]:%Y-%m}", len(m),
                    round(float(m.pct_change().abs().max()), 3)])
        time.sleep(0.3)
    cov = pd.DataFrame(cov, columns=["kind", "country", "ticker", "first", "last", "n", "max_abs_ret"])
    core_failed = [t for t in failed if t in {v[0] for v in EQUITY.values()} | {v[0] for v in BOND.values()}]
    if core_failed:   # keep the previous file rather than write a panel with holes
        print(cov.to_string(index=False))
        sys.exit(f"download failed for traded instruments: {core_failed}")
    out.mkdir(parents=True, exist_ok=True)
    pd.concat(rows).to_csv(out / "market.csv", index=False)
    cov.to_csv(out / "market_coverage.csv", index=False)
    return cov


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2008-01-01")
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    print(build(a.start, pathlib.Path(a.out)).to_string(index=False))
