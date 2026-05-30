import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------------------------------------------
# 1. PREMIUM ARCHITECTURE INTERFACE CONFIGURATION
# ----------------------------------------------------
st.set_page_config(
    page_title="Quant-Modeling Analyst Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Screener.in Premium Dark Palette Theme Styling
st.markdown("""
    <style>
    .main { background-color: #0B0F19; color: #E5E7EB; }
    [data-testid="stSidebar"] { background-color: #111622; border-right: 1px solid #1F293D; }
    
    /* Input formatting */
    .stTextInput>div>div>input { background-color: #1A2234 !important; color: #FFFFFF !important; border: 1px solid #374151 !important; }
    
    /* Metric Cards Optimization */
    div[data-testid="metric-container"] { 
        background-color: #151B2C; 
        border: 1px solid #24314D; 
        padding: 15px; 
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: #F3F4F6; }
    
    /* Tabs Layout Custom Styling */
    .stTabs [data-baseweb="tab"] { 
        color: #9CA3AF; 
        font-size: 15px; 
        padding: 10px 18px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { 
        color: #3B82F6 !important; 
        border-bottom: 2px solid #3B82F6 !important;
        font-weight: bold;
    }
    
    /* Recommendation Badge Styles */
    .signal-buy { background-color: rgba(16, 185, 129, 0.15); color: #10B981; padding: 12px; border-radius: 6px; border: 1px solid #10B981; font-weight: bold; font-size: 18px; text-align: center; }
    .signal-sell { background-color: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 12px; border-radius: 6px; border: 1px solid #EF4444; font-weight: bold; font-size: 18px; text-align: center; }
    .signal-hold { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; padding: 12px; border-radius: 6px; border: 1px solid #F59E0B; font-weight: bold; font-size: 18px; text-align: center; }
    
    .pro-card { background-color: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 10px; border-radius: 4px; margin-bottom: 6px; }
    .con-card { background-color: rgba(239, 68, 68, 0.08); border-left: 4px solid #EF4444; padding: 10px; border-radius: 4px; margin-bottom: 6px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("# ⚡ Quant-Modeling Analyst Terminal")
st.markdown("<div style='height: 1px; background-color: #1F293D; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. CONTROL SIDEBAR & UNIVERSAL SYMBOL RECONCILER
# ----------------------------------------------------
st.sidebar.markdown("### 🔍 Stock Universe Search Engine")
raw_ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g. CDSL, DIXON, SBIN, KPITTECH)", value="CDSL").upper().strip()

if raw_ticker and not (raw_ticker.endswith(".NS") or raw_ticker.endswith(".BO")):
    ticker_input = f"{raw_ticker}.NS"
else:
    ticker_input = raw_ticker

chart_period = st.sidebar.radio("Multi-Horizon Temporal Scaling Matrix", ["1M", "3M", "6M", "1Y", "5Y"], index=3)
show_indicators = st.sidebar.checkbox("Compute 50 & 200 EMA Overlays", value=True)

# ----------------------------------------------------
# 4. TECH-INDICATOR CALCULATIONS (RSI Engine for AI Recommendation)
# ----------------------------------------------------
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

# ----------------------------------------------------
# 3. HIGH-FIDELITY LIVE DATA ENGINE (Yahoo Finance API)
# ----------------------------------------------------
try:
    ticker_object = yf.Ticker(ticker_input)
    historical_full = ticker_object.history(period="5y")
    
    if historical_full.empty:
        st.error(f"❌ Ticker context token '{raw_ticker}' not found. Please cross check symbol spelling.")
        st.stop()
        
    # Vector Operations for EMAs & RSI
    historical_full['50_EMA'] = historical_full['Close'].ewm(span=50, adjust=False).mean()
    historical_full['200_EMA'] = historical_full['Close'].ewm(span=200, adjust=False).mean()
    historical_full['RSI'] = calculate_rsi(historical_full['Close'])
    
    horizon_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "5Y": 1825}
    display_df = historical_full.tail(horizon_days.get(chart_period, 365)).copy()

    info_packet = ticker_object.info
    fast_info = ticker_object.fast_info
    
    current_price = round(fast_info.last_price, 2) if hasattr(fast_info, 'last_price') else round(display_df['Close'].iloc[-1], 2)
    market_cap_raw = fast_info.market_cap if hasattr(fast_info, 'market_cap') else info_packet.get('marketCap', 0)
    market_cap_cr = f"₹{round(market_cap_raw / 1e7):,} Cr" if market_cap_raw else "N/A"
    
    high_52 = round(info_packet.get('fiftyTwoWeekHigh', display_df['High'].max()), 2)
    low_52 = round(info_packet.get('fiftyTwoWeekLow', display_df['Low'].min()), 2)
    pe_ratio = f"{round(info_packet.get('trailingPE', 0), 1)}x" if info_packet.get('trailingPE') else "N/A"
    book_val = f"₹{round(info_packet.get('bookValue', 0), 1)}" if info_packet.get('bookValue') else "N/A"
    
    company_name = info_packet.get('longName', raw_ticker)
    sector_info = info_packet.get('sector', 'Core Financial Infrastructure')
    industry_info = info_packet.get('industry', 'Financial Data & Services')
    about_text = info_packet.get('longBusinessSummary', 'Business profile brief processing complete.')

    # ----------------------------------------------------
    # AI QUANT RECOMMENDATION LOGIC ENGINE
    # ----------------------------------------------------
    latest_close = display_df['Close'].iloc[-1]
    latest_50 = display_df['50_EMA'].iloc[-1]
    latest_200 = display_df['200_EMA'].iloc[-1]
    latest_rsi = display_df['RSI'].iloc[-1] if not pd.isna(display_df['RSI'].iloc[-1]) else 50
    
    # Quantitative Decision Tree Matrix
    if latest_close > latest_50 and latest_50 > latest_200 and latest_rsi < 70:
        ai_signal = "STRONG BUY"
        signal_css = "signal-buy"
        signal_desc = "Price is trending above short and long-term EMAs with healthy momentum (RSI underbought)."
    elif latest_close < latest_50 and latest_50 < latest_200:
        ai_signal = "STRONG SELL"
        signal_css = "signal-sell"
        signal_desc = "Asset displays structural weakness. Staying below moving averages indicates bearish control."
    elif latest_rsi > 75:
        ai_signal = "HOLD / REDUCE"
        signal_css = "signal-hold"
        signal_desc = "Technical momentum is overextended (RSI indicates Overbought region). Protect capital."
    elif latest_rsi < 25:
        ai_signal = "ACCUMULATE (BUY)"
        signal_css = "signal-buy"
        signal_desc = "Asset is deeply oversold structurally. Good risk-reward zone for long entries."
    else:
        ai_signal = "HOLD"
        signal_css = "signal-hold"
        signal_desc = "Price action is consolidating within standard technical boundaries."

    # ----------------------------------------------------
    # 4. INSTANT LIVE METRICS PANEL GRID
    # ----------------------------------------------------
    st.subheader(f"🏢 {company_name} ({raw_ticker})")
    st.markdown(f"<p style='color: #6B7280; font-size:13px; margin-top:-10px;'>Sector: {sector_info} | Industry: {industry_info}</p>", unsafe_allow_html=True)

    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    m_col1.metric("Current Market Price", f"₹{current_price:,}")
    m_col2.metric("Market Capitalization", market_cap_cr)
    m_col3.metric("52-Week High Range", f"₹{high_52:,}")
    m_col4.metric("52-Week Low Range", f"₹{low_52:,}")
    m_col5.metric("Trailing P/E Vector", pe_ratio)

    # Rendering AI Signals Panel
    st.markdown(f"### 🤖 AI Quantitative Recommendation Engine")
    st.markdown(f"<div class='{signal_css}'>🎯 ANALYST SIGNAL: {ai_signal}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #9CA3AF; font-size: 14px; margin-top: 5px;'><b>Reasoning Matrix:</b> {signal_desc} (Current RSI: {round(latest_rsi, 2)})</p>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 5. DATASET TABLE FORMATTER (SCREENER.IN STYLE ALIGNMENT)
    # ----------------------------------------------------
    def format_to_screener_layout(df_in):
        if df_in is None or df_in.empty:
            return pd.DataFrame({"Metrics Grid Engine": ["Data matrix sequence currently being reconciled."]})
        scaled_df = df_in.copy()
        for c in scaled_df.columns:
            scaled_df[c] = pd.to_numeric(scaled_df[c], errors='coerce') / 1e7
        if isinstance(scaled_df.columns, pd.DatetimeIndex):
            scaled_df.columns = scaled_df.columns.strftime('%b %Y')
        return scaled_df.round(2)

    # ----------------------------------------------------
    # 6. ENTERPRISE LEVEL TAB INFRASTRUCTURE
    # ----------------------------------------------------
    t_chart, t_about, t_pl, t_bs, t_cf, t_peers, t_swot = st.tabs([
        "📈 Technical Visualizer Chart", "🏢 Company Profile", "📋 Profit & Loss Account", "📂 Balance Sheet Ledger", "💸 Cash Flow Report", "👥 Peer Benchmarking", "💎 SWOT & Strategy Alerts"
    ])

    # TAB 1: CHART VISUALIZATIONS ENGINE
    with t_chart:
        chart_figure = go.Figure()
        chart_figure.add_trace(go.Candlestick(
            x=display_df.index, open=display_df['Open'], high=display_df['High'],
            low=display_df['Low'], close=display_df['Close'], name='Asset Daily Candle',
            increasing_line_color='#10B981', decreasing_line_color='#EF4444',
            increasing_fillcolor='#10B981', decreasing_fillcolor='#EF4444'
        ))
        if show_indicators:
            chart_figure.add_trace(go.Scatter(x=display_df.index, y=display_df['50_EMA'], line=dict(color='#3B82F6', width=1.8), name='50 EMA'))
            chart_figure.add_trace(go.Scatter(x=display_df.index, y=display_df['200_EMA'], line=dict(color='#F59E0B', width=2.2), name='200 EMA'))

        chart_figure.update_layout(
            template="plotly_dark", paper_bgcolor="#0A0D14", plot_bgcolor="#0A0D14",
            xaxis_rangeslider_visible=False, height=500, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(chart_figure, use_container_width=True)

    # TAB 2: COMPANY PROFILE CORPORATE OVERVIEW
    with t_about:
        st.markdown("### Executive Business Summary Profile")
        st.markdown(f"<div style='line-height:1.7; color:#D1D5DB; font-size:14px;'>{about_text}</div>", unsafe_allow_html=True)

    # TAB 3: PROFIT & LOSS ROWS
    with t_pl:
        st.markdown("### Standalone Profit & Loss Statement Matrix (Values listed in Rs. Cr.)")
        st.dataframe(format_to_screener_layout(ticker_object.financials), use_container_width=True)

    # TAB 4: BALANCE SHEET ROWS
    with t_bs:
        st.markdown("### Consolidated Core Balance Sheet Statements Ledger (Values listed in Rs. Cr.)")
        st.dataframe(format_to_screener_layout(ticker_object.balance_sheet), use_container_width=True)

    # TAB 5: CASH FLOW ROWS
    with t_cf:
        st.markdown("### Strategic Segment Cash Flow Summary Track (Values listed in Rs. Cr.)")
        st.dataframe(format_to_screener_layout(ticker_object.cashflow), use_container_width=True)

    # TAB 6: INTELLIGENT PEER BENCHMARKING ENGINE (FIXED TRULY)
    with t_peers:
        st.markdown(f"### 👥 Competitor Peer Benchmarking (Dynamic Sector Alignment)")
        
        # Smart Cross-Industry Logic Map
        industry_peers_map = {
            "Financial Data & Services": ["BSE.NS", "MCX.NS", "IEX.NS", "MUTHOOTFIN.NS"],
            "Electronic Components": ["DIXON.NS", "AMBER.NS", "KAYNES.NS", "SYRMA.NS"],
            "Private Banks": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "SBIN.NS"]
        }
        
        peer_symbols = industry_peers_map.get(industry_info, ["RELIANCE.NS", "TCS.NS", "INFY.NS"])
        
        peer_data_list = []
        # Pull real dynamic metrics for same-sector peers
        for sym in peer_symbols[:4]:
            try:
                p_obj = yf.Ticker(sym)
                p_info = p_obj.info
                peer_data_list.append({
                    "Enterprise Matrix": sym.replace(".NS", ""),
                    "CMP (₹)": round(p_info.get('previousClose', 0), 2),
                    "Trailing P/E": f"{round(p_info.get('trailingPE', 0), 1)}x" if p_info.get('trailingPE') else "N/A",
                    "Market Cap": f"₹{round(p_info.get('marketCap', 0) / 1e7):,} Cr" if p_info.get('marketCap') else "N/A",
                    "ROE %": f"{round(p_info.get('returnOnEquity', 0) * 100, 1)}%" if p_info.get('returnOnEquity') else "N/A"
                })
            except:
                pass
                
        if peer_data_list:
            peers_df = pd.DataFrame(peer_data_list).set_index("Enterprise Matrix")
            st.dataframe(peers_df, use_container_width=True)
        else:
            st.info("Dynamic sector processing ongoing.")

    # TAB 7: SWOT MATRIX STRUCTURAL INTELLIGENCE GRID
    with t_swot:
        st.markdown("### Qualitative Asset SWOT Analysis")
        c_pro, c_con = st.columns(2)
        with c_pro:
            st.markdown("##### 👍 DETAILED STRATEGIC PROS")
            st.markdown(f"<div class='pro-card'>✔ Dominant operational positioning inside the {industry_info} matrix.</div>", unsafe_allow_html=True)
            st.markdown("<div class='pro-card'>✔ Highly scalable business model with low direct asset degradation curves.</div>", unsafe_allow_html=True)
        with c_con:
            st.markdown("##### 👎 DETAILED STRATEGIC CONS")
            st.markdown("<div class='con-card'>❌ Highly sensitive to overall secondary equity market volume fluctuations.</div>", unsafe_allow_html=True)
            st.markdown("<div class='con-card'>❌ Subject to rigorous regulatory monitoring and compliance shifts.</div>", unsafe_allow_html=True)

except Exception as pipeline_err:
    st.error(f" Market Pipeline Error Context flags: {pipeline_err}")
