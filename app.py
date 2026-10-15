from __future__ import annotations

import sqlite3
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "aktieapp.db"

DEFAULT_STOCKS = {
    "Investor B": "INVE-B.ST",
    "Volvo B": "VOLV-B.ST",
    "Atlas Copco B": "ATCO-B.ST",
    "Assa Abloy B": "ASSA-B.ST",
    "Sandvik": "SAND.ST",
    "SEB A": "SEB-A.ST",
    "Swedbank A": "SWED-A.ST",
    "Handelsbanken A": "SHB-A.ST",
    "AstraZeneca": "AZN.ST",
    "Tele2 B": "TEL2-B.ST",
    "Telia Company": "TELIA.ST",
    "Svenska Cellulosa B": "SCA-B.ST",
    "Axfood": "AXFO.ST",
    "Essity B": "ESSITY-B.ST",
    "H&M B": "HM-B.ST",
    "Ericsson B": "ERIC-B.ST",
    "Saab B": "SAAB-B.ST",
    "Evolution": "EVO.ST",
    "Nordea": "NDA-SE.ST",
    "Lifco B": "LIFCO-B.ST",
}


# Brett universum med svenska börsaktier. Tickers som saknar data markeras i appen.
STOCK_UNIVERSE = {
    "ABB Ltd": "ABB.ST", "Addtech B": "ADDT-B.ST", "Acast": "ACAST.ST", "Academedia": "ACAD.ST",
    "Alfa Laval": "ALFA.ST", "Alleima": "ALLEI.ST", "Alimak Group": "ALIG.ST", "Arjo B": "ARJO-B.ST",
    "Assa Abloy B": "ASSA-B.ST", "AstraZeneca": "AZN.ST", "Atlas Copco A": "ATCO-A.ST", "Atlas Copco B": "ATCO-B.ST",
    "Atrium Ljungberg B": "ATRLJ-B.ST", "Avanza Bank": "AZA.ST", "Axfood": "AXFO.ST", "Bilia A": "BILI-A.ST",
    "BioArctic B": "BIOA-B.ST", "BioGaia B": "BIOG-B.ST", "Biotage": "BIOT.ST", "Boliden": "BOL.ST",
    "Boozt": "BOOZT.ST", "Bure Equity": "BURE.ST", "Billerud": "BILL.ST", "Castellum": "CAST.ST",
    "Cint Group": "CINT.ST", "Cloetta B": "CLA-B.ST", "Dometic": "DOM.ST", "Elekta B": "EKTA-B.ST",
    "Embracer B": "EMBRAC-B.ST", "Epiroc A": "EPI-A.ST", "Epiroc B": "EPI-B.ST", "Ericsson B": "ERIC-B.ST",
    "Essity A": "ESSITY-A.ST", "Essity B": "ESSITY-B.ST", "Evolution": "EVO.ST", "Fabege": "FABG.ST",
    "Fastighets AB Balder B": "BALD-B.ST", "Fortnox": "FNOX.ST", "Getinge B": "GETI-B.ST", "Gränges": "GRNG.ST",
    "H&M B": "HM-B.ST", "Hacksaw": "HACK.ST", "Handelsbanken A": "SHB-A.ST", "Hexpol B": "HPOL-B.ST",
    "Hexagon B": "HEXA-B.ST", "HMS Networks": "HMS.ST", "Holmen B": "HOLM-B.ST", "Hufvudstaden A": "HUFV-A.ST",
    "Husqvarna B": "HUSQ-B.ST", "Indutrade": "INDT.ST", "Industrivärden A": "INDU-A.ST", "Industrivärden C": "INDU-C.ST",
    "Instalco": "INSTAL.ST", "Investor A": "INVE-A.ST", "Investor B": "INVE-B.ST", "Inwido": "INWI.ST",
    "JM": "JM.ST", "Knowit": "KNOW.ST", "Lagercrantz B": "LAGR-B.ST", "Lifco B": "LIFCO-B.ST",
    "Loomis": "LOOMIS.ST", "Lundbergföretagen B": "LUND-B.ST", "Lundin Mining": "LUMI.ST", "Millicom": "TIGO-SDB.ST",
    "Mips": "MIPS.ST", "Modern Times Group B": "MTG-B.ST", "Munters": "MTRS.ST", "Mycronic": "MYCR.ST",
    "NCC B": "NCC-B.ST", "Nibe Industrier B": "NIBE-B.ST", "Nordea": "NDA-SE.ST", "Nordnet": "SAVE.ST",
    "OEM International B": "OEM-B.ST", "Peab B": "PEAB-B.ST", "Platzer B": "PLAZ-B.ST", "PowerCell Sweden": "PCELL.ST",
    "Ratos B": "RATO-B.ST", "RaySearch Laboratories B": "RAY-B.ST", "Saab B": "SAAB-B.ST", "Sagax B": "SAGA-B.ST",
    "Sandvik": "SAND.ST", "SCA B": "SCA-B.ST", "SEB A": "SEB-A.ST", "Sectra B": "SECT-B.ST",
    "Securitas B": "SECU-B.ST", "Skanska B": "SKA-B.ST", "SKF B": "SKF-B.ST", "SSAB B": "SSAB-B.ST",
    "Stillfront": "SF.ST", "Stora Enso R": "STE-R.ST", "Storytel B": "STORY-B.ST", "Sweco B": "SWEC-B.ST",
    "Swedbank A": "SWED-A.ST", "Swedish Orphan Biovitrum": "SOBI.ST", "Synsam": "SYNSAM.ST", "Systemair": "SYSR.ST",
    "Tele2 B": "TEL2-B.ST", "Telia Company": "TELIA.ST", "Thule Group": "THULE.ST", "Trelleborg B": "TREL-B.ST",
    "Truecaller B": "TRUE-B.ST", "Vitrolife": "VITR.ST", "Volvo A": "VOLV-A.ST", "Volvo B": "VOLV-B.ST",
    "Wallenstam B": "WALL-B.ST", "Wihlborgs Fastigheter": "WIHL.ST", "Xvivo Perfusion": "XVIVO.ST",
    "Yubico": "YUBICO.ST", "Öresund": "ORES.ST", "Kinnevik B": "KINV-B.ST", "Kambi": "KAMBI.ST",
    "Lime Technologies": "LIME.ST", "Net Insight B": "NETI-B.ST", "Nolato B": "NOLA-B.ST", "Oncopeptides": "ONCO.ST",
    "Orexo": "ORX.ST", "Sinch": "SINCH.ST", "Smart Eye": "SEYE.ST", "BONESUPPORT": "BONEX.ST",
    "Cavotec": "CCC.ST", "Dedicare B": "DEDI.ST", "Elanders B": "ELAN-B.ST", "Enad Global 7": "EG7.ST",
    "Fenix Outdoor B": "FOI-B.ST", "G5 Entertainment": "G5EN.ST", "Hanza": "HANZA.ST", "Inission B": "INISS-B.ST",
    "Karnov Group": "KAR.ST", "Lammhults Design Group B": "LAMM-B.ST", "Medicover B": "MCOV-B.ST", "Nobia": "NOBI.ST",
    "Pandox B": "PNDX-B.ST", "Rusta": "RUSTA.ST", "Sdiptech B": "SDIP-B.ST", "Storskogen B": "STOR-B.ST",
    "Vitec Software B": "VIT-B.ST", "VBG Group B": "VBG-B.ST", "W5 Solutions": "W5.ST", "Xano Industri B": "XANO-B.ST"
}

