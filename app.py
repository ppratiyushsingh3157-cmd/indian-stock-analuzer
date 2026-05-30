import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Indian Stock Analyzer", page_icon="📈", layout="wide")
st.title("📈 Indian Stock Market Analyzer")
st.markdown("### By Pratyush Singh | MBA - Banking & Financial Engineering")

ticker = st.text_input("Enter NSE Stock Symbol (e.g. DIXON.NS, RELIANCE.NS, TCS.NS)", value="DIXON.NS")

if ticker:
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y")
    info = stock.info

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"₹{info.get('currentPrice', 'N/A')}")
    col2.metric("Market Cap", f"₹{round(info.get('marketCap', 0)/1e9, 2)}B")
    col3.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
    col4.metric("P/B Ratio", info.get('priceToBook', 'N/A'))

    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 Day MA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 Day MA'))
    fig.update_layout(title=f'{ticker} - 5 Year Chart with Moving Averages')
    st.plotly_chart(fig, use_container_width=True)

    last = df['Close'].iloc[-1]
    ma50 = df['MA50'].iloc[-1]
    ma200 = df['MA200'].iloc[-1]

    if last > ma50 and last > ma200:
        st.success("🟢 AI Signal: BUY — Price above both moving averages!")
    elif last < ma50 and last < ma200:
        st.error("🔴 AI Signal: SELL — Price below both moving averages!")
    else:
        st.warning("🟡 AI Signal: HOLD — Mixed signals")
