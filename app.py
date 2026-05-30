import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Indian Equity Research Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Indian Equity Research Analyzer")
st.markdown("##### By Pratyush Singh | MBA - Banking & Financial Engineering | Chandigarh University")
st.markdown("---")

PEERS_MAP = {
    "DIXON.NS":     ["KAYNES.NS", "AMBER.NS", "PGEL.NS"],
    "KAYNES.NS":    ["DIXON.NS",  "AMBER.NS", "PGEL.NS"],
    "TCS.NS":       ["INFY.NS",   "WIPRO.NS", "HCLTECH.NS"],
    "RELIANCE.NS":  ["ONGC.NS",   "IOC.NS",   "BPCL.NS"],
    "HDFCBANK.NS":  ["ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "LICI.NS":      ["SBILIFE.NS",   "HDFCLIFE.NS", "ICICIGI.NS"],
    "INFY.NS":      ["TCS.NS",    "WIPRO.NS", "HCLTECH.NS"],
    "WIPRO.NS":     ["TCS.NS",    "INFY.NS",  "HCLTECH.NS"],
    "ICICIBANK.NS": ["HDFCBANK.NS","AXISBANK.NS","KOTAKBANK.NS"],
    "AXISBANK.NS":  ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS"],
}

ticker = st.text_input("🔍 Enter NSE Stock Symbol (e.g. DIXON.NS)", value="DIXON.NS")

if st.button("🚀 Analyze Stock", type="primary"):
    try:
        with st.spinner("Fetching data..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y", auto_adjust=True)

        if df.empty:
            st.error("❌ Stock not found!")
            st.stop()

        try:
            fi = stock.fast_info
            current = round(fi.last_price, 2)
            high_52w = round(fi.year_high, 2)
            low_52w = round(fi.year_low, 2)
            mkt_cap = round(fi.market_cap / 1e7, 0)
        except:
            current = round(df["Close"].iloc[-1], 2)
            high_52w = round(df["High"].max(), 2)
            low_52w = round(df["Low"].min(), 2)
            mkt_cap = 0

        returns_1y = round(((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100, 2)

        try:
            info = stock.info
            pe = round(info.get("trailingPE", 0) or 0, 1)
            pb = round(info.get("priceToBook", 0) or 0, 1)
            roe = round((info.get("returnOnEquity", 0) or 0) * 100, 1)
            debt_eq = round(info.get("debtToEquity", 0) or 0, 2)
            div = round((info.get("dividendYield", 0) or 0) * 100, 2)
            book_val = round(info.get("bookValue", 0) or 0, 2)
            profit_margin = round((info.get("profitMargins", 0) or 0) * 100, 1)
            rev_growth = round((info.get("revenueGrowth", 0) or 0) * 100, 1)
            company_name = info.get("longName", ticker)
            description = info.get("longBusinessSummary", "N/A")
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
        except:
            pe = pb = roe = debt_eq = div = book_val = profit_margin = rev_growth = 0
            company_name = ticker
            description = sector = industry = "N/A"

        st.markdown(f"### 🏢 {company_name}")
        st.markdown(f"**Sector:** {sector} | **Industry:** {industry}")
        st.markdown("---")

        st.markdown("## 📊 Key Metrics")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("💰 Price", f"₹{current}")
        c2.metric("📈 52W High", f"₹{high_52w}")
        c3.metric("📉 52W Low", f"₹{low_52w}")
        c4.metric("🏢 Mkt Cap (Cr)", f"₹{mkt_cap:,.0f}")
        c5.metric("📊 1Y Return", f"{returns_1y}%")

        st.markdown("---")
        st.markdown("## 📐 Fundamental Ratios")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("P/E", pe)
        c2.metric("P/B", pb)
        c3.metric("ROE %", f"{roe}%")
        c4.metric("Debt/Eq", debt_eq)
        c5.metric("Div Yield", f"{div}%")
        c6.metric("Book Value", f"₹{book_val}")

        st.markdown("---")
        st.markdown("## 📋 About the Company")
        desc_text = str(description)
        st.write(desc_text[:600] + "..." if len(desc_text) > 600 else desc_text)

        st.markdown("---")
        st.markdown("## 📉 Price Chart + Moving Averages")
        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color="white", width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="50 DMA", line=dict(color="#00bfff", width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="200 DMA", line=dict(color="orange", width=1.5)))
        fig.update_layout(template="plotly_dark", title=f"{company_name} — 1Y Price Chart", height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("## 📊 RSI Indicator")
        rsi_val = round(df["RSI"].iloc[-1], 1)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="yellow")))
        fig2.add_hline(y=70, line_color="red", annotation_text="Overbought (70)")
        fig2.add_hline(y=30, line_color="green", annotation_text="Oversold (30)")
        fig2.update_layout(template="plotly_dark", title=f"RSI — Current: {rsi_val}", height=300)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.markdown("## 💹 Financial Statements")
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Income Statement", "🏦 Balance Sheet", "💵 Cash Flow", "👥 Investors"])

        with tab1:
            try:
                income = stock.financials.T
                income.index = income.index.year
                income = income.sort_index()
                cols = [c for c in ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"] if c in income.columns]
                if cols:
                    st.dataframe((income[cols] / 1e7).style.format("{:,.0f}"), use_container_width=True)
                    fig3 = go.Figure()
                    for col in cols:
                        fig3.add_trace(go.Bar(name=col, x=income.index.astype(str), y=income[col] / 1e7))
                    fig3.update_layout(template="plotly_dark", title="Revenue & Profit (₹ Cr)", barmode="group", height=400)
                    st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Income statement data not available")

        with tab2:
            try:
                balance = stock.balance_sheet.T
                balance.index = balance.index.year
                balance = balance.sort_index()
                cols = [c for c in ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity", "Total Debt"] if c in balance.columns]
                if cols:
                    st.dataframe((balance[cols] / 1e7).style.format("{:,.0f}"), use_container_width=True)
                    fig4 = go.Figure()
                    for col in ["Total Assets", "Stockholders Equity", "Total Debt"]:
                        if col in balance.columns:
                            fig4.add_trace(go.Bar(name=col, x=balance.index.astype(str), y=balance[col] / 1e7))
                    fig4.update_layout(template="plotly_dark", title="Balance Sheet (₹ Cr)", barmode="group", height=400)
                    st.plotly_chart(fig4, use_container_width=True)
            except:
                st.warning("Balance sheet not available")

        with tab3:
            try:
                cashflow = stock.cashflow.T
                cashflow.index = cashflow.index.year
                cashflow = cashflow.sort_index()
                cols = [c for c in ["Operating Cash Flow", "Investing Cash Flow", "Free Cash Flow"] if c in cashflow.columns]
                if cols:
                    st.dataframe((cashflow[cols] / 1e7).style.format("{:,.0f}"), use_container_width=True)
                    fig5 = go.Figure()
                    for col in cols:
                        fig5.add_trace(go.Bar(name=col, x=cashflow.index.astype(str), y=cashflow[col] / 1e7))
                    fig5.update_layout(template="plotly_dark", title="Cash Flow (₹ Cr)", barmode="group", height=400)
                    st.plotly_chart(fig5, use_container_width=True)
            except:
                st.warning("Cash flow data not available")

        with tab4:
            try:
                st.markdown("### 📊 Shareholding Pattern")
                major = stock.major_holders
                if major is not None and not major.empty:
                    values = major.iloc[:, 0].tolist()
                    labels = ["👤 Promoters/Insiders", "🏦 FIIs + DIIs", "📊 Float (Inst.)", "🏢 No. of Institutions"]
                    c1, c2, c3, c4 = st.columns(4)
                    cols_ui = [c1, c2, c3, c4]
                    for i, (lbl, val) in enumerate(zip(labels, values)):
                        try:
                            fval = float(val)
                            display = f"{round(fval*100,2)}%" if i < 3 else str(int(fval))
                        except:
                            display = str(val)
                        cols_ui[i].metric(lbl, display)
                st.markdown("### 🏦 Top Institutional Holders")
                holders = stock.institutional_holders
                if holders is not None and not holders.empty:
                    st.dataframe(holders, use_container_width=True)
                else:
                    st.info("No institutional holder data available.")
            except:
                st.warning("Investor data not available")

        st.markdown("---")
        st.markdown("## 🔍 SWOT Analysis")
        col_l, col_r = st.columns(2)

        with col_l:
            strengths = []
            if roe > 15: strengths.append(f"Strong ROE of {roe}% — efficient equity use")
            if profit_margin > 10: strengths.append(f"Healthy profit margin of {profit_margin}%")
            if rev_growth > 10: strengths.append(f"Strong revenue growth of {rev_growth}%")
            if debt_eq < 0.5: strengths.append(f"Low D/E of {debt_eq} — strong balance sheet")
            if returns_1y > 15: strengths.append(f"Strong 1Y return of {returns_1y}%")
            if not strengths: strengths.append("Established listed company with operational history")
            st.success("**💪 STRENGTHS**\n" + "\n".join(f"- {s}" for s in strengths))

            weaknesses = []
            if roe < 12: weaknesses.append(f"Low ROE of {roe}% — below 15% benchmark")
            if debt_eq > 1: weaknesses.append(f"High leverage — D/E of {debt_eq}")
            if profit_margin < 8: weaknesses.append(f"Thin margins of {profit_margin}%")
            if pe > 50: weaknesses.append(f"Expensive P/E of {pe} — priced for perfection")
            if returns_1y < 0: weaknesses.append(f"Negative 1Y return of {returns_1y}%")
            if not weaknesses: weaknesses.append("Valuation requires consistent growth delivery")
            st.error("**⚠️ WEAKNESSES**\n" + "\n".join(f"- {w}" for w in weaknesses))

        with col_r:
            st.info(f"""🚀 **OPPORTUNITIES**
- India GDP 6-7% growth tailwind
- {sector} sector expansion in India
- PLI scheme & Make in India support
- Growing middle-class consumption
- Export market potential""")

            st.warning(f"""🌧️ **THREATS**
- Global recession & FII outflow risk
- RBI rate hike impact
- Competition in {industry}
- Regulatory & compliance changes
- INR depreciation risk""")

        st.markdown("---")
        st.markdown("## 👥 Peer Comparison")
        peer_list = PEERS_MAP.get(ticker.upper(), [])
        peers_df = pd.DataFrame()

        if peer_list:
            all_tickers = [ticker] + peer_list
            rows = []
            with st.spinner("Loading peer data..."):
                for t in all_tickers:
                    try:
                        p = yf.Ticker(t)
                        pi = p.info
                        rows.append({
                            "Company": pi.get("longName", t),
                            "Price (₹)": round(pi.get("currentPrice", 0) or 0, 2),
                            "Mkt Cap (Cr)": round((pi.get("marketCap", 0) or 0) / 1e7, 0),
                            "P/E": round(pi.get("trailingPE", 0) or 0, 1),
                            "P/B": round(pi.get("priceToBook", 0) or 0, 1),
                            "ROE %": round((pi.get("returnOnEquity", 0) or 0) * 100, 1),
                            "Debt/Eq": round(pi.get("debtToEquity", 0) or 0, 2),
                            "Rev Growth %": round((pi.get("revenueGrowth", 0) or 0) * 100, 1),
                        })
                    except:
                        pass
            if rows:
                peers_df = pd.DataFrame(rows)
                st.dataframe(peers_df.style.format({
                    "Price (₹)": "{:,.2f}",
                    "Mkt Cap (Cr)": "{:,.0f}",
                    "P/E": "{:.1f}",
                    "P/B": "{:.1f}",
                    "ROE %": "{:.1f}%",
                    "Rev Growth %": "{:.1f}%",
                }), use_container_width=True)
        else:
            st.info("Supported tickers: DIXON, KAYNES, TCS, RELIANCE, HDFCBANK, LICI, INFY, WIPRO, ICICIBANK, AXISBANK")

        st.markdown("---")
        st.markdown("## 🏦 Analyst Consensus")
        try:
            rec = stock.recommendations
            if rec is not None and not rec.empty:
                st.dataframe(rec.tail(20), use_container_width=True)
            else:
                st.info("No analyst recommendation data available.")
        except:
            st.warning("Analyst recommendations unavailable")

        st.markdown("---")
        st.markdown("## 📈 Earnings Growth (Net Profit Trend)")
        try:
            earnings = stock.income_stmt.T
            if "Net Income" in earnings.columns:
                fig6 = go.Figure()
                fig6.add_trace(go.Bar(
                    x=earnings.index.year.astype(str),
                    y=earnings["Net Income"] / 1e7,
                    name="Net Income",
                    marker_color="#00bfff",
                ))
                fig6.update_layout(template="plotly_dark", title="Net Profit Trend (₹ Cr)", height=400)
                st.plotly_chart(fig6, use_container_width=True)
        except:
            st.warning("Earnings data not available")

        st.markdown("---")
        st.markdown("## 📰 Latest News")
        try:
            news = stock.news
            if news:
                for n in news[:5]:
                    title = n.get("title", "No title")
                    publisher = n.get("publisher", "Unknown")
                    link = n.get("link", "#")
                    st.markdown(f"**{title}**  \n🗞️ {publisher}  \n🔗 [{link}]({link})")
                    st.markdown("---")
            else:
                st.info("No recent news found.")
        except:
            st.warning("News unavailable")

        st.markdown("---")
        st.markdown("## 🤖 AI Buy / Sell / Hold Signal")
        ma50_val = df["MA50"].iloc[-1]
        ma200_val = df["MA200"].iloc[-1]
        score = 0
        reasons = []

        if current > ma50_val:
            score += 1; reasons.append("✅ Above 50 DMA — short-term bullish")
        else:
            score -= 1; reasons.append("❌ Below 50 DMA — short-term bearish")

        if current > ma200_val:
            score += 1; reasons.append("✅ Above 200 DMA — long-term uptrend")
        else:
            score -= 1; reasons.append("❌ Below 200 DMA — long-term downtrend")

        if 30 < rsi_val < 70:
            score += 1; reasons.append(f"✅ RSI {rsi_val} — healthy zone")
        elif rsi_val >= 70:
            score -= 1; reasons.append(f"⚠️ RSI {rsi_val} — overbought")
        else:
            score += 1; reasons.append(f"✅ RSI {rsi_val} — oversold, bounce possible")

        if roe > 15: score += 1; reasons.append(f"✅ ROE {roe}% — strong fundamentals")
        if debt_eq < 0.5: score += 1; reasons.append(f"✅ Low debt D/E {debt_eq}")
        if rev_growth > 10: score += 1; reasons.append(f"✅ Revenue growing {rev_growth}%")

        for r in reasons:
            st.write(r)

        st.markdown("### 🎯 Final Signal")
        if score >= 4:
            st.success(f"🟢 **BUY** — Score {score}/6 — Strong bullish setup!")
        elif score <= 1:
            st.error(f"🔴 **SELL** — Score {score}/6 — Bearish signals dominate!")
        else:
            st.warning(f"🟡 **HOLD** — Score {score}/6 — Mixed signals, watch closely!")

        st.markdown("---")
        if not peers_df.empty:
            st.download_button(
                label="📥 Download Peer Comparison (CSV)",
                data=peers_df.to_csv(index=False),
                file_name=f"{ticker}_peer_comparison.csv",
                mime="text/csv",
            )

        st.markdown("---")
        st.caption("⚠️ For educational purposes only. Not financial advice.")
        st.caption("Built by Pratyush Singh | MBA Banking & Financial Engineering | Chandigarh University")

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)[:200]}")
        st.info("Try again in 2 minutes — Yahoo Finance has rate limits.")
