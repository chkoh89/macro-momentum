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
| 2 | Backtest | `src/mm/`, `scripts/`, `results/` | v1 running on real data: FRED signals, tradeable instruments |

## Result so far (run of 2026-11-09, Nov 2016 to Oct 2026, gross of costs)

`results/summary.md` is the source of truth and is refreshed by the weekly
GitHub Action; the table below is a snapshot.

| 10% vol target, excess returns | Ann. return | Sharpe | t-stat | Max drawdown |
|---|---|---|---|---|
| Macro momentum | 7.3% | 0.69 | 2.2 | -15.4% |
| Trend following (1/3/12-month) | -0.6% | -0.05 | -0.2 | -22.8% |
| 50/50 | 3.4% | 0.39 | 1.2 | -9.5% |

- **It held up, at about half the paper's Sharpe** (1.2 for 1970 to 2016, 0.7 for 2010 to 2016).
- **Two different halves.** Sharpe 0.25 to Dec 2021, 1.19 from Jan 2022. Three
  years (2018, 2022, 2025) carry most of the return.
- **Where it came from.** Bonds (0.82) more than FX (0.37) or equities (0.17);
  risk sentiment (0.67) and business cycle (0.52) more than monetary policy
  (0.35) or trade (0.25); long-short portfolios (0.94) far more than
  directional ones (0.23).
- **Diversifying.** Correlation 0.31 with trend following, -0.27 with US equities.
  Trend following on these 26 markets made nothing over the decade.
- **Fragile to delay.** Waiting one extra month keeps the Sharpe at 0.65; two
  months cuts it to 0.21.
- **Not yet credible as a live number**: gross of costs, ten years, latest-vintage
  GDP data, and the inflation signal is stale for five countries after
  early 2025 (see Known gaps).

