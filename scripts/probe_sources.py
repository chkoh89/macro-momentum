"""Check which market-data symbols are downloadable (Yahoo via yfinance, Stooq CSV).
Writes data/probe.csv. Run from the probe workflow; never raises."""
import io
import pathlib
import time

import pandas as pd
import requests

YAHOO = """^GSPC ^GDAXI ^STOXX50E ^N225 ^FTSE ^GSPTSE ^AXJO ^SSMI ^OMX ^NZ50 ^OSEAX OBX.OL OSEBX.OL
ES=F NIY=F NKD=F ZN=F ZB=F ZF=F ZT=F
SPY EWG EWJ EWU EWC EWA EWL EWD ENZL NORW ENOR EZU
IEF TLT GOVT BWX IGOV SHY BIL
EXHD.DE EXX6.DE EXHB.DE X03G.DE IS0L.DE IBGM.L IBGM.AS SEGA.L EUN8.DE EXVM.DE
IGLT.L VGOV.L 2510.T 2561.T XGB.TO ZFM.TO VGB.AX IGB.AX RGB.AX CSBGC0.SW CSBGC7.SW NGB.NZ
EURUSD=X JPY=X GBPUSD=X CAD=X AUDUSD=X CHF=X SEK=X NZDUSD=X NOK=X
^TNX ^IRX ^FVX""".split()

STOOQ = """^spx ^dax ^nkx ^ukx ^tsx ^aor ^smi ^omxs ^nz50 ^oseax
10yusy.b 10ydey.b 10yjpy.b 10yuky.b 10ycay.b 10yauy.b 10ychy.b 10ysey.b 10ynzy.b 10ynoy.b
2yusy.b 2ydey.b 2yjpy.b 2yuky.b 2ycay.b 2yauy.b 2ychy.b 2ysey.b 2ynzy.b 2ynoy.b
eurusd usdjpy""".split()

rows = []


def add(src, sym, s=None, err=""):
    if s is not None and len(s):
        rows.append([src, sym, True, s.index[0].date(), s.index[-1].date(), len(s), round(float(s.iloc[-1]), 4), ""])
    else:
        rows.append([src, sym, False, "", "", 0, "", str(err)[:120]])


try:
    import yfinance as yf
    for t in YAHOO:
        try:
            h = yf.Ticker(t).history(start="2008-01-01", auto_adjust=True)
            add("yahoo", t, h["Close"].dropna() if len(h) else None, "empty")
        except Exception as e:  # noqa: BLE001
            add("yahoo", t, None, repr(e))
        time.sleep(0.4)
except Exception as e:  # noqa: BLE001
    add("yahoo", "IMPORT", None, repr(e))

for sym in STOOQ:
    try:
        r = requests.get(f"https://stooq.com/q/d/l/?s={sym}&i=d&d1=20080101", timeout=30,
                         headers={"User-Agent": "Mozilla/5.0"})
        txt = r.text
        if txt.lstrip().lower().startswith("date"):
            df = pd.read_csv(io.StringIO(txt), parse_dates=["Date"], index_col="Date")
            add("stooq", sym, df["Close"].dropna())
        else:
            add("stooq", sym, None, f"{r.status_code} {txt[:90]!r}")
    except Exception as e:  # noqa: BLE001
        add("stooq", sym, None, repr(e))
    time.sleep(0.6)

out = pathlib.Path("data")
out.mkdir(exist_ok=True)
pd.DataFrame(rows, columns=["source", "symbol", "ok", "first", "last", "n", "last_value", "error"]).to_csv(
    out / "probe.csv", index=False)
