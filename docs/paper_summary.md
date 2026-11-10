# Paper summary: A Half Century of Macro Momentum

Jordan Brooks, AQR Capital Management, August 2017.
https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/A-Half-Century-of-Macro-Momentum.pdf

## The idea

Asset prices under-react to macro news. Economic data and forecasts move
gradually, and markets take time to price a change in the growth, inflation,
policy or risk backdrop. So a country whose fundamentals have been improving
over the past year tends to keep outperforming one whose fundamentals have
been deteriorating. Macro momentum buys the first and sells the second. It is
the fundamental cousin of price trend following: same under-reaction story,
but the signal is the macro variable, not the asset's own price.

## Four themes, each a one-year change

| Theme | What is measured |
|---|---|
| Business cycle | half the 1y change in real GDP growth forecasts, half the 1y change in CPI inflation forecasts (Consensus Economics from 1990, lagged realised OECD data before) |
| International trade | 1y change in the spot exchange rate against an export-weighted basket |
| Monetary policy | 1y change in the 2y yield (Libor-type rates before 1992) |
| Risk sentiment | 1y equity market excess return |

## How each theme maps to positions (Exhibit 1)

Position taken when the variable is rising:

| | Growth up | Inflation up | Currency depreciating | Policy tightening | Risk sentiment improving |
|---|:-:|:-:|:-:|:-:|:-:|
| Equity indices | long | short | long | short | long |
| Currencies | long | long | short | long | long |
| 10y government bonds | short | short | short | short | short |
| 3m interest-rate futures | short | short | short | short | short |

Why:

- **Growth.** Higher growth lifts earnings (equities up) and the expected
  policy path (bonds and rate futures down), and supports the currency.
- **Inflation.** Bad for bonds directly. Bad for equities because it brings
  tighter policy and a higher discount rate. Good for the currency because the
  central bank is expected to respond with higher rates.
- **Trade.** A weaker currency makes exporters more competitive (equities up)
  and adds growth and imported inflation (bonds down). For the currency itself
  the paper simply follows the move, which it describes as close to price
  momentum.
- **Monetary policy.** Tightening is bad for equities and bonds and good for
  the currency through the rate differential.
- **Risk sentiment.** Rising equity markets signal stronger demand ahead: good
  for equities and currencies, bad for bonds as safe-haven demand fades.

Bonds and rate futures are short on every column: any sign of a hotter economy
or tighter policy is bearish fixed income. Equities are the interesting case,
because growth and inflation pull in opposite directions.

## Construction

- **Universe.** Developed-market equity index futures, 10y government bonds,
  currencies and 3m interest-rate futures, starting 1970 where data exist and
  adding markets over time.
- **Two portfolio types** for every asset class and theme:
  - *Long-short*: rank markets on the signal, standardise the ranks so longs
    and shorts offset, adjust each side for volatility. Market-neutral at all
    times.
  - *Directional*: long each market with a positive trend, short each with a
    negative one, equal volatility per position. Equity-based signals are
    measured against their own expanding mean, since equities go up on
    average. Market-neutral only on average.
- **Risk.** Three-year rolling risk model on monthly returns; every portfolio
  scaled to 10% forecast volatility.
- **Aggregation.** 4 asset classes x 4 themes x 2 types = 32 portfolios, equal
  weighted. Growth and inflation are averaged into one business-cycle theme.

## What the paper reports (Jan 1970 to Dec 2016, hypothetical, gross)

| | Excess return | Volatility | Sharpe | Max drawdown |
|---|---|---|---|---|
| Macro momentum | 13.0% | 10.7% | 1.2 | -21.6% |
| Trend following (1/3/12-month) | 12.1% | 11.2% | 1.1 | -23.5% |
| 50/50 | 12.6% | 9.3% | 1.4 | -12.8% |

- Sharpe by asset class: equities 0.7, currencies 0.6, bonds 0.5, rate futures 0.8.
- Sharpe by theme: business cycle 0.5, trade 0.6, monetary policy 0.9, risk sentiment 0.7.
- Themes and asset classes are close to uncorrelated with each other (about 0.1
  on average), which is where the composite's Sharpe comes from.
- Correlation with trend following 0.4, with US equities -0.22, with US 10y
  bonds 0.03.
- Positive in every decade, but the last period in the sample, 2010 to 2016,
  was the weakest: 6.5% a year, Sharpe 0.7.
- Made money in the ten worst equity quarters (average +13.7%) and in eight of
  the ten sharpest rises in real yields (average +12.0%, against -14.2% for
  Treasuries).
- Global macro hedge funds load mainly on the monetary-policy trend and little
  on the other three.

The paper's own caveats: results are a backtest, gross of costs and fees, with
deliberately simple signals, and likely overstated by hindsight.

## Can we use this for the last ten years?

Yes, with substitutions. The signals are simple enough to rebuild from free
data for three of the four asset classes.

| Ingredient | Free substitute | Quality |
|---|---|---|
| 1y equity return | OECD share price indices | good |
| 1y change in trade-weighted FX | BIS effective exchange rates | good |
| 1y change in 2y yield | 3m interbank rates | weak in 2016 to 2021, when short rates sat at the floor |
| Growth and inflation forecasts | realised GDP growth and CPI with publication lags | weaker and later than forecasts; this is what the paper itself uses before 1990 |
| Equity, bond, FX returns | index, yield-implied and spot-plus-carry returns | adequate for a first pass |
| 3m rate futures | none | dropped in v0 |

What to expect before running it:

1. **A lower Sharpe than 1.2.** The paper's last seven years were already at
   0.7, three asset classes diversify less than four, and realised data are a
   blunter business-cycle signal.
2. **Two very different halves.** 2016 to 2021 had pinned policy rates and low
   macro dispersion, a poor environment for the monetary-policy theme. 2022
   onward had the largest global inflation and tightening trends since the
   1970s, exactly what the strategy is built for.
3. **Wide error bars.** Ten years gives a standard error on the Sharpe ratio
   of about 0.32, so only a Sharpe above roughly 0.6 is distinguishable from
   zero.

The honest framing for the deck: this is the first out-of-sample decade for a
strategy published in 2017, tested with coarser data than the authors had.
