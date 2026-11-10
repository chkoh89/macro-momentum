"""Download the FRED series in universe.py and build data/panel.csv.

    python -m mm.fetch [--start 2005-01-01] [--out data]

Needs network access to fred.stlouisfed.org. Writes
  data/raw/<ID>.csv   one file per series as downloaded
  data/panel.csv      long format: date (month-end), field, country, value
  data/coverage.csv   which candidate id was used, first/last date, n obs
"""
import argparse
import pathlib
import time

import pandas as pd

from .universe import COUNTRIES, FIELDS, candidates

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}"


def fred(sid: str, start: str, retries: int = 2):
    for k in range(retries + 1):
        try:
            df = pd.read_csv(URL.format(sid=sid, start=start), na_values=".")
            break
        except Exception:
            if k == retries:
                return None
            time.sleep(1 + k)
    if df.shape[1] != 2 or df.empty:
        return None
    s = pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(),
                  index=pd.to_datetime(df.iloc[:, 0]), name=sid).dropna()
    return s if len(s) else None


def to_monthly(s: pd.Series, freq: str, transform):
    """Raw FRED series -> month-end series. Quarterly values sit on the last
    month of their quarter and are carried forward (publication lags are
    applied later, in signals.py)."""
    if transform == "inv":
        s = 1.0 / s
    if transform == "yoy":
        s = 100 * (s / s.shift({"M": 12, "Q": 4}[freq]) - 1)
    if freq == "D":   # month-end value; an unfinished current month is dropped
        m = s.resample("ME").last().dropna()
        return m[m.index <= s.index[-1] + pd.offsets.BDay(1)]
    if freq == "M":
        s.index = s.index + pd.offsets.MonthEnd(0)
        return s.dropna()
    s.index = s.index + pd.offsets.MonthEnd(3)       # quarter start -> quarter end
    return s.dropna().resample("ME").last().ffill(limit=5).dropna()


def build(start: str, out: pathlib.Path):
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    rows, cov = [], []
    for field in FIELDS:
        for c in COUNTRIES:
            best, tried = None, []
            for sid, freq, tr in candidates(field, c):
                s = fred(sid, start)
                if s is None:
                    continue
                s.to_csv(raw / f"{sid}.csv", header=["value"], index_label="date")
                m = to_monthly(s, freq, tr)
                if m.empty:
                    continue
                tried.append(f"{sid}:{m.index[-1]:%Y-%m}")
                if best is None or m.index[-1] > best[1].index[-1]:
                    best = (sid, m)
            if best:
                sid, m = best
                rows.append(pd.DataFrame({"date": m.index, "field": field,
                                          "country": c, "value": m.to_numpy()}))
                cov.append([field, c, sid, m.index[0].date(), m.index[-1].date(), len(m),
                            " ".join(tried)])
            elif candidates(field, c):
                cov.append([field, c, "MISSING", "", "", 0, ""])
    pd.concat(rows).to_csv(out / "panel.csv", index=False)
    cov = pd.DataFrame(cov, columns=["field", "country", "fred_id", "first", "last", "n", "found"])
    cov.to_csv(out / "coverage.csv", index=False)
    return cov


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2005-01-01")
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    cov = build(a.start, pathlib.Path(a.out))
    print(cov.drop(columns="found").to_string(index=False))
    print(f"\nmissing: {(cov.fred_id == 'MISSING').sum()} of {len(cov)}")
