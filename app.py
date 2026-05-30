import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import time
import requests

st.set_page_config(page_title="Indian Equity Research Analyzer", page_icon="📈", layout="wide")

# Custom CSS - Screener style
st.markdown("""
<style>
.metric-box {
    background-color: #1e2130;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #00bfff;
    margin: 5px;
}
.company-header {
    background: linear-gradient(90deg, #1a1a2e, #16213e);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Indian Equity Research Analyzer")
st.markdown("##### By Pratyush Singh | MBA - Banking & Financial Engineering | Chandigarh University")
st.markdown("---")

ticker = st.text_input("🔍 Enter NSE Stock Symbol", value="DIXON.NS", placeholder="e.g. DIXON.NS, KAYNES.NS, TCS.NS")

if st.button("🚀 Analyze Stock", type="primary"):
    try:
        with st.spinner("Fetching live data..."):
            time.sleep(4)
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y", auto_adjust=True)

            if df.empty:
                st.error("❌ Stock not found! Check symbol.")
                st.stop()

        # COMPANY HEADER
        try:
            quote = stock.info
            company_name = quote.get('longName', ticker)
            sector = quote.get('sector', 'N/A')
            industry = quote.get('industry', 'N/A')
            website = quote.get('website', 'N/A')
            description = quote.get('longBusinessSummary', 'No description available')
            employees = quote.get('fullTimeEmployees', 'N/A')
            pe = round(quote.get('trailingPE', 0), 1)
            pb = round(quote.get('priceToBook', 0), 1)
            roe = round(quote.get('returnOnEquity', 0) * 100, 1)
            roce = round(quote.get('returnOnAssets', 0) * 100, 1)
            debt_equity = round(quote.get('debtToEquity', 0), 2)
            div_yield = round(quote.get('dividendYield', 0) * 100, 2)
            book_value = round(quote.get('bookValue', 0), 2)
            profit_margin = round(quote.get('profitMargins', 0) * 100, 1)
            revenue_growth = round(quote.get('revenueGrowth', 0) * 100, 1)
            earnings_growth = round(quote.get('earningsGrowth', 0) * 100, 1)
        except:
            company_name = ticker
            sector = industry = 'N/A'
            pe = pb = roe = roce = debt_equity = div_yield = book_value = profit_margin = 0
            revenue_growth = earnings_growth = 0
            description = 'Data loading...'
            employees = 'N/A'

        # COMPANY NAME + BASIC INFO
        st.markdown(f"## 🏢 {company_name}")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Sector:** {sector}")
        col2.markdown(f"**Industry:** {industry}")
        col3.markdown(f"**Website:** {website}")

        # KEY METRICS - SCREENER STYLE
        st.markdown("---")
        st.markdown("## 📊 Key Metrics")

        try:
            info = stock.fast_info
            current_price = round(info.last_price, 2)
            high_52w = round(info.year_high, 2)
            low_52w = round(info.year_low, 2)
            mkt_cap = round(info.market_cap / 1e7, 2)
        except:
            current_price = round(df['Close'].iloc[-1], 2)
            high_52w = round(df['High'].max(), 2)
            low_52w = round(df['Low'].min(), 2)
            mkt_cap = 0

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Market Cap (₹ Cr)", f"{mkt_cap:,.0f}")
        col2.metric("Current Price", f"₹{current_price}")
        col3.metric("High / Low", f"₹{high_52w} / ₹{low_52w}")
        col4.metric("Stock P/E", pe)
        col5.metric("Book Value", f"₹{book_value}")
        col6.metric("Dividend Yield", f"{div_yield}%")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("ROCE %", f"{roce}%")
        col2.metric("ROE %", f"{roe}%")
        col3.metric("P/B Ratio", pb)
        col4.metric("Debt/Equity", debt_equity)
        col5.metric("Profit Margin", f"{profit_margin}%")
        col6.metric("Revenue Growth", f"{revenue_growth}%")

        # ABOUT COMPANY
        st.markdown("---")
        st.markdown("## 📋 About Company")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(description[:800] + "..." if len(str(description)) > 800 else description)
        with col2:
            st.info(f"""
**🏭 Sector:** {sector}
**🔧 Industry:** {industry}
**👥 Employees:** {employees:,} if isinstance(employees, int) else {employees}
**📈 Earnings Growth:** {earnings_growth}%
**💹 Revenue Growth:** {revenue_growth}%
            """)

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
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='white', width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 DMA', line=dict(color='#00bfff', width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 DMA', line=dict(color='orange', width=1.5)))
        fig.update_layout(template='plotly_dark', title=f'{company_name} — 1Y Price Chart', height=400)
        st.plotly_chart(fig, use_container_width=True)

        # RSI
        st.markdown("## 📊 RSI Indicator")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='yellow')))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought (70)")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold (30)")
        fig2.update_layout(template='plotly_dark', title='RSI Indicator', height=300)
        st.plotly_chart(fig2, use_container_width=True)

        # FINANCIAL STATEMENTS
        st.markdown("---")
        st.markdown("## 💹 Financial Statements")
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Income Statement", "🏦 Balance Sheet", "💵 Cash Flow", "👥 Investors"])

        with tab1:
            try:
                income = stock.financials.T
                income.index = income.index.year
                income = income.sort_index()
                cols = [c for c in ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income'] if c in income.columns]
                df_show = (income[cols] / 1e7).round(0)
                df_show.columns = [c + ' (₹ Cr)' for c in cols]
                st.dataframe(df_show.style.format("{:,.0f}"), use_container_width=True)
                fig3 = go.Figure()
                for col in cols:
                    fig3.add_trace(go.Bar(name=col, x=income.index.astype(str), y=income[col] / 1e7))
                fig3.update_layout(template='plotly_dark', title='Revenue & Profit Trend (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Income statement data not available for this stock")

        with tab2:
            try:
                balance = stock.balance_sheet.T
                balance.index = balance.index.year
                balance = balance.sort_index()
                cols = [c for c in ['Total Assets', 'Total Liabilities Net Minority Interest', 'Stockholders Equity', 'Total Debt'] if c in balance.columns]
                df_show = (balance[cols] / 1e7).round(0)
                st.dataframe(df_show.style.format("{:,.0f}"), use_container_width=True)
                fig4 = go.Figure()
                if 'Total Assets' in balance.columns:
                    fig4.add_trace(go.Bar(name='Total Assets', x=balance.index.astype(str), y=balance['Total Assets'] / 1e7))
                if 'Stockholders Equity' in balance.columns:
                    fig4.add_trace(go.Bar(name='Equity', x=balance.index.astype(str), y=balance['Stockholders Equity'] / 1e7))
                if 'Total Debt' in balance.columns:
                    fig4.add_trace(go.Bar(name='Total Debt', x=balance.index.astype(str), y=balance['Total Debt'] / 1e7))
                fig4.update_layout(template='plotly_dark', title='Balance Sheet Trend (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig4, use_container_width=True)
            except:
                st.warning("Balance sheet data not available")

        with tab3:
            try:
                cashflow = stock.cashflow.T
                cashflow.index = cashflow.index.year
                cashflow = cashflow.sort_index()
                cols = [c for c in ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow', 'Free Cash Flow'] if c in cashflow.columns]
                df_show = (cashflow[cols] / 1e7).round(0)
                df_show.columns = [c + ' (₹ Cr)' for c in cols]
                st.dataframe(df_show.style.format("{:,.0f}"), use_container_width=True)
                fig5 = go.Figure()
                for col in cols:
                    fig5.add_trace(go.Bar(name=col, x=cashflow.index.astype(str), y=cashflow[col] / 1e7))
                fig5.update_layout(template='plotly_dark', title='Cash Flow Trend (₹ Cr)', barmode='group', height=400)
                st.plotly_chart(fig5, use_container_width=True)
            except:
                st.warning("Cash flow data not available")

        with tab4:
            try:
                st.markdown("### 🏦 Top Institutional Holders")
                holders = stock.institutional_holders
                if holders is not None and not holders.empty:
                    st.dataframe(holders, use_container_width=True)
                else:
                    st.warning("Institutional data not available")

                st.markdown("### 📊 Major Shareholding Pattern")
                major = stock.major_holders
                if major is not None and not major.empty:
                    st.dataframe(major, use_container_width=True)
            except:
                st.warning("Investor data not available")

        # AI POWERED STOCK SPECIFIC SWOT
        st.markdown("---")
        st.markdown("## 🔍 AI-Powered SWOT Analysis")
        st.caption("Generated based on actual financial data of this company")

        col1, col2 = st.columns(2)
        with col1:
            # STRENGTHS based on actual data
            strengths = ["Listed on NSE/BSE — Regulated & transparent"]
            if roe > 15:
                strengths.append(f"Strong ROE of {roe}% — Efficient use of equity")
            if profit_margin > 10:
                strengths.append(f"Healthy profit margins of {profit_margin}%")
            if revenue_growth > 10:
                strengths.append(f"Strong revenue growth of {revenue_growth}%")
            if debt_equity < 0.5:
                strengths.append(f"Low debt — D/E ratio of {debt_equity} — financially strong")
            if pe > 0 and pe < 25:
                strengths.append(f"Reasonably valued at P/E of {pe}")
            if len(strengths) < 3:
                strengths.append("Established business with operational track record")

            st.success("**💪 STRENGTHS**\n" + "\n".join([f"- {s}" for s in strengths]))

            # WEAKNESSES based on actual data
            weaknesses = []
            if roe < 12:
                weaknesses.append(f"Low ROE of {roe}% — below industry benchmark of 15%")
            if debt_equity > 1:
                weaknesses.append(f"High debt — D/E ratio of {debt_equity} — leverage risk")
            if profit_margin < 8:
                weaknesses.append(f"Thin profit margins of {profit_margin}% — execution risk")
            if pe > 50:
                weaknesses.append(f"Expensive valuation — P/E of {pe} — priced for perfection")
            if revenue_growth < 0:
                weaknesses.append(f"Negative revenue growth of {revenue_growth}% — demand concern")
            if len(weaknesses) == 0:
                weaknesses.append("High valuation requires sustained growth delivery")
            weaknesses.append("Dependent on broader market & macro conditions")

            st.error("**⚠️ WEAKNESSES**\n" + "\n".join([f"- {w}" for w in weaknesses]))

        with col2:
            # OPPORTUNITIES - sector specific
            opportunities = [
                "India GDP growth 6-7% — domestic consumption tailwind",
                "Government PLI schemes supporting Indian manufacturing",
                "Rising middle class & premiumization trend in India",
                "Digital India & Make in India policy support",
                "Export market expansion — India becoming global supplier"
            ]
            if revenue_growth > 0:
                opportunities.append(f"Positive revenue momentum of {revenue_growth}% continuing")

            st.info("**🚀 OPPORTUNITIES**\n" + "\n".join([f"- {o}" for o in opportunities[:4]]))

            # THREATS - data driven
            threats = [
                "Global recession risk impacting demand",
                "RBI monetary policy & interest rate risk",
                "Intense competition from domestic & global players",
                "Regulatory & compliance risk",
                "INR depreciation impacting import costs"
            ]
            if pe > 40:
                threats.append(f"High P/E of {pe} — any growth miss can cause sharp correction")
            if debt_equity > 0.5:
                threats.append(f"Rising interest rates impact on debt servicing")

            st.warning("**🌧️ THREATS**\n" + "\n".join([f"- {t}" for t in threats[:4]]))

        # AI SIGNAL
        st.markdown("---")
        st.markdown("## 🤖 AI Buy/Sell/Hold Signal")
        last = df['Close'].iloc[-1]
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]
        rsi = df['RSI'].iloc[-1]

        score = 0
        reasons = []

        if last > ma50:
            score += 1
            reasons.append("✅ Price above 50 DMA — short term bullish")
        else:
            score -= 1
            reasons.append("❌ Price below 50 DMA — short term bearish")

        if last > ma200:
            score += 1
            reasons.append("✅ Price above 200 DMA — long term uptrend")
        else:
            score -= 1
            reasons.append("❌ Price below 200 DMA — long term downtrend")

        if rsi < 70 and rsi > 40:
            score += 1
            reasons.append(f"✅ RSI at {round(rsi,1)} — healthy momentum")
        elif rsi > 70:
            score -= 1
            reasons.append(f"⚠️ RSI at {round(rsi,1)} — overbought zone")
        else:
            score += 1
            reasons.append(f"✅ RSI at {round(rsi,1)} — oversold — potential bounce")

        if roe > 15:
            score += 1
            reasons.append(f"✅ ROE {roe}% — strong fundamentals")
        if debt_equity < 0.5:
            score += 1
            reasons.append(f"✅ Low debt D/E {debt_equity} — financially stable")
        if revenue_growth > 10:
            score += 1
            reasons.append(f"✅ Revenue growing at {revenue_growth}%")

        for r in reasons:
            st.write(r)

        st.markdown("### Final Signal:")
        if score >= 3:
            st.success(f"🟢 **BUY** — Score: {score}/6 — Strong bullish signals!")
        elif score <= 0:
            st.error(f"🔴 **SELL** — Score: {score}/6 — Bearish signals dominating!")
        else:
            st.warning(f"🟡 **HOLD** — Score: {score}/6 — Mixed signals — watch closely!")

        st.markdown("---")
        st.caption("⚠️ Disclaimer: This tool is for educational purposes only. Not financial advice. Always do your own research.")
        st.caption("🏗️ Built by Pratyush Singh | MBA Banking & Financial Engineering | Chandigarh University")

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)[:150]}")
        st.info("💡 Yahoo Finance rate limit — wait 2-3 minutes and retry!")