st.set_page_config(page_title="Svensk Aktiebevakning", page_icon="📈", layout="wide")


def db_connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with db_connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS watchlist (
            ticker TEXT PRIMARY KEY, name TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
            added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS paper_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, name TEXT NOT NULL,
            invested REAL NOT NULL, buy_price REAL NOT NULL, buy_date TEXT NOT NULL,
            stop_pct REAL NOT NULL DEFAULT 6.0, notes TEXT DEFAULT '', active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL, signal TEXT NOT NULL,
            message TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        for name, ticker in DEFAULT_STOCKS.items():
            con.execute("INSERT OR IGNORE INTO watchlist(ticker,name,enabled) VALUES(?,?,1)", (ticker, name))


def read_watchlist() -> pd.DataFrame:
    with db_connect() as con:
        return pd.read_sql_query("SELECT ticker,name,enabled FROM watchlist ORDER BY name", con)


def save_watchlist(df: pd.DataFrame):
    with db_connect() as con:
        for _, r in df.iterrows():
            con.execute("UPDATE watchlist SET enabled=? WHERE ticker=?", (int(bool(r["Bevaka"])), str(r["ticker"])))


def add_ticker(name: str, ticker: str):
    with db_connect() as con:
        con.execute("INSERT OR REPLACE INTO watchlist(ticker,name,enabled) VALUES(?,?,1)", (ticker.strip().upper(), name.strip()))


def remove_ticker(ticker: str):
    with db_connect() as con:
        con.execute("DELETE FROM watchlist WHERE ticker=?", (ticker,))


@st.cache_data(ttl=900, show_spinner=False)
def load_history(ticker: str, period: str = "2y") -> pd.DataFrame:
    data = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True, actions=False)
    if data is None or data.empty:
        return pd.DataFrame()
    data = data.rename(columns={c: c.title() for c in data.columns})
    data.index = pd.to_datetime(data.index).tz_localize(None) if getattr(data.index, "tz", None) is not None else pd.to_datetime(data.index)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in data.columns:
            return pd.DataFrame()
    data = data[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])
    return data


