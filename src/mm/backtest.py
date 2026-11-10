"""Macro momentum and the trend-following benchmark.

Every return stream is carried together with the positions that produce it
(`Stream`), so turnover and transaction costs can be measured on the final,
vol-targeted portfolio and not only on its building blocks.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import portfolio as pf
from .data import asset_returns
from .signals import THEMES, asset_signal, macro_trends

ASSETS = ["eq", "bond", "fx"]
STYLES = {"xs": pf.xs_weights, "ts": pf.ts_weights}

# One-way cost per unit of notional traded, by asset class. An assumption, not
# a measurement: roughly the half-spread plus impact of liquid developed-market
# futures and FX forwards, on the high side of what trend-following studies
# use. Cash indices, bond ETFs and spot FX in this repo stand in for those
# futures; trading the ETFs themselves would cost more. See README.
COST_BPS = {"eq": 4.0, "bond": 3.0, "fx": 3.0}


@dataclass
class Stream:
    """Monthly excess return and the positions behind it.

    pos[asset].loc[t] is the weight per unit of NAV held over month t (set at
    the end of t-1), so ret[t] == sum over assets and markets of pos * r at t.
    """
    ret: pd.Series
    pos: dict

    def scaled(self, k: pd.Series) -> "Stream":
        return Stream(self.ret * k, {a: p.mul(k, axis=0) for a, p in self.pos.items()})

    def target_vol(self) -> "Stream":
        return self.scaled(pf.vol_scale(self.ret))


def _leaf(w: pd.DataFrame, r: pd.DataFrame, asset: str) -> Stream:
    held = w.shift(1)
    return Stream(pf.pnl(w, r), {asset: held})


def _avg(streams, scale=True, min_share=0.75) -> Stream:
    """Equal-weight the streams that are live; blank if fewer than min_share are."""
    df = pd.concat([s.ret for s in streams], axis=1)
    live = df.notna()
    ok = live.mean(axis=1) >= min_share
    n = live.sum(axis=1).where(ok)
    ret = df.mean(axis=1).where(ok)
    pos = {}
    for i, s in enumerate(streams):
        on = live.iloc[:, i]
        for a, p in s.pos.items():
            part = p.where(on, axis=0).fillna(0.0).div(n, axis=0)
            pos[a] = part if a not in pos else pos[a].add(part, fill_value=0.0)
    out = Stream(ret, pos)
    return out.target_vol() if scale else out


def macro_momentum(panel: dict, impl_lag: int = 0, source: str | None = None) -> dict:
    """Returns {"sleeves": DataFrame of (asset, theme, style) portfolios at 10%
    vol, "by_theme", "by_asset", "total", "positions", "asset_returns"}.

    impl_lag: extra months between observing a signal and trading on it. 0 is
    right for month-end tradeable prices (trade at the close the signal is
    measured on). Use at least 1 with source="fred": those prices are monthly
    averages, and a signal built from an average must not trade that average.
    """
    rets = asset_returns(panel, source)
    trends = macro_trends(panel, rets["eq"])
    # Directional risk-sentiment signals are measured against their expanding
    # mean, since one-year equity returns are positive on average.
    trends_ts = dict(trends, risk=trends["risk"] - trends["risk"].expanding(12).mean())
    sleeves = {}
    for a in ASSETS:
        vol = pf.ann_vol(rets[a])
        for theme, variables in THEMES.items():
            for style, wfun in STYLES.items():
                src = trends_ts if style == "ts" else trends
                parts = []
                for v in variables:
                    sig = asset_signal(src[v], a, v).shift(impl_lag)
                    sig = sig.reindex(columns=rets[a].columns)
                    parts.append(_leaf(wfun(sig, vol), rets[a], a).target_vol())
                sleeves[(a, theme, style)] = parts[0] if len(parts) == 1 else _avg(parts, min_share=0.5)
    s = pd.DataFrame({k: v.ret for k, v in sleeves.items()})
    s.columns.names = ["asset", "theme", "style"]
    by_theme = {t: _avg([v for k, v in sleeves.items() if k[1] == t]) for t in THEMES}
    by_asset = {a: _avg([v for k, v in sleeves.items() if k[0] == a]) for a in ASSETS}
    total = _avg(list(sleeves.values()))
    return {"sleeves": s,
            "by_theme": pd.DataFrame({k: v.ret for k, v in by_theme.items()}),
            "by_asset": pd.DataFrame({k: v.ret for k, v in by_asset.items()}),
            "total": total.ret, "positions": total.pos, "asset_returns": rets}


def trend_following(panel: dict, impl_lag: int = 0, source: str | None = None) -> dict:
    """Time-series momentum on the same markets: equal blend of the sign of the
    1-, 3- and 12-month excess return, equal-volatility sizing."""
    rets = asset_returns(panel, source)
    out = {}
    for a in ASSETS:
        r = rets[a]
        sig = sum(np.sign(r.rolling(k, min_periods=k).sum()) for k in (1, 3, 12)) / 3
        w = pf.ts_weights(sig.shift(impl_lag), pf.ann_vol(r))
        out[a] = _leaf(w, r, a).target_vol()
    total = _avg(list(out.values()))
    return {"by_asset": pd.DataFrame({k: v.ret for k, v in out.items()}),
            "total": total.ret, "positions": total.pos, "asset_returns": rets}


def blend(*results, weights=None) -> dict:
    """Fixed-weight mix of strategy results (no re-targeting), positions included."""
    weights = weights or [1 / len(results)] * len(results)
    ret = sum(w * r["total"] for w, r in zip(weights, results))
    pos = {}
    for w, r in zip(weights, results):
        for a, p in r["positions"].items():
            pos[a] = p * w if a not in pos else pos[a].add(p * w, fill_value=0.0)
    return {"total": ret, "positions": pos}


def turnover(pos: dict) -> pd.DataFrame:
    """Notional traded each month (sum of |change in weight|), per asset class,
    as a fraction of NAV. Trades at the end of t-1 are booked in month t."""
    return pd.DataFrame({a: p.fillna(0.0).diff().abs().sum(axis=1) for a, p in pos.items()})


def costs(pos: dict, bps: dict = COST_BPS, mult: float = 1.0) -> pd.Series:
    """Monthly transaction cost as a return drag."""
    t = turnover(pos)
    return sum(t[a] * bps[a] * mult / 1e4 for a in t)


def stats(x: pd.Series) -> dict:
    x = x.dropna()
    if len(x) < 12:
        return {}
    mu, sd = x.mean() * 12, x.std() * np.sqrt(12)
    cum = (1 + x).cumprod()
    return {"start": x.index[0].strftime("%Y-%m"), "end": x.index[-1].strftime("%Y-%m"),
            "months": len(x), "ann_ret": mu, "ann_vol": sd, "sharpe": mu / sd,
            "t_stat": mu / sd * np.sqrt(len(x) / 12),
            "max_dd": (cum / cum.cummax() - 1).min(), "hit": (x > 0).mean()}
