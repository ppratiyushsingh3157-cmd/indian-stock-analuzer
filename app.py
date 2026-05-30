import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(page_title="Indian Stock Analyzer", page_icon="📈", layout="wide")
st.title("📈 Indian Stock Market Analyzer")
st.markdown("### By Pratyush Singh | MBA - Banking & Financial Engineering")

ticker = st.text_input("Enter NSE Stock Symbol (e.g. DIXON.NS, RELIANCE.NS, TCS.NS)", value="DIXON.NS")

if st.button("Analyze Stock"):
    with st.spinner("Fetching data..."):
        time.sleep(2)
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        info = stock.fast_info

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"₹{round(info.last_price, 2)}")
        col2.metric("52W High", f"₹{round(info.year_high, 2)}")
        col3.metric("52W Low", f"₹{round(info.year_low, 2)}")
        col4.metric("Market Cap", f"₹{round(info.market_cap/1e9, 2)}B")

        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 Day MA'))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 Day MA'))
        fig.update_layout(title=f'{ticker} - Price Chart with Moving Averages')
        st.plotly_chart(fig, use_container_width=True)

        last = df['Close'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]

        if last > ma50 and last > ma200:
            st.success("🟢 AI Signal: BUY!")
        elif last < ma50 and last < ma200:
            st.error("🔴 AI Signal: SELL!")
        else:
            st.warning("🟡 AI Signal: HOLD!")
