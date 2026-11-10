# deck

`macro_momentum.pdf`: the results deck (LaTeX beamer, metropolis, 16:9).
Written for a reader with basic finance and macro: a college freshman should
be able to follow it. Every term is explained where it first appears, and the
last slides are a glossary and the sources.

## Build

```bash
python scripts/run_backtest.py        # results/
python scripts/make_deck_assets.py    # deck/figs/*.pdf, deck/generated/*.tex
cd deck && latexmk -xelatex macro_momentum.tex
```

Needs TeX packages `beamer`, `beamertheme-metropolis`, `pgf`, `fira`, `booktabs`
and `appendixnumberbeamer`. TinyTeX: `tlmgr install beamer beamertheme-metropolis pgf fira appendixnumberbeamer`.

## Rules

- **No numbers typed into the slides.** Text uses the `\n...` macros from
  `generated/numbers.tex`; tables are `generated/*.tex`; figures are
  `figs/*.pdf`. All are written by `scripts/make_deck_assets.py` from the same
  backtest as `results/`, so a data refresh is: rerun the three commands above.
- Every slide with a number or claim has a `\src{}` footer naming the file or
  paper it comes from.
- Series colours match across figures and slide text: macro momentum blue,
  trend following orange, 50/50 aqua.
- The original template (`deck_macro101_2026-10-27.tex`) was not in the repo;
  this deck follows its stated conventions (metropolis, 16:9, `\src{}` footers,
  TikZ diagrams).