@st.cache_data(ttl=900, show_spinner=False)
def load_universe_histories(tickers: tuple[str, ...], period: str = "2y") -> dict[str, pd.DataFrame]:
    """Hämta många aktier i en batch för att minska antal anrop och risken för rate limits."""
    if not tickers:
        return {}
    try:
        raw = yf.download(list(tickers), period=period, interval="1d", auto_adjust=True,
                          actions=False, group_by="ticker", threads=True, progress=False,
                          timeout=25)
    except Exception:
        return {}
    out: dict[str, pd.DataFrame] = {}
    if raw is None or raw.empty:
        return out
    for ticker in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                if ticker in raw.columns.get_level_values(0):
                    frame = raw[ticker].copy()
                elif ticker in raw.columns.get_level_values(-1):
                    frame = raw.xs(ticker, axis=1, level=-1).copy()
                else:
                    continue
            else:
                if len(tickers) != 1:
                    continue
                frame = raw.copy()
            frame = frame.rename(columns={c: str(c).title() for c in frame.columns})
            needed = ["Open", "High", "Low", "Close", "Volume"]
            if not all(c in frame.columns for c in needed):
                continue
            frame.index = pd.to_datetime(frame.index)
            if getattr(frame.index, "tz", None) is not None:
                frame.index = frame.index.tz_localize(None)
            frame = frame[needed].dropna(subset=["Close"])
            if not frame.empty:
                out[ticker] = frame
        except Exception:
            continue
    return out


def indicators(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    close = d["Close"]
    d["SMA20"] = close.rolling(20).mean()
    d["SMA50"] = close.rolling(50).mean()
    d["SMA200"] = close.rolling(200).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))
    d["RSI14"] = d["RSI14"].fillna(50)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    d["MACD"] = ema12 - ema26
    d["MACDSignal"] = d["MACD"].ewm(span=9, adjust=False).mean()
    prev_close = close.shift(1)
    tr = pd.concat([(d["High"] - d["Low"]), (d["High"] - prev_close).abs(), (d["Low"] - prev_close).abs()], axis=1).max(axis=1)
    d["ATR14"] = tr.rolling(14).mean()
    d["ATRpct"] = d["ATR14"] / close * 100
    d["VolAvg20"] = d["Volume"].rolling(20).mean()
    d["RelVolume"] = d["Volume"] / d["VolAvg20"].replace(0, np.nan)
    d["Return20"] = close.pct_change(20) * 100
    d["Peak90"] = close.rolling(90, min_periods=20).max()
    d["Drawdown90"] = (close / d["Peak90"] - 1) * 100
    return d


def assess(data: pd.DataFrame) -> dict:
    if data.empty or len(data) < 60:
        return {"signal": "OTILLRÄCKLIG DATA", "score": 0, "risk": "Okänd", "risk_score": 100, "reasons": ["För lite historik för en rimlig bedömning."], "stop": None}
    d = indicators(data)
    r = d.iloc[-1]
    prev = d.iloc[-2]
    score = 0
    reasons = []
    if pd.notna(r.SMA50) and r.Close > r.SMA50:
        score += 15; reasons.append("Kursen ligger över 50-dagars medelvärde.")
    else:
        reasons.append("Kursen ligger inte över 50-dagars medelvärde.")
    if pd.notna(r.SMA200) and r.Close > r.SMA200:
        score += 20; reasons.append("Långsiktig trend ligger över 200-dagars medelvärde.")
    else:
        reasons.append("Långsiktig trend är svag eller under 200-dagars medelvärde.")
    if r.SMA20 > r.SMA50:
        score += 10; reasons.append("Kortare trend är starkare än 50-dagars trend.")
    if r.MACD > r.MACDSignal:
        score += 15; reasons.append("MACD visar positivt momentum.")
    if 45 <= r.RSI14 <= 65:
        score += 15; reasons.append("RSI ligger i ett måttligt momentumintervall.")
    elif 35 <= r.RSI14 < 45:
        score += 7; reasons.append("RSI är svagare men inte extremt låg.")
    elif r.RSI14 > 75:
        score -= 10; reasons.append("RSI är hög; kortsiktig rekylrisk kan vara förhöjd.")
    else:
        reasons.append("RSI ger inget tydligt positivt momentumstöd.")
    if pd.notna(r.RelVolume) and r.RelVolume >= 1.2 and r.Close > prev.Close:
        score += 10; reasons.append("Uppgången stöds av högre än normal volym.")
    if pd.notna(r.Return20) and r.Return20 > 0:
        score += 10; reasons.append("Aktien har positiv utveckling senaste 20 handelsdagarna.")
    elif pd.notna(r.Return20) and r.Return20 < -5:
        score -= 10; reasons.append("Aktien har fallit tydligt senaste 20 handelsdagarna.")
    score = int(max(0, min(100, score)))

    atr_pct = float(r.ATRpct) if pd.notna(r.ATRpct) else 5.0
    drawdown = float(r.Drawdown90) if pd.notna(r.Drawdown90) else 0.0
    risk_score = int(max(0, min(100, 35 + atr_pct * 5 + max(0, -drawdown) * 0.8)))
    if risk_score < 45: risk = "Lägre (relativt)"
    elif risk_score < 65: risk = "Medel"
    else: risk = "Hög"

    downtrend = (r.Close < r.SMA50 and r.MACD < r.MACDSignal) or (r.Close < r.SMA20 and r.Return20 < -5)
    if downtrend:
        signal = "NEDÅT-RISK"
    elif score >= 70 and risk_score < 65 and r.RSI14 < 70:
        signal = "KÖPKANDIDAT"
    elif score >= 50:
        signal = "BEVAKA"
    else:
        signal = "AVVAKTA"
    stop = float(r.Close - 2.5 * r.ATR14) if pd.notna(r.ATR14) else float(r.Close * 0.94)
    stop = max(0.01, stop)
    return {"signal": signal, "score": score, "risk": risk, "risk_score": risk_score,
            "reasons": reasons, "stop": stop, "close": float(r.Close), "rsi": float(r.RSI14),
            "atr_pct": atr_pct, "rel_volume": float(r.RelVolume) if pd.notna(r.RelVolume) else np.nan,
            "return20": float(r.Return20) if pd.notna(r.Return20) else np.nan, "history": d}


