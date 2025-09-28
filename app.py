import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quant Phone Starter", layout="wide")
st.title("📈 Quant Phone Starter")

# ---------- Controls
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Ticker", "AAPL").strip().upper()
    period = st.selectbox(
        "Period",
        ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=2,
    )
    interval = st.selectbox(
        "Interval",
        ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "1wk", "1mo"],
        index=8,  # 1d
    )

@st.cache_data(show_spinner=False)
def load(tkr: str, per: str, iv: str) -> pd.DataFrame:
    df = yf.download(tkr, period=per, interval=iv, progress=False, auto_adjust=False)
    if df.empty:
        return df
    # yfinance sometimes returns MultiIndex columns -> flatten
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c if isinstance(c, str) else c[0] for c in df.columns]
    df = df.reset_index().rename(columns={"Datetime": "Date"})
    if "Date" not in df.columns:  # daily frames call it "Date"
        df = df.rename(columns={"index": "Date"})
    # Basic indicators (lightweight)
    if "Close" in df.columns:
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        # RSI(14) quick calc
        delta = df["Close"].diff()
        up = np.where(delta > 0, delta, 0.0)
        down = np.where(delta < 0, -delta, 0.0)
        roll_up = pd.Series(up).rolling(14).mean()
        roll_dn = pd.Series(down).rolling(14).mean()
        rs = roll_up / (roll_dn.replace(0, np.nan))
        df["RSI14"] = 100 - (100 / (1 + rs))
    return df

df = load(ticker, period, interval)

# ---------- Page content
if df.empty:
    st.warning("No data returned. Try a longer period or a different ticker.")
else:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"{ticker} — {period} / {interval}")
        st.line_chart(df.set_index("Date")[["Close"]])
    with c2:
        last = df.iloc[-1]
        st.metric("Last", f"{last['Close']:.2f}")
        if not np.isnan(last.get("SMA20", np.nan)):
            st.metric("SMA20", f"{last['SMA20']:.2f}")
        if not np.isnan(last.get("SMA50", np.nan)):
            st.metric("SMA50", f"{last['SMA50']:.2f}")
        if not np.isnan(last.get("RSI14", np.nan)):
            st.metric("RSI14", f"{last['RSI14']:.1f}")
    st.divider()
    st.dataframe(df.tail(200), use_container_width=True)

st.caption("If you see a chart and a table, the build is good. Add features on top of this.")
