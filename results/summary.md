# Backtest summary (real data)

Returns: `market`. Implementation lag: 0 month(s). Gross of costs unless marked net. Excess returns; each stream is targeted at 10% volatility. Markets traded: eq 10, bond 7, fx 9.

|                                 | start   | end     |   months | ann_ret   | ann_vol   |   sharpe |   t_stat | max_dd   | hit   |
|:--------------------------------|:--------|:--------|---------:|:----------|:----------|---------:|---------:|:---------|:------|
| Macro momentum                  | 2016-11 | 2026-10 |      120 | 7.3%      | 10.7%     |     0.69 |     2.17 | -15.4%   | 57%   |
| Trend following                 | 2016-11 | 2026-10 |      120 | -0.6%     | 10.7%     |    -0.05 |    -0.17 | -22.8%   | 48%   |
| 50/50                           | 2016-11 | 2026-10 |      120 | 3.4%      | 8.7%      |     0.39 |     1.23 | -9.5%    | 54%   |
| MM theme: business_cycle        | 2016-11 | 2026-10 |      120 | 5.8%      | 11.1%     |     0.52 |     1.65 | -18.3%   | 51%   |
| MM theme: trade                 | 2016-11 | 2026-10 |      120 | 2.5%      | 10.1%     |     0.25 |     0.79 | -15.5%   | 48%   |
| MM theme: monetary              | 2016-11 | 2026-10 |      120 | 3.4%      | 9.8%      |     0.35 |     1.09 | -14.7%   | 56%   |
| MM theme: risk                  | 2016-11 | 2026-10 |      120 | 6.5%      | 9.7%      |     0.67 |     2.1  | -20.8%   | 60%   |
| MM asset: eq                    | 2016-11 | 2026-10 |      120 | 2.1%      | 12.0%     |     0.17 |     0.55 | -16.5%   | 54%   |
| MM asset: bond                  | 2016-11 | 2026-10 |      120 | 9.5%      | 11.5%     |     0.82 |     2.6  | -19.2%   | 62%   |
| MM asset: fx                    | 2016-11 | 2026-10 |      120 | 3.9%      | 10.6%     |     0.37 |     1.16 | -26.3%   | 54%   |
| MM style: xs                    | 2016-11 | 2026-10 |      120 | 3.2%      | 3.3%      |     0.94 |     2.99 | -4.7%    | 62%   |
| MM style: ts                    | 2016-11 | 2026-10 |      120 | 0.8%      | 3.6%      |     0.23 |     0.73 | -9.4%    | 58%   |
| TF asset: eq                    | 2016-11 | 2026-10 |      120 | 0.3%      | 12.2%     |     0.02 |     0.07 | -30.8%   | 56%   |
| TF asset: bond                  | 2016-11 | 2026-10 |      120 | 0.1%      | 9.9%      |     0.01 |     0.04 | -23.7%   | 47%   |
| TF asset: fx                    | 2016-11 | 2026-10 |      120 | -1.8%     | 10.2%     |    -0.18 |    -0.56 | -26.4%   | 48%   |
| Macro momentum (net, 1x costs)  | 2016-11 | 2026-10 |      120 | 6.0%      | 10.7%     |     0.57 |     1.79 | -16.5%   | 54%   |
| Trend following (net, 1x costs) | 2016-11 | 2026-10 |      120 | -1.4%     | 10.7%     |    -0.13 |    -0.4  | -24.0%   | 48%   |
| 50/50 (net, 1x costs)           | 2016-11 | 2026-10 |      120 | 2.5%      | 8.7%      |     0.29 |     0.93 | -9.8%    | 54%   |

## Turnover and transaction costs

Turnover is notional traded per year as a multiple of NAV, measured on the final vol-targeted portfolio (offsetting trades across sleeves net out). Costs are one-way, per unit of notional: eq 4bp, bond 3bp, fx 3bp (1x), an assumption for futures and forwards; see README. Sharpe ratios net of 0x to 4x those costs; vol not re-targeted after costs.