@st.cache_data(ttl=1800, show_spinner=False)
def load_news(query: str, limit: int = 8) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={quote_plus(query + ' aktie')}&hl=sv&gl=SE&ceid=SE:sv"
    try:
        response = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = []
        for item in root.findall("./channel/item")[:limit]:
            items.append({"title": item.findtext("title", "Utan rubrik"), "link": item.findtext("link", ""),
                          "pubDate": item.findtext("pubDate", ""), "source": (item.findtext("source", "") or "Nyhetskälla")})
        return items
    except Exception:
        return []


def backtest(data: pd.DataFrame) -> dict:
    """Simple transparent demonstration: signal at close, enter next close, exit after 10 days or at ATR stop."""
    if len(data) < 250:
        return {"trades": 0, "win_rate": np.nan, "avg_return": np.nan, "max_dd": np.nan, "returns": []}
    d = indicators(data).dropna(subset=["SMA50", "SMA200", "MACDSignal", "ATR14"]).copy()
    # Conservative simplified signal; entry at next day's close to avoid same-close look-ahead.
    candidate = (d["Close"] > d["SMA50"]) & (d["Close"] > d["SMA200"]) & (d["MACD"] > d["MACDSignal"]) & d["RSI14"].between(45, 68)
    exits = []
    i = 0
    while i < len(d) - 12:
        if bool(candidate.iloc[i]):
            entry_i = i + 1
            entry = float(d["Close"].iloc[entry_i])
            atr = float(d["ATR14"].iloc[i])
            stop = entry - 2.5 * atr
            last_exit_i = min(entry_i + 10, len(d) - 1)
            exit_i = last_exit_i
            exit_price = float(d["Close"].iloc[last_exit_i])
            hit_stop = False
            for j in range(entry_i + 1, last_exit_i + 1):
                if float(d["Low"].iloc[j]) <= stop:
                    exit_i = j
                    # If the market opens below the stop, model a worse fill at the open.
                    exit_price = min(stop, float(d["Open"].iloc[j]))
                    hit_stop = True
                    break
            exits.append((exit_price / entry - 1) * 100 - 0.4)  # illustrative round-trip costs
            i = exit_i + 1
        else:
            i += 1
    if not exits:
        return {"trades": 0, "win_rate": np.nan, "avg_return": np.nan, "max_dd": np.nan, "returns": []}
    equity = np.cumprod(1 + np.array(exits) / 100)
    peak = np.maximum.accumulate(equity)
    max_dd = float(np.min((equity / peak - 1) * 100))
    return {"trades": len(exits), "win_rate": float(np.mean(np.array(exits) > 0) * 100),
            "avg_return": float(np.mean(exits)), "max_dd": max_dd, "returns": exits}


init_db()
st.title("📈 Svensk Aktiebevakning")
st.caption("Första prototypen • dagliga kurser • köpskandidater, nedåtrisk, stop-loss och simulerade affärer")
st.warning("Detta är ett testverktyg, inte personlig finansiell rådgivning. Data från Yahoo Finance kan vara fördröjd, ofullständig eller ändras. Signaler garanterar inte vinst. Ingen automatisk handel sker.")

with st.sidebar:
    st.header("Inställningar")
    refresh = st.button("↻ Hämta om data nu", use_container_width=True)
    if refresh:
        load_history.clear(); load_news.clear()
        st.rerun()
    st.caption("Kurser cachelagras i 15 minuter. Nyheter cachelagras i 30 minuter.")
    st.divider()
    st.subheader("Lägg till aktie")
    new_name = st.text_input("Bolagsnamn", placeholder="Exempel: Exempelbolag")
    new_ticker = st.text_input("Yahoo-ticker", placeholder="Exempel: VOLV-B.ST")
    if st.button("Lägg till i bevakningslistan", use_container_width=True):
        if new_name.strip() and new_ticker.strip():
            add_ticker(new_name, new_ticker)
            st.success("Aktien har lagts till.")
            st.rerun()
        else:
            st.error("Fyll i både namn och ticker.")

