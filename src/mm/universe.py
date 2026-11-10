"""Universe and data map. Every series is a free FRED id (no API key needed).

Each field has a list of candidate ids per country, tried in order. A candidate
is (fred_id, freq, transform):
  freq       D = daily (month-end last), M = monthly, Q = quarterly
  transform  None, "inv" (take 1/x) or "yoy" (level -> year-on-year % change)

Ids marked UNVERIFIED in docs/data.md have not been confirmed against FRED yet;
`python -m mm.fetch` writes data/coverage.csv showing which candidate was used.
"""

COUNTRIES = ["US", "DE", "JP", "GB", "CA", "AU", "CH", "SE", "NZ", "NO"]
BASE = "US"  # FX is quoted against the dollar

# FX: USD per unit of local currency, daily H.10 series.
_FX = {
    "DE": ("DEXUSEU", None), "JP": ("DEXJPUS", "inv"), "GB": ("DEXUSUK", None),
    "CA": ("DEXCAUS", "inv"), "AU": ("DEXUSAL", None), "CH": ("DEXSZUS", "inv"),
    "SE": ("DEXSDUS", "inv"), "NZ": ("DEXUSNZ", None), "NO": ("DEXNOUS", "inv"),
}
_ISO3 = {"US": "USA", "DE": "DEU", "JP": "JPN", "GB": "GBR", "CA": "CAN",
         "AU": "AUS", "CH": "CHE", "SE": "SWE", "NZ": "NZL", "NO": "NOR"}
_GDP_EXTRA = {"US": ["GDPC1"], "JP": ["JPNRGDPEXP"], "DE": ["CLVMNACSCAB1GQDE"],
              "GB": ["CLVMNACSCAB1GQUK"], "CH": ["CLVMNACSCAB1GQCH"],
              "SE": ["CLVMNACSCAB1GQSE"], "NO": ["CLVMNACSCAB1GQNO"]}


def candidates(field: str, c: str):
    """Ordered FRED candidates for one (field, country)."""
    iso3 = _ISO3[c]
    if field == "eq":      # OECD share price index, monthly average
        return [(f"SPASTT01{c}M661N", "M", None)]
    if field == "y10":     # 10y government bond yield, %, monthly average
        return [(f"IRLTLT01{c}M156N", "M", None)]
    if field == "r3m":     # 3m interbank rate, %, monthly average
        out = [(f"IR3TIB01{c}M156N", "M", None)]
        if c == "DE":
            out.append(("IR3TIB01EZM156N", "M", None))
        return out + [(f"IRSTCI01{c}M156N", "M", None)]
    if field == "fx":      # USD per local currency, month-end
        if c == BASE:
            return []
        sid, tr = _FX[c]
        return [(sid, "D", tr)]
    if field == "neer":    # BIS broad nominal effective exchange rate
        code = "XM" if c == "DE" else c
        return [(f"NB{code}BIS", "M", None), (f"RB{code}BIS", "M", None)]
    if field == "cpi_yoy":  # CPI, % change on a year earlier
        return [(f"CPALTT01{c}M659N", "M", None), (f"CPALTT01{c}Q659N", "Q", None),
                (f"{iso3}CPIALLMINMEI", "M", "yoy"), (f"{iso3}CPIALLQINMEI", "Q", "yoy")]
    if field == "gdp_yoy":  # real GDP, % change on a year earlier
        ids = _GDP_EXTRA.get(c, []) + [f"NGDPRSAXDC{c}Q", f"NAEXKP01{c}Q661S"]
        return [(i, "Q", "yoy") for i in ids]
    raise KeyError(field)


FIELDS = ["eq", "y10", "r3m", "fx", "neer", "cpi_yoy", "gdp_yoy"]
