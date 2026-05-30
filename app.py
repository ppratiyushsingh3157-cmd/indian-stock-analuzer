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
            quote = stock.info

        # COMPANY OVERVIEW
        st.markdown("## 🏢 Company Overview")
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown(f"### {quote.get('longName', ticker)}")
            st.markdown(f"**Sector:** {quote.get('sector', 'N/A')} | **Industry:** {quote.get('industry', 'N/A')}")
            st.markdown(f"**Website:** {quote.get('website', 'N/A')}")
            st.markdown("#### 📋 About")
            st.write(quote.get('longBusinessSummary', 'No description available'))
        with col2:
            st.markdown("#### 🔑 Key Info")
            st.info(f"""
**Exchange:** NSE/BSE
**Country:** India
**Currency:** INR
**Employees:** {quote.get('fullTimeEmployees', 'N/A'):,} if isinstance(quote.get('fullTimeEmployees'), int) else 'N/A'
            """)

        # KEY METRICS
        st.markdown("---")
        st.markdown("## 📊 Key Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("💰 Price", f"₹{round(info.last_price, 2)}")
        col2.metric("📈 52W High", f"₹{round(info.year_high, 2)}")
        col3.metric("📉 52W Low", f"₹{round(info.year_low, 2)}")
        col4.metric("🏢 Mkt Cap", f"₹{round(info.market_cap/1e9, 2)}B")
        col5.metric("📊 P/E", round(quote.get('trailingPE', 0), 1))
        col6.metric("📚 P/B", round(quote.get('priceToBook', 0), 1))

        st.markdown("---")
        st.markdown("## 📐 Fundamental Ratios")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("ROE %", f"{round(quote.get('returnOnEquity', 0)*100, 1)}%")
        col2.metric("ROCE %", f"{round(quote.get('returnOnAssets', 0)*100, 1)}%")
        col3.metric("Debt/Equity", round(quote.get('debtToEquity', 0), 2))
        col4.metric("Div Yield", f"{round(quote.get('dividendYield', 0)*100, 2)}%")
        col5.metric("Book Value", f"₹{round(quote.get('bookValue', 0), 2)}")

        # PRICE CHART
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

        # RSI
        st.markdown("## 📊 RSI Indicator")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='yellow')))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold")
        fig2.update_layout(template='plotly_dark', title='RSI Indicator')
        st.plotly_chart(fig2, use_container_width=True)

        # FINANCIALS
        st.markdown("---")
        st.markdown("## 💹 Financial Statements")
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Income Statement", "🏦 Balance Sheet", "💵 Cash Flow", "👥 Investors"])

        with tab1:
            try:
                income = stock.financials.T
                income.index = income.index.year
                income = income.sort_index()
                cols = ['Total Revenue', 'Gross Profit', 'Net Income']
                cols = [c for c in cols if c in income.columns]
                income_show = income[cols] / 1e7
                income_show.columns = [c + ' (₹ Cr)' for c in cols]
                st.dataframe(income_show.style.format("{:,.0f}"))
                fig3 = go.Figure()
                for col in cols:
                    fig3.add_trace(go.Bar(name=col, x=income.index.astype(str), y=income[col]/1e7))
                fig3.update_layout(template='plotly_dark', title='Revenue & Profit Trend (₹ Cr)', barmode='group')
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Income statement data not available")

        with tab2:
            try:
                balance = stock.balance_sheet.T
                balance.index = balance.index.year
                balance = balance.sort_index()
                cols = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Stockholders Equity']
                cols = [c for c in cols if c in balance.columns]
                balance_show = balance[cols] / 1e7
                st.dataframe(balance_show.style.format("{:,.0f}"))
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(name='Assets', x=balance.index.astype(str), y=balance['Total Assets']/1e7))
                if 'Stockholders Equity' in balance.columns:
                    fig4.add_trace(go.Bar(name='Equity', x=balance.index.astype(str), y=balance['Stockholders Equity']/1e7))
                fig4.update_layout(template='plotly_dark', title='Balance Sheet Trend (₹ Cr)', barmode='group')
                st.plotly_chart(fig4, use_container_width=True)
            except:
                st.warning("Balance sheet data not available")

        with tab3:
            try:
                cashflow = stock.cashflow.T
                cashflow.index = cashflow.index.year
                cashflow = cashflow.sort_index()
                cols = ['Operating Cash Flow', 'Free Cash Flow']
                cols = [c for c in cols if c in cashflow.columns]
                cashflow_show = cashflow[cols] / 1e7
                cashflow_show.columns = [c + ' (₹ Cr)' for c in cols]
                st.dataframe(cashflow_show.style.format("{:,.0f}"))
                fig5 = go.Figure()
                for col in cols:
                    fig5.add_trace(go.Bar(name=col, x=cashflow.index.astype(str), y=cashflow[col]/1e7))
                fig5.update_layout(template='plotly_dark', title='Cash Flow Trend (₹ Cr)', barmode='group')
                st.plotly_chart(fig5, use_container_width=True)
            except:
                st.warning("Cash flow data not available")

        with tab4:
            try:
                holders = stock.institutional_holders
                if holders is not None and not holders.empty:
                    st.markdown("### 🏦 Top Institutional Investors")
                    st.dataframe(holders)
                else:
                    st.warning("Institutional investor data not available")
                major = stock.major_holders
                if major is not None and not major.empty:
                    st.markdown("### 📊 Shareholding Pattern")
                    st.dataframe(major)
            except:
                st.warning("Investor data not available")

        # SWOT
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

        # AI SIGNAL
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
        st.info("💡 Yahoo Finance rate limit — wait a moment and retry!")
