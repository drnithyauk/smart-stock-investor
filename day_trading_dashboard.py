# Ensure required modules are installed before proceeding
try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed in the current environment.")

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Stock Investor", layout="wide")

st.title("📈 Smart Stock Investor Dashboard")

# Sidebar for stock ticker
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g., AAPL, TSLA, MSFT):", value="AAPL")

# Date range selection
st.sidebar.subheader("Date Range")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=2)
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

# Fetch stock data
def fetch_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

df = fetch_data(ticker, period, interval)

if df.empty:
    st.warning("No data available for this ticker.")
else:
    st.subheader(f"{ticker} Stock Price ({period}, {interval})")
    st.line_chart(df['Close'])

    # Moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    st.subheader("Moving Averages")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df['Close'], label='Close')
    ax.plot(df.index, df['MA20'], label='MA20')
    ax.plot(df.index, df['MA50'], label='MA50')
    ax.legend()
    st.pyplot(fig)

    # Recent data table
    st.subheader("Recent Stock Data")
    st.dataframe(df.tail(10))

    # Placeholder for future features
    st.markdown("🛠️ *Upcoming Features: Sentiment Analysis, AI Trading Signals, Portfolio Backtesting*")
