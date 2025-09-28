import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import json

# --------- Sidebar Controls ---------
st.sidebar.header("Quant Phone Starter v2")
ticker = st.sidebar.text_input("Ticker", "PLTR")
tf = st.sidebar.selectbox("Timeframe", ["15m","1h","1d"], index=0)
bars = st.sidebar.slider("Bars", 100, 1200, 500)
show_mc = st.sidebar.checkbox("Monte Carlo Projection", False)

# --------- Data Fetch ---------
@st.cache_data
def get_data(ticker, tf, bars):
    interval_map = {"15m":"15m","1h":"60m","1d":"1d"}
    df = yf.download(ticker, period="60d", interval=interval_map[tf])
    if df.empty:
        return pd.DataFrame()
    df = df.tail(bars).copy()
    df.reset_index(inplace=True)
    return df

df = get_data(ticker, tf, bars)

# --------- Indicators ---------
def add_indicators(df):
    if df.empty: return df
    for p in [9,15,30,65,200]:
        df[f"EMA{p}"] = df["Close"].ewm(span=p).mean()
    df["ATR14"] = (df["High"]-df["Low"]).rolling(14).mean()
    df["RSI14"] = 100 - (100/(1+df["Close"].pct_change().add(1).rolling(14).apply(np.prod)**(1/14)))
    df["MACD"] = df["Close"].ewm(span=12).mean()-df["Close"].ewm(span=26).mean()
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    return df

df = add_indicators(df)

# --------- ICT Levels ---------
def ict_levels(df):
    out={}
    if df.empty: return out
    out["PDH"]=df["High"].iloc[-2]
    out["PDL"]=df["Low"].iloc[-2]
    out["PDC"]=df["Close"].iloc[-2]
    out["IBH"]=df["High"].head(5).max()
    out["IBL"]=df["Low"].head(5).min()
    return out

levels = ict_levels(df)

# --------- Chart ---------
st.title(f"{ticker} — {tf} ({bars} bars)")
if not df.empty:
    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price")])

    # Overlay EMAs
    for p in [9,15,30,65,200]:
        fig.add_trace(go.Scatter(x=df["Date"], y=df[f"EMA{p}"],
            mode="lines", name=f"EMA{p}"))

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Show ICT + metrics
    st.subheader("Levels & Metrics")
    st.json(levels)

    st.subheader("Latest Metrics")
    lastrow = df.iloc[-1].to_dict()
    st.json({k:float(v) if isinstance(v,(int,float,np.number)) else str(v)
             for k,v in lastrow.items()})

else:
    st.warning("No data found.")

# --------- Monte Carlo ---------
if show_mc and not df.empty:
    st.subheader("Monte Carlo Projection")
    last_price = df["Close"].iloc[-1]
    rets = df["Close"].pct_change().dropna()
    mu, sigma = rets.mean(), rets.std()
    sims = []
    for _ in range(200):
        prices = [last_price]
        for _ in range(50):
            prices.append(prices[-1]*np.exp(np.random.normal(mu,sigma)))
        sims.append(prices)
    simdf = pd.DataFrame(sims).T
    st.line_chart(simdf)

# --------- CSV endpoints ---------
query = st.experimental_get_query_params()
if "csv_candles" in query:
    st.write(df.to_csv(index=False))
if "csv_levels" in query:
    payload = {"last":df["Close"].iloc[-1] if not df.empty else None,
               "atr14":df["ATR14"].iloc[-1] if not df.empty else None,
               "ema_cluster":{f"EMA{p}":df[f"EMA{p}"].iloc[-1] for p in [9,15,30,65,200]} if not df.empty else {},
               **levels}
    st.write(",".join(payload.keys()))
    st.write(",".join(str(v) for v in payload.values()))
