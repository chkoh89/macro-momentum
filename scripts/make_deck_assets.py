"""Figures (deck/figs/*.pdf) and numbers (deck/generated/*.tex) for the deck.

    python scripts/make_deck_assets.py      # after run_backtest.py, needs data/

Everything the deck quotes is computed here from the same backtest, so a data
refresh followed by this script and `latexmk` keeps slides and results in sync.
"""
import glob
import pathlib
import sys

import matplotlib
import matplotlib.dates

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from mm.backtest import COST_BPS, costs, stats  # noqa: E402
from mm.data import load_panel  # noqa: E402
from run_backtest import MAIN, streams  # noqa: E402

FIGS, GEN = ROOT / "deck" / "figs", ROOT / "deck" / "generated"

# Reference categorical palette, slots 1-3 (validated all-pairs, light mode).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
COLORS = dict(zip(MAIN, (BLUE, ORANGE, AQUA)))
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
PAPER = "#8a8984"   # neutral marker for the paper's numbers


def setup_style():
    for f in glob.glob(str(pathlib.Path.home() / "Library/TinyTeX/texmf-dist/fonts/opentype/public/fira/FiraSans-*.otf")) \
            + glob.glob("/usr/share/fonts/**/FiraSans-*.otf", recursive=True):
        font_manager.fontManager.addfont(f)
    have_fira = any("Fira Sans" == f.name for f in font_manager.fontManager.ttflist)
    plt.rcParams.update({
        "font.family": "Fira Sans" if have_fira else "sans-serif", "font.size": 9,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "legend.frameon": False, "pdf.fonttype": 42, "axes.axisbelow": True,
        "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    })


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf")
    plt.close(fig)


def year_ticks(ax, idx):
    years = range(idx[0].year + 1, idx[-1].year + 1, 2)
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in years], [str(y) for y in years])
    ax.spines["bottom"].set_bounds(matplotlib.dates.date2num(idx[0]), matplotlib.dates.date2num(idx[-1]))


def end_label(ax, x, y, text, color, dy=0):
    ax.annotate(text, (x, y), xytext=(4, dy), textcoords="offset points", va="center",
                fontsize=8.5, color=INK, fontweight="medium")
    ax.plot([x], [y], "o", ms=4, color=color, mec="white", mew=1, zorder=5)


def fig_cumulative(df, net):
    fig, ax = plt.subplots(figsize=(5.6, 2.7))
    lines = {m: (1 + df[m]).cumprod() * 100 for m in MAIN}
    lines["Macro momentum, after costs"] = (1 + net["Macro momentum"]).cumprod() * 100
    start = df.index[0] - pd.offsets.MonthEnd(1)
    for k, s in lines.items():
        s = pd.concat([pd.Series({start: 100.0}), s])
        c = COLORS.get(k, BLUE)
        ax.plot(s.index, s, color=c, lw=2 if k in MAIN else 1.4, ls="--" if "after costs" in k else "-")
        lines[k] = s
    ax.axhline(100, color=MUTED, lw=0.8, zorder=0)
    ends = sorted(((s.iloc[-1], k) for k, s in lines.items()), reverse=True)
    last_y = None
    for y, k in ends:     # nudge labels apart
        dy = 0 if last_y is None or last_y - y > 9 else -9
        end_label(ax, lines[k].index[-1], y, f"{k} {y - 100:+.0f}%", COLORS.get(k, BLUE), dy)
        last_y = y + dy / 3
    ax.set_xlim(right=lines["Macro momentum"].index[-1] + pd.Timedelta(days=1250))
    ax.set_ylabel("value of \$100 invested")
    year_ticks(ax, lines["Macro momentum"].index)
    ax.grid(axis="x", visible=False)
    save(fig, "cumulative")


