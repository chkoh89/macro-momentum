"""Macro momentum and the trend-following benchmark."""
import numpy as np
import pandas as pd

from . import portfolio as pf
from .data import asset_returns
from .signals import THEMES, asset_signal, macro_trends

ASSETS = ["eq", "bond", "fx"]
STYLES = {"xs": pf.xs_weights, "ts": pf.ts_weights}


def _avg(streams, scale=True):
    x = pd.concat(streams, axis=1).mean(axis=1, skipna=False)
    return pf.target_vol(x) if scale else x


def macro_momentum(panel: dict, impl_lag: int = 1) -> dict:
    """Returns {"sleeves": DataFrame of (asset, theme, style) portfolios at 10%
    vol, "by_theme", "by_asset", "total"}.

    impl_lag: extra months between observing a signal and trading on it.
    Default 1 because the free price data are monthly averages: a signal built
    from average-of-month prices must not trade the same month's average.
    """
    rets = asset_returns(panel)
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
                    parts.append(pf.target_vol(pf.pnl(wfun(sig, vol), rets[a])))
                sleeves[(a, theme, style)] = parts[0] if len(parts) == 1 else _avg(parts)
    s = pd.DataFrame(sleeves)
    s.columns.names = ["asset", "theme", "style"]
    by_theme = pd.DataFrame({t: _avg([s[c] for c in s.columns if c[1] == t]) for t in THEMES})
    by_asset = pd.DataFrame({a: _avg([s[c] for c in s.columns if c[0] == a]) for a in ASSETS})
    return {"sleeves": s, "by_theme": by_theme, "by_asset": by_asset,
            "total": _avg([s[c] for c in s.columns]), "asset_returns": rets}


def trend_following(panel: dict, impl_lag: int = 1) -> dict:
    """Time-series momentum on the same markets: equal blend of the sign of the
    1-, 3- and 12-month excess return, equal-volatility sizing."""
    rets = asset_returns(panel)
    out = {}
    for a in ASSETS:
        r = rets[a]
        sig = sum(np.sign(r.rolling(k, min_periods=k).sum()) for k in (1, 3, 12)) / 3
        w = pf.ts_weights(sig.shift(impl_lag), pf.ann_vol(r))
        out[a] = pf.target_vol(pf.pnl(w, r))
    by_asset = pd.DataFrame(out)
    return {"by_asset": by_asset, "total": _avg([by_asset[a] for a in ASSETS])}


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