| strategy        | turnover eq   | turnover bond   | turnover fx   | turnover total   |   sharpe 0x | drag 1x   |   sharpe 1x |   sharpe 2x |   sharpe 4x |
|:----------------|:--------------|:----------------|:--------------|:-----------------|------------:|:----------|------------:|------------:|------------:|
| Macro momentum  | 8.0x          | 21.6x           | 10.9x         | 40.4x            |        0.69 | 1.29%     |        0.57 |        0.44 |        0.2  |
| Trend following | 5.3x          | 11.4x           | 7.4x          | 24.1x            |       -0.05 | 0.78%     |       -0.13 |       -0.2  |       -0.34 |
| 50/50           | 5.7x          | 13.1x           | 7.3x          | 26.1x            |        0.39 | 0.84%     |        0.29 |        0.2  |        0    |

## Sharpe ratio by sub-period

|                 |   to Dec 2021 |   from Jan 2022 |
|:----------------|--------------:|----------------:|
| Macro momentum  |          0.25 |            1.19 |
| Trend following |         -0.02 |           -0.1  |
| 50/50           |          0.15 |            0.63 |

## Calendar-year returns

|   date | Macro momentum   | Trend following   | 50/50   |
|-------:|:-----------------|:------------------|:--------|
|   2016 | -1.6%            | 4.4%              | 1.4%    |
|   2017 | 2.3%             | -3.7%             | -0.7%   |
|   2018 | 21.7%            | -7.0%             | 6.8%    |
|   2019 | -4.0%            | 6.0%              | 1.1%    |
|   2020 | 2.4%             | -2.1%             | 0.5%    |
|   2021 | -7.4%            | -1.1%             | -4.1%   |
|   2022 | 28.6%            | 9.5%              | 18.9%   |
|   2023 | 4.2%             | -12.7%            | -4.5%   |
|   2024 | 6.3%             | -3.4%             | 1.4%    |
|   2025 | 22.1%            | 4.4%              | 13.0%   |
|   2026 | 1.4%             | -3.6%             | -0.9%   |

## Sensitivity (Sharpe ratio, same window length; net = 1x costs)

| returns   |   impl_lag |   months |   Macro momentum |   Trend following |   50/50 |   Macro momentum net |   Trend following net |   corr MM/TF | note                        |
|:----------|-----------:|---------:|-----------------:|------------------:|--------:|---------------------:|----------------------:|-------------:|:----------------------------|
| market    |          0 |      120 |             0.69 |             -0.05 |    0.39 |                 0.57 |                 -0.13 |         0.31 |                             |
| market    |          1 |      120 |             0.65 |             -0.2  |    0.27 |                 0.52 |                 -0.28 |         0.43 |                             |
| market    |          2 |      120 |             0.21 |             -0.02 |    0.11 |                 0.09 |                 -0.09 |         0.37 |                             |
| fred      |          0 |      120 |             1.03 |              0.63 |    0.98 |                 0.87 |                  0.55 |         0.42 | look-ahead: averaged prices |
| fred      |          1 |      120 |             0.5  |             -0.26 |    0.14 |                 0.36 |                 -0.33 |         0.55 |                             |
| fred      |          2 |      120 |             0.15 |             -0.25 |   -0.06 |                 0.03 |                 -0.31 |         0.67 |                             |

## Correlations

|                 |   Macro momentum |   Trend following |   US equities |   US bonds |
|:----------------|-----------------:|------------------:|--------------:|-----------:|
| Macro momentum  |             1    |              0.31 |         -0.27 |      -0.08 |
| Trend following |             0.31 |              1    |         -0.21 |      -0.11 |
| US equities     |            -0.27 |             -0.21 |          1    |       0.17 |
| US bonds        |            -0.08 |             -0.11 |          0.17 |       1    |

## Countries with a live signal (of 10)

| date    |   growth |   inflation |   trade |   monetary |   risk |
|:--------|---------:|------------:|--------:|-----------:|-------:|
| 2016-11 |       10 |          10 |      10 |         10 |     10 |
| 2021-11 |       10 |          10 |      10 |         10 |     10 |
| 2026-10 |       10 |           5 |      10 |         10 |     10 |
