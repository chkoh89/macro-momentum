# Data map

Two separate data sets: macro series for the **signals** (FRED) and tradeable
price series for the **returns** (Yahoo Finance). Countries: US, DE (euro for
FX and the trade-weighted rate), JP, GB, CA, AU, CH, SE, NZ, NO.

## Signals: FRED (`src/mm/universe.py`, `data/panel.csv`, `data/coverage.csv`)

CSV endpoint `fredgraph.csv?id=...`, no key. For each field the fetch tries
several ids and keeps the one with the most recent data.

| Field | Used for | FRED ids in use (run of 2026-11-09) | Original source | Freq |
|---|---|---|---|---|
| `gdp_yoy` | growth | `GDPC1`, `JPNRGDPEXP`, `NGDPRSAXDC{c}Q` (DE, GB, CA, AU), `CLVMNACSCAB1GQ{c}` (CH, SE, NO), `NZLGDPRQPSMEI` | BEA, Cabinet Office, IMF, Eurostat, OECD | quarterly |
| `cpi_yoy` | inflation | `CPIAUCSL`, `CP0000{c}M086NEST` (DE, CH, SE, NO), `CPALTT01{c}M659N` (GB, CA), `CPALTT01AUQ659N`, `NZLCPIALLQINMEI`, `CPALCY01JPM661N` | BLS, Eurostat, OECD | monthly/quarterly |
| `neer` | trade | `NB{c}BIS` (`NBXMBIS` for the euro) | BIS | monthly avg |
| `r3m` | monetary policy, cash leg, FX carry | `IR3TIB01{c}M156N`; `IRSTCI01{c}M156N` for JP, GB, AU | OECD | monthly avg |
| `fx` | FX spot returns | `DEXUSEU`, `DEXJPUS`, `DEXUSUK`, `DEXCAUS`, `DEXUSAL`, `DEXSZUS`, `DEXSDUS`, `DEXUSNZ`, `DEXNOUS` | Fed H.10 | daily, month-end |
| `eq`, `y10` | v0 returns and the bond cross-check only | `SPASTT01{c}M661N`, `IRLTLT01{c}M156N` | OECD | monthly avg |

Timing: growth is used 3 months after the quarter ends, inflation 2 months
after the month, the trade-weighted rate 1 month after. If a figure is not out
yet the last one is carried for up to 3 months, then the country drops out of
that signal.

## Returns: Yahoo Finance (`src/mm/instruments.py`, `data/market.csv`)

Adjusted daily closes sampled at the last trading day of each month. See the
README table for the instruments. `results/data_qa.md` cross-checks every
series: equity indices against US-listed country ETFs converted to local
currency, bond ETFs against yield-implied returns, FX against a second source.

## Known issues

- **Stale CPI** for JP (Apr 2022), GB, CA, AU, NZ (Mar 2025): FRED's OECD feed
  stopped updating. JP, GB and AU policy rates fall back to the overnight
  interbank rate for the same reason.
- **Revisions.** FRED serves the latest vintage of GDP and CPI.
- **Price indices omit dividends** (S&P 500, Nikkei, FTSE, TSX, ASX, SMI, OMXS30).
  This lowers the level of equity excess returns by 2 to 3% a year and matters
  for the directional portfolios, not the long-short ones.
- **Bond ETFs differ in duration** (IEF about 7.5 years, IGLT longer, 2510.T is
  a broad Japanese bond index, mostly JGBs). Positions are volatility-scaled.
- **Yahoo data are unofficial.** The NORW ETF history on Yahoo is wrong before
  2021 (found by the cross-check), so Norway is checked against ENOR instead.
- **Monthly-average series** (rates, effective exchange rates) are known at
  month-end, so using them at month-end is not look-ahead. v0 returns built
  from monthly-average prices do need `impl_lag >= 1`.
