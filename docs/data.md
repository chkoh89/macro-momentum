# Data map (v0)

All series come from FRED's CSV endpoint (`fredgraph.csv?id=...`), no key.
Countries: US, DE (euro for FX and the trade-weighted rate), JP, GB, CA, AU, CH, SE, NZ, NO.

| Field | Meaning | FRED id pattern | Original source | Freq | Checked |
|---|---|---|---|---|---|
| `eq` | share price index | `SPASTT01{c}M661N` | OECD | monthly avg | not yet |
| `y10` | 10y government yield | `IRLTLT01{c}M156N` | OECD | monthly avg | US, DE, JP, GB, CA resolve |
| `r3m` | 3m interbank rate | `IR3TIB01{c}M156N`, fallback `IRSTCI01{c}M156N` | OECD | monthly avg | not yet |
| `fx` | USD per local currency | `DEXUSEU`, `DEXJPUS`, `DEXUSUK`, `DEXCAUS`, `DEXUSAL`, `DEXSZUS`, `DEXSDUS`, `DEXUSNZ`, `DEXNOUS` | Fed H.10 | daily, month-end | resolve |
| `neer` | broad nominal effective exchange rate | `NB{c}BIS` (`NBXMBIS` for the euro) | BIS | monthly avg | resolve |
| `cpi_yoy` | CPI, % yoy | `CPALTT01{c}M659N`, quarterly `...Q659N` for AU, NZ | OECD | monthly/quarterly | not yet |
| `gdp_yoy` | real GDP, % yoy | `GDPC1`, `JPNRGDPEXP`, `CLVMNACSCAB1GQ{c}`, `NGDPRSAXDC{c}Q` | BEA, Cabinet Office, Eurostat, IMF | quarterly | not yet |

"Resolve" means FRED returned a file for the id on 2026-11-09; the contents
were not inspected. "Not yet" means at least one id in the batch failed, so
some countries will need a different id. `python -m mm.fetch` tries each
candidate in order and records the outcome in `data/coverage.csv`.

## Known issues

- **Monthly averages.** OECD equity, yield and rate series are averages over
  the month, which smooths returns and creates spurious autocorrelation.
  `impl_lag=1` keeps signals from trading the month they were measured in. v1
  should use month-end prices from daily data.
- **Some OECD series on FRED stop early** for some countries. Check the `last`
  column in `coverage.csv`; a series ending before the current year needs a
  replacement.
- **Equity returns are price-only**, bonds are a par-bond approximation from
  yield changes, FX carry uses 3m interbank differentials.
- **Realised macro data are revised.** FRED serves the latest vintage, so the
  growth signal sees revisions that were not known at the time. ALFRED
  vintages would fix this.