pages = st.tabs(["Översikt & signaler", "Min bevakningslista", "Testportfölj", "Historiskt test", "Nyheter", "Alla aktier"])

with pages[0]:
    wl = read_watchlist()
    enabled = wl[wl["enabled"] == 1]
    st.subheader("Marknadsskanning")
    st.caption(f"Aktier i bevakningslistan: {len(enabled)}. Skanningen görs när sidan körs och använder senaste tillgängliga dagsdata.")
    results = []
    histories = {}
    progress = st.progress(0, text="Laddar aktiedata …")
    for idx, row in enumerate(enabled.itertuples(index=False)):
        try:
            hist = load_history(row.ticker)
            if not hist.empty:
                a = assess(hist)
                histories[row.ticker] = hist
                results.append({"Bolag": row.name, "Ticker": row.ticker, "Signal": a["signal"], "Signalpoäng": a["score"],
                                "Risk": a["risk"], "Riskpoäng": a["risk_score"], "Senaste kurs": a.get("close", np.nan),
                                "Stop-loss (indikativ)": a.get("stop", np.nan), "RSI": a.get("rsi", np.nan),
                                "20d %": a.get("return20", np.nan), "Orsak": " ".join(a["reasons"][:2])})
            else:
                results.append({"Bolag": row.name, "Ticker": row.ticker, "Signal": "DATA SAKNAS", "Signalpoäng": 0, "Risk": "Okänd", "Riskpoäng": 100,
                                "Senaste kurs": np.nan, "Stop-loss (indikativ)": np.nan, "RSI": np.nan, "20d %": np.nan, "Orsak": "Ingen kurshistorik hittades. Kontrollera tickern."})
        except Exception as exc:
            results.append({"Bolag": row.name, "Ticker": row.ticker, "Signal": "FEL VID HÄMTNING", "Signalpoäng": 0, "Risk": "Okänd", "Riskpoäng": 100,
                            "Senaste kurs": np.nan, "Stop-loss (indikativ)": np.nan, "RSI": np.nan, "20d %": np.nan, "Orsak": str(exc)[:120]})
        progress.progress((idx + 1) / max(1, len(enabled)), text=f"Analyserar {idx + 1} av {len(enabled)} aktier")
        time.sleep(0.05)
    progress.empty()
    res = pd.DataFrame(results)
    if res.empty:
        st.info("Välj minst en aktie i fliken Min bevakningslista.")
    else:
        candidates = int((res["Signal"] == "KÖPKANDIDAT").sum())
        down = int((res["Signal"] == "NEDÅT-RISK").sum())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Skannade aktier", len(res))
        c2.metric("Köpkandidater", candidates)
        c3.metric("Nedåtrisk", down)
        c4.metric("Datafel", int(res["Signal"].isin(["DATA SAKNAS", "FEL VID HÄMTNING"]).sum()))
        st.dataframe(res, use_container_width=True, hide_index=True, column_config={
            "Senaste kurs": st.column_config.NumberColumn(format="%.2f kr"),
            "Stop-loss (indikativ)": st.column_config.NumberColumn(format="%.2f kr"),
            "20d %": st.column_config.NumberColumn(format="%.2f%%"), "RSI": st.column_config.NumberColumn(format="%.1f")})
        st.subheader("Fördjupad analys")
        valid_options = [f"{r['Bolag']} ({r['Ticker']})" for r in results if r["Ticker"] in histories]
        if valid_options:
            choice = st.selectbox("Välj aktie", valid_options)
            ticker = choice.rsplit("(", 1)[-1].rstrip(")")
            row = res[res["Ticker"] == ticker].iloc[0]
            hist = indicators(histories[ticker])
            assessment = assess(histories[ticker])
            cc1, cc2, cc3, cc4 = st.columns(4)
            cc1.metric("Senaste kurs", f"{assessment['close']:.2f} kr")
            cc2.metric("Signalpoäng", f"{assessment['score']}/100")
            cc3.metric("Risknivå", assessment["risk"])
            cc4.metric("RSI (14)", f"{assessment['rsi']:.1f}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Kurs", line=dict(width=2)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA20"], name="SMA20", line=dict(width=1)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA50"], name="SMA50", line=dict(width=1)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA200"], name="SMA200", line=dict(width=1)))
            fig.update_layout(height=430, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="Datum", yaxis_title="Kurs (SEK)", legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**Signal: {assessment['signal']}** · Indikativ stop-loss: **{assessment['stop']:.2f} kr**")
            for reason in assessment["reasons"]:
                st.write("• " + reason)
            st.caption("Stop-loss beräknas som kurs minus 2,5 × ATR(14). Det är en uppskattad nivå, inte en garanterad säljkurs.")

with pages[1]:
    st.subheader("Välj vilka aktier som ska bevakas")
    wl = read_watchlist()
    edit = wl.rename(columns={"ticker": "Ticker", "name": "Bolag", "enabled": "Bevaka"})[["Bevaka", "Bolag", "Ticker"]]
    edited = st.data_editor(edit, hide_index=True, use_container_width=True, disabled=["Bolag", "Ticker"],
                            column_config={"Bevaka": st.column_config.CheckboxColumn("Bevaka", default=True)})
    if st.button("Spara bevakningslista"):
        save_watchlist(edited.rename(columns={"Ticker":"ticker", "Bolag":"name"})[["ticker", "name", "Bevaka"]].rename(columns={"Bevaka":"Bevaka"}))
        st.success("Bevakningslistan sparad.")
    st.divider()
    st.subheader("Ta bort en aktie")
    chosen_remove = st.selectbox("Aktie att ta bort", options=wl["ticker"].tolist(), format_func=lambda x: f"{wl.loc[wl.ticker==x,'name'].iloc[0]} ({x})")
    if st.button("Ta bort vald aktie"):
        remove_ticker(chosen_remove); st.rerun()
    st.caption("Tickerformat kan skilja sig mellan datakällor. Om en aktie saknar data, kontrollera dess Yahoo Finance-ticker.")

with pages[2]:
    st.subheader("Testportfölj – inga riktiga order")
    st.caption("Inköpskursen föreslås automatiskt från senaste tillgängliga dagskurs. Kontrollera kurs och datum innan du sparar en simulering.")
    wl = read_watchlist()
    opts = {f"{r['name']} ({r['ticker']})": (r["name"], r["ticker"]) for _, r in wl.iterrows()}
    selected = st.selectbox("Aktie", list(opts.keys()), key="paper_trade_stock")
    name, ticker = opts[selected]

    latest_price = np.nan
    quote_history = load_history(ticker, "5d")
    if not quote_history.empty:
        latest_price = float(quote_history["Close"].dropna().iloc[-1])
        latest_date = quote_history["Close"].dropna().index[-1].date()
        st.caption(f"Senaste tillgängliga kurs från datakällan: {latest_price:.2f} kr ({latest_date}). Dagsdata kan vara fördröjd.")
    else:
        st.warning("Kunde inte hämta senaste kurs för vald aktie. Ange inköpskurs manuellt och kontrollera den mot en annan källa.")

    with st.form("add_trade"):
        a1, a2 = st.columns(2)
        invested = a1.number_input("Investerat belopp (kr)", min_value=1.0, value=1000.0, step=100.0)
        default_buy_price = float(latest_price) if pd.notna(latest_price) and latest_price > 0 else 100.0
        buy_price = a2.number_input("Inköpskurs (kr per aktie)", min_value=0.01, value=default_buy_price, step=1.0, key=f"buy_price_{ticker}")
        a3, a4 = st.columns(2)
        buy_date = a3.date_input("Testdatum", value=date.today())
        stop_pct = a4.number_input("Stop-loss (%)", min_value=1.0, max_value=30.0, value=6.0, step=0.5)
        notes = st.text_input("Anteckning (valfritt)")
        submitted = st.form_submit_button("Spara testaffär", type="primary")
    if submitted:
        if buy_price <= 0:
            st.error("Inköpskurs måste vara större än noll.")
        else:
            with db_connect() as con:
                con.execute("INSERT INTO paper_trades(ticker,name,invested,buy_price,buy_date,stop_pct,notes) VALUES(?,?,?,?,?,?,?)",
                            (ticker, name, invested, buy_price, buy_date.isoformat(), stop_pct, notes))
            st.success("Testaffären sparades. Kontrollera att inköpskursen motsvarar din simulerade köpdag.")
    with db_connect() as con:
        trades = pd.read_sql_query("SELECT * FROM paper_trades ORDER BY active DESC, buy_date DESC", con)
    if trades.empty:
        st.info("Inga testaffärer ännu. Lägg till en ovan.")
    else:
        values = []
        for t in trades.to_dict("records"):
            try:
                h = load_history(t["ticker"], "1y")
                last = float(h["Close"].iloc[-1]) if not h.empty else np.nan
                if pd.notna(last):
                    pct = (last / t["buy_price"] - 1) * 100
                    pl = t["invested"] * pct / 100
                    stop = t["buy_price"] * (1 - t["stop_pct"] / 100)
                else: pct = pl = stop = np.nan
            except Exception:
                last = pct = pl = stop = np.nan
            values.append({"ID": t["id"], "Aktie": t["name"], "Ticker": t["ticker"], "Investerat kr": t["invested"],
                           "Inköpskurs": t["buy_price"], "Senaste kurs": last, "Resultat kr": pl, "Resultat %": pct,
                           "Fast stop-loss": stop, "Datum": t["buy_date"], "Aktiv": bool(t["active"]), "Anteckning": t["notes"]})
        trade_df = pd.DataFrame(values)
        if (trades["buy_price"].round(2) == 100.00).any():
            st.warning("Minst en äldre testaffär har inköpskursen exakt 100 kr. Om du inte avsiktligt angav den kursen är resultatet för den affären missvisande. Avsluta/ta bort den och skapa en ny testaffär med rätt kurs.")
        st.dataframe(trade_df, use_container_width=True, hide_index=True, column_config={
            "Investerat kr": st.column_config.NumberColumn(format="%.2f kr"), "Inköpskurs": st.column_config.NumberColumn(format="%.2f kr"),
            "Senaste kurs": st.column_config.NumberColumn(format="%.2f kr"), "Resultat kr": st.column_config.NumberColumn(format="%+.2f kr"),
            "Resultat %": st.column_config.NumberColumn(format="%+.2f%%"), "Fast stop-loss": st.column_config.NumberColumn(format="%.2f kr")})
        ids = trades["id"].tolist()
        selected_id = st.selectbox("Markera testaffär som avslutad", options=ids, format_func=lambda x: f"ID {x}: {trades.loc[trades.id==x,'name'].iloc[0]}")
        if st.button("Avsluta vald testaffär"):
            with db_connect() as con: con.execute("UPDATE paper_trades SET active=0 WHERE id=?", (int(selected_id),))
            st.rerun()
        st.download_button("Ladda ned testportfölj som CSV", trade_df.to_csv(index=False).encode("utf-8-sig"), file_name="testportfolj.csv", mime="text/csv")

with pages[3]:
    st.subheader("Historiskt test – förenklad strategi")
    st.write("Testet letar efter positiv trend över SMA50/SMA200, positiv MACD och RSI 45–68. Inträde sker nästa dags stängning. Utträde sker vid ATR-baserad stop eller efter 10 handelsdagar. En förenklad kostnad på 0,4 % per affär dras av.")
    wl = read_watchlist(); enabled = wl[wl.enabled == 1]
    selected_ticker = st.selectbox("Aktie att testa", enabled["ticker"].tolist(), format_func=lambda x: f"{enabled.loc[enabled.ticker==x,'name'].iloc[0]} ({x})")
    if st.button("Kör historiskt test", type="primary"):
        with st.spinner("Hämtar historik och testar …"):
            h = load_history(selected_ticker, "5y")
            if h.empty:
                st.error("Ingen historik kunde hämtas för denna ticker.")
            else:
                bt = backtest(h)
                b1,b2,b3,b4 = st.columns(4)
                b1.metric("Antal affärer", bt["trades"])
                b2.metric("Vinstaffärer", "–" if pd.isna(bt["win_rate"]) else f"{bt['win_rate']:.1f}%")
                b3.metric("Snitt per affär", "–" if pd.isna(bt["avg_return"]) else f"{bt['avg_return']:+.2f}%")
                b4.metric("Max nedgång i testkurva", "–" if pd.isna(bt["max_dd"]) else f"{bt['max_dd']:.2f}%")
                if bt["trades"] == 0:
                    st.info("Inga affärer hittades eller historiken är för kort.")
                else:
                    eq = pd.Series(np.cumprod(1 + np.array(bt["returns"])/100), name="Strategiindex")
                    st.line_chart(eq)
                st.warning("Historiskt test är förenklat och inte ett bevis på framtida resultat. Det saknar bland annat fullständig bolagshistorik, detaljerad spread, skatt, likviditetsbegränsningar och rigorös out-of-sample-validering. Använd det som första kontroll, inte som beslutsunderlag ensamt.")
    else:
        st.info("Välj en aktie och kör testet. Testet kan ta en stund eftersom historiska kurser hämtas från datakällan.")

with pages[4]:
    st.subheader("Senaste nyheter")
    wl = read_watchlist()
    all_names = {r["name"]: r["ticker"] for _, r in wl.iterrows()}
    selected_name = st.selectbox("Visa nyheter för", list(all_names.keys()))
    query = selected_name
    news = load_news(query)
    if not news:
        st.info("Inga nyheter kunde hämtas just nu. RSS-källan kan vara otillgänglig eller sakna relevanta träffar.")
    for item in news:
        st.markdown(f"**[{item['title']}]({item['link']})**")
        st.caption(f"{item['source']} · {item['pubDate']}")
    st.caption("Nyheter hämtas via Google News RSS. Detta är rubriksökning, inte en verifierad sentimentmodell; öppna källan och kontrollera sammanhanget innan du agerar.")

with pages[5]:
    st.subheader("Alla aktier – brett svenskt urval")
    st.caption(f"Universum: {len(STOCK_UNIVERSE)} svenska aktier och bolag. Kurser är dagsdata och kan vara fördröjda. Skanningen uppdateras automatiskt ungefär var 15:e minut medan denna flik är öppen.")

    @st.fragment(run_every="15m")
    def render_all_stocks():
        names = list(STOCK_UNIVERSE.keys())
        tickers = tuple(STOCK_UNIVERSE[n] for n in names)
        with st.spinner("Skannar aktier och hämtar senaste dagsdata …"):
            histories = load_universe_histories(tickers, "2y")
            rows = []
            for name, ticker in STOCK_UNIVERSE.items():
                hist = histories.get(ticker, pd.DataFrame())
                if hist.empty:
                    rows.append({"Bolag": name.strip(), "Ticker": ticker, "Signal": "DATA SAKNAS", "Signalpoäng": 0,
                                 "Risk": "Okänd", "Riskpoäng": 100, "Senaste kurs (kr)": np.nan,
                                 "Stop-loss (kr)": np.nan, "RSI": np.nan, "20 handelsdagar %": np.nan,
                                 "Trend/kommentar": "Kursdata saknas eller tickern kunde inte hämtas."})
                    continue
                a = assess(hist)
                last_date = hist.index[-1].date().isoformat()
                rows.append({"Bolag": name.strip(), "Ticker": ticker, "Signal": a["signal"], "Signalpoäng": a["score"],
                             "Risk": a["risk"], "Riskpoäng": a["risk_score"], "Senaste kurs (kr)": a.get("close", np.nan),
                             "Stop-loss (kr)": a.get("stop", np.nan), "RSI": a.get("rsi", np.nan),
                             "20 handelsdagar %": a.get("return20", np.nan),
                             "Trend/kommentar": f"Senaste datapunkt: {last_date}. " + " ".join(a["reasons"][:2])})
        all_results = pd.DataFrame(rows)
        if all_results.empty:
            st.error("Kunde inte skapa aktielistan. Försök uppdatera igen senare.")
            return

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aktier i universum", len(all_results))
        c2.metric("Köpkandidater", int((all_results["Signal"] == "KÖPKANDIDAT").sum()))
        c3.metric("Nedåtrisk", int((all_results["Signal"] == "NEDÅT-RISK").sum()))
        c4.metric("Saknar data", int((all_results["Signal"] == "DATA SAKNAS").sum()))

        f1, f2, f3 = st.columns([1.1, 1.1, 1.4])
        signal_filter = f1.multiselect("Visa signaler", ["KÖPKANDIDAT", "BEVAKA", "AVVAKTA", "NEDÅT-RISK", "OTILLRÄCKLIG DATA", "DATA SAKNAS"],
                                       default=["KÖPKANDIDAT", "BEVAKA", "AVVAKTA", "NEDÅT-RISK"])
        risk_filter = f2.multiselect("Risknivå", ["Lägre (relativt)", "Medel", "Hög", "Okänd"],
                                     default=["Lägre (relativt)", "Medel", "Hög", "Okänd"])
        sort_by = f3.selectbox("Sortera efter", ["Högst signalpoäng", "Lägst risk", "Starkast 20-dagars utveckling", "Störst kursfall", "Bolagsnamn"], index=0)
        query = st.text_input("Sök bolag eller ticker", placeholder="Exempel: Volvo, SEB eller VOLV-B.ST")
        filtered = all_results[all_results["Signal"].isin(signal_filter) & all_results["Risk"].isin(risk_filter)].copy()
        if query.strip():
            q = query.strip().casefold()
            filtered = filtered[filtered["Bolag"].str.casefold().str.contains(q, na=False) | filtered["Ticker"].str.casefold().str.contains(q, na=False)]
        if sort_by == "Högst signalpoäng":
            filtered = filtered.sort_values(["Signalpoäng", "Riskpoäng"], ascending=[False, True])
        elif sort_by == "Lägst risk":
            filtered = filtered.sort_values(["Riskpoäng", "Signalpoäng"], ascending=[True, False])
        elif sort_by == "Starkast 20-dagars utveckling":
            filtered = filtered.sort_values("20 handelsdagar %", ascending=False, na_position="last")
        elif sort_by == "Störst kursfall":
            filtered = filtered.sort_values("20 handelsdagar %", ascending=True, na_position="first")
        else:
            filtered = filtered.sort_values("Bolag")

        st.caption(f"Visar {len(filtered)} av {len(all_results)} bolag. Signalpoäng är en teknisk indikator, inte en prognos eller garanti.")
        st.dataframe(filtered, use_container_width=True, hide_index=True, column_config={
            "Signalpoäng": st.column_config.ProgressColumn("Signalpoäng", min_value=0, max_value=100, format="%d/100"),
            "Riskpoäng": st.column_config.NumberColumn("Riskpoäng", format="%d/100"),
            "Senaste kurs (kr)": st.column_config.NumberColumn(format="%.2f kr"),
            "Stop-loss (kr)": st.column_config.NumberColumn(format="%.2f kr"),
            "20 handelsdagar %": st.column_config.NumberColumn(format="%.2f%%"),
            "RSI": st.column_config.NumberColumn(format="%.1f")
        })
        st.download_button("Ladda ned aktielistan som CSV", filtered.to_csv(index=False).encode("utf-8-sig"),
                           file_name="svenska_aktiesignaler.csv", mime="text/csv", key="download_all_stocks")
        st.caption("Uppdatering sker ungefär var 15:e minut medan appen är aktiv och fliken visas. Detta är inte en bakgrundsskanning när appen är stängd. Dagsdata är inte realtidsdata.")

    render_all_stocks()


st.divider()
st.caption(f"Senast sidan kördes: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Prototypen använder dagsdata, inte garanterat realtidsdata.")
