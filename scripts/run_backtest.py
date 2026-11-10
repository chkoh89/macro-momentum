"""Run macro momentum vs trend following and write results/.

    python scripts/run_backtest.py                 # tradeable returns, FRED signals
    python scripts/run_backtest.py --source fred   # v0: non-tradeable FRED/OECD returns
    python scripts/run_backtest.py --synthetic     # random data, plumbing check only
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from mm.backtest import COST_BPS, blend, costs, macro_momentum, stats, trend_following, turnover  # noqa: E402
from mm.data import load_panel  # noqa: E402
from mm.signals import macro_trends  # noqa: E402

MAIN = ["Macro momentum", "Trend following", "50/50"]


def streams(panel, impl_lag, source, months):
    mm = macro_momentum(panel, impl_lag, source)
    tf = trend_following(panel, impl_lag, source)
    s = {"Macro momentum": mm["total"], "Trend following": tf["total"],
         "50/50": (mm["total"] + tf["total"]) / 2}
    s |= {f"MM theme: {k}": v for k, v in mm["by_theme"].items()}
    s |= {f"MM asset: {k}": v for k, v in mm["by_asset"].items()}
    s |= {f"MM style: {k}": mm["sleeves"].xs(k, axis=1, level="style").mean(axis=1) for k in ("xs", "ts")}
    s |= {f"TF asset: {k}": v for k, v in tf["by_asset"].items()}
    df = pd.DataFrame(s).dropna(subset=MAIN).tail(months)
    pos = {"Macro momentum": mm["positions"], "Trend following": tf["positions"],
           "50/50": blend(mm, tf)["positions"]}
    return df, mm, pos


COST_MULTS = (0, 1, 2, 4)


def cost_table(df, pos):
    """Turnover, cost drag and net Sharpe for each main strategy over df's window."""
    rows = []
    for m in MAIN:
        t = turnover(pos[m]).reindex(df.index)
        row = {"strategy": m, **{f"turnover {a}": t[a].mean() * 12 for a in t},
               "turnover total": t.sum(axis=1).mean() * 12}
        for k in COST_MULTS:
            c = costs(pos[m], mult=k).reindex(df.index)
            if k == 1:
                row["drag 1x"] = c.mean() * 12
            row[f"sharpe {k}x"] = stats(df[m] - c).get("sharpe", float("nan"))
        rows.append(row)
    return pd.DataFrame(rows).set_index("strategy")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/panel.csv")
    ap.add_argument("--market", default="data/market.csv")
    ap.add_argument("--source", choices=["market", "fred"], default=None)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--months", type=int, default=120, help="evaluation window, most recent months")
    ap.add_argument("--impl-lag", type=int, default=None)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    if a.synthetic:
        from mm.synth import make_panel
        panel, tag = make_panel(), "SYNTHETIC RANDOM DATA: plumbing check, not a result"
    else:
        panel, tag = load_panel(a.panel, a.market), "real data"
    source = a.source or ("market" if "px_eq" in panel else "fred")
    lag = a.impl_lag if a.impl_lag is not None else (0 if source == "market" else 1)
    df, mm, pos = streams(panel, lag, source, a.months)
    ct = cost_table(df, pos)
    net = {m: df[m] - costs(pos[m]).reindex(df.index) for m in MAIN}

    table = pd.DataFrame({k: stats(df[k]) for k in df}
                         | {f"{m} (net, 1x costs)": stats(net[m]) for m in MAIN}).T
    us = pd.DataFrame({"US equities": mm["asset_returns"]["eq"]["US"],
                       "US bonds": mm["asset_returns"]["bond"]["US"]}).reindex(df.index)
    corr = pd.concat([df[MAIN[:2]], us], axis=1).corr()
    halves = {"to Dec 2021": df.loc[:"2021-12"], "from Jan 2022": df.loc["2022-01":]}
    sub = pd.DataFrame({k: {m: stats(v[m]).get("sharpe", float("nan")) for m in MAIN}
                        for k, v in halves.items()}).round(2)
    years = df[MAIN].groupby(df.index.year).apply(lambda x: (1 + x).prod() - 1)

    # Sensitivity: every combination, not only the ones that look good.
    sens = []
    for src in (["market", "fred"] if "px_eq" in panel and "eq" in panel else [source]):
        for lg in (0, 1, 2):
            d, _, ps = streams(panel, lg, src, a.months)
            note = "look-ahead: averaged prices" if (src == "fred" and lg == 0) else ""
            sens.append({"returns": src, "impl_lag": lg, "months": len(d),
                         **{m: round(stats(d[m]).get("sharpe", float("nan")), 2) for m in MAIN},
                         **{f"{m} net": round(stats(d[m] - costs(ps[m]).reindex(d.index)).get("sharpe", float("nan")), 2)
                            for m in MAIN[:2]},
                         "corr MM/TF": round(d[MAIN[0]].corr(d[MAIN[1]]), 2), "note": note})
    sens = pd.DataFrame(sens)

    trends = macro_trends(panel, mm["asset_returns"]["eq"])
    live = pd.DataFrame({k: v.reindex(df.index).notna().sum(axis=1).iloc[[0, len(df) // 2, -1]]
                         for k, v in trends.items()})
    live.index = live.index.strftime("%Y-%m")
    n_assets = pd.Series({k: int(v.reindex(df.index).notna().iloc[[0, -1]].sum(axis=1).max())
                          for k, v in mm["asset_returns"].items()})

    out = pathlib.Path(a.out)
    out.mkdir(exist_ok=True)
    df.to_csv(out / "returns.csv")
    table.to_csv(out / "stats.csv")
    corr.to_csv(out / "correlations.csv")
    sens.to_csv(out / "sensitivity.csv", index=False)
    years.to_csv(out / "calendar_years.csv")
    ct.to_csv(out / "costs.csv")
    ctab = ct.copy()
    for c in ctab:
        ctab[c] = ctab[c].map(("{:.1f}x" if c.startswith("turnover") else
                               "{:.2%}" if c.startswith("drag") else "{:.2f}").format)
    show = table.copy()
    for c, f in {"ann_ret": "{:.1%}", "ann_vol": "{:.1%}", "sharpe": "{:.2f}", "t_stat": "{:.2f}",
                 "max_dd": "{:.1%}", "hit": "{:.0%}"}.items():
        show[c] = show[c].map(lambda v: f.format(v))
    md = [f"# Backtest summary ({tag})", "",
          f"Returns: `{source}`. Implementation lag: {lag} month(s). Gross of costs unless marked net. "
          "Excess returns; each stream is targeted at 10% volatility. Markets traded: "
          + ", ".join(f"{k} {v}" for k, v in n_assets.items()) + ".",
          "", show.to_markdown(),
          "", "## Turnover and transaction costs", "",
          "Turnover is notional traded per year as a multiple of NAV, measured on the final "
          "vol-targeted portfolio (offsetting trades across sleeves net out). Costs are one-way, "
          "per unit of notional: " + ", ".join(f"{k} {v:g}bp" for k, v in COST_BPS.items())
          + " (1x), an assumption for futures and forwards; see README. Sharpe ratios net of "
          "0x to 4x those costs; vol not re-targeted after costs.",
          "", ctab.to_markdown(),
          "", "## Sharpe ratio by sub-period", "", sub.to_markdown(),
          "", "## Calendar-year returns", "", years.map("{:.1%}".format).to_markdown(),
          "", "## Sensitivity (Sharpe ratio, same window length; net = 1x costs)", "", sens.to_markdown(index=False),
          "", "## Correlations", "", corr.round(2).to_markdown(),
          "", "## Countries with a live signal (of 10)", "", live.to_markdown(), ""]
    (out / "summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
