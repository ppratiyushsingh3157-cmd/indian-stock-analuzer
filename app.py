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
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "Axis Bank": "AXISBANK.NS",
    "L&T": "LT.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Wipro": "WIPRO.NS",
    "Nestle India": "NESTLEIND.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "Titan Company": "TITAN.NS",
    "Tech Mahindra": "TECHM.NS",
    "Power Grid": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Tata Steel": "TATASTEEL.NS",
    "ONGC": "ONGC.NS",
    "Coal India": "COALINDIA.NS",
    "Grasim Industries": "GRASIM.NS",
    "Cipla": "CIPLA.NS",
    "Dr. Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Divis Laboratories": "DIVISLAB.NS",
    "Britannia": "BRITANNIA.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "BPCL": "BPCL.NS",
    "Hindalco": "HINDALCO.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "SBI Life Insurance": "SBILIFE.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "LTIMindtree": "LTIM.NS",
    "Shriram Finance": "SHRIRAMFIN.NS",
    "BEL": "BEL.NS",
}

BANKNIFTY = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Bank of Baroda": "BANKBARODA.NS",
    "Punjab National Bank": "PNB.NS",
    "IDFC First Bank": "IDFCFIRSTB.NS",
    "Federal Bank": "FEDERALBNK.NS",
    "Canara Bank": "CANBK.NS",
    "AU Small Finance Bank": "AUBANK.NS",
}

SENSEX = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "L&T": "LT.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "State Bank of India": "SBIN.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Wipro": "WIPRO.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Titan Company": "TITAN.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "Power Grid": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Tata Steel": "TATASTEEL.NS",
    "ONGC": "ONGC.NS",
    "Nestle India": "NESTLEIND.NS",
    "Tech Mahindra": "TECHM.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
}

