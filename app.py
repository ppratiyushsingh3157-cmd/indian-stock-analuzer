import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Indian Equity Research Analyzer", page_icon="📈", layout="wide")

API_KEY = "JTZEICIDLVXZEO06"

st.title("📈 Indian Equity Research Analyzer")
st.markdown("##### By Pratyush Singh | MBA - Banking & Financial Engineering | Chandigarh University")
st.markdown("---")

ticker = st.text_input("🔍 Enter BSE/NSE Stock Symbol", value="RELIANCE.BSE", placeholder="e.g. RELIANCE.BSE, TCS.BSE, DIXON.BSE")

if st.button("🚀 Analyze Stock", type="primary"):
    with st.spinner("Fetching live data..."):

        # FETCH PRICE DATA
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={API_KEY}"
        r = requests.get(url)
        data = r.json()

        if "Time Series (Daily)" not in data:
            st.error("❌ Stock not found! Try: RELIANCE.BSE or TCS.BSE")
            st.stop()

        ts = data["Time Series (Daily)"]
        df = pd.DataFrame(ts).T
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.astype(float)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.last('365D')

        # KEY METRICS
        st.markdown("## 📊 Key Metrics")
        current = df['Close'].iloc[-1]
        high_52w = df['High'].max()
        low_52w = df['Low'].min()
        returns_1y = round(((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100, 2)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Current Price", f"₹{round(current, 2)}")
        col2.metric("📈 52W High", f"₹{round(high_52w, 2)}")
        col3.metric("📉 52W Low", f"₹{round(low_52w, 2)}")
        col4.metric("📊 1Y Return", f"{returns_1y}%")

        # PRICE CHART
        st.markdown("---")
        st.markdown("## 📉 Price Chart + Moving Averages")
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='white', width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 DMA', line=dict(color='#00bfff', width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 DMA', line=dict(color='orange', width=1.5)))
        fig.update_layout(template='plotly_dark', title=f'{ticker} - Price Chart', height=450)
        st.plotly_chart(fig, use_container_width=True)

        # RSI
        st.markdown("## 📊 RSI Indicator")
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        rsi = df['RSI'].iloc[-1]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='yellow')))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold")
        fig2.update_layout(template='plotly_dark', title='RSI Indicator', height=300)
        st.plotly_chart(fig2, use_container_width=True)

        # SWOT
        st.markdown("---")
        st.markdown("## 🔍 SWOT Analysis")
        col1, col2 = st.columns(2)
        with col1:
            strengths = [
                f"1Y Return of {returns_1y}% shows strong performance" if returns_1y > 10 else "Stable price action",
                f"Trading near 52W High ₹{round(high_52w,0)}" if current > high_52w * 0.85 else "Price consolidating",
                "Listed on BSE/NSE — High liquidity & transparency",
                "Part of India growth story"
            ]
            st.success("**💪 STRENGTHS**\n" + "\n".join([f"- {s}" for s in strengths]))
            weaknesses = [
                f"Down {round(((current/high_52w)-1)*100,1)}% from 52W High" if current < high_52w * 0.9 else "Near 52W high — limited upside",
                f"RSI at {round(rsi,1)} — Overbought risk" if rsi > 65 else f"RSI at {round(rsi,1)}",
                "Dependent on macro & global factors",
                "Sector competition risk"
            ]
            st.error("**⚠️ WEAKNESSES**\n" + "\n".join([f"- {w}" for w in weaknesses]))
        with col2:
            st.info("""
**🚀 OPPORTUNITIES**
- India GDP growth 6-7% tailwind
- Government PLI scheme support
- Export market expansion
- Growing middle class demand
- Digital India momentum
            """)
            st.warning("""
**🌧️ THREATS**
- Global recession risk
- RBI rate hike risk
- Rupee depreciation
- Intense competition
- Regulatory changes
            """)

        # AI SIGNAL
        st.markdown("---")
        st.markdown("## 🤖 AI Buy/Sell/Hold Signal")
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]

        score = 0
        reasons = []

        if current > ma50:
            score += 1
            reasons.append("✅ Price above 50 DMA — short term bullish")
        else:
            score -= 1
            reasons.append("❌ Price below 50 DMA — bearish")

        if current > ma200:
            score += 1
            reasons.append("✅ Price above 200 DMA — long term uptrend")
        else:
            score -= 1
            reasons.append("❌ Price below 200 DMA — downtrend")

        if 30 < rsi < 70:
            score += 1
            reasons.append(f"✅ RSI {round(rsi,1)} — healthy zone")
        elif rsi > 70:
            score -= 1
            reasons.append(f"⚠️ RSI {round(rsi,1)} — overbought")
        else:
            score += 1
            reasons.append(f"✅ RSI {round(rsi,1)} — oversold bounce possible")

        if returns_1y > 15:
            score += 1
            reasons.append(f"✅ Strong 1Y return of {returns_1y}%")
        elif returns_1y < 0:
            score -= 1
            reasons.append(f"❌ Negative 1Y return of {returns_1y}%")

        for r in reasons:
            st.write(r)

        st.markdown("### 🎯 Final Signal:")
        if score >= 3:
            st.success(f"🟢 **BUY** — Score {score}/4 — Strong bullish setup!")
        elif score <= 0:
            st.error(f"🔴 **SELL** — Score {score}/4 — Bearish signals!")
        else:
            st.warning(f"🟡 **HOLD** — Score {score}/4 — Mixed signals, watch closely!")

        st.markdown("---")
        st.caption("⚠️ Educational purpose only. Not financial advice.")
        st.caption("Built by Pratyush Singh | MBA Banking & Financial Engineering | Chandigarh University")
