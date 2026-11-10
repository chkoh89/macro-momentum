import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from mm import portfolio as pf  # noqa: E402
from mm.backtest import macro_momentum, trend_following  # noqa: E402
from mm.data import _par_bond_return  # noqa: E402
from mm.synth import make_panel  # noqa: E402


def test_runs_and_hits_vol_target():
    for source in ("market", "fred"):
        mm = macro_momentum(make_panel(), source=source)
        tf = trend_following(make_panel(), source=source)
        assert mm["sleeves"].shape[1] == 3 * 4 * 2
        for x in (mm["total"], tf["total"]):
            x = x.dropna()
            assert len(x) > 120
            assert 0.06 < x.std() * np.sqrt(12) < 0.15


def test_no_look_ahead():
    """Changing data after month T must not change any P&L up to T."""
    base = make_panel()
    cut = base["eq"].index[200]
    other = {k: v.copy() for k, v in base.items()}
    rng = np.random.default_rng(1)
    for v in other.values():
        late = v.index > cut
        v.loc[late] = v.loc[late] * (1 + rng.normal(0, 0.2, v.loc[late].shape))
    for fn in (macro_momentum, trend_following):
        for lag in (0, 1):
            a, b = fn(base, impl_lag=lag), fn(other, impl_lag=lag)
            pd.testing.assert_series_equal(a["total"].loc[:cut], b["total"].loc[:cut])
    pd.testing.assert_frame_equal(macro_momentum(base)["sleeves"].loc[:cut],
                                  macro_momentum(other)["sleeves"].loc[:cut])


def test_long_short_weights_sum_to_zero_before_vol_scaling():
    sig = pd.DataFrame(np.random.default_rng(2).normal(size=(5, 6)))
    w = pf.xs_weights(sig, pd.DataFrame(1.0, index=sig.index, columns=sig.columns))
    assert np.allclose(w.sum(axis=1), 0) and np.allclose(w.abs().sum(axis=1), 1)


def test_par_bond_return():
    y0 = pd.DataFrame({"a": [0.05, 0.05, 0.0]})
    y1 = pd.DataFrame({"a": [0.05, 0.06, 0.0]})
    r = _par_bond_return(y0, y1)["a"]
    assert abs(r[0] - 0.05 / 12) < 1e-12          # unchanged yield: carry only
    assert -0.075 < r[1] - 0.05 / 12 < -0.070     # +100bp on a 10y at 5%: about -7.4%
    assert abs(r[2]) < 1e-12                      # zero yields handled


def test_unit_fix_and_month_end():
    from mm.fetch_market import fix_units, month_end
    idx = pd.bdate_range("2024-01-01", "2024-03-15")
    s = pd.Series(10.0, index=idx)
    s.loc["2024-02-01":] *= 100          # ticker flips from pounds to pence
    assert np.allclose(fix_units(s), 10.0)
    m = month_end(s)
    assert list(m.index.strftime("%Y-%m")) == ["2024-01", "2024-02"]   # March unfinished
