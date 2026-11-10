"""Check each traded series against an independent one. Writes results/data_qa.md.

  equities  index (local) vs US-listed country ETF converted back to local currency
  bonds     ETF total return vs return implied by the FRED 10y yield (monthly average)
  fx        Fed H.10 month-end vs Yahoo month-end
A low correlation or a large monthly move is a reason to open the raw data.
"""
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from mm.data import _par_bond_return, load_panel  # noqa: E402
from mm.instruments import BOND, EQ_REF, EQUITY, FX  # noqa: E402

p = load_panel()
r = lambda x: x.pct_change(fill_method=None)  # noqa: E731
fx = r(p["fx"])
eq, bond = r(p["px_eq"]), r(p["px_bond"])
ref_usd = r(p["px_eq_ref"])
ref_eq = ref_usd.copy()
for c in fx.columns:
    ref_eq[c] = (1 + ref_usd[c]) / (1 + fx[c]) - 1
y = p["y10"] / 100
ref_bond = _par_bond_return(y.shift(1), y)
ref_fx = r(p["px_fx_yahoo"])

rows = []


def add(asset, c, ticker, name, x, ref, ref_name, limit):
    d = pd.concat([x, ref], axis=1, keys=["x", "ref"]).loc["2014-01":].dropna()
    xs = x.dropna()
    rows.append({"asset": asset, "country": c, "ticker": ticker, "name": name,
                 "first": f"{xs.index[0]:%Y-%m}", "last": f"{xs.index[-1]:%Y-%m}",
                 "ann_ret": f"{xs.loc['2016-11':].mean() * 12:.1%}",
                 "ann_vol": f"{xs.loc['2016-11':].std() * np.sqrt(12):.1%}",
                 "worst_month": f"{xs.min():.1%}", "best_month": f"{xs.max():.1%}",
                 "check_vs": ref_name, "corr": round(d["x"].corr(d["ref"]), 2) if len(d) > 24 else np.nan,
                 "ann_gap": f"{(d['x'] - d['ref']).mean() * 12:+.1%}" if len(d) > 24 else "",
                 "flag": "CHECK" if xs.abs().max() > limit else ""})


for c, (t, name, _, _) in EQUITY.items():
    add("eq", c, t, name, eq[c], ref_eq[c], f"{EQ_REF[c]} in local ccy", 0.25)
for c, (t, name, _) in BOND.items():
    add("bond", c, t, name, bond[c], ref_bond[c], "FRED 10y yield-implied", 0.10)
for c, (pair, t, _) in FX.items():
    add("fx", c, pair, "Fed H.10 month-end", fx[c], ref_fx[c], f"Yahoo {t}", 0.15)

qa = pd.DataFrame(rows)
out = pathlib.Path("results")
out.mkdir(exist_ok=True)
md = ["# Data check: traded series", "",
      "Raw (not excess) monthly returns. `ann_ret`, `ann_vol` from Nov 2016; `corr` and `ann_gap` "
      "(series minus check, per year) from 2014. Equity gaps are mostly dividends for price indices; "
      "bond correlations are held down by the check using monthly-average yields.", "",
      qa.to_markdown(index=False), ""]
(out / "data_qa.md").write_text("\n".join(md))
print("\n".join(md))
