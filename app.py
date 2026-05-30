import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(page_title="Indian Equity Research Analyzer", page_icon="📈", layout="wide")

st.title("📈 Indian Equity Research Analyzer")
st.markdown("### By Pratyush Singh | MBA - Banking & Financial Engineering | CU")
st.markdown("---")

ticker = st.text_input("🔍 Enter NSE Stock Symbol", value="DIXON.NS")

if st.button("🚀 Analyze Stock", type="primary"):
    try:
        with st.spinner("Fetching live data... please wait"):
            time.sleep(3)
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y")
            info = stock.fast_info

        st.markdown("## 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Current Price", f"₹{round(info.last_price, 2)}")
        col2.metric("📈 52W High", f"₹{round(info.year_high, 2)}")
        col3.metric("📉 52W Low", f"₹{round(info.year_low, 2)}")
        col4.metric("🏢 Market Cap", f"₹{round(info.market_cap/1e9, 2)}B")

        st.markdown("---")
        st.markdown("## 📉 Price Chart + Moving Averages")
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 Day MA', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 Day MA', line=dict(color='orange')))
        fig.update_layout(template='plotly_dark', title=f'{ticker} - Price Chart')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("## 📊 RSI Indicator")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='yellow')))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold")
        fig2.update_layout(template='plotly_dark', title='RSI Indicator')
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.markdown("## 🔍 SWOT Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.success("""
**💪 STRENGTHS**
- Strong brand presence in India
- Listed on NSE — High liquidity
- Growing revenue trajectory
- Professional management team
            """)
            st.error("""
**⚠️ WEAKNESSES**
- Dependent on macro environment
- Valuation risk if growth slows
- Margin pressure risk
- Limited global diversification
            """)
        with col2:
            st.info("""
**🚀 OPPORTUNITIES**
- India GDP growth 6-7% tailwind
- PLI scheme benefits
- Export market expansion
- Growing middle class consumption
            """)
            st.warning("""
**🌧️ THREATS**
- Global recession risk
- RBI interest rate changes
- New competition risk
- Regulatory changes
            """)

        st.markdown("---")
        st.markdown("## 🤖 AI Signal")
        last = df['Close'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]
        rsi = df['RSI'].iloc[-1]

        if last > ma50 and last > ma200 and rsi < 70:
            st.success(f"🟢 BUY — Price above 50MA & 200MA. RSI: {round(rsi,1)} — Bullish!")
        elif last < ma50 and last < ma200 and rsi > 30:
            st.error(f"🔴 SELL — Price below 50MA & 200MA. RSI: {round(rsi,1)} — Bearish!")
        elif rsi > 70:
            st.warning(f"🟡 HOLD — RSI: {round(rsi,1)} — Overbought!")
        else:
            st.warning(f"🟡 HOLD — Mixed signals. RSI: {round(rsi,1)}")

        st.markdown("---")
        st.caption("⚠️ Disclaimer: Educational purpose only. Not financial advice.")
        st.caption("Built by Pratyush Singh | MBA Banking & Financial Engineering | CU")

    except Exception as e:
        st.error("⚠️ Data fetch failed! Please wait 30 seconds and try again.")
        st.info("💡 Tip: Yahoo Finance has rate limits. Wait a moment and retry!")
