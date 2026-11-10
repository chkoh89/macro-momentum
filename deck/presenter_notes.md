# Presenter notes: macro momentum deck

For presenting `deck/macro_momentum` to college freshmen. Numbers are from the
backtest run of 2026-11-10 (Nov 2016 to Oct 2026). Slide numbers refer to the
30-slide PowerPoint / Google Slides version, which counts section dividers;
the PDF numbers its slides differently.

## The story in three sentences

1. A strategy published in 2017 still worked over the next ten years, at about
   half its original strength (Sharpe 0.69, against 1.2 in the paper).
2. Almost all of it came from 2022 on, when inflation and interest rates moved
   at different speeds in different countries.
3. Trend following made nothing on the same markets, so mixing the two did not
   help this time.

**What they should leave with:** a strategy that looked great in the past can
be much weaker in the future. The honest check is to test it on data it has
never seen, which is what this project did.

## Before you start

- Click through the Google Slides version once. It was converted from
  PowerPoint, and the conversion can shift text boxes or chart labels. Check
  slide 11 (diagram), slide 15 (timeline) and the chart slides (19 to 22, 25).
- Check the attendance code is on slide 1.
- Charts in Google Slides are fixed images after conversion; the numbers are
  right but the charts cannot be edited there.
- These results have not been reviewed by anyone else on the project yet.
  If that matters for your setting, say so.

## Timing

30 slides, 5 of them section dividers: about 35 to 40 minutes at 1.5 minutes a
slide. For about 25 to 30 minutes, skip or go fast on these. They explain how
the test was run, which freshmen need least:

| Slide | Topic |
|---|---|
| 9 | What a backtest is (keep one sentence: "we tested it on ten years it had never seen") |
| 15 | Publication delays and timing |
| 16 | Data differences from the paper |
| 23 | Trading one or two months late |
| 25 | Rolling correlation |

## Where to slow down

The basics (slides 5 to 8) carry the whole talk. If they understand
the Sharpe ratio and going short, the rest follows.

- **Sharpe ratio.** "Two friends both made 10%. One account swung wildly, the
  other barely moved. The second did better: same reward, less risk. The
  Sharpe ratio measures reward per unit of risk."
- **Going short.** "Borrow a friend's textbook, sell it for $100, buy it back
  later for $70, return it. You keep $30."
- **Macro momentum vs. trend following.** "One watches how the team has been
  playing, the other watches the scoreboard."
- On the scorecard (slide 18), point at the Sharpe column only. Don't explain
  t-stats, turnover or position sizes unless someone asks.

## Likely questions

| Question | Answer |
|---|---|
| Wouldn't I have done better just buying the S&P 500? | Over this decade, about the same: US stocks had a Sharpe of 0.74 above cash (higher still with dividends, which our index leaves out), against 0.69 for macro momentum. The difference is that macro momentum moved differently from stocks (correlation -0.27), so it could help a portfolio that already owns stocks. It was also an unusually good decade for US stocks. |
| Can I do this with my own money? | Not really. It needs futures, short selling and a lot of trading. It's a research test, not a how-to, and not investment advice. |
| Why doesn't everyone do this? | Some large funds do something like it. When many people trade on an idea, it tends to work less well, which may be part of why our result is weaker than the paper's. |
| What happened in 2022? | Inflation jumped and central banks raised rates fast, at different speeds in different countries: the kind of change the strategy looks for. |
| What's a good Sharpe ratio? | About 0.5 is decent, 1 is excellent. For reference, over 2016 to 2026: US stocks 0.74, German stocks 0.57, UK stocks 0.26 (above cash, dividends not counted). |
| Does trend following ever work? | Yes: the paper found a Sharpe of 1.1 from 1970 to 2016. It just had a bad decade on these markets. |
| Could it just be luck? | Possibly. Ten years is not much data: the Sharpe could easily be off by about 0.35 either way. |

If asked why bonds did best or why the interest-rate theme did worst: the
likely reasons (selling bonds as rates rose in 2022; rates stuck near zero
before that) are plausible but untested, so present them as guesses.

## Limits, in one sentence

"This is a simulation on ten years of free data, before most real-world costs,
so treat the numbers as a rough guide." Details if pressed: trading costs are
our estimate; GDP figures are today's revised versions; free inflation data
stops early for 5 of the 10 countries; acting two months late wipes out most of
the edge.

## Sources for the numbers

`results/summary.md`, `results/costs.csv`, `results/correlations.csv`; stock
index Sharpe ratios from `mm.data.asset_returns` over the same 120 months.
