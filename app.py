import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(page_title="Indian Equity Research Analyzer", page_icon="📈", layout="wide")

st.title("📈 Indian Equity Research Analyzer")
st.markdown("##### By Pratyush Singh | MBA - Banking & Financial Engineering | Chandigarh University")
st.markdown("---")

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    @st.cache_data(ttl=3600)
    info = stock.fast_info
    return stock, df, info

ticker = st.text_input("🔍 Enter NSE Stock Symbol", value="DIXON.NS")

if st.button("🚀 Analyze Stock", type="primary"):
    try:
        with st.spinner("Fetching data..."):
            stock, df, info = get_stock_data(ticker)
            if df.empty:
                st.error("❌ Stock not found!")
                st.stop()

        # KEY METRICS
        st.markdown("## 📊 Key Metrics")
        current = round(info.last_price, 2)
        high_52w = round(info.year_high, 2)
        low_52w = round(info.year_low, 2)
        mkt_cap = round(info.market_cap/1e7, 0)
        returns_1y = round(((df['Close'].iloc[-1]/df['Close'].iloc[0])-1)*100, 2)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 Price", f"₹{current}")
        col2.metric("📈 52W High", f"₹{high_52w}")
        col3.metric("📉 52W Low", f"₹{low_52w}")
        col4.metric("🏢 Mkt Cap (Cr)", f"₹{mkt_cap:,.0f}")
        col5.metric("📊 1Y Return", f"{returns_1y}%")

        # FUNDAMENTAL RATIOS
        try:
            quote = stock.info
            pe = round(quote.get('trailingPE', 0), 1)
            pb = round(quote.get('priceToBook', 0), 1)
            roe = round(quote.get('returnOnEquity', 0)*100, 1)
            debt_eq = round(quote.get('debtToEquity', 0), 2)
            div = round(quote.get('dividendYield', 0)*100, 2)
            book_val = round(quote.get('bookValue', 0), 2)
            profit_margin = round(quote.get('profitMargins', 0)*100, 1)
            rev_growth = round(quote.get('revenueGrowth', 0)*100, 1)
            company_name = quote.get('longName', ticker)
            description = quote.get('longBusinessSummary', 'N/A')
            sector = quote.get('sector', 'N/A')
            industry = quote.get('industry', 'N/A')
        except:
            pe=pb=roe=debt_eq=div=book_val=profit_margin=rev_growth=0
            company_name=ticker
            description=sector=industry='N/A'

        st.markdown(f"### 🏢 {company_name}")
        st.markdown(f"**Sector:** {sector} | **Industry:** {industry}")

        st.markdown("---")
        st.markdown("## 📐 Fundamental Ratios")
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        col1.metric("P/E", pe)
        col2.metric("P/B", pb)
        col3.metric("ROE%", f"{roe}%")
        col4.metric("Debt/Eq", debt_eq)
        col5.metric("Div Yield", f"{div}%")
        col6.metric("Book Val", f"₹{book_val}")

        # ABOUT
        st.markdown("---")
        st.markdown("## 📋 About Company")
        st.write(str(description)[:600]+"..." if len(str(description))>600 else description)

        # PRICE CHART
        st.markdown("---")
        st.markdown("## 📉 Price Chart + Moving Averages")
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        delta = df['Close'].diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = (-delta.where(delta<0,0)).rolling(14).mean()
        df['RSI'] = 100-(100/(1+(gain/loss)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='white',width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 DMA', line=dict(color='#00bfff',width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 DMA', line=dict(color='orange',width=1.5)))
        fig.update_layout(template='plotly_dark', title=f'{company_name} — Price Chart', height=450)
        st.plotly_chart(fig, use_container_width=True)

        # RSI
        st.markdown("## 📊 RSI Indicator")
        rsi_val = df['RSI'].iloc[-1]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='yellow')))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold")
        fig2.update_layout(template='plotly_dark', title='RSI Indicator', height=300)
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
                cols = [c for c in ['Total Revenue','Gross Profit','Operating Income','Net Income'] if c in income.columns]
                st.dataframe((income[cols]/1e7).style.format("{:,.0f}"), use_container_width=True)
                fig3 = go.Figure()
                for col in cols:
                    fig3.add_trace(go.Bar(name=col, x=income.index.astype(str), y=income[col]/1e7))
                fig3.update_layout(template='plotly_dark', title='Revenue & Profit (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Income data not available")

        with tab2:
            try:
                balance = stock.balance_sheet.T
                balance.index = balance.index.year
                balance = balance.sort_index()
                cols = [c for c in ['Total Assets','Total Liabilities Net Minority Interest','Stockholders Equity','Total Debt'] if c in balance.columns]
                st.dataframe((balance[cols]/1e7).style.format("{:,.0f}"), use_container_width=True)
                fig4 = go.Figure()
                for col in ['Total Assets','Stockholders Equity','Total Debt']:
                    if col in balance.columns:
                        fig4.add_trace(go.Bar(name=col, x=balance.index.astype(str), y=balance[col]/1e7))
                fig4.update_layout(template='plotly_dark', title='Balance Sheet (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig4, use_container_width=True)
            except:
                st.warning("Balance sheet not available")

        with tab3:
            try:
                cashflow = stock.cashflow.T
                cashflow.index = cashflow.index.year
                cashflow = cashflow.sort_index()
                cols = [c for c in ['Operating Cash Flow','Investing Cash Flow','Free Cash Flow'] if c in cashflow.columns]
                st.dataframe((cashflow[cols]/1e7).style.format("{:,.0f}"), use_container_width=True)
                fig5 = go.Figure()
                for col in cols:
                    fig5.add_trace(go.Bar(name=col, x=cashflow.index.astype(str), y=cashflow[col]/1e7))
                fig5.update_layout(template='plotly_dark', title='Cash Flow (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig5, use_container_width=True)
            except:
                st.warning("Cash flow not available")

        with tab4:
            try:
                holders = stock.institutional_holders
                if holders is not None and not holders.empty:
                    st.markdown("### 🏦 Institutional Investors")
                    st.dataframe(holders, use_container_width=True)
                major = stock.major_holders
                if major is not None and not major.empty:
                    st.markdown("### 📊 Shareholding Pattern")
                    st.dataframe(major, use_container_width=True)
            except:
                st.warning("Investor data not available")

        # SWOT - DATA DRIVEN
        st.markdown("---")
        st.markdown("## 🔍 AI-Powered SWOT Analysis")

        col1, col2 = st.columns(2)
        with col1:
            S = []
            if roe > 15: S.append(f"Strong ROE of {roe}% — efficient equity use")
            if profit_margin > 10: S.append(f"Healthy profit margin of {profit_margin}%")
            if rev_growth > 10: S.append(f"Strong revenue growth of {rev_growth}%")
            if debt_eq < 0.5: S.append(f"Low debt — D/E of {debt_eq} — strong balance sheet")
            if returns_1y > 15: S.append(f"Strong 1Y stock return of {returns_1y}%")
            if not S: S.append("Established listed company with operational history")
            st.success("**💪 STRENGTHS**\n" + "\n".join([f"- {s}" for s in S]))

            W = []
            if roe < 12: W.append(f"Low ROE of {roe}% — below 15% benchmark")
            if debt_eq > 1: W.append(f"High leverage — D/E of {debt_eq}")
            if profit_margin < 8: W.append(f"Thin margins of {profit_margin}%")
            if pe > 50: W.append(f"Expensive P/E of {pe} — priced for perfection")
            if returns_1y < 0: W.append(f"Negative 1Y return of {returns_1y}%")
            if not W: W.append("Valuation requires consistent growth delivery")
            st.error("**⚠️ WEAKNESSES**\n" + "\n".join([f"- {w}" for w in W]))

        with col2:
            st.info(f"""
**🚀 OPPORTUNITIES**
- India GDP 6-7% growth tailwind
- {sector} sector expansion in India
- PLI scheme & Make in India support
- Growing middle class consumption
- Export market potential
            """)
            st.warning(f"""
**🌧️ THREATS**
- Global recession & FII outflow risk
- RBI rate hike impact
- Competition in {industry}
- Regulatory & compliance changes
- INR depreciation risk
            """)

        # AI SIGNAL
        st.markdown("---")
        st.markdown("## 🤖 AI Buy/Sell/Hold Signal")
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]
        score = 0
        reasons = []

        if current > ma50: score+=1; reasons.append("✅ Above 50 DMA — short term bullish")
        else: score-=1; reasons.append("❌ Below 50 DMA — short term bearish")

        if current > ma200: score+=1; reasons.append("✅ Above 200 DMA — long term uptrend")
        else: score-=1; reasons.append("❌ Below 200 DMA — long term downtrend")

        if 30 < rsi_val < 70: score+=1; reasons.append(f"✅ RSI {round(rsi_val,1)} — healthy zone")
        elif rsi_val > 70: score-=1; reasons.append(f"⚠️ RSI {round(rsi_val,1)} — overbought")
        else: score+=1; reasons.append(f"✅ RSI {round(rsi_val,1)} — oversold bounce possible")

        if roe > 15: score+=1; reasons.append(f"✅ ROE {roe}% — strong fundamentals")
        if debt_eq < 0.5: score+=1; reasons.append(f"✅ Low debt D/E {debt_eq}")
        if rev_growth > 10: score+=1; reasons.append(f"✅ Revenue growing {rev_growth}%")

        for r in reasons:
            st.write(r)

        st.markdown("### 🎯 Final Signal:")
        if score >= 4:
            st.success(f"🟢 **BUY** — Score {score}/6 — Strong bullish setup!")
        elif score <= 1:
            st.error(f"🔴 **SELL** — Score {score}/6 — Bearish signals!")
        else:
            st.warning(f"🟡 **HOLD** — Score {score}/6 — Mixed signals!")

        st.markdown("---")
        st.caption("⚠️ Educational purpose only. Not financial advice.")
        st.caption("Built by Pratyush Singh | MBA Banking & Financial Engineering | Chandigarh University")

    except Exception as e:
        st.error(f"⚠️ Try again in 2 mins — {str(e)[:100]}")
