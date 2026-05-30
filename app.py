import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="ProAnalyzer — Indian Equity Research",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.main { background-color: #0a0e1a; }
.stApp { background-color: #0a0e1a; }
[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #21262d; }
.metric-card {
    background: linear-gradient(135deg, #1a1f2e, #16213e);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    margin: 4px 0;
}
.section-header {
    background: linear-gradient(90deg, #1a1f2e, transparent);
    border-left: 3px solid #00d4ff;
    padding: 8px 16px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
}
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1f2e, #16213e);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px;
}
/* Fixed truncated metric text overflow issue */
div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1a1f2e;
    border-radius: 8px 8px 0 0;
    color: #8b949e;
}
.stTabs [aria-selected="true"] {
    background-color: #00d4ff20;
    color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}
.stButton button {
    background: linear-gradient(135deg, #00d4ff, #0099cc);
    color: #000;
    font-weight: 600;
    border: none;
    border-radius: 8px;
}
.buy-signal {
    background: linear-gradient(135deg, #0d2818, #1a4a2e);
    border: 1px solid #238636;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.sell-signal {
    background: linear-gradient(135deg, #2d0f0f, #4a1a1a);
    border: 1px solid #da3633;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.hold-signal {
    background: linear-gradient(135deg, #2d2200, #4a3800);
    border: 1px solid #e3b341;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Stock Lists ──────────────────────────────────────────────
NIFTY50 = {
    "Reliance Industries": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS", "Infosys": "INFY.NS", "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS", "ITC": "ITC.NS", "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Hindustan Unilever": "HINDUNILVR.NS", "Axis Bank": "AXISBANK.NS", "L&T": "LT.NS",
    "Asian Paints": "ASIANPAINT.NS", "HCL Technologies": "HCLTECH.NS", "Bajaj Finance": "BAJFINANCE.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Wipro": "WIPRO.NS", "Nestle India": "NESTLEIND.NS",
    "UltraTech Cement": "ULTRACEMCO.NS", "Titan Company": "TITAN.NS", "Tech Mahindra": "TECHM.NS",
    "Power Grid": "POWERGRID.NS", "NTPC": "NTPC.NS", "IndusInd Bank": "INDUSINDBK.NS",
    "Tata Motors": "TATAMOTORS.NS", "Mahindra & Mahindra": "M&M.NS", "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Maruti Suzuki": "MARUTI.NS", "JSW Steel": "JSWSTEEL.NS", "Tata Steel": "TATASTEEL.NS",
    "ONGC": "ONGC.NS", "Coal India": "COALINDIA.NS", "Grasim Industries": "GRASIM.NS",
    "Cipla": "CIPLA.NS", "Dr. Reddy's": "DRREDDY.NS", "Eicher Motors": "EICHERMOT.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS", "Divis Laboratories": "DIVISLAB.NS", "Britannia": "BRITANNIA.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS", "Adani Ports": "ADANIPORTS.NS", "Adani Enterprises": "ADANIENT.NS",
    "BPCL": "BPCL.NS", "Hindalco": "HINDALCO.NS", "Tata Consumer": "TATACONSUM.NS",
    "SBI Life Insurance": "SBILIFE.NS", "HDFC Life": "HDFCLIFE.NS", "LTIMindtree": "LTIM.NS",
    "Shriram Finance": "SHRIRAMFIN.NS", "BEL": "BEL.NS"
}

BANKNIFTY = {
    "HDFC Bank": "HDFCBANK.NS", "ICICI Bank": "ICICIBANK.NS", "State Bank of India": "SBIN.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS", "Axis Bank": "AXISBANK.NS", "IndusInd Bank": "INDUSINDBK.NS",
    "Bank of Baroda": "BANKBARODA.NS", "Punjab National Bank": "PNB.NS", "IDFC First Bank": "IDFCFIRSTB.NS",
    "Federal Bank": "FEDERALBNK.NS", "Canara Bank": "CANBK.NS", "AU Small Finance Bank": "AUBANK.NS"
}

SENSEX = {
    "Reliance Industries": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS", "Infosys": "INFY.NS", "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS", "L&T": "LT.NS", "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS", "State Bank of India": "SBIN.NS", "HCL Technologies": "HCLTECH.NS",
    "Bajaj Finance": "BAJFINANCE.NS", "Asian Paints": "ASIANPAINT.NS", "Hindustan Unilever": "HINDUNILVR.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Maruti Suzuki": "MARUTI.NS", "Mahindra & Mahindra": "M&M.NS",
    "Wipro": "WIPRO.NS", "Tata Motors": "TATAMOTORS.NS", "Titan Company": "TITAN.NS",
    "UltraTech Cement": "ULTRACEMCO.NS", "Power Grid": "POWERGRID.NS", "NTPC": "NTPC.NS",
    "JSW Steel": "JSWSTEEL.NS", "Tata Steel": "TATASTEEL.NS", "ONGC": "ONGC.NS",
    "Nestle India": "NESTLEIND.NS", "Tech Mahindra": "TECHM.NS", "Bajaj Finserv": "BAJAJFINSV.NS"
}

PEERS_MAP = {
    "TCS.NS": ["INFY.NS","WIPRO.NS","HCLTECH.NS"], "INFY.NS": ["TCS.NS","WIPRO.NS","HCLTECH.NS"],
    "HDFCBANK.NS": ["ICICIBANK.NS","AXISBANK.NS","SBIN.NS"], "ICICIBANK.NS": ["HDFCBANK.NS","AXISBANK.NS","SBIN.NS"],
    "RELIANCE.NS": ["ONGC.NS","BPCL.NS"], "MARUTI.NS": ["TATAMOTORS.NS","M&M.NS"]
}

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 ProAnalyzer")
    st.markdown("*Indian Equity Research Platform*")
    st.markdown("---")

    index_choice = st.selectbox("🔍 Browse by Index", ["-- Type Manually --", "Nifty 50", "Bank Nifty", "Sensex"])

    ticker = ""
    if index_choice == "Nifty 50":
        name = st.selectbox("Select Stock", list(NIFTY50.keys()))
        ticker = NIFTY50[name]
    elif index_choice == "Bank Nifty":
        name = st.selectbox("Select Stock", list(BANKNIFTY.keys()))
        ticker = BANKNIFTY[name]
    elif index_choice == "Sensex":
        name = st.selectbox("Select Stock", list(SENSEX.keys()))
        ticker = SENSEX[name]
    else:
        ticker = st.text_input("Enter NSE Symbol", value="DIXON.NS")

    st.markdown("---")
    period_label = st.radio("📅 Chart Period", ["1M","3M","6M","1Y","3Y","5Y"], index=3, horizontal=True)
    period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}

    show_volume = st.checkbox("Show Volume", value=True)
    show_bollinger = st.checkbox("Show Bollinger Bands", value=False)

    st.markdown("---")
    analyze = st.button("🚀 Analyze", type="primary", use_container_width=True)

# ── Main Landing View ────────────────────────────────────────
if not analyze:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-card'><h3>50+</h3><p>Nifty 50 Stocks</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><h3>12+</h3><p>Bank Nifty Stocks</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><h3>30+</h3><p>Sensex Stocks</p></div>", unsafe_allow_html=True)
    c4.markdown("<div class='metric-card'><h3>Live</h3><p>Real-time Connection</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("👈 Select a financial instrument from the sidebar panel and trigger 'Analyze'.")
    st.stop()

# ── Data Processing Engine ───────────────────────────────────
try:
    with st.spinner(f"Requesting data matrix for {ticker}..."):
        stock = yf.Ticker(ticker)
        df = stock.history(period=period_map[period_label], auto_adjust=True)
        df_1y = stock.history(period="1y", auto_adjust=True)

    if df.empty:
        st.error("❌ Specified symbol cannot be resolved by the engine data feed.")
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

    prev_close = round(df["Close"].iloc[-2], 2) if len(df) > 1 else current
    day_change = round(current - prev_close, 2)
    day_change_p = round((day_change / prev_close) * 100, 2)
    returns_1y = round(((df_1y["Close"].iloc[-1] / df_1y["Close"].iloc[0]) - 1) * 100, 2) if not df_1y.empty else 0.0

    try:
        info = stock.info
        pe = round(info.get("trailingPE", 0) or 0, 1)
        pb = round(info.get("priceToBook", 0) or 0, 1)
        roe = round((info.get("returnOnEquity", 0) or 0) * 100, 1)
        roa = round((info.get("returnOnAssets", 0) or 0) * 100, 1)
        debt_eq = round(info.get("debtToEquity", 0) or 0, 2)
        div = round((info.get("dividendYield", 0) or 0) * 100, 2)
        profit_margin = round((info.get("profitMargins", 0) or 0) * 100, 1)
        rev_growth = round((info.get("revenueGrowth", 0) or 0) * 100, 1)
        fwd_pe = round(info.get("forwardPE", 0) or 0, 1)
        peg = round(info.get("pegRatio", 0) or 0, 2)
        current_ratio = round(info.get("currentRatio", 0) or 0, 2)
        quick_ratio = round(info.get("quickRatio", 0) or 0, 2)
        beta = round(info.get("beta", 0) or 0, 2)
        company_name = info.get("longName", ticker)
        description = info.get("longBusinessSummary", "No corporate profile summary available.")
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
    except:
        pe=pb=roe=roa=debt_eq=div=profit_margin=rev_growth=fwd_pe=peg=current_ratio=quick_ratio=beta=0
        company_name=ticker; description="N/A Framework Profile"; sector=industry="N/A"

    # ── Header View ──────────────────────────────────────────
    chg_color = "#26a641" if day_change >= 0 else "#da3633"
    chg_icon = "▲" if day_change >= 0 else "▼"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1f2e,#16213e); border:1px solid #30363d; border-radius:16px; padding:20px; margin-bottom:16px;'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <h2 style='color:#00d4ff; margin:0;'>{company_name}</h2>
                <p style='color:#8b949e; margin:4px 0 0 0;'>{ticker} | {sector} | {industry}</p>
            </div>
            <div style='text-align:right;'>
                <h2 style='color:#fff; margin:0;'>₹{current:,}</h2>
                <p style='color:{chg_color}; margin:4px 0 0 0;'>{chg_icon} ₹{abs(day_change)} ({abs(day_change_p)}%)</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("52W High", f"₹{high_52w:,}")
    c2.metric("52W Low", f"₹{low_52w:,}")
    c3.metric("Mkt Cap (Cr)", f"₹{mkt_cap:,.0f}")
    c4.metric("1Y Return", f"{returns_1y}%")
    c5.metric("Beta Coefficient", beta)

    st.markdown("---")

    t1, t2, t3, t4, t5, t6 = st.tabs(["📈 Charts", "📐 Fundamentals", "💹 Financials", "👥 Peers", "🔍 SWOT", "🤖 AI Signal"])

    # ── TAB 1: CHARTS ────────────────────────────────────────
    with t1:
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        df["BB_mid"] = df["Close"].rolling(20).mean()
        df["BB_std"] = df["Close"].rolling(20).std()
        df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
        df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]

        delta_c = df["Close"].diff()
        gain = delta_c.where(delta_c > 0, 0).rolling(14).mean()
        loss = (-delta_c.where(delta_c < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss if loss.any() else 1)))

        rsi_val = round(df["RSI"].iloc[-1], 1) if not df["RSI"].empty and not np.isnan(df["RSI"].iloc[-1]) else 50.0

        rows = 3 if show_volume else 2
        row_heights = [0.60, 0.20, 0.20] if show_volume else [0.75, 0.25]
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=row_heights, vertical_spacing=0.03)

        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price", increasing_line_color="#26a641", decreasing_line_color="#da3633"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="50 dMA", line=dict(color="#00bfff", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="200 dMA", line=dict(color="orange", width=1.5)), row=1, col=1)

        if show_bollinger:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB Upper", line=dict(color="#ffffff", dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB Lower", fill="tonexty", fillcolor="rgba(255,255,255,0.03)", line=dict(color="#ffffff", dash="dot")), row=1, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI (14)", line=dict(color="#e3b341", width=1.5)), row=2, col=1)
        
        # FIX: Replaced transparent 8-digit hex codes with valid clean string styles
        fig.add_hline(y=70, line_color="#da3633", line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_color="#26a641", line_dash="dash", row=2, col=1)

        if show_volume:
            v_colors = ["#26a641" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#da3633" for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=v_colors, opacity=0.5), row=3, col=1)

        fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=600, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: FUNDAMENTALS ──────────────────────────────────
    with t2:
        st.markdown("### Corporate Operational Overview")
        st.write(description[:900] + "..." if len(description) > 900 else description)

        st.markdown("<div class='section-header'><h3>Valuation Framework</h3></div>", unsafe_allow_html=True)
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Trailing P/E", pe if pe else "N/A")
        v2.metric("Forward P/E", fwd_pe if fwd_pe else "N/A")
        v3.metric("Price to Book (P/B)", pb if pb else "N/A")
        v4.metric("PEG Ratio", peg if peg else "N/A")

        st.markdown("<div class='section-header'><h3>Profitability Metrics</h3></div>", unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Return on Equity (ROE)", f"{roe}%" if roe else "N/A")
        p2.metric("Return on Assets (ROA)", f"{roa}%" if roa else "N/A")
        p3.metric("Net Profit Margin", f"{profit_margin}%" if profit_margin else "N/A")
        p4.metric("Revenue Growth YoY", f"{rev_growth}%" if rev_growth else "N/A")

        st.markdown("<div class='section-header'><h3>Financial Health Structural Balance</h3></div>", unsafe_allow_html=True)
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Debt to Equity", debt_eq if debt_eq else "N/A")
        h2.metric("Current Ratio", current_ratio if current_ratio else "N/A")
        h3.metric("Quick Ratio", quick_ratio if quick_ratio else "N/A")
        h4.metric("Dividend Yield", f"{div}%" if div else "N/A")

    # ── TAB 3: FINANCIALS ────────────────────────────────────
    with t3:
        st.markdown("### Core Statements")
        st_tabs = st.tabs(["Income Statement", "Balance Sheet"])
        with st_tabs[0]:
            try:
                st.dataframe(stock.financials.iloc[:8], use_container_width=True)
            except:
                st.info("Statement tracking currently updating or unavailable.")
        with st_tabs[1]:
            try:
                st.dataframe(stock.balance_sheet.iloc[:8], use_container_width=True)
            except:
                st.info("Balance structural sheet mapping currently updating.")

    # ── TAB 4: PEERS ─────────────────────────────────────────
    with t4:
        st.markdown("### Industry Competitor Matrix")
        peer_list = PEERS_MAP.get(ticker, [])
        if peer_list:
            records = []
            for p in peer_list:
                try:
                    t_obj = yf.Ticker(p)
                    records.append({
                        "Symbol": p,
                        "Price": t_obj.fast_info.last_price,
                        "Trailing P/E": t_obj.info.get("trailingPE", "N/A"),
                        "P/B": t_obj.info.get("priceToBook", "N/A")
                    })
                except: pass
            if records:
                st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
            else:
                st.info("Competitor structural parameters processing offline.")
        else:
            st.info("Custom relative industry data group maps not compiled.")

    # ── TAB 5: SWOT MATRIX ───────────────────────────────────
    with t5:
        st.markdown("### Analytical Factor Evaluation Matrix")
        s1, s2 = st.columns(2)
        with s1:
            st.success("**Strengths**\n* Structural inclusion within foundational benchmarks.\n* Resilient 52-week pricing floors support equity momentum metrics.")
            st.warning("**Weaknesses**\n* Operating capital variables subject to domestic cash liquidity cycles.\n* Historical beta data implies exposure to systemic sector corrections.")
        with s2:
            st.info("**Opportunities**\n* Digital infrastructure transformation scales market penetration velocity.\n* Strategic value parameters reset dynamically during local corrections.")
            st.error("**Threats**\n* Structural changes in direct sovereign tariff or trade policies.\n* Foreign institutional capital outflows impact near-term velocity.")

    # ── TAB 6: AI TECHNICAL SIGNAL ───────────────────────────
    with t6:
        st.markdown("### Algorithmic Evaluation Vector")
        if rsi_val > 70:
            st.markdown("<div class='sell-signal'><h2>Signal: OVERBOUGHT DISTRIBUTION BLOCK</h2><p>Risk parameters indicate price extension beyond standard deviation parameters.</p></div>", unsafe_allow_html=True)
        elif rsi_val < 30:
            st.markdown("<div class='buy-signal'><h2>Signal: OVERSOLD ACCUMULATION ALIGNMENT</h2><p>Asset price tracking indicators match potential reversal trigger parameters.</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='hold-signal'><h2>Signal: MEAN REVERSION CONSOLIDATION</h2><p>Indicators suggest asset metrics remain bound within standard technical channels.</p></div>", unsafe_allow_html=True)

except Exception as err:
    st.error(f"⚠️ Script Execution Halting: {err}")
    st.info("Verify your internet link configuration and ensure accurate NSE asset token suffix syntax format (.NS).")
