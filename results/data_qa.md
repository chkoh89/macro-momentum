# Data check: traded series

Raw (not excess) monthly returns. `ann_ret`, `ann_vol` from Nov 2016; `flag` looks at 2012 on; `corr` and `ann_gap` (series minus check, per year) from 2014. Equity gaps are mostly dividends for price indices; bond correlations are held down by the check using monthly-average yields.

| asset   | country   | ticker    | name                                          | first   | last    | ann_ret   | ann_vol   | worst_month   | best_month   | check_vs               |   corr | ann_gap   | flag   |
|:--------|:----------|:----------|:----------------------------------------------|:--------|:--------|:----------|:----------|:--------------|:-------------|:-----------------------|-------:|:----------|:-------|
| eq      | US        | ^GSPC     | S&P 500                                       | 2008-02 | 2026-10 | 13.9%     | 15.3%     | -16.9%        | 12.7%        | SPY in local ccy       |   1    | -1.7%     |        |
| eq      | DE        | ^GDAXI    | DAX                                           | 2008-02 | 2026-10 | 10.2%     | 16.2%     | -19.2%        | 16.8%        | EWG in local ccy       |   0.98 | +1.6%     |        |
| eq      | JP        | ^N225     | Nikkei 225                                    | 2008-02 | 2026-10 | 14.6%     | 18.0%     | -23.8%        | 16.6%        | EWJ in local ccy       |   0.89 | +1.1%     |        |
| eq      | GB        | ^FTSE     | FTSE 100                                      | 2008-02 | 2026-10 | 5.1%      | 12.1%     | -13.8%        | 12.4%        | EWU in local ccy       |   0.97 | -3.1%     |        |
| eq      | CA        | ^GSPTSE   | S&P/TSX Composite                             | 2008-02 | 2026-10 | 9.7%      | 13.1%     | -17.7%        | 11.2%        | EWC in local ccy       |   0.99 | -2.4%     |        |
| eq      | AU        | ^AXJO     | S&P/ASX 200                                   | 2008-02 | 2026-10 | 6.1%      | 13.6%     | -21.2%        | 10.0%        | EWA in local ccy       |   0.95 | -3.4%     |        |
| eq      | CH        | ^SSMI     | SMI                                           | 2008-02 | 2026-10 | 7.1%      | 12.1%     | -11.3%        | 10.1%        | EWL in local ccy       |   0.97 | -2.1%     |        |
| eq      | SE        | ^OMX      | OMX Stockholm 30                              | 2008-12 | 2026-10 | 9.3%      | 14.9%     | -11.2%        | 17.0%        | EWD in local ccy       |   0.95 | -2.7%     |        |
| eq      | NZ        | ^NZ50     | S&P/NZX 50 Gross                              | 2008-02 | 2026-10 | 7.4%      | 10.7%     | -13.0%        | 8.4%         | ENZL in local ccy      |   0.96 | +0.9%     |        |
| eq      | NO        | OSEBX.OL  | Oslo Bors Benchmark                           | 2013-04 | 2026-10 | 13.1%     | 13.8%     | -14.8%        | 14.6%        | ENOR in local ccy      |   0.97 | +2.3%     |        |
| bond    | US        | IEF       | iShares 7-10 Year Treasury                    | 2008-02 | 2026-10 | 0.8%      | 6.7%      | -4.7%         | 7.8%         | FRED 10y yield-implied |   0.74 | +0.1%     |        |
| bond    | DE        | EXHD.DE   | iShares eb.rexx Government Germany 5.5-10.5yr | 2008-02 | 2026-10 | -1.0%     | 5.2%      | -5.3%         | 4.3%         | FRED 10y yield-implied |   0.58 | +0.4%     |        |
| bond    | JP        | 2510.T    | NEXT FUNDS Japan Bond NOMURA-BPI              | 2018-01 | 2026-10 | -1.8%     | 2.7%      | -2.4%         | 1.7%         | FRED 10y yield-implied |   0.85 | +0.5%     |        |
| bond    | GB        | IGLT.L    | iShares Core UK Gilts                         | 2008-02 | 2026-10 | -0.6%     | 7.8%      | -7.8%         | 5.5%         | FRED 10y yield-implied |   0.61 | +0.3%     |        |
| bond    | CA        | XGB.TO    | iShares Core Canadian Government Bond         | 2008-02 | 2026-10 | 1.0%      | 5.5%      | -3.6%         | 5.0%         | FRED 10y yield-implied |   0.67 | +0.4%     |        |
| bond    | AU        | VGB.AX    | Vanguard Australian Government Bond           | 2012-05 | 2026-10 | 1.5%      | 4.8%      | -3.9%         | 3.6%         | FRED 10y yield-implied |   0.68 | +0.0%     |        |
| bond    | CH        | CSBGC0.SW | iShares Swiss Domestic Government Bond 7-15   | 2008-02 | 2026-10 | 0.5%      | 5.7%      | -4.6%         | 7.2%         | FRED 10y yield-implied |   0.96 | +0.9%     |        |
| fx      | DE        | EURUSD    | Fed H.10 month-end                            | 2005-02 | 2026-10 | 0.4%      | 7.0%      | -9.9%         | 9.7%         | Yahoo EURUSD=X         |   0.96 | +0.0%     |        |
| fx      | JP        | USDJPY    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -3.6%     | 8.8%      | -8.1%         | 7.8%         | Yahoo JPY=X            |   0.95 | +0.1%     |        |
| fx      | GB        | GBPUSD    | Fed H.10 month-end                            | 2005-02 | 2026-10 | 1.2%      | 7.7%      | -9.2%         | 9.2%         | Yahoo GBPUSD=X         |   0.97 | -0.0%     |        |
| fx      | CA        | USDCAD    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -0.2%     | 6.5%      | -12.8%        | 9.0%         | Yahoo CAD=X            |   0.97 | +0.0%     |        |
| fx      | AU        | AUDUSD    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -0.3%     | 9.8%      | -16.8%        | 9.2%         | Yahoo AUDUSD=X         |   0.97 | +0.0%     |        |
| fx      | CH        | USDCHF    | Fed H.10 month-end                            | 2005-02 | 2026-10 | 2.1%      | 7.6%      | -11.2%        | 14.0%        | Yahoo CHF=X            |   0.97 | +0.1%     |        |
| fx      | SE        | USDSEK    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -0.4%     | 10.0%     | -10.7%        | 9.4%         | Yahoo SEK=X            |   0.97 | -0.0%     |        |
| fx      | NZ        | NZDUSD    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -1.8%     | 10.9%     | -13.1%        | 13.2%        | Yahoo NZDUSD=X         |   0.97 | +0.0%     |        |
| fx      | NO        | USDNOK    | Fed H.10 month-end                            | 2005-02 | 2026-10 | -0.4%     | 11.8%     | -12.2%        | 7.7%         | Yahoo NOK=X            |   0.97 | +0.0%     |        |
