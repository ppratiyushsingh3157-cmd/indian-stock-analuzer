import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------
# 1. INSTITUTIONAL TERMINAL ARCHITECTURE CANVAS
# ----------------------------------------------------
st.set_page_config(
    page_title="ProAnalyzer — Institutional Equity Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Screener.in Palette Styling Framework
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp, .main { background-color: #0A0F1D; color: #F3F4F6; }
[data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #1F2937; }
div[data-testid="metric-container"] {
    background-color: #1F2937; border: 1px solid #2D3748;
    border-radius: 10px; padding: 14px;
}
div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: #10B981 !important; }
div[data-testid="stMetricLabel"] { color: #9CA3AF !important; font-size: 12px !important; text-transform: uppercase; }
.stTabs [data-baseweb="tab"] { color: #6B7280; font-size: 14px; font-weight: 500; padding: 10px 20px; }
.stTabs [data-baseweb="tab"]:hover { color: #F3F4F6; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #3B82F6 !important; border-bottom: 2px solid #3B82F6 !important; font-weight: 600; }
.signal-buy { background: rgba(16,185,129,0.10); border: 1px solid #10B981; border-radius: 10px; padding: 20px; text-align: center; color: #10B981; font-size: 1.6rem; font-weight: 700; }
.signal-sell { background: rgba(239,68,68,0.10); border: 1px solid #EF4444; border-radius: 10px; padding: 20px; text-align: center; color: #EF4444; font-size: 1.6rem; font-weight: 700; }
.signal-hold { background: rgba(245,158,11,0.10); border: 1px solid #F59E0B; border-radius: 10px; padding: 20px; text-align: center; color: #F59E0B; font-size: 1.6rem; font-weight: 700; }
.pro-card { background: rgba(16,185,129,0.06); border-left: 4px solid #10B981; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; font-size: 14px; color: #D1FAE5; }
.con-card { background: rgba(239,68,68,0.06); border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; font-size: 14px; color: #FEE2E2; }
.opp-card { background: rgba(59,130,246,0.06); border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; font-size: 14px; color: #DBEAFE; }
.threat-card { background: rgba(245,158,11,0.06); border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 8px; font-size: 14px; color: #FEF3C7; }
.divider { height:1px; background:#1F2937; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. CORE MASTER INDEX DEFINITIONS
# ----------------------------------------------------
NIFTY50 = {
    "Reliance Industries":"RELIANCE.NS","TCS":"TCS.NS","HDFC Bank":"HDFCBANK.NS",
    "ICICI Bank":"ICICIBANK.NS","Infosys":"INFY.NS","SBI":"SBIN.NS",
    "Bharti Airtel":"BHARTIARTL.NS","ITC":"ITC.NS","Kotak Mahindra Bank":"KOTAKBANK.NS",
    "HUL":"HINDUNILVR.NS","Axis Bank":"AXISBANK.NS","L&T":"LT.NS",
    "Asian Paints":"ASIANPAINT.NS","HCL Technologies":"HCLTECH.NS",
    "Bajaj Finance":"BAJFINANCE.NS","Sun Pharma":"SUNPHARMA.NS","Wipro":"Wipro.NS",
    "Nestle India":"NESTLEIND.NS","UltraTech Cement":"ULTRACEMCO.NS","Titan":"TITAN.NS",
    "Tech Mahindra":"TECHM.NS","Power Grid":"POWERGRID.NS","NTPC":"NTPC.NS",
    "IndusInd Bank":"INDUSINDBK.NS","Tata Motors":"TATAMOTORS.NS","M&M":"M&M.NS",
    "Bajaj Auto":"BAJAJ-AUTO.NS","Maruti Suzuki":"MARUTI.NS","JSW Steel":"JSWSTEEL.NS",
    "Tata Steel":"TATASTEEL.NS","ONGC":"ONGC.NS","Coal India":"COALINDIA.NS",
    "Grasim":"GRASIM.NS","Cipla":"CIPLA.NS","Dr. Reddys":"DRREDDY.NS",
    "Eicher Motors":"EICHERMOT.NS","Hero MotoCorp":"HEROMOTOCO.NS",
    "Divis Labs":"DIVISLAB.NS","Britannia":"BRITANNIA.NS",
    "Apollo Hospitals":"APOLLOHOSP.NS","Adani Ports":"ADANIPORTS.NS",
    "Adani Enterprises":"ADANIENT.NS","BPCL":"BPCL.NS","Hindalco":"HINDALCO.NS",
    "Tata Consumer":"TATACONSUM.NS","SBI Life":"SBILIFE.NS","HDFC Life":"HDFCLIFE.NS",
    "LTIMindtree":"LTIM.NS","Shriram Finance":"SHRIRAMFIN.NS","BEL":"BEL.NS",
}

BANKNIFTY = {
    "HDFC Bank":"HDFCBANK.NS","ICICI Bank":"ICICIBANK.NS","SBI":"SBIN.NS",
    "Kotak Mahindra Bank":"KOTAKBANK.NS","Axis Bank":"AXISBANK.NS",
    "IndusInd Bank":"INDUSINDBK.NS","Bank of Baroda":"BANKBARODA.NS",
    "PNB":"PNB.NS","IDFC First Bank":"IDFCFIRSTB.NS","Federal Bank":"FEDERALBNK.NS",
    "Canara Bank":"CANBK.NS","AU Small Finance":"AUBANK.NS",
}

SENSEX = {
    "Reliance Industries":"RELIANCE.NS","TCS":"TCS.NS","HDFC Bank":"HDFCBANK.NS",
    "ICICI Bank":"ICICIBANK.NS","Infosys":"INFY.NS","Bharti Airtel":"BHARTIARTL.NS",
    "ITC":"ITC.NS","L&T":"LT.NS","Kotak Mahindra Bank":"KOTAKBANK.NS",
    "Axis Bank":"AXISBANK.NS","SBI":"SBIN.NS","HCL Technologies":"HCLTECH.NS",
    "Bajaj Finance":"BAJFINANCE.NS","Asian Paints":"ASIANPAINT.NS","HUL":"HINDUNILVR.NS",
    "Sun Pharma":"SUNPHARMA.NS","Maruti Suzuki":"MARUTI.NS","M&M":"M&M.NS",
    "Wipro":"WIPRO.NS","Tata Motors":"TATAMOTORS.NS","Titan":"TITAN.NS",
    "UltraTech Cement":"ULTRACEMCO.NS","Power Grid":"POWERGRID.NS","NTPC":"NTPC.NS",
    "JSW Steel":"JSWSTEEL.NS","Tata Steel":"TATASTEEL.NS","ONGC":"ONGC.NS",
    "Nestle India":"NESTLEIND.NS","Tech Mahindra":"TECHM.NS","Bajaj Finserv":"BAJAJFINSV.NS",
}

# High-Fidelity Comprehensive Dynamic Target Array Pool
TICKER_UNIVERSE_POOL = [
    "INFY.NS", "TCS.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "KPITTECH.NS",
    "CDSL.NS", "BSE.NS", "MCX.NS", "IEX.NS",
    "DIXON.NS", "AMBER.NS", "KAYNES.NS", "SYRMA.NS",
    "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS",
    "SBIN.NS", "HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"
]

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def safe(val, mult=1, dec=2):
    try:
        if pd.isna(val) or val is None:
            return 0
        return round(float(val) * mult, dec)
    except:
        return 0

# ----------------------------------------------------
# 3. SIDEBAR CONTROLS MAPPING NODE
# ----------------------------------------------------
with st.sidebar:
    st.markdown("## 📊 ProAnalyzer")
    st.markdown("<p style='color:#6B7280;font-size:12px;'>Institutional Equity Terminal</p>", unsafe_allow_html=True)
    st.markdown("---")
    index_choice = st.selectbox("Browse by Index", ["-- Type Symbol --","Nifty 50","Bank Nifty","Sensex"])
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
        raw = st.text_input("NSE Symbol", value="INFY", placeholder="e.g. DIXON").upper().strip()
        ticker = raw if raw.endswith(".NS") or raw.endswith(".BO") else f"{raw}.NS"
    st.markdown("---")
    period_label = st.radio("Chart Period", ["1M","3M","6M","1Y","3Y","5Y"], index=3, horizontal=True)
    show_ema = st.checkbox("50 & 200 EMA", value=True)
    show_bb  = st.checkbox("Bollinger Bands", value=False)
    show_vol = st.checkbox("Volume", value=True)
    st.markdown("---")
    analyze = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("<p style='color:#6B7280;font-size:12px;'>Built by<br><b style='color:#F3F4F6'>Pratyush Singh</b><br>MBA — Banking & Financial Engineering<br>Chandigarh University</p>", unsafe_allow_html=True)

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
    c1.metric("Nifty 50 Stocks","50+")
    c2.metric("Bank Nifty Stocks","12")
    c3.metric("Sensex Stocks","30+")
    c4.metric("Indices Covered","3")
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Select a stock from the sidebar and click Run Analysis")
    st.stop()

horizon = {"1M":30,"3M":90,"6M":180,"1Y":365,"3Y":1095,"5Y":1825}

# ----------------------------------------------------
# 4. ROBUST PIPELINE DATA INGESTION ENGINE
# ----------------------------------------------------
try:
    with st.spinner(f"Fetching data for {ticker}..."):
        stock   = yf.Ticker(ticker)
        df_full = stock.history(period="5y", auto_adjust=True)

    if df_full.empty:
        st.error("Symbol not found. Check ticker and try again.")
        st.stop()

    # Financial Signal Track Computations
    df_full["EMA50"]    = df_full["Close"].ewm(span=50,  adjust=False).mean()
    df_full["EMA200"]   = df_full["Close"].ewm(span=200, adjust=False).mean()
    df_full["RSI"]      = calc_rsi(df_full["Close"])
    df_full["MACD"]     = df_full["Close"].ewm(span=12).mean() - df_full["Close"].ewm(span=26).mean()
    df_full["MACD_sig"] = df_full["MACD"].ewm(span=9).mean()
    df_full["BB_mid"]   = df_full["Close"].rolling(20).mean()
    df_full["BB_std"]   = df_full["Close"].rolling(20).std()
    df_full["BB_up"]    = df_full["BB_mid"] + 2 * df_full["BB_std"]
    df_full["BB_lo"]    = df_full["BB_mid"] - 2 * df_full["BB_std"]

    df = df_full.tail(horizon[period_label]).copy()

    try:
        fi = stock.fast_info
        current = round(fi.last_price, 2)
        mkt_cap = fi.market_cap
    except:
        current = round(df["Close"].iloc[-1], 2)
        mkt_cap = 0

    prev    = round(df["Close"].iloc[-2], 2) if len(df) > 1 else current
    chg     = round(current - prev, 2)
    chg_pct = round((chg / prev) * 100, 2)

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
        company_name  = info.get("longName", ticker)
        description   = info.get("longBusinessSummary", "N/A")
        sector        = info.get("sector",   "N/A")
        industry      = info.get("industry", "N/A")
        website       = info.get("website",  "")
    except:
        pe=fwd_pe=pb=peg=ev_ebitda=eps=roe=roa=0
        profit_margin=rev_growth=debt_eq=curr_ratio=quick_ratio=0
        div_yield=book_val=beta=high_52=low_52=0
        employees=0
        company_name=ticker; description=sector=industry="N/A"; website=""

    df_1y  = df_full.tail(365).copy()
    ret_1y = round(((df_1y["Close"].iloc[-1]/df_1y["Close"].iloc[0])-1)*100, 2)

    rsi_last = df["RSI"].iloc[-1]
    rsi_now  = round(rsi_last, 1) if not pd.isna(rsi_last) else 50
    ema50_now  = round(df["EMA50"].iloc[-1],  1)
    ema200_now = round(df["EMA200"].iloc[-1], 1)
    macd_now   = round(df["MACD"].iloc[-1],   2)

    chg_color = "#10B981" if chg >= 0 else "#EF4444"
    chg_icon  = "▲" if chg >= 0 else "▼"

    st.markdown(f"""
    <div style='background:#1F2937;border:1px solid #2D3748;border-radius:12px;padding:20px 24px;margin-bottom:16px;'>
        <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;'>
            <div>
                <h2 style='color:#F3F4F6;margin:0;font-size:1.5rem;font-weight:700;'>{company_name}</h2>
                <p style='color:#6B7280;margin:4px 0 0 0;font-size:13px;'>{ticker} · {sector} · {industry}</p>
            </div>
            <div style='text-align:right;'>
                <div style='color:#F3F4F6;font-size:2rem;font-weight:700;'>₹{current:,}</div>
                <div style='color:{chg_color};font-size:1rem;font-weight:600;'>{chg_icon} ₹{abs(chg)} ({abs(chg_pct)}%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("52W High",     f"₹{high_52:,}")
    c2.metric("52W Low",      f"₹{low_52:,}")
    c3.metric("Mkt Cap (Cr)", f"₹{round((mkt_cap or 0)/1e7):,}")
    c4.metric("1Y Return",    f"{ret_1y}%", delta=f"{ret_1y}%")
    c5.metric("Beta",         beta)
    c6.metric("RSI (14)",     rsi_now)
    c7.metric("Employees",    f"{employees:,}" if employees else "N/A")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs([
        "📈 Charts","📐 Valuation","📋 P&L",
        "🏦 Balance Sheet","💸 Cash Flow",
        "👥 Peers","🔍 SWOT","🤖 AI Signal"
    ])

    with t1:
        rows = 4 if show_vol else 3
        heights = [0.50,0.20,0.15,0.15] if show_vol else [0.55,0.25,0.20]
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
            row_heights=heights, vertical_spacing=0.03)

        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="Price",
            increasing_line_color="#10B981", decreasing_line_color="#EF4444",
            increasing_fillcolor="#10B981", decreasing_fillcolor="#EF4444",
        ), row=1, col=1)

        if show_ema:
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"],  name="50 EMA",  line=dict(color="#3B82F6", width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="200 EMA", line=dict(color="#F59E0B", width=2.0)), row=1, col=1)

        if show_bb:
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_up"], name="BB Upper",
                line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["BB_lo"], name="BB Lower",
                fill="tonexty", fillcolor="rgba(255,255,255,0.03)",
                line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot")), row=1, col=1)

        rsi_color = "#EF4444" if rsi_now > 70 else ("#10B981" if rsi_now < 30 else "#3B82F6")
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
            line=dict(color=rsi_color, width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_color="rgba(239,68,68,0.5)",  line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_color="rgba(16,185,129,0.5)", line_dash="dash", row=2, col=1)

        macd_hist = df["MACD"] - df["MACD_sig"]
        macd_colors = ["#10B981" if v >= 0 else "#EF4444" for v in macd_hist]
        fig.add_trace(go.Bar(x=df.index, y=macd_hist, name="MACD Hist",
            marker_color=macd_colors, opacity=0.7), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],     name="MACD",   line=dict(color="#3B82F6", width=1.2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_sig"], name="Signal", line=dict(color="#F59E0B", width=1.2)), row=3, col=1)

        if show_vol:
            vcols = ["#10B981" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#EF4444" for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                marker_color=vcols, opacity=0.6), row=4, col=1)

        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0A0F1D", plot_bgcolor="#0A0F1D",
            height=680, showlegend=True, xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.02, x=1, xanchor="right"),
            margin=dict(l=0,r=0,t=30,b=0),
        )
        fig.update_yaxes(gridcolor="#1F2937", zerolinecolor="#1F2937")
        fig.update_xaxes(gridcolor="#1F2937")
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("RSI (14)",  rsi_now)
        c2.metric("MACD",      macd_now)
        c3.metric("50 EMA",    f"₹{ema50_now:,}")
        c4.metric("200 EMA",   f"₹{ema200_now:,}")
        c5.metric("vs 200 EMA",f"{round(((current/ema200_now)-1)*100,1)}%")

    with t2:
        st.markdown("### Company Overview")
        desc_text = str(description)
        st.markdown(f"<div style='color:#D1D5DB;line-height:1.8;font-size:14px;'>{desc_text[:700]}{'...' if len(desc_text)>700 else ''}</div>", unsafe_allow_html=True)
        if website:
            st.markdown(f"🌐 [Official Website]({website})")
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        st.markdown("### Valuation Ratios")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("P/E (TTM)",   f"{pe}x")
        c2.metric("Forward P/E", f"{fwd_pe}x")
        c3.metric("P/B Ratio",   f"{pb}x")
        c4.metric("PEG Ratio",   peg)
        c5.metric("EV/EBITDA",   f"{ev_ebitda}x")
        c6.metric("EPS (Rs)",    eps)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("### Profitability & Growth")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("ROE %",        f"{roe}%")
        c2.metric("ROA %",        f"{roa}%")
        c3.metric("Net Margin %", f"{profit_margin}%")
        c4.metric("Rev Growth %", f"{rev_growth}%")
        c5.metric("Div Yield %",  f"{div_yield}%")
        c6.metric("Book Value",   f"Rs {book_val}")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("### Financial Health")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Debt/Equity",   debt_eq)
        c2.metric("Current Ratio", curr_ratio)
        c3.metric("Quick Ratio",   quick_ratio)
        c4.metric("Beta",          beta)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("### DCF — Intrinsic Value Estimator")
        col1,col2,col3 = st.columns(3)
        g  = col1.slider("Growth Rate %", 5, 40, 15)
        dr = col2.slider("Discount Rate %", 8, 20, 12)
        yr = col3.slider("Years", 3, 10, 5)
        if eps > 0:
            future_eps = eps * ((1 + g/100) ** yr)
            dcf_value  = (future_eps * 15) / ((1 + dr/100) ** yr)
            mos        = round(((dcf_value - current) / current) * 100, 1)
            verdict    = "Undervalued" if dcf_value > current else "Overvalued"
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("DCF Value",        f"Rs {round(dcf_value,1)}")
            c2.metric("Current Price",    f"Rs {current}")
            c3.metric("Margin of Safety", f"{mos}%")
            c4.metric("Verdict",          verdict)
        else:
            st.warning("EPS unavailable — DCF cannot be calculated.")

    with t3:
        st.markdown("### Profit & Loss Statement (Rs Crores)")
        try:
            inc = stock.financials.copy()
            if not inc.empty:
                # Transpose and normalize columns to safe numeric types
                inc = inc.T
                inc.index = pd.to_datetime(inc.index).year
                inc = inc.sort_index()
                
                # Resilient column checks to prevent key crashes
                available_cols = [col for col in ["Total Revenue","Gross Profit","Operating Income","Net Income"] if col in inc.columns]
                
                if available_cols:
                    # Dynamically convert elements to prevent text-based float parsing issues
                    for col in available_cols:
                        inc[col] = pd.to_numeric(inc[col], errors='coerce')
                    
                    st.dataframe((inc[available_cols]/1e7).style.format("{:,.1f}").background_gradient(cmap="Greens",axis=0), use_container_width=True)
                    
                    fig_pl = go.Figure()
                    cf_colors = ["#3B82F6","#10B981","#F59E0B","#EF4444"]
                    for i,col in enumerate(available_cols):
                        fig_pl.add_trace(go.Bar(name=col, x=inc.index.astype(str), y=inc[col]/1e7, marker_color=cf_colors[i%4]))
                    fig_pl.update_layout(template="plotly_dark", paper_bgcolor="#0A0F1D", plot_bgcolor="#0A0F1D",
                        title="P&L Trend (Rs Cr)", barmode="group", height=400)
                    st.plotly_chart(fig_pl, use_container_width=True)
            else:
                st.warning("P&L data matrices currently not synchronized by standard quote endpoints.")
        except Exception as pl_err:
            st.warning(f"P&L ledger generation update pending: {pl_err}")

    with t4:
        st.markdown("### Balance Sheet (Rs Crores)")
        try:
            bs = stock.balance_sheet.copy()
            if not bs.empty:
                bs = bs.T
                bs.index = pd.to_datetime(bs.index).year
                bs = bs.sort_index()
                
                # Resilient mapping matching alternate accounting naming systems
                bs = bs.rename(columns={"Total Liabilities Net Minority Interest": "Total Liabilities"})
                available_cols = [col for col in ["Total Assets","Total Liabilities","Stockholders Equity","Total Debt"] if col in bs.columns]
                
                if available_cols:
                    for col in available_cols:
                        bs[col] = pd.to_numeric(bs[col], errors='coerce')
                        
                    st.dataframe((bs[available_cols]/1e7).style.format("{:,.1f}").background_gradient(cmap="Blues",axis=0), use_container_width=True)
                    fig_bs = go.Figure()
                    for col in ["Total Assets","Stockholders Equity","Total Debt"]:
                        if col in bs.columns:
                            fig_bs.add_trace(go.Bar(name=col, x=bs.index.astype(str), y=bs[col]/1e7))
                    fig_bs.update_layout(template="plotly_dark", paper_bgcolor="#0A0F1D", plot_bgcolor="#0A0F1D",
                        title="Balance Sheet Trend (Rs Cr)", barmode="group", height=400)
                    st.plotly_chart(fig_bs, use_container_width=True)
            else:
                st.warning("Balance sheet ledger currently not returning valid coordinates.")
        except Exception as bs_err:
            st.warning(f"Balance sheet matrix update pending: {bs_err}")

    with t5:
        st.markdown("### Cash Flow Statement (Rs Crores)")
        try:
            cf = stock.cashflow.copy()
            if not cf.empty:
                cf = cf.T
                cf.index = pd.to_datetime(cf.index).year
                cf = cf.sort_index()
                available_cols = [col for col in ["Operating Cash Flow","Investing Cash Flow","Free Cash Flow","Capital Expenditure"] if col in cf.columns]
                
                if available_cols:
                    for col in available_cols:
                        cf[col] = pd.to_numeric(cf[col], errors='coerce')
                        
                    st.dataframe((cf[available_cols]/1e7).style.format("{:,.1f}"), use_container_width=True)
                    colors_cf = ["#10B981","#F59E0B","#3B82F6","#EF4444"]
                    fig_cf = go.Figure()
                    for i,col in enumerate(available_cols):
                        fig_cf.add_trace(go.Bar(name=col, x=cf.index.astype(str), y=cf[col]/1e7, marker_color=colors_cf[i%4]))
                    fig_cf.update_layout(template="plotly_dark", paper_bgcolor="#0A0F1D", plot_bgcolor="#0A0F1D",
                        title="Cash Flow Trend (Rs Cr)", barmode="group", height=400)
                    st.plotly_chart(fig_cf, use_container_width=True)
            else:
                st.warning("Cash flows metrics currently processing structural updates.")
        except Exception as cf_err:
            st.warning(f"Cash flow reporting tracking details pending: {cf_err}")

    # TRUE DYNAMIC MARKET SECTOR & INDUSTRY MATCHING PEER ENGINE FIXED
    with t6:
        st.markdown(f"### 👥 Competitor Peer Benchmarking (Dynamic Structural Industry Matching)")
        
        dynamic_peers_pool = []
        
        # Scrape and select only companies having exact same 'industry' parameter match
        with st.spinner("Executing direct sector cross-matching..."):
            for potential_peer in TICKER_UNIVERSE_POOL:
                if potential_peer == ticker:
                    continue
                try:
                    peer_obj = yf.Ticker(potential_peer)
                    p_info = peer_obj.info
                    
                    # Core validation rule: Verify industry string matches perfectly
                    if p_info.get('industry') == industry:
                        dynamic_peers_pool.append({
                            "Company": p_info.get("longName", potential_peer).replace(".NS", ""),
                            "Price (Rs)": safe(p_info.get("currentPrice")),
                            "Mkt Cap (Cr)": round((p_info.get("marketCap", 0) or 0) / 1e7, 0),
                            "P/E": safe(p_info.get("trailingPE")),
                            "Fwd P/E": safe(p_info.get("forwardPE")),
                            "P/B": safe(p_info.get("priceToBook")),
                            "EV/EBITDA": safe(p_info.get("enterpriseToEbitda")),
                            "ROE %": safe(p_info.get("returnOnEquity"), 100, 1),
                            "ROA %": safe(p_info.get("returnOnAssets"), 100, 1),
                            "Net Margin %": safe(p_info.get("profitMargins"), 100, 1),
                            "Debt/Eq": safe(p_info.get("debtToEquity")),
                            "Rev Growth %": safe(p_info.get("revenueGrowth"), 100, 1),
                            "EPS (Rs)": safe(p_info.get("trailingEps")),
                            "Div Yield %": safe(p_info.get("dividendYield"), 100, 2),
                            "Beta": safe(p_info.get("beta")),
                        })
                except:
                    pass
                    
        # Include baseline stock details inside the dynamic pool for comparison layout
        if dynamic_peers_pool:
            # Injecting base tracked stock metrics as row index item 0
            base_row = {
                "Company": company_name, "Price (Rs)": current, "Mkt Cap (Cr)": round((mkt_cap or 0)/1e7, 0),
                "P/E": pe, "Fwd P/E": fwd_pe, "P/B": pb, "EV/EBITDA": ev_ebitda, "ROE %": roe, "ROA %": roa,
                "Net Margin %": profit_margin, "Debt/Eq": debt_eq, "Rev Growth %": rev_growth, "EPS (Rs)": eps,
                "Div Yield %": div_yield, "Beta": beta
            }
            dynamic_peers_pool.insert(0, base_row)
            
            peers_df = pd.DataFrame(dynamic_peers_pool)
            st.dataframe(
                peers_df.style.format({
                    "Price (Rs)":"{:,.2f}","Mkt Cap (Cr)":"{:,.0f}",
                    "P/E":"{:.1f}x","Fwd P/E":"{:.1f}x","P/B":"{:.1f}x",
                    "ROE %":"{:.1f}%","ROA %":"{:.1f}%",
                    "Net Margin %":"{:.1f}%","Rev Growth %":"{:.1f}%","Div Yield %":"{:.2f}%",
                }).highlight_max(subset=["ROE %","Net Margin %","Rev Growth %","EPS (Rs)"], color="#064e3b")
                .highlight_min(subset=["P/E","Debt/Eq","P/B"], color="#064e3b"),
                use_container_width=True, height=300
            )
            
            metric_pick = st.selectbox("Visualize Metric:",
                ["P/E","P/B","ROE %","Net Margin %","Rev Growth %","Debt/Eq","EV/EBITDA","EPS (Rs)","Beta"])
            bar_colors = ["#3B82F6" if i==0 else "#374151" for i in range(len(peers_df))]
            fig_peer = go.Figure(go.Bar(
                x=peers_df["Company"], y=peers_df[metric_pick],
                marker_color=bar_colors,
                text=peers_df[metric_pick].round(1),
                textposition="outside", textfont=dict(color="#F3F4F6")
            ))
            fig_peer.update_layout(template="plotly_dark", paper_bgcolor="#0A0F1D",
                plot_bgcolor="#0A0F1D", title=f"{metric_pick} — Dynamic Peer Comparison",
                height=420, xaxis_tickangle=-15)
            st.plotly_chart(fig_peer, use_container_width=True)
        else:
            st.info(f"Analyzing proxy industry sectors... Pure peers list for {industry} currently undergoing pipeline matching.")

    with t7:
        st.markdown("### SWOT Strategic Analysis")
        c_l,c_r = st.columns(2)
        with c_l:
            st.markdown("#### Strengths")
            S = []
            if roe > 15:           S.append(f"ROE {roe}% — above 15% benchmark")
            if profit_margin > 10: S.append(f"Net margin {profit_margin}% — healthy")
            if rev_growth > 10:    S.append(f"Revenue growing {rev_growth}% YoY")
            if debt_eq < 0.5:      S.append(f"Low leverage — D/E {debt_eq}")
            if curr_ratio > 1.5:   S.append(f"Strong liquidity — current ratio {curr_ratio}")
            if ret_1y > 15:        S.append(f"Outperformed market — {ret_1y}% 1Y return")
            if div_yield > 1:      S.append(f"Consistent dividends — yield {div_yield}%")
            if beta < 1:           S.append(f"Low volatility — beta {beta}")
            if not S:              S.append("Established company with stable operational history")
            for s in S:
                st.markdown(f"<div class='pro-card'>✅ {s}</div>", unsafe_allow_html=True)

            st.markdown("#### Weaknesses")
            W = []
            if roe < 12:           W.append(f"ROE {roe}% below 15% benchmark")
            if debt_eq > 1:        W.append(f"High leverage — D/E {debt_eq}")
            if profit_margin < 8:  W.append(f"Thin margins at {profit_margin}%")
            if pe > 50:            W.append(f"Premium valuation — P/E {pe}x")
            if ret_1y < 0:         W.append(f"Negative 1Y return of {ret_1y}%")
            if curr_ratio < 1:     W.append(f"Liquidity risk — current ratio {curr_ratio}")
            if beta > 1.5:         W.append(f"High volatility — beta {beta}")
            if not W:              W.append("Consistent execution needed to sustain valuations")
            for w in W:
                st.markdown(f"<div class='con-card'>❌ {w}</div>", unsafe_allow_html=True)

        with c_r:
            st.markdown("#### Opportunities")
            for o in [
                "India GDP 7%+ growth — strong macro tailwind",
                f"{sector} sector seeing structural expansion in India",
                "PLI schemes and government capex push",
                "Growing middle class driving consumption upgrade",
                "Digital India and financialization of savings",
                "China+1 strategy — India gaining manufacturing share",
            ]:
                st.markdown(f"<div class='opp-card'>🚀 {o}</div>", unsafe_allow_html=True)

            st.markdown("#### Threats")
            for th in [
                "Global macro uncertainty — FII outflows can pressure valuations",
                "RBI monetary tightening — higher rates compress P/E multiples",
                f"Intense competition in {industry}",
                "Regulatory and compliance policy changes",
                "INR depreciation impact on import-heavy businesses",
                "Commodity price volatility affecting input costs",
            ]:
                st.markdown(f"<div class='threat-card'>⚠️ {th}</div>", unsafe_allow_html=True)

    with t8:
        st.markdown("### AI Quantitative Signal Engine")
        score   = 0
        signals = []
        checks = [
            (current > ema50_now,    f"Price Rs{current} above 50 EMA Rs{ema50_now}",   "Short-term bullish momentum",       f"Price below 50 EMA Rs{ema50_now}",    "Short-term bearish pressure"),
            (current > ema200_now,   f"Price Rs{current} above 200 EMA Rs{ema200_now}", "Long-term uptrend intact",          f"Price below 200 EMA Rs{ema200_now}",  "Long-term downtrend"),
            (ema50_now > ema200_now, "50 EMA above 200 EMA — Golden Cross",             "Bullish structural alignment",      "50 EMA below 200 EMA — Death Cross",   "Bearish structure"),
            (30 < rsi_now < 70,      f"RSI {rsi_now} — Neutral zone",                  "Healthy momentum zone",             f"RSI {rsi_now} extreme reading",        "Overbought or oversold"),
            (macd_now > 0,           f"MACD {macd_now} positive",                      "Bullish momentum confirmed",        f"MACD {macd_now} negative",             "Bearish momentum"),
            (roe > 15,               f"ROE {roe}% strong returns",                      "High quality business",             f"ROE {roe}% below benchmark",           "Weak equity returns"),
            (debt_eq < 0.5,          f"D/E {debt_eq} — low leverage",                  "Financial strength",                f"D/E {debt_eq} — high leverage",        "Balance sheet risk"),
            (rev_growth > 10,        f"Revenue +{rev_growth}%",                         "Strong business momentum",          f"Revenue growth {rev_growth}%",         "Weak top-line growth"),
        ]
        for cond,pos_l,pos_n,neg_l,neg_n in checks:
            if cond:
                score += 1
                signals.append(("✅", pos_l, pos_n, "#10B981"))
            else:
                signals.append(("❌", neg_l, neg_n, "#EF4444"))

        for icon,label,note,color in signals:
            st.markdown(f"""
            <div style='background:#1F2937;border:1px solid #2D3748;border-left:3px solid {color};
                        border-radius:8px;padding:12px 16px;margin:5px 0;
                        display:flex;justify-content:space-between;align-items:center;'>
                <span style='color:#F3F4F6;font-weight:600;font-size:14px;'>{icon} {label}</span>
                <span style='color:#9CA3AF;font-size:13px;'>{note}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if score >= 7:
            css,text,sub = "signal-buy",  "STRONG BUY",    f"Score {score}/8 — Exceptional alignment"
        elif score >= 5:
            css,text,sub = "signal-buy",  "BUY",           f"Score {score}/8 — Majority indicators bullish"
        elif score == 4:
            css,text,sub = "signal-hold", "HOLD / WATCH",  f"Score {score}/8 — Mixed signals"
        elif score == 3:
            css,text,sub = "signal-hold", "CAUTIOUS HOLD", f"Score {score}/8 — More bearish than bullish"
        else:
            css,text,sub = "signal-sell", "SELL / AVOID",  f"Score {score}/8 — Significant red flags"

        st.markdown(f"<div class='{css}'>🎯 {text}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#9CA3AF;font-size:14px;margin-top:8px;'>{sub}</p>", unsafe_allow_html=True)
        st.caption("For educational purposes only. Not financial advice.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;color:#6B7280;font-size:13px;'>
    For educational purposes only. Not financial advice.<br>
    Built by <b style='color:#F3F4F6;'>Pratyush Singh</b> |
    MBA Banking & Financial Engineering | Chandigarh University
    </p>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {str(e)[:300]}")
    st.info("Try again in 2 minutes — Yahoo Finance rate limits apply.")