## How to run

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m mm.fetch          # FRED macro series for the signals, no API key
PYTHONPATH=src python -m mm.fetch_market   # tradeable series from Yahoo Finance
python scripts/data_qa.py                  # cross-check every traded series -> results/data_qa.md
python scripts/run_backtest.py             # -> results/summary.md, stats.csv, returns.csv, sensitivity.csv
python -m pytest -q
```

Or run the `data-and-backtest` Action (Actions tab, "Run workflow"): it does
all of the above and commits `data/` and `results/`. It also runs every Monday.
Sandboxed agents that cannot reach FRED or Yahoo should trigger the Action and
`git pull`.

## The strategy in one table

Go long assets whose macro trend is improving, short those where it is
deteriorating. Every signal is a one-year change. Sign = position when the
variable is rising.

| Theme | Variable (1y change) | Paper | This repo | Equities | Currencies | Bonds |
|---|---|---|---|:-:|:-:|:-:|
| Business cycle | real GDP growth | consensus forecasts | realised yoy growth (FRED), 3m lag | + | + | − |
| Business cycle | CPI inflation | consensus forecasts | realised yoy CPI (FRED), 2m lag | − | + | − |
| International trade | trade-weighted FX, appreciation | export-weighted spot | BIS broad nominal EER (FRED), 1m lag | − | + | + |
| Monetary policy | short rate, tightening | 2y yield | 3m interbank rate (FRED) | − | + | − |
| Risk sentiment | equity excess return | 1y equity return | 1y excess return of the traded index | + | + | − |

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

## What is traded

Month-end closes, daily data from Yahoo Finance (`src/mm/instruments.py`).

| | US | DE | JP | GB | CA | AU | CH | SE | NZ | NO |
|---|---|---|---|---|---|---|---|---|---|---|
| Equity index | S&P 500 | DAX | Nikkei 225 | FTSE 100 | S&P/TSX | ASX 200 | SMI | OMXS30 | NZX 50 | OSEBX |
| Bond ETF | IEF | EXHD.DE | 2510.T (from 2018) | IGLT.L | XGB.TO | VGB.AX | CSBGC0.SW | none | none | none |
| FX vs USD | n/a | EURUSD | USDJPY | GBPUSD | USDCAD | AUDUSD | USDCHF | USDSEK | NZDUSD | USDNOK |

- Equities: index return minus local 3m rate, i.e. what an index future earns.
  Price indices omit dividends (about 2 to 3% a year, see `results/data_qa.md`);
  DAX, NZX 50 and OSEBX are total-return indices.
- Bonds: local-currency government bond ETF total return minus local 3m rate.
- FX: Fed H.10 month-end spot plus the 3m interbank rate differential, i.e. a
  rolling forward. Cross-checked against Yahoo.

## Where this departs from the paper

| | Paper | This repo | Why it matters |
|---|---|---|---|
| Sample | 1970 to 2016 | Nov 2016 to Oct 2026 | true out-of-sample test, but short: the standard error on a 10-year Sharpe is about 0.32 |
| Growth, inflation | Consensus Economics forecasts | realised data with publication lags | forecasts are forward-looking and timelier |
| Monetary policy | 2y yields | 3m interbank | 3m rates sat at the floor in 2016 to 2021, so the signal is noisy there |
| Asset classes | equities, FX, bonds, short-rate futures | no short-rate futures | the paper's best asset class (Sharpe 0.8) is missing |
| Instruments | futures and forwards | cash indices, bond ETFs, spot plus carry | close to futures returns; ETF durations differ by country (handled by vol scaling) |
| Bond markets | 10+ | 6, plus Japan from 2020 | thinner cross-section |
| Costs | gross | gross | add turnover-based costs before quoting numbers |

## Known gaps

- **CPI on FRED is stale** for JP (ends Apr 2022), GB, CA, AU, NZ (end Mar 2025):
  FRED's OECD feed stopped. The inflation signal runs on the other five
  countries after that. Fix: pull CPI from the OECD API or national sources.
- **GDP is latest-vintage**, so the growth signal sees revisions. Fix: ALFRED vintages.
- **No transaction costs.**
- **Japan bonds** enter only in 2020 (ETF listed Dec 2017, then two years of
  volatility history).
- **v0 for reference**: `--source fred` reruns the first version on non-tradeable
  OECD monthly-average indices and yield-implied bond returns (Sharpe 0.50 at
  a one-month lag). The sensitivity table in `results/summary.md` shows both.

## Layout

```
src/mm/universe.py      countries and FRED ids for the signals
src/mm/instruments.py   traded instruments and their Yahoo tickers
src/mm/fetch.py         FRED download -> data/panel.csv
src/mm/fetch_market.py  Yahoo download -> data/market.csv
src/mm/data.py          panel loader, excess returns per asset class
src/mm/signals.py       macro trends, publication lags, Exhibit 1 sign map
src/mm/portfolio.py     long-short and directional weights, vol targeting
src/mm/backtest.py      macro momentum, trend following, statistics
src/mm/synth.py         random panel for tests
scripts/run_backtest.py, scripts/data_qa.py, scripts/dispatch.sh
tests/                  pytest (includes a look-ahead test)
docs/paper_summary.md   what the paper does and finds
docs/data.md            data map
deck/                   beamer deck (to build)
```

## Roadmap

- [x] Fetch FRED data, fix missing ids, commit the panel.
- [x] Trade real instruments; cross-check each against an independent series.
- [x] First robustness table: implementation lag 0/1/2, tradeable vs v0 returns.
- [ ] Fresh CPI for JP, GB, CA, AU, NZ (OECD API).
- [ ] Turnover and a cost assumption per asset class.
- [ ] More robustness: 6- and 18-month lookbacks, drop one country at a time,
      2y yields for the policy signal, bootstrap confidence interval on the Sharpe.
- [ ] Episodes: 2018 Q4, Mar-2020, 2022 rate shock, 2026 energy shock. Did macro
      momentum help when bonds and equities fell together?
- [ ] Figures for the deck: cumulative returns, theme and asset-class bars,
      rolling correlation with trend following, Exhibit 1 as a diagram.
- [ ] Deck: reuse the `deck_macro101_2026-10-27.tex` template (metropolis, 16:9,
      `\src{}` footers, TikZ diagrams). Sections: themes and transmission,
      construction, data and instruments, results, vs trend, caveats, sources.

See `AGENTS.md` before contributing.