PEERS_MAP = {
    "TCS.NS":        ["INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS"],
    "INFY.NS":       ["TCS.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS"],
    "WIPRO.NS":      ["TCS.NS","INFY.NS","HCLTECH.NS","TECHM.NS"],
    "HCLTECH.NS":    ["TCS.NS","INFY.NS","WIPRO.NS","TECHM.NS"],
    "HDFCBANK.NS":   ["ICICIBANK.NS","AXISBANK.NS","KOTAKBANK.NS","SBIN.NS"],
    "ICICIBANK.NS":  ["HDFCBANK.NS","AXISBANK.NS","KOTAKBANK.NS","SBIN.NS"],
    "AXISBANK.NS":   ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","SBIN.NS"],
    "SBIN.NS":       ["HDFCBANK.NS","ICICIBANK.NS","PNB.NS","BANKBARODA.NS"],
    "KOTAKBANK.NS":  ["HDFCBANK.NS","ICICIBANK.NS","AXISBANK.NS","INDUSINDBK.NS"],
    "MARUTI.NS":     ["TATAMOTORS.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","EICHERMOT.NS"],
    "TATAMOTORS.NS": ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS"],
    "M&M.NS":        ["MARUTI.NS","TATAMOTORS.NS","BAJAJ-AUTO.NS"],
    "SUNPHARMA.NS":  ["DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","APOLLOHOSP.NS"],
    "DRREDDY.NS":    ["SUNPHARMA.NS","CIPLA.NS","DIVISLAB.NS"],
    "CIPLA.NS":      ["SUNPHARMA.NS","DRREDDY.NS","DIVISLAB.NS"],
    "RELIANCE.NS":   ["ONGC.NS","BPCL.NS","IOC.NS","ADANIENT.NS"],
    "ONGC.NS":       ["RELIANCE.NS","BPCL.NS","IOC.NS","COALINDIA.NS"],
    "HINDUNILVR.NS": ["ITC.NS","NESTLEIND.NS","BRITANNIA.NS","TATACONSUM.NS"],
    "ITC.NS":        ["HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS"],
    "DIXON.NS":      ["KAYNES.NS","AMBER.NS","PGEL.NS"],
    "KAYNES.NS":     ["DIXON.NS","AMBER.NS","PGEL.NS"],
}

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 ProAnalyzer")
    st.markdown("*Indian Equity Research Platform*")
    st.markdown("---")

    index_choice = st.selectbox(
        "🔍 Browse by Index",
        ["-- Type Manually --", "Nifty 50", "Bank Nifty", "Sensex"]
    )

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
        ticker = st.text_input("Enter NSE Symbol", value="DIXON.NS", placeholder="e.g. DIXON.NS")

    st.markdown("---")
    period_label = st.radio(
        "📅 Chart Period",
        ["1M","3M","6M","1Y","3Y","5Y"],
        index=3,
        horizontal=True
    )
    period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}

    show_volume    = st.checkbox("Show Volume", value=True)
    show_bollinger = st.checkbox("Show Bollinger Bands", value=False)

    st.markdown("---")
    analyze = st.button("🚀 Analyze", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("**Built by**")
    st.markdown("Pratyush Singh")
    st.markdown("MBA — Banking & Financial Engineering")
    st.markdown("Chandigarh University")

# ── Main Header ──────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 10px 0 20px 0;'>
    <h1 style='color:#00d4ff; font-size:2.2rem; font-weight:700; margin:0;'>
        📊 ProAnalyzer
    </h1>
    <p style='color:#8b949e; margin:4px 0 0 0; font-size:0.95rem;'>
        Professional Indian Equity Research Platform — Nifty 50 | Bank Nifty | Sensex
    </p>
</div>
""", unsafe_allow_html=True)

if not analyze:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-card'><h3 style='color:#00d4ff'>50+</h3><p style='color:#8b949e'>Nifty 50 Stocks</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><h3 style='color:#00d4ff'>12+</h3><p style='color:#8b949e'>Bank Nifty Stocks</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><h3 style='color:#00d4ff'>30+</h3><p style='color:#8b949e'>Sensex Stocks</p></div>", unsafe_allow_html=True)
    c4.markdown("<div class='metric-card'><h3 style='color:#00d4ff'>Live</h3><p style='color:#8b949e'>Real-time Data</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("👈 Select a stock from the sidebar and click **Analyze** to get started")
    st.stop()

# ── Fetch Data ───────────────────────────────────────────────
try:
    with st.spinner(f"Fetching data for {ticker}..."):
        stock    = yf.Ticker(ticker)
        df       = stock.history(period=period_map[period_label], auto_adjust=True)
        df_1y    = stock.history(period="1y", auto_adjust=True)

    if df.empty:
        st.error("❌ Stock not found! Check the symbol.")
        st.stop()

    try:
        fi       = stock.fast_info
        current  = round(fi.last_price, 2)
        high_52w = round(fi.year_high,  2)
        low_52w  = round(fi.year_low,   2)
        mkt_cap  = round(fi.market_cap / 1e7, 0)
    except:
        current  = round(df["Close"].iloc[-1], 2)
        high_52w = round(df["High"].max(), 2)
        low_52w  = round(df["Low"].min(),  2)
        mkt_cap  = 0

    prev_close   = round(df["Close"].iloc[-2], 2) if len(df) > 1 else current
    day_change   = round(current - prev_close, 2)
    day_change_p = round((day_change / prev_close) * 100, 2)
    returns_1y   = round(((df_1y["Close"].iloc[-1] / df_1y["Close"].iloc[0]) - 1) * 100, 2)

    try:
        info          = stock.info
        pe            = round(info.get("trailingPE",       0) or 0, 1)
        pb            = round(info.get("priceToBook",      0) or 0, 1)
        roe           = round((info.get("returnOnEquity",  0) or 0) * 100, 1)
        roa           = round((info.get("returnOnAssets",  0) or 0) * 100, 1)
        debt_eq       = round(info.get("debtToEquity",     0) or 0, 2)
        div           = round((info.get("dividendYield",   0) or 0) * 100, 2)
        book_val      = round(info.get("bookValue",        0) or 0, 2)
        profit_margin = round((info.get("profitMargins",   0) or 0) * 100, 1)
        rev_growth    = round((info.get("revenueGrowth",   0) or 0) * 100, 1)
        eps           = round(info.get("trailingEps",      0) or 0, 2)
        fwd_pe        = round(info.get("forwardPE",        0) or 0, 1)
        peg           = round(info.get("pegRatio",         0) or 0, 2)
        ev_ebitda     = round(info.get("enterpriseToEbitda",0) or 0, 1)
        current_ratio = round(info.get("currentRatio",    0) or 0, 2)
        quick_ratio   = round(info.get("quickRatio",      0) or 0, 2)
        beta          = round(info.get("beta",             0) or 0, 2)
        company_name  = info.get("longName",           ticker)
        description   = info.get("longBusinessSummary", "N/A")
        sector        = info.get("sector",               "N/A")
        industry      = info.get("industry",             "N/A")
        employees     = info.get("fullTimeEmployees",      0)
        website       = info.get("website",               "")
    except:
        pe=pb=roe=roa=debt_eq=div=book_val=profit_margin=rev_growth=eps=0
        fwd_pe=peg=ev_ebitda=current_ratio=quick_ratio=beta=0
        company_name=ticker; description=sector=industry="N/A"
        employees=0; website=""

    # ── Company Header ───────────────────────────────────────
    color = "#00d4ff"
    chg_color = "#26a641" if day_change >= 0 else "#da3633"
    chg_icon  = "▲" if day_change >= 0 else "▼"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a1f2e,#16213e);
                border:1px solid #30363d; border-radius:16px; padding:20px; margin-bottom:16px;'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <h2 style='color:{color}; margin:0; font-size:1.6rem;'>{company_name}</h2>
                <p style='color:#8b949e; margin:4px 0 0 0;'>{ticker} &nbsp;|&nbsp; {sector} &nbsp;|&nbsp; {industry}</p>
            </div>
            <div style='text-align:right;'>
                <h2 style='color:#fff; margin:0; font-size:2rem;'>₹{current:,}</h2>
                <p style='color:{chg_color}; margin:4px 0 0 0; font-size:1.1rem;'>
                    {chg_icon} ₹{abs(day_change)} ({abs(day_change_p)}%)
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("52W High",     f"₹{high_52w:,}")
    c2.metric("52W Low",      f"₹{low_52w:,}")
    c3.metric("Mkt Cap (Cr)", f"₹{mkt_cap:,.0f}")
    c4.metric("1Y Return",    f"{returns_1y}%", delta=f"{returns_1y}%")
    c5.metric("Beta",         beta)
    c6.metric("Employees",    f"{employees:,}" if employees else "N/A")

    st.markdown("---")

    t1,t2,t3,t4,t5,t6,t7 = st.tabs([
        "📈 Charts",
        "📐 Fundamentals",
        "💹 Financials",
        "👥 Peers",
        "🔍 SWOT",
        "🤖 AI Signal",
        "📰 News"
    ])

    # ════════════════════════════════════════════════
    # TAB 1 — CHARTS
    # ════════════════════════════════════════════════
    with t1:
        df["MA20"]  = df["Close"].rolling(20).mean()
        df["MA50"]  = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()

        df["BB_mid"]   = df["Close"].rolling(20).mean()
        df["BB_std"]   = df["Close"].rolling(20).std()
        df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
        df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]

        delta_c = df["Close"].diff()
        gain    = delta_c.where(delta_c > 0, 0).rolling(14).mean()
        loss    = (-delta_c.where(delta_c < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss if loss.any() else 1)))

        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        df["MACD"]        = ema12 - ema26
        df["MACD_signal"] = df["MACD"].ewm(span=9).mean()
        df["MACD_hist"]   = df["MACD"] - df["MACD_signal"]

        rsi_val  = round(df["RSI"].iloc[-1],  1) if not df["RSI"].empty and not np.isnan(df["RSI"].iloc[-1]) else 50.0
        macd_val = round(df["MACD"].iloc[-1], 2) if not df["MACD"].empty and not np.isnan(df["MACD"].iloc[-1]) else 0.0

        rows = 3 if show_volume else 2
        row_heights = [0.55, 0.25, 0.20] if show_volume else [0.65, 0.35]

        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            row_heights=row_heights,
            vertical_spacing=0.03
        )

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"],   close=df["Close"],
            name="Price",
            increasing_line_color="#26a641",
            decreasing_line_color="#da3633",
        ), row=1, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"],  name="20 MA",  line=dict(color="#f0f", width=1.2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"],  name="50 MA",  line=dict(color="#00bfff", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="200 MA", line=dict(color="orange", width=1.5)), row=1, col=1)

        if show_bollinger:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB Upper", line=dict(color="#ffffff40", width=1, dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB Lower", fill="tonexty", fillcolor="rgba(255,255,255,0.03)", line=dict(color="#ffffff40", width=1, dash="dot")), row=1, col=1)

        rsi_color = "#da3633" if rsi_val > 70 else ("#26a641" if rsi_val < 30 else "#e3b341")
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color=rsi_color, width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_color="#da363360", line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_color="#26a64160", line_dash="dash", row=2, col=1)
        fig.add_hline(y=50, line_color="#ffffff20", line_dash="dot",  row=2, col=1)

        if show_volume:
            vol_colors = ["#26a641" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#da3633" for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=vol_colors, opacity=0.7), row=3, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0a0e1a",
            plot_bgcolor="#0d1117",
            title=dict(text=f"{company_name} — {period_label} Chart", font=dict(color="#00d4ff", size=16)),
            height=600,
            showlegend=True,
            legend=dict(bgcolor="#0d111780", bordercolor="#30363d", borderwidth=1),
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig.update_yaxes(gridcolor="#21262d", zerolinecolor="#21262d")
        fig.update_xaxes(gridcolor="#21262d")
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("RSI (14)",  rsi_val,  help="<30 Oversold | >70 Overbought")
        c2.metric("MACD",      macd_val, help="Positive = Bullish momentum")
        c3.metric("50 DMA",    f"₹{round(df['MA50'].iloc[-1],1)}" if not df["MA50"].empty else "N/A")
        c4.metric("200 DMA",   f"₹{round(df['MA200'].iloc[-1],1)}" if not df["MA200"].empty else "N/A")

    # ════════════════════════════════════════════════
    # TAB 2 — FUNDAMENTALS (Error Fixed Here)
    # ════════════════════════════════════════════════
    with t2:
        st.markdown("### 📋 Company Overview")
        desc_text = str(description)
        st.write(desc_text[:700] + "..." if len(desc_text) > 700 else desc_text)
        if website:
            st.markdown(f"🔗 **Website:** [{website}]({website})")

        st.markdown("<div class='section-header'><h3>Valuation Metrics</h3></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Trailing P/E", pe if pe else "N/A")
        c2.metric("Forward P/E", fwd_pe if fwd_pe else "N/A")
        c3.metric("Price to Book (P/B)", pb if pb else "N/A")
        # ── FIXED LINE 507 BELOW ───────────────────────────────────────────
        c4.metric("PEG Ratio", peg, help="P/E to Growth - Values < 1 indicate undervaluation")

        st.markdown("<div class='section-header'><h3>Profitability & Margins</h3></div>", unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Return on Equity (ROE)", f"{roe}%" if roe else "N/A")
        c6.metric("Return on Assets (
