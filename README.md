# macro-momentum

Does macro momentum still work? A simple, free-data replication of
Brooks, *A Half Century of Macro Momentum* (AQR, 2017) over the last ten years,
compared with trend following on the same markets.

Paper: https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/A-Half-Century-of-Macro-Momentum.pdf

## Goal

1. **Explain** the four macro themes (business cycle, international trade,
   monetary policy, risk sentiment) and how each should move equities,
   currencies and bonds (the paper's Exhibit 1).
2. **Replicate** a simple version of the strategy with the paper's own signals
   and test it out of sample: the paper's data end in 2016, ours start there.
3. **Compare** macro momentum with price trend following, alone and combined.

## Deliverables

| # | Deliverable | Where | Status |
|---|---|---|---|
| 1 | Slide deck (LaTeX beamer, metropolis, compiled to PDF, with data sources and diagrams) | `deck/` | not started |
| 2 | Backtest | `src/mm/`, `scripts/run_backtest.py`, `results/` | code and tests done; **not yet run on real data** |

## Status (2026-11-09)

- Backtest engine written and tested on synthetic data (4 tests, including a
  look-ahead test).
- **No real results yet.** The environment this was built in cannot reach
  FRED. Run the two commands below anywhere with internet, or trigger the
  `data-and-backtest` GitHub Action, which fetches the data, runs the backtest
  and commits `data/panel.csv` and `results/`.
- Some FRED ids in `src/mm/universe.py` are unverified. The first fetch writes
  `data/coverage.csv`; fix any `MISSING` rows before trusting results.

## Quick start

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m mm.fetch          # downloads ~70 FRED series, no API key
python scripts/run_backtest.py             # writes results/summary.md, stats.csv, returns.csv
python -m pytest -q                        # plumbing and look-ahead tests
python scripts/run_backtest.py --synthetic --out /tmp/x   # dry run on random data
```

## The strategy in one table

Go long assets whose macro trend is improving, short those where it is
deteriorating. Every signal is a one-year change. Sign = position when the
variable is rising.

| Theme | Variable (1y change) | Paper | This repo (v0) | Equities | Currencies | 10y bonds |
|---|---|---|---|:-:|:-:|:-:|
| Business cycle | real GDP growth | consensus forecasts | realised yoy growth, 3m lag | + | + | − |
| Business cycle | CPI inflation | consensus forecasts | realised yoy CPI, 2m lag | − | + | − |
| International trade | trade-weighted FX, appreciation | export-weighted spot | BIS broad nominal EER | − | + | + |
| Monetary policy | short rate, tightening | 2y yield | 3m interbank rate | − | + | − |
| Risk sentiment | equity excess return | 1y equity return | same | + | + | − |

The paper states the trade row as depreciation (equities +, currencies −,
bonds −); it is the same position. Rationale for each sign is in
`docs/paper_summary.md`.

**Construction** (follows the paper): for each asset class and theme build a
long-short portfolio (rank markets, weights sum to zero) and a directional one
(sign of the signal), size each market by inverse 3-year volatility, scale each
portfolio to 10% volatility, then equal-weight. 3 asset classes x 4 themes x 2
styles = 24 portfolios.

**Benchmark**: time-series momentum, equal blend of 1-, 3- and 12-month signs,
same markets, same sizing.

## Where v0 departs from the paper

| | Paper | v0 | Why it matters |
|---|---|---|---|
| Sample | 1970 to 2016 | last 120 months | true out-of-sample test, but short: a Sharpe of 0.6 has a t-stat under 2 |
| Growth, inflation | Consensus Economics forecasts | realised data with publication lags | forecasts are forward-looking and timelier; expect a weaker business-cycle theme |
| Monetary policy | 2y yields | 3m interbank | 3m rates sat at the floor in 2016 to 2021, so the signal is noisy there |
| Asset classes | equities, FX, bonds, short-rate futures | no short-rate futures | no free data; the paper's best asset class (Sharpe 0.8) is missing |
| Markets | futures and forwards, up to 10+ markets | 10 countries, index/yield based | price-only equities, bonds repriced from yields |
| Prices | daily | monthly averages for equities, yields, rates | signals wait one extra month (`impl_lag=1`) to avoid look-ahead |
| Costs | gross | gross | add turnover-based costs before quoting numbers |

## Layout

```
src/mm/universe.py    countries and FRED ids
src/mm/fetch.py       download and build data/panel.csv
src/mm/data.py        panel loader, excess returns per asset class
src/mm/signals.py     macro trends, publication lags, Exhibit 1 sign map
src/mm/portfolio.py   long-short and directional weights, vol targeting
src/mm/backtest.py    macro momentum, trend following, statistics
src/mm/synth.py       random panel for tests
scripts/run_backtest.py
tests/                pytest
docs/paper_summary.md what the paper does and finds
docs/data.md          data map, known gaps
deck/                 beamer deck (to build)
```

## Roadmap

- [ ] **Run the fetch**, fix `MISSING` ids in `universe.py`, commit `data/panel.csv`.
- [ ] **Run the backtest** on real data; sanity-check asset returns against known
      index returns (S&P 500, Bund, EURUSD) before reading any Sharpe ratio.
- [ ] Robustness: `impl_lag` 0/1/2, long-short vs directional, by theme and asset class,
      6- and 18-month lookbacks, drop one country at a time.
- [ ] Episodes: 2018 Q4, Mar-2020, 2022 rate shock, 2026 energy shock. Did macro
      momentum help when bonds and equities fell together?
- [ ] Add turnover and a cost assumption.
- [ ] v1 data: daily index/futures prices (Yahoo), 2y yields, OECD CLI or survey
      forecasts for the business cycle, short-rate futures.
- [ ] Deck: reuse the `deck_macro101_2026-10-27.tex` template (metropolis, 16:9,
      `\src{}` footers, TikZ diagrams). Sections: themes and transmission (Exhibit 1
      as a diagram), construction, results, vs trend, caveats, sources.

See `AGENTS.md` before contributing.
