"""What we trade. Signals come from FRED macro data (universe.py); returns come
from these tradeable series, daily from Yahoo Finance, sampled at month-end.

Equities  local-currency index, held against local cash (= index future).
Bonds     local-currency government bond ETF, total return, against local cash.
FX        spot vs USD plus the 3m rate differential (= rolling 3m forward).
"""

# country: (yahoo ticker, name, listed future on it, index includes dividends?)
EQUITY = {
    "US": ("^GSPC", "S&P 500", "ES", False),
    "DE": ("^GDAXI", "DAX", "FDAX", True),
    "JP": ("^N225", "Nikkei 225", "NK", False),
    "GB": ("^FTSE", "FTSE 100", "Z", False),
    "CA": ("^GSPTSE", "S&P/TSX Composite", "SXF (TSX 60)", False),
    "AU": ("^AXJO", "S&P/ASX 200", "AP (SPI 200)", False),
    "CH": ("^SSMI", "SMI", "FSMI", False),
    "SE": ("^OMX", "OMX Stockholm 30", "OMXS30", False),
    "NZ": ("^NZ50", "S&P/NZX 50 Gross", "none liquid", True),
    "NO": ("OSEBX.OL", "Oslo Bors Benchmark", "OBX", True),
}

# country: (yahoo ticker, name, closest bond future). No liquid local ETF with
# enough history exists for SE, NZ, NO; JP only starts in Dec 2017.
BOND = {
    "US": ("IEF", "iShares 7-10 Year Treasury", "TY"),
    "DE": ("EXHD.DE", "iShares eb.rexx Government Germany 5.5-10.5yr", "RX (Bund)"),
    "JP": ("2510.T", "NEXT FUNDS Japan Bond NOMURA-BPI", "JB (JGB)"),
    "GB": ("IGLT.L", "iShares Core UK Gilts", "G (long gilt)"),
    "CA": ("XGB.TO", "iShares Core Canadian Government Bond", "CGB"),
    "AU": ("VGB.AX", "Vanguard Australian Government Bond", "XM"),
    "CH": ("CSBGC0.SW", "iShares Swiss Domestic Government Bond 7-15", "CONF"),
}

# country: (pair, yahoo ticker, invert to get USD per local?). Returns use the
# Fed H.10 month-end rate from FRED; Yahoo is the cross-check.
FX = {
    "DE": ("EURUSD", "EURUSD=X", False), "JP": ("USDJPY", "JPY=X", True),
    "GB": ("GBPUSD", "GBPUSD=X", False), "CA": ("USDCAD", "CAD=X", True),
    "AU": ("AUDUSD", "AUDUSD=X", False), "CH": ("USDCHF", "CHF=X", True),
    "SE": ("USDSEK", "SEK=X", True), "NZ": ("NZDUSD", "NZDUSD=X", False),
    "NO": ("USDNOK", "NOK=X", True),
}

# US-listed country ETFs (USD, total return): used only to cross-check the indices.
EQ_REF = {"US": "SPY", "DE": "EWG", "JP": "EWJ", "GB": "EWU", "CA": "EWC",
          "AU": "EWA", "CH": "EWL", "SE": "EWD", "NZ": "ENZL", "NO": "ENOR"}
