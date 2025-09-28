# Quant Phone Starter v2 (iPhone-first)

A lightweight Streamlit app designed to run on Streamlit Cloud and feed data into Google Sheets.

## Features
- Live candlestick charts with Plotly
- Indicators: EMA (9,15,30,65,200), ATR14, RSI, MACD
- ICT levels (PDH, PDL, PDC, IBH, IBL)
- Simple fair value gap (FVG) scan
- Monte Carlo random walk simulation
- CSV endpoints for Sheets / automation
  - Candles: `?csv_candles=1&ticker=PLTR&tf=15m&bars=800`
  - Levels:  `?csv_levels=1&ticker=PLTR&tf=15m&bars=800`

Works great with iPhone → Safari → “Add to Home Screen” for an app-like experience.