def fig_years(years):
    fig, ax = plt.subplots(figsize=(5.6, 2.5))
    x = np.arange(len(years))
    w = 0.38
    for i, m in enumerate(MAIN[:2]):
        ax.bar(x + (i - 0.5) * w, years[m] * 100, w - 0.04, color=COLORS[m], label=m)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvspan(len(years) - 5.5, len(years) - 0.5, color="#f1f0ec", zorder=0)
    ax.text(len(years) - 3, ax.get_ylim()[1] * 0.97, "from 2022", ha="center", va="top", color=INK2, fontsize=8)
    labels = [str(y) + ("*" if i in (0, len(years) - 1) else "") for i, y in enumerate(years.index)]
    ax.set_xticks(x, labels)
    ax.set_ylabel("return in the year, %")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.12)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.5, handlelength=1, borderaxespad=0.2)
    save(fig, "years")


def fig_breakdown(table):
    """Sharpe by theme, asset class and style, against the paper's."""
    rows = [("Business cycle", "MM theme: business_cycle", 0.5), ("Trade", "MM theme: trade", 0.6),
            ("Monetary policy", "MM theme: monetary", 0.9), ("Risk sentiment", "MM theme: risk", 0.7),
            None,
            ("Equities", "MM asset: eq", 0.7), ("Currencies", "MM asset: fx", 0.6),
            ("Bonds", "MM asset: bond", 0.5),
            None,
            ("Long-short", "MM style: xs", None), ("Directional", "MM style: ts", None)]
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    y, ticks, names = 0, [], []
    for r in rows:
        if r is None:
            y += 0.6
            continue
        name, key, paper = r
        v = table.loc[key, "sharpe"]
        ax.barh(y, v, 0.62, color=BLUE)
        lx = max(v, 0) + 0.03
        if paper is not None and -0.02 < paper - max(v, 0) < 0.12:
            lx = paper + 0.03
        ax.text(lx, y, f"{v:.2f}", va="center", fontsize=8, color=INK)
        if paper is not None:
            ax.plot([paper, paper], [y - 0.38, y + 0.38], color=INK2, lw=1.6, solid_capstyle="butt")
        ticks.append(y)
        names.append(name)
        y += 1
    ax.set_yticks(ticks, names)
    ax.invert_yaxis()
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlim(-0.05, 1.25)
    ax.set_xlabel("Sharpe ratio")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend([Patch(color=BLUE), Line2D([], [], color=INK2, lw=1.6)],
              ["2016 to 2026 (this test)", "1970 to 2016 (paper)"],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7.5, handlelength=1.2,
              borderaxespad=0.2)
    save(fig, "breakdown")


