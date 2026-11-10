"""Run macro momentum vs trend following and write results/.

    python scripts/run_backtest.py                 # real data from data/panel.csv
    python scripts/run_backtest.py --synthetic     # random data, plumbing check only
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from mm.backtest import macro_momentum, stats, trend_following  # noqa: E402
from mm.data import load_panel  # noqa: E402
from mm.signals import macro_trends  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/panel.csv")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--months", type=int, default=120, help="evaluation window, most recent months")
    ap.add_argument("--impl-lag", type=int, default=1)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    if a.synthetic:
        from mm.synth import make_panel
        panel, tag = make_panel(), "SYNTHETIC RANDOM DATA: plumbing check, not a result"
    else:
        panel, tag = load_panel(a.panel), "FRED data"
    mm, tf = macro_momentum(panel, a.impl_lag), trend_following(panel, a.impl_lag)

    streams = {"Macro momentum": mm["total"], "Trend following": tf["total"],
               "50/50": (mm["total"] + tf["total"]) / 2}
    streams |= {f"MM theme: {k}": v for k, v in mm["by_theme"].items()}
    streams |= {f"MM asset: {k}": v for k, v in mm["by_asset"].items()}
    streams |= {f"TF asset: {k}": v for k, v in tf["by_asset"].items()}
    df = pd.DataFrame(streams).dropna(subset=["Macro momentum", "Trend following"]).tail(a.months)

    table = pd.DataFrame({k: stats(df[k]) for k in df}).T
    us = pd.DataFrame({"US equities": mm["asset_returns"]["eq"]["US"],
                       "US 10y bonds": mm["asset_returns"]["bond"]["US"]}).reindex(df.index)
    corr = pd.concat([df[["Macro momentum", "Trend following"]], us], axis=1).corr()

    out = pathlib.Path(a.out)
    out.mkdir(exist_ok=True)
    df.to_csv(out / "returns.csv")
    table.to_csv(out / "stats.csv")
    corr.to_csv(out / "correlations.csv")
    fmt = {"ann_ret": "{:.1%}", "ann_vol": "{:.1%}", "sharpe": "{:.2f}", "t_stat": "{:.2f}",
           "max_dd": "{:.1%}", "hit": "{:.0%}"}
    show = table.copy()
    for c, f in fmt.items():
        show[c] = show[c].map(lambda v: f.format(v))
    main3 = ["Macro momentum", "Trend following", "50/50"]
    halves = {"2021 and earlier": df.loc[:"2021-12"], "2022 onward": df.loc["2022-01":]}
    sub = pd.DataFrame({k: {m: stats(v[m]).get("sharpe", float("nan")) for m in main3}
                        for k, v in halves.items()}).round(2)
    trends = macro_trends(panel, mm["asset_returns"]["eq"])
    live = pd.DataFrame({k: v.reindex(df.index).notna().sum(axis=1).iloc[[0, len(df) // 2, -1]]
                         for k, v in trends.items()})
    live.index = live.index.strftime("%Y-%m")
    md = [f"# Backtest summary ({tag})", "",
          f"Implementation lag: {a.impl_lag} month(s). Gross of costs. Excess returns, each stream targeted at 10% volatility.",
          "", show.to_markdown(), "", "## Sharpe ratio by sub-period", "", sub.to_markdown(),
          "", "## Correlations", "", corr.round(2).to_markdown(),
          "", "## Countries with a live signal (of 10)", "", live.to_markdown(), ""]
    (out / "summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
