 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/stock_trading_agent.py b/stock_trading_agent.py
index d061dc4128bbb3db40c4fe0e0966e254252ab3de..64d487e6c20f46871f87379acd39b82e63581e1b 100644
--- a/stock_trading_agent.py
+++ b/stock_trading_agent.py
@@ -1,39 +1,53 @@
 import yfinance as yf
 import pandas as pd
 import numpy as np
 import datetime
 import streamlit as st
 import plotly.graph_objects as go
 from plotly.subplots import make_subplots
 import requests
 
+# Helper to search tickers from Yahoo Finance
+def search_tickers(query: str):
+    """Return a list of ticker symbols matching the search query."""
+    if not query:
+        return []
+    url = "https://query1.finance.yahoo.com/v1/finance/search"
+    try:
+        resp = requests.get(url, params={"q": query, "quotesCount": 10, "newsCount": 0})
+        if resp.status_code == 200:
+            data = resp.json()
+            return [item.get("symbol") for item in data.get("quotes", [])]
+    except Exception:
+        pass
+    return []
+
 # Optional: for paper/live trading
 from alpaca_trade_api.rest import REST, TimeFrame
 
 # Define key parameters
-TICKERS = ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'AMZN']
 INTERVAL = '5m'
 PERIOD = '1d'
 MAX_RISK_PER_TRADE = 0.01
 CAPITAL = 100000
 TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
 TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
 ALPACA_API_KEY = st.secrets["ALPACA_API_KEY"]
 ALPACA_SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
 ALPACA_ENDPOINT = st.secrets.get("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets")
 
 alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_ENDPOINT)
 
 # Historical backtest data
 def get_historical_data(ticker, period='6mo', interval='1d'):
     df = yf.download(ticker, period=period, interval=interval)
     df['Ticker'] = ticker
     return df
 
 # Strategy selector
 def generate_signals(df, strategy='SMA_MACD_RSI'):
     df['SMA_5'] = df['Close'].rolling(window=5).mean()
     df['SMA_20'] = df['Close'].rolling(window=20).mean()
     df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
     df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
     df['MACD'] = df['EMA_12'] - df['EMA_26']
diff --git a/stock_trading_agent.py b/stock_trading_agent.py
index d061dc4128bbb3db40c4fe0e0966e254252ab3de..64d487e6c20f46871f87379acd39b82e63581e1b 100644
--- a/stock_trading_agent.py
+++ b/stock_trading_agent.py
@@ -46,41 +60,55 @@ def generate_signals(df, strategy='SMA_MACD_RSI'):
     rs = avg_gain / avg_loss
     df['RSI'] = 100 - (100 / (1 + rs))
     df['Signal'] = 0
 
     if strategy == 'SMA_MACD_RSI':
         df.loc[(df['SMA_5'] > df['SMA_20']) & (df['MACD'] > df['Signal_Line']) & (df['RSI'] < 70), 'Signal'] = 1
         df.loc[(df['SMA_5'] < df['SMA_20']) & (df['MACD'] < df['Signal_Line']) & (df['RSI'] > 30), 'Signal'] = -1
     elif strategy == 'RSI_only':
         df.loc[df['RSI'] < 30, 'Signal'] = 1
         df.loc[df['RSI'] > 70, 'Signal'] = -1
 
     return df
 
 # Backtesting
 
 def backtest_strategy(df):
     df['Position'] = df['Signal'].shift(1).fillna(0)
     df['Returns'] = df['Close'].pct_change().fillna(0)
     df['Strategy'] = df['Position'] * df['Returns']
     df['Cumulative Market Returns'] = (1 + df['Returns']).cumprod()
     df['Cumulative Strategy Returns'] = (1 + df['Strategy']).cumprod()
     return df
 
 # Streamlit App
 st.title("Backtesting and Live Trading Dashboard")
-selected_ticker = st.selectbox("Select Ticker", TICKERS)
+
+# Sidebar search for tickers
+query = st.sidebar.text_input("Company name")
+tickers = search_tickers(query) if query else []
+
+if tickers:
+    selected_ticker = st.sidebar.selectbox("Select Ticker", tickers)
+else:
+    st.sidebar.write("Enter a company name to search tickers")
+    selected_ticker = None
+
 strategy = st.selectbox("Select Strategy", ['SMA_MACD_RSI', 'RSI_only'])
 
-# Historical Backtest
-hist_data = get_historical_data(selected_ticker)
-hist_data = generate_signals(hist_data, strategy)
-bt = backtest_strategy(hist_data)
-st.subheader("Backtest Results")
-st.line_chart(bt[['Cumulative Market Returns', 'Cumulative Strategy Returns']])
-
-# Live Run
-if st.button("Run Live Agent"):
-    df_live = get_historical_data(selected_ticker, period='5d', interval='5m')
-    df_live = generate_signals(df_live, strategy)
-    latest = df_live.iloc[-1]
-    st.write("Latest Signal:", 'BUY' if latest['Signal'] == 1 else 'SELL' if latest['Signal'] == -1 else 'HOLD')
+if selected_ticker:
+    # Historical Backtest
+    hist_data = get_historical_data(selected_ticker)
+    hist_data = generate_signals(hist_data, strategy)
+    bt = backtest_strategy(hist_data)
+    st.subheader("Backtest Results")
+    st.line_chart(bt[['Cumulative Market Returns', 'Cumulative Strategy Returns']])
+
+    # Live Run
+    if st.button("Run Live Agent"):
+        df_live = get_historical_data(selected_ticker, period='5d', interval='5m')
+        df_live = generate_signals(df_live, strategy)
+        latest = df_live.iloc[-1]
+        st.write("Latest Signal:", 'BUY' if latest['Signal'] == 1 else 'SELL' if latest['Signal'] == -1 else 'HOLD')
+else:
+    st.info("Search for a company and select a ticker to run the analysis.")
+
 
EOF
)
