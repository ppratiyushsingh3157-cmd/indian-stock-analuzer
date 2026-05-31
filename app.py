import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ProAnalyzer — Institutional Equity Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp, .main { background-color: #0A0F1D; color: #F3F4F6; }
[data-testid="stSidebar"] {
    background-color: #0D1117;
    border-right: 1px solid #1F2937;
}
div[data-testid="metric-container"] {
    background-color: #1F2937;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 14px;
}
div[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #10B981 !important;
}
div[data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
    font-size: 12px !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.stTabs [data-baseweb="tab"] {
    color: #6B7280;
    font-size: 14px;
    font-weight: 500;
    padding: 10px 20px;
}
.stTabs [data-baseweb="tab"]:hover { color: #F3F4F6; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #3B82F6 !important;
    border-bottom: 2px solid #3B82F6 !important;
    font-weight: 600;
}
.signal-buy {
    background: rgba(16,185,129,0.10);
    border: 1px solid #10B981;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: #10B981;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.signal-sell {
    background: rgba(239,68,68,0.10);
    border: 1px solid #EF4444;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: #EF4444;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.signal-hold {
    background: rgba(245,158,11,0.10);
    border: 1px solid #F59E0B;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: #F59E0B;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
.stat-row {
    background: #1F2937;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 5px 0;
    display: flex;
    justify-content: space-between;
}
.pro-card {
    background: rgba(16,185,129,0.06);
    border-left: 4px solid #10B981;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 14px;
    color: #D1FAE5;
}
.con-card {
    background: rgba(239,68,68,0.06);
    border-left: 4px solid #EF4444;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 14px;
    color: #FEE2E2;
}
.opp-card {
    background: rgba(59,130,246,0.06);
    border-left: 4px solid #3B82F6;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 14px;
    color: #DBEAFE;
}
.threat-card {
    background: rgba(245,158,11,0.06);
    border-left: 4px solid #F59E0B;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 14px;
    color: #FEF3C7;
}
.divider { height:1px; background:#1F2937; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STOCK UNIVERSE
# ─────────────────────────────────────────────
NIFTY50 = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "SBI": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "HUL": "HINDUNILVR.NS",
    "Axis Bank": "AXISBANK.NS",
    "L&T": "LT.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Wipro": "WIPRO.NS",
    "Nestle India": "NESTLEIND.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "Titan": "TITAN.NS",
    "Tech Mahindra": "TECHM.NS",
    "Power Grid": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "M&M": "M&M.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Tata Steel": "TATASTEEL.NS",
    "ONGC": "ONGC.NS",
    "Coal India": "COALINDIA.NS",
    "Grasim": "GRASIM.NS",
    "Cipla": "CIPLA.NS",
    "Dr. Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Divis Labs": "DIVISLAB.NS",
    "Britannia": "BRITANNIA.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "BPCL": "BPCL.NS",
    "Hindalco": "HINDALCO.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "SBI Life": "SBILIFE.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "LTIMindtree": "LTIM.NS",
    "Shriram Finance": "SHRIRAMFIN.NS",
    "BEL": "BEL.NS",
}

BANKNIFTY = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "SBI": "SBIN.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Bank of Baroda": "BANKBARODA.NS",
    "PNB": "PNB.NS",
    "IDFC First Bank": "IDFCFIRSTB.NS",
    "Federal Bank": "FEDERALBNK.NS",
    "Canara Bank": "CANBK.NS",
    "AU Small Finance": "AUBANK.NS",
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
    "SBI": "SBIN.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HUL": "HINDUNILVR.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "M&M": "M&M.NS",
    "Wipro": "WIPRO.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Titan": "TITAN.NS",
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
    "HDFCBANK.NS":   ["ICICIBANK.NS","AXISBANK.NS","KOTAKBANK.NS","SBIN.NS","INDUSINDBK.NS"],
    "ICICIBANK.NS":  ["HDFCBANK.NS","AXISBANK.NS","KOTAKBANK.NS","SBIN.NS"],
    "AXISBANK.NS":   ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","SBIN.NS"],
    "SBIN.NS":       ["HDFCBANK.NS","ICICIBANK.NS","PNB.NS","BANKBARODA.NS","CANBK.NS"],
    "KOTAKBANK.NS":  ["HDFCBANK.NS","ICICIBANK.NS","AXISBANK.NS","INDUSINDBK.NS"],
    "MARUTI.NS":     ["TATAMOTORS.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","EICHERMOT.NS"],
    "TATAMOTORS.NS": ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS"],
    "SUNPHARMA.NS":  ["DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
    "DRREDDY.NS":    ["SUNPHARMA.NS","CIPLA.NS","DIVISLAB.NS"],
    "RELIANCE.NS":   ["ONGC.NS","BPCL.NS","ADANIENT.NS"],
    "HINDUNILVR.NS": ["ITC.NS","NESTLEIND.NS","BRITANNIA.NS","TATACONSUM.NS"],
    "ITC.NS":        ["HINDUNILVR.NS","NESTLEIND.NS","BRITANNIA.NS"],
    "DIXON.NS":      ["KAYNES.NS","AMBER.NS","PGEL.NS"],
    "KAYNES.NS":     ["DIXON.NS","AMBER.NS","PGEL.NS"],
    "LT.NS":         ["SIEMENS.NS","ABB.NS","BHEL.NS"],
    "BAJFINANCE.NS": ["BAJAJFINSV.NS","CHOLAFIN.NS","MUTHOOTFIN.NS"],
}

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs    = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def safe(val, mult=1, dec=2):
    try:
        return round((val or 0) * mult, dec)
    except:
        return 0

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 ProAnalyzer")
    st.markdown("<p style='color:#6B7280;font-size:12px;'>Institutional Equity Terminal</p>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    index_choice = st.selectbox("Browse by Index", ["-- Type Symbol --","Nifty 50","Bank Nifty","Sensex"])

    ticker = ""
    if index_choice == "Nifty 50":
        name   = st.selectbox("Select Stock", list(NIFTY50.keys()))
        ticker = NIFTY50[name]
    elif index_choice == "Bank Nifty":
        name   = st.selectbox("Select Stock", list(BANKNIFTY.keys()))
        ticker = BANKNIFTY[name]
    elif index_choice == "Sensex":
        name   = st.selectbox("Select Stock", list(SENSEX.keys()))
        ticker = SENSEX[name]
    else:
        raw = st.text_input("NSE Symbol", value="INFY", placeholder="e.g. DIXON").upper().strip()
        ticker = raw if raw.endswith(".NS") or raw.endswith(".BO") else f"{raw}.NS"

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    period_label = st.radio("Chart Period", ["1M","3M","6M","1Y","3Y","5Y"], index=3, horizontal=True)
    show_ema     = st.checkbox("50 & 200 EMA", value=True)
    show_bb      = st.checkbox("Bollinger Bands", value=False)
    show_vol     = st.checkbox("Volume", value=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    analyze = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;font-size:12px;'>Built by<br><b style='color:#F3F4F6'>Pratyush Singh</b><br>MBA — Banking & Financial Engineering<br>Chandigarh University</p>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding:8px 0 20px 0;'>
    <h1 style='color:#F3F4F6;font-size:1.8rem;font-weight:700;margin:0;'>
        ⚡ ProAnalyzer
        <span style='font-size:1rem;color:#6B7280;font-weight:400;margin-left:12px;'>
        Institutional Equity Research Terminal
        </span>
    </h1>
    <p style='color:#6B7280;font-size:13px;margin:4px 0 0 0;'>
        Nifty 50 &nbsp;|&nbsp; Bank Nifty &nbsp;|&nbsp; Sensex &nbsp;|&nbsp; Any NSE Stock
    </p>
</div>
""", unsafe_allow_html=True)

if not analyze:
    c1,c2,c3,c4 = st.columns(4)
    for col, label, val in zip(
        [c1,c2,c3,c4],
        ["Nifty 50 Stocks","Bank Nifty Stocks","Sensex Stocks","Indices Covered"],
        ["50+","12","30+","3"]
    ):
        col.metric(label, val)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Select a stock from the sidebar and click **Run Analysis**")
    st.stop()

# ─────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────
period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}
horizon    = {"1M":30,"3M":90,"6M":180,"1Y":365,"3Y":1095,"5Y":1825}

try:
    with st.spinner(f"Fetching data for {ticker}..."):
        stock   = yf.Ticker(ticker)
        df_full = stock.history(period="5y", auto_adjust=True)

    if df_full.empty:
        st.error("❌ Symbol not found. Check ticker and try again.")
        st.stop()

    df = df_full.tail(horizon[period_label]).copy()

    # Indicators on full data (to avoid NaN on short periods)
    df_full["EMA50"]  = df_full["Close"].ewm(span=50,  adjust=False).mean()
    df_full["EMA200"] = df_full["Close"].ewm(span=200, adjust=False).mean()
    df_full["RSI"]    = calc_rsi(df_full["Close"])
    df_full["MACD"]   = df_full["Close"].ewm(span=12).mean() - df_full["Close"].ewm(span=26).mean()
    df_full["MACD_sig"] = df_full["MACD"].ewm(span=9).mean()
    df_full["BB_mid"] = df_full["Close"].rolling(20).mean()
    df_full["BB_std"] = df_full["Close"].rolling(20).std()
    df_full["BB_up"]  = df_full["BB_mid"] + 2 * df_full["BB_std"]
    df_full["BB_lo"]  = df_full["BB_mid"] - 2 * df_full["BB_std"]

    df = df_full.tail(horizon[period_label]).copy()

    # Prices
    try:
        fi       = stock.fast_info
        current  = round(fi.last_price, 2)
        mkt_cap  = fi.market_cap
    except:
        current  = round(df["Close"].iloc[-1], 2)
        mkt_cap  = 0

    prev      = round(df["Close"].iloc[-2], 2) if len(df) > 1 else current
    chg       = round(current - prev, 2)
    chg_pct   = round((chg / prev) * 100, 2)

    try:
        info          = stock.info
        pe            = safe(info.get("trailingPE"))
        fwd_pe        = safe(info.get("forwardPE"))
        pb            = safe(info.get("priceToBook"))
        peg           = safe(info.get("pegRatio"))
        ev_ebitda     = safe(info.get("enterpriseToEbitda"))
        eps           = safe(info.get("trailingEps"))
        roe           = safe(info.get("returnOnEquity"), 100, 1)
        roa           = safe(info.get("returnOnAssets"), 100, 1)
        profit_margin = safe(info.get("profitMargins"),  100, 1)
        rev_growth    = safe(info.get("revenueGrowth"),  100, 1)
        debt_eq       = safe(info.get("debtToEquity"))
        curr_ratio    = safe(info.get("currentRatio"))
        quick_ratio   = safe(info.get("quickRatio"))
        div_yield     = safe(info.get("dividendYield"), 100, 2)
        book_val      = safe(info.get("bookValue"))
        beta          = safe(info.get("beta"))
        high_52       = safe(info.get("fiftyTwoWeekHigh"))
        low_52        = safe(info.get("fiftyTwoWeekLow"))
        employees     = info.get("fullTimeEmployees", 0)
        company_name  = info.get("longName",           ticker)
        description   = info.get("longBusinessSummary","N/A")
        sector        = info.get("sector",             "N/A")
        industry      = info.get("industry",           "N/A")
        website       = info.get("website",            "")
    except:
        pe=fwd_pe=pb=peg=ev_ebitda=eps=roe=roa=0
        profit_margin=rev_growth=debt_eq=curr_ratio=quick_ratio=0
        div_yield=book_val=beta=high_52=low_52=0
        employees=0
        company_name=ticker; description=sector=industry="N/A"; website=""

    df_1y = df_full.tail(365).copy()
    ret_1y = round(((df_1y["Close"].iloc[-1]/df_1y["Close"].iloc[0])-1)*100, 2)

    rsi_now  = round(df["RSI"].iloc[-1],  1) if not pd.isna(df["RSI"].iloc[-1"])  else 50
    ema50_now  = round(df["EMA50"].iloc[-1],  1)
    ema200_now = round(df["EMA200"].iloc[-1], 1)
    macd_now   = round(df["MACD"].iloc[-1],   2)

    # ─────────────────────────────────────────
    # COMPANY HEADER
    # ─────────────────────────────────────────
    chg_color = "#10B981" if chg >= 0 else "#EF4444"
    chg_icon  = "▲" if chg >= 0 else "▼"

    st.markdown(f"""
    <div style='background:#1F2937; border:1px solid #2D3748; border-radius:12px;
                padding:20px 24px; margin-bottom:16px;'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;'>
            <div>
                <h2 style='color:#F3F4F6; margin:0; font-size:1.5rem; font-weight:700;'>
                    {company_name}
                </h2>
                <p style='color:#6B7280; margin:4px 0 0 0; font-size:13px;'>
                    {ticker} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {industry}
                    {"&nbsp;·&nbsp; <a href='" + website + "' target='_blank' style='color:#3B82F6;'>Website ↗</a>" if website else ""}
                </p>
            </div>
            <div style='text-align:right;'>
                <div style='color:#F3F4F6; font-size:2rem; font-weight:700;'>₹{current:,}</div>
                <div style='color:{chg_color}; font-size:1rem; font-weight:600;'>
                    {chg_icon} ₹{abs(chg)} ({abs(chg_pct)}%) Today
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("52W High",      f"₹{high_52:,}")
    c2.metric("52W Low",       f"₹{low_52:,}")
    c3.metric("Mkt Cap (Cr)",  f"₹{round((mkt_cap or 0)/1e7):,}")
    c4.metric("1Y Return",     f"{ret_1y}%",  delta=f"{ret_1y}%")
    c5.metric("Beta",          beta)
    c6.metric("RSI (14)",      rsi_now)
    c7.metric("Employees",     f"{employees:,}" if employees else "N/A")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # TABS
    # ─────────────────────────────────────────
    t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs([
        "📈 Charts",
        "📐 Valuation",
        "📋 P&L",
        "🏦 Balance Sheet",
        "💸 Cash Flow",
        "👥 Peers",
        "🔍 SWOT",
        "🤖 AI Signal"
    ])

    # ══════════════════════════════════════════
    # TAB 1 — CHARTS
    # ══════════════════════════════════════════
    with t1:
        rows = 4 if show_vol else 3
        heights = [0.50, 0.20, 0.15, 0.15] if show_vol else [0.55, 0.25, 0.20]

        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            row_heights=heights,
            vertical_spacing=0.03,
            subplot_titles=["Price", "RSI", "MACD", "Volume"][:rows]
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"],   close=df["Close"],
            name="Price",
            increasing_line_color="#10B981",
            decreasing_line_color="#EF4444",
            increasing_fillcolor="#10B981",
            decreasing_fillcolor="#EF4444",
        ), row=1, col=1)

        if show_ema:
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"],  name="50 EMA",
                line=dict(color="#3B82F6", width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="200 EMA",
                line=dict(color="#F59E0B", width=2.0)), row=1, col=1)

        if show_bb:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_up"], name="BB Upper",
                line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lo"], name="BB Lower",
                fill="tonexty", fillcolor="rgba(255,255,255,0.03)",
                line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot")), row=1, col=1)

        # RSI
        rsi_color = "#EF4444" if rsi_now > 70 else ("#10B981" if rsi_now < 30 else "#3B82F6")
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
            line=dict(color=rsi_color, width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_color="rgba(239,68,68,0.5)",   line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_color="rgba(16,185,129,0.5)",  line_dash="dash", row=2, col=1)
        fig.add_hline(y=50, line_color="rgba(255,255,255,0.15)",line_dash="dot",  row=2, col=1)

        # MACD
        macd_colors = ["#10B981" if v >= 0 else "#EF4444" for v in df["MACD"] - df["MACD_sig"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD"]-df["MACD_sig"],
            name="MACD Hist", marker_color=macd_colors, opacity=0.7), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],     name="MACD",
            line=dict(color="#3B82F6", width=1.2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_sig"], name="Signal",
            line=dict(color="