def fig_costs(df, pos):
    mults = np.linspace(0, 5, 21)
    fig, ax = plt.subplots(figsize=(4.4, 2.6))
    for m in MAIN:
        sh = [stats(df[m] - costs(pos[m], mult=k).reindex(df.index))["sharpe"] for k in mults]
        ax.plot(mults, sh, color=COLORS[m], lw=2)
        ax.annotate(m, (mults[-1], sh[-1]), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(1, color=INK2, lw=0.8, ls=":")
    ax.text(1.05, ax.get_ylim()[1], "our\nestimate", va="top", fontsize=7.5, color=INK2)
    ax.set_xlim(0, 7.2)
    ax.set_xticks(range(6), [f"{k}x" for k in range(6)])
    ax.set_xlabel("trading costs, as a multiple of our estimate")
    ax.set_ylabel("Sharpe ratio after costs")
    save(fig, "costs")


def fig_rollcorr(df, us_eq):
    fig, ax = plt.subplots(figsize=(5.6, 2.3))
    win = 36
    series = {"with trend following": (df["Macro momentum"].rolling(win).corr(df["Trend following"]), ORANGE),
              "with US equities": (df["Macro momentum"].rolling(win).corr(us_eq), BLUE)}
    ends = {k: s.dropna().iloc[-1] for k, (s, _) in series.items()}
    gap = abs(np.subtract(*ends.values())) < 0.15
    for i, (k, (s, c)) in enumerate(series.items()):
        s = s.dropna()
        ax.plot(s.index, s, color=c, lw=2)
        hi = s.iloc[-1] == max(ends.values())
        end_label(ax, s.index[-1], s.iloc[-1], k, c, dy=(5 if hi else -5) if gap else 0)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_ylim(-1, 1)
    ax.set_xlim(right=df.index[-1] + pd.Timedelta(days=1200))
    ax.set_ylabel(f"correlation, last {win} months")
    year_ticks(ax, df.index[win - 1:])
    ax.grid(axis="x", visible=False)
    save(fig, "rollcorr")


def write_numbers(df, net, table, ct, sens, sub, corr):
    """\\newcommand macros for every number the slide text quotes."""
    def pct(v):
        return f"{v * 100:.1f}\\%".replace("-", "$-$")

    def num(v, d=2):
        return f"{v:.{d}f}".replace("-", "$-$")
    n = {}
    keys = {"MM": "Macro momentum", "TF": "Trend following", "Mix": "50/50"}
    for k, m in keys.items():
        s = table.loc[m]
        n |= {f"{k}Ret": pct(s.ann_ret), f"{k}Vol": pct(s.ann_vol), f"{k}Sharpe": num(s.sharpe),
              f"{k}T": num(s.t_stat, 1), f"{k}DD": pct(s.max_dd)}
        sn = stats(net[m])
        n |= {f"{k}NetRet": pct(sn["ann_ret"]), f"{k}NetSharpe": num(sn["sharpe"]),
              f"{k}Turn": f"{ct.loc[m, 'turnover total']:.0f}", f"{k}Drag": pct(ct.loc[m, "drag 1x"]),
              f"{k}SharpeTwo": num(ct.loc[m, "sharpe 2x"]), f"{k}SharpeFour": num(ct.loc[m, "sharpe 4x"]),
              f"{k}FirstHalf": num(sub.loc[m, "to Dec 2021"]), f"{k}SecondHalf": num(sub.loc[m, "from Jan 2022"])}
    n |= {"MMBondTurn": f"{ct.loc['Macro momentum', 'turnover bond']:.0f}",
          "MMFxTurn": f"{ct.loc['Macro momentum', 'turnover fx']:.0f}",
          "MMEqTurn": f"{ct.loc['Macro momentum', 'turnover eq']:.0f}",
          "CorrMMTF": num(corr.loc["Macro momentum", "Trend following"]),
          "CorrMMEq": num(corr.loc["Macro momentum", "US equities"]),
          "CorrMMBond": num(corr.loc["Macro momentum", "US bonds"]),
          "Start": df.index[0].strftime("%b %Y"), "End": df.index[-1].strftime("%b %Y"),
          "Months": str(len(df)),
          "SharpeSE": num(np.sqrt((1 + 0.5 * table.loc["Macro momentum", "sharpe"] ** 2) / (len(df) / 12))),
          "CostEq": f"{COST_BPS['eq']:g}", "CostBond": f"{COST_BPS['bond']:g}", "CostFx": f"{COST_BPS['fx']:g}"}
    for k, label in {"Bond": "MM asset: bond", "Fx": "MM asset: fx", "Eq": "MM asset: eq",
                     "Cycle": "MM theme: business_cycle", "Trade": "MM theme: trade",
                     "Monetary": "MM theme: monetary", "Risk": "MM theme: risk",
                     "XS": "MM style: xs", "TS": "MM style: ts"}.items():
        n[f"MM{k}Sharpe"] = num(table.loc[label, "sharpe"])
    for _, r in sens[sens.returns == "market"].iterrows():
        w = ["Zero", "One", "Two"][int(r.impl_lag)]
        n[f"MMLag{w}"] = num(r["Macro momentum"])
        n[f"MMLag{w}Net"] = num(r["Macro momentum net"])
    lines = ["% generated by scripts/make_deck_assets.py, do not edit"]
    lines += [f"\\newcommand{{\\n{k}}}{{{v}}}" for k, v in n.items()]
    (GEN / "numbers.tex").write_text("\n".join(lines) + "\n")


def write_tables(df, net, table, sens):
    def row(name, s, bold=False):
        cells = [f"{s['ann_ret'] * 100:.1f}\\%", f"{s['ann_vol'] * 100:.1f}\\%", f"{s['sharpe']:.2f}",
                 f"{s['t_stat']:.1f}", f"{s['max_dd'] * 100:.1f}\\%", f"{s['hit'] * 100:.0f}\\%"]
        cells = [c.replace("-", "$-$") for c in cells]
        if bold:
            cells = [f"\\textbf{{{c}}}" for c in cells]
        return f"{name} & " + " & ".join(cells) + r" \\"
    out = [r"\begin{tabular}{l rrrrrr}", r"\toprule",
           r" & Return per year & Risk (volatility) & Sharpe ratio & $t$-stat & Worst fall & Months up \\",
           r"\midrule"]
    for m in MAIN:
        out.append(row(m, table.loc[m], bold=(m == "Macro momentum")))
    out.append(r"\midrule")
    for m in MAIN:
        out.append(row(f"{m}, after costs", pd.Series(stats(net[m]))))
    out += [r"\bottomrule", r"\end{tabular}"]
    (GEN / "headline.tex").write_text("\n".join(out) + "\n")

    s = sens[sens.returns == "market"]
    out = [r"\begin{tabular}{l rrr rr}", r"\toprule",
           r"Trade & \multicolumn{3}{c}{Sharpe ratio, before costs} & \multicolumn{2}{c}{after costs} \\",
           r"\cmidrule(lr){2-4}\cmidrule(lr){5-6}",
           r" & Macro mom. & Trend & 50/50 & Macro mom. & Trend \\", r"\midrule"]
    for _, r in s.iterrows():
        lab = {0: "right away", 1: "one month late", 2: "two months late"}[int(r.impl_lag)]
        v = [r["Macro momentum"], r["Trend following"], r["50/50"], r["Macro momentum net"], r["Trend following net"]]
        out.append(lab + " & " + " & ".join(f"{x:.2f}".replace("-", "$-$") for x in v) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}"]
    (GEN / "lag.tex").write_text("\n".join(out) + "\n")


def main():
    FIGS.mkdir(parents=True, exist_ok=True)
    GEN.mkdir(parents=True, exist_ok=True)
    setup_style()
    panel = load_panel(ROOT / "data/panel.csv", ROOT / "data/market.csv")
    df, mm, pos = streams(panel, 0, "market", 120)
    net = {m: df[m] - costs(pos[m]).reindex(df.index) for m in MAIN}
    table = pd.DataFrame({k: stats(df[k]) for k in df}).T
    years = df[MAIN].groupby(df.index.year).apply(lambda x: (1 + x).prod() - 1)
    us_eq = mm["asset_returns"]["eq"]["US"].reindex(df.index)
    res = ROOT / "results"
    ct = pd.read_csv(res / "costs.csv", index_col=0)
    sens = pd.read_csv(res / "sensitivity.csv")
    corr = pd.read_csv(res / "correlations.csv", index_col=0)
    halves = {"to Dec 2021": df.loc[:"2021-12"], "from Jan 2022": df.loc["2022-01":]}
    sub = pd.DataFrame({k: {m: stats(v[m])["sharpe"] for m in MAIN} for k, v in halves.items()})
    # Guard: the deck must describe the same run as results/.
    assert abs(ct.loc["Macro momentum", "sharpe 0x"] - table.loc["Macro momentum", "sharpe"]) < 1e-9, \
        "results/ is stale: run scripts/run_backtest.py first"

    fig_cumulative(df, net)
    fig_years(years)
    fig_breakdown(table)
    fig_costs(df, pos)
    fig_rollcorr(df, us_eq)
    write_numbers(df, net, table, ct, sens, sub, corr)
    write_tables(df, net, table, sens)
    print("wrote", sorted(p.name for p in FIGS.glob("*.pdf")), sorted(p.name for p in GEN.glob("*.tex")))


if __name__ == "__main__":
    main()
