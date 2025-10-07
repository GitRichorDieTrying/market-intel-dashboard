import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.title("📊 Market Intelligence Dashboard")

ticker = st.text_input("Enter stock ticker:", "AAPL")

if ticker:
    end = datetime.today()
    start = end - timedelta(days=180)

    # Fetch data with adjusted close to ensure Close column exists
    data = yf.download(ticker, start=start, end=end, auto_adjust=False)

    # If yfinance returns MultiIndex columns, flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]

    # Verify we have Close column
    if not data.empty and "Close" in data.columns:
        data = data.dropna(subset=["Close"])

        start_price = data["Close"].iloc[0]
        end_price = data["Close"].iloc[-1]
        pct_change = (end_price - start_price) / start_price * 100

        # Moving averages
        data["MA20"] = data["Close"].rolling(window=20).mean()
        data["MA50"] = data["Close"].rolling(window=50).mean()

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index, y=data["Close"],
            mode="lines", name="Price",
            line=dict(color="royalblue")
        ))
        fig.add_trace(go.Scatter(
            x=data.index, y=data["MA20"],
            mode="lines", name="MA20",
            line=dict(color="orange")
        ))
        fig.add_trace(go.Scatter(
            x=data.index, y=data["MA50"],
            mode="lines", name="MA50",
            line=dict(color="green")
        ))
        fig.update_layout(
            title=f"{ticker.upper()} — 6-Month Price History with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("6-Month Change", f"{pct_change:.2f}%")
        col2.metric("Last Close Price", f"${end_price:.2f}")

    else:
        st.error("Downloaded data doesn’t have a Close column — try a different ticker.")
