# Working in this repo (humans and agents)

- **No look-ahead.** Anything that sets a weight at month t may use data up to
  t only, after publication lags (`signals.PUB_LAG`) and `impl_lag`.
  `tests/test_pipeline.py::test_no_look_ahead` must pass.
- **No results from synthetic data.** `mm.synth` is noise for plumbing checks.
  Never quote its Sharpe ratios.
- **Every number needs a source.** Signal ids live in `src/mm/universe.py`,
  traded tickers in `src/mm/instruments.py`; deck
  slides carry a `\src{}` footer naming series and dates.
- **Report departures from the paper** in the README table when you add or
  change a signal, market or construction rule.
- **Don't tune on the test window.** Parameters come from the paper (12-month
  lookback, 3-year vol, 10% target). Variations go in a robustness table, all
  of them, not only the ones that work.
- Run `python -m pytest -q` before committing. Commit `data/panel.csv`,
  `data/market.csv`, the coverage files and `results/`; `data/raw/` is ignored.
- **This sandbox may not reach FRED or Yahoo.** Run `scripts/dispatch.sh
  data-and-backtest.yml` to fetch and backtest on GitHub, then pull.
- **Check `results/data_qa.md` after every data refresh.** A traded series
  with a low correlation to its check, or a `CHECK` flag, gets looked at
  before any result is quoted.
- Deck: LaTeX beamer, metropolis theme, 16:9, compiled with `latexmk -xelatex`
  (or pdflatex); figures as PDF in `deck/figs/`.
