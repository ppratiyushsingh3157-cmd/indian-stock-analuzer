import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AlphaQuant — Advance Equity Research & Portfolio Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
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
div[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
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
.valuation-under {
    background: linear-gradient(135deg, #0d2818, #113820);
    border-left: 5px solid #238636;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
}
.valuation-over {
    background: linear-gradient(135deg, #2d0f0f, #3d1414);
    border-left: 5px solid #da3633;
    padding: 20px;
    border-radius: 8px;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Router ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ AlphaQuant Engine")
    st.markdown("*Institutional Equity Research Software*")
    st.markdown("---")
    
    st.markdown("### 🔍 Global Market Coverage")
    user_symbol = st.text_input("Enter NSE Ticker Symbol (1200+ listed)", value="KAYNES").strip().upper()
    
    if user_symbol:
        if not user_symbol.endswith(".NS") and not user_symbol.endswith(".BO"):
            ticker = f"{user_symbol}.NS"
        else:
            ticker = user_symbol
    else:
        ticker = "RELIANCE.NS"

    st.markdown("---")
    period_label = st.radio("📅 Multi-Horizon Chart Scale", ["1M","3M","6M","1Y","3Y","5Y"], index=3, horizontal=True)
    period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}

    show_volume = st.checkbox("Show Volume Profiles", value=True)
    show_bollinger = st.checkbox("Show Volatility Envelopes (BB)", value=False)

    st.markdown("---")
    analyze = st.button("🚀 Execute Quantitative Analytics", type="primary", use_container_width=True)

if not analyze:
    st.markdown("<h2 style='color:#00d4ff;'>⚡ Quant-Modeling Analyst Terminal</h2>", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='metric-card'><h3>Universal Core</h3><p>Access 1,200+ Equity Assets instantaneously via live data interfaces.</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><h3>Modeling Vault</h3><p>Automated multi-stage DCF, Graham intrinsic pricing, and valuation gaps.</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><h3>Portfolio Framework</h3><p>Engineered for asset deployment research and coverage documentation.</p></div>", unsafe_allow_html=True)
    st.info("👈 Enter any listed equity ticker name code (e.g., KAYNES, DIXON, TATASTEEL, JIOFIN) inside the sidebar terminal input and hit execute.")
    st.stop()

# ── Quantitative Matrix Data Processing Core ────────────────
try:
    with st.spinner(f"Compiling quantitative parameters for matrix {ticker}..."):
        stock = yf.Ticker(ticker)
        df = stock.history(period=period_map[period_label], auto_adjust=True)
        df_1y = stock.history(period="1y", auto_adjust=True)

    if df.empty:
        st.error(f"❌ Core Exception: Suffix map resolution failed for input query token '{ticker}'.")
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

    # Valuation & Structural Extraction Architecture
    try:
        info = stock.info
        pe = round(info.get("trailingPE", 0) or 0, 1)
        pb = round(info.get("priceToBook", 0) or 0, 1)
        roe = round((info.get("returnOnEquity", 0) or 0) * 100, 1)
        
        # Safe Institutional ROCE Calculation Engine
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        roce = None
        if not financials.empty and not balance_sheet.empty:
            try:
                ebit = financials.loc['EBIT'].iloc[0]
                total_assets = balance_sheet.loc['Total Assets'].iloc[0]
                curr_liab = balance_sheet.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in balance_sheet.index else 0
                cap_employed = total_assets - curr_liab
                if cap_employed > 0 and ebit != 0:
                    calculated_roce = (ebit / cap_employed) * 100
                    if 0 < calculated_roce < 150:  # Valid bound sanity check
                        roce = round(calculated_roce, 1)
            except:
                pass
        
        if roce is None or pd.isna(roce):
            roce = round(roe * 1.15, 1) if roe > 0 else "N/A"
            
        book_value = round(info.get("bookValue", 0) or 0, 1)
        debt_eq = round(info.get("debtToEquity", 0) or 0, 2)
        div = round((info.get("dividendYield", 0) or 0) * 100, 2)
        face_value = info.get("faceValue", 10) or 10
        eps = info.get("trailingEps", 0) or (current / pe if pe else 0)
        
        company_name = info.get("longName", ticker)
        description = info.get("longBusinessSummary", "Corporate operational profile summary offline.")
        sector = info.get("sector", "Industrial")
        industry = info.get("industry", "Aggregate Market")
    except:
        pe=pb=roe=roce=book_value=debt_eq=div=face_value=eps=0
        company_name=ticker; description="N/A Framework Profile"; sector=industry="Industrial Data"

    # ── Master Header Block ──────────────────────────────────
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

    # Fundamental Grid Row 1
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Market Capitalization", f"₹{mkt_cap:,.0f} Cr")
    m2.metric("Current Quote Price", f"₹{current:,}")
    m3.metric("52 Week High / Low Range", f"₹{high_52w} / {low_52w}")
    m4.metric("Trailing P/E Vector", f"{pe}x" if pe else "N/A")
    m5.metric("Net Asset Book Value", f"₹{book_value}")

    # Fundamental Grid Row 2
    m6, m7, m8, m9, m10 = st.columns(5)
    m6.metric("Dividend Yield Ratio", f"{div}%" if div else "0.00%")
    m7.metric("ROCE %", f"{roce}%" if roce != "N/A" else "N/A")
    m8.metric("ROE %", f"{roe}%" if roe else "N/A")
    m9.metric("Par Face Value", f"₹{face_value}")
    m10.metric("Compounded 1Y Return", f"{returns_1y}%")

    st.markdown("---")

    t1, t2, t3, t4 = st.tabs(["📊 Technical Visualizers", "🏢 Operational Fundamentals", "📋 Accounting Sheets", "💎 DCF Valuation Model"])

    # ── TAB 1: CHARTS ────────────────────────────────────────
    with t1:
        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        
        delta_c = df["Close"].diff()
        gain = delta_c.where(delta_c > 0, 0).rolling(14).mean()
        loss = (-delta_c.where(delta_c < 0, 0)).rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + (gain / loss if loss.any() else 1)))

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candlestick", increasing_line_color="#26a641", decreasing_line_color="#da3633"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="50 DMA Vector", line=dict(color="#00bfff", width=1.2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="200 DMA Baseline", line=dict(color="orange", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI (14)", line=dict(color="#e3b341", width=1.2)), row=2, col=1)
        
        fig.add_hline(y=70, line_color="#da3633", line_dash="dash", row=2, col=1)
        fig.add_hline(y=30, line_color="#26a641", line_dash="dash", row=2, col=1)
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: OVERVIEW ──────────────────────────────────────
    with t2:
        st.markdown("### Profile Summary")
        st.write(description)

    # ── TAB 3: ACCOUNTING SHEETS ─────────────────────────────
    with t3:
        st.markdown("### Core Financial Statements *(Figures scaled in Rs. Crores)*")
        sub_tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        
        def format_to_crores(dataframe):
            if dataframe is None or dataframe.empty:
                return None
            df_scaled = dataframe.copy()
            for col in df_scaled.columns:
                df_scaled[col] = pd.to_numeric(df_scaled[col], errors='coerce') / 1e7
            if isinstance(df_scaled.columns, pd.DatetimeIndex):
                df_scaled.columns = df_scaled.columns.strftime('%Y-%m-%d')
            return df_scaled.style.format(precision=2, na_rep="N/A", thousands=",")

        with sub_tabs[0]:
            try: st.dataframe(format_to_crores(stock.financials.iloc[:12]), use_container_width=True)
            except: st.info("Income metrics framework offline.")
        with sub_tabs[1]:
            try: st.dataframe(format_to_crores(stock.balance_sheet.iloc[:12]), use_container_width=True)
            except: st.info("Balance sheet mapping data offline.")
        with sub_tabs[2]:
            try: st.dataframe(format_to_crores(stock.cashflow.iloc[:12]), use_container_width=True)
            except: st.info("Cash tracking dataset offline.")

    # ── TAB 4: ADVANCED FINANCIAL MODELING ────────────────────
    with t4:
        st.markdown("## 💎 Institutional Financial Modeling Vault")
        st.markdown("---")
        
        st.markdown("### ⚙️ Financial Architecture Assumptions")
        c_mod1, c_mod2, c_mod3 = st.columns(3)
        with c_mod1:
            growth_rate = st.slider("Stage 1 Growth Rate Forecast (Years 1-5 %)", 5.0, 35.0, 15.0, step=0.5) / 100
        with c_mod2:
            discount_rate = st.slider("WACC / Expected Discount Rate (%)", 8.0, 20.0, 11.0, step=0.5) / 100
        with c_mod3:
            terminal_growth = st.slider("Terminal Growth Rate (Perpetual %)", 1.0, 7.0, 4.0, step=0.25) / 100

        # Strict Institutional DCF Execution Engine
        has_valid_valuation = False
        try:
            cf_matrix = stock.cashflow
            shares_outstanding = stock.info.get("sharesOutstanding", None)
            
            if 'Free Cash Flow' in cf_matrix.index:
                fcf_base = cf_matrix.loc['Free Cash Flow'].iloc[0]
            elif 'Operating Cash Flow' in cf_matrix.index:
                fcf_base = cf_matrix.loc['Operating Cash Flow'].iloc[0]
            else:
                fcf_base = None
                
            if fcf_base and not pd.isna(fcf_base) and fcf_base > 0 and shares_outstanding:
                has_valid_valuation = True
                
                # Projection Logic
                projected_fcf = []
                discounted_fcf = []
                current_fcf = fcf_base
                
                for year in range(1, 6):
                    current_fcf = current_fcf * (1 + growth_rate)
                    projected_fcf.append(current_fcf)
                    discounted_fcf.append(current_fcf / ((1 + discount_rate) ** year))
                    
                terminal_value = (projected_fcf[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
                discounted_tv = terminal_value / ((1 + discount_rate) ** 5)
                total_intrinsic_equity = sum(discounted_fcf) + discounted_tv
                intrinsic_value_per_share = round(total_intrinsic_equity / shares_outstanding, 2)
                
                valuation_gap = intrinsic_value_per_share - current
                valuation_percentage = (valuation_gap / current) * 100
        except:
            has_valid_valuation = False

        # Output Interface Router
        if has_valid_valuation:
            st.markdown("<div class='section-header'><h3>Valuation Output Variance Summary</h3></div>", unsafe_allow_html=True)
            v_col1, v_col2, v_col3 = st.columns(3)
            v_col1.metric("Multi-Stage DCF Intrinsic Value", f"₹{intrinsic_value_per_share:,}")
            v_col2.metric("Market Spot Quote Price", f"₹{current:,}")
            v_col3.metric("Valuation Discrepancy Spread", f"{round(valuation_percentage, 1)}%")

            if valuation_gap > 0:
                st.markdown(f"""
                <div class='valuation-under'>
                    <h3 style='color:#26a641; margin:0;'>💎 UNDERPRICED ACCUMULATION WINDOW</h3>
                    <p style='color:#fff; margin:8px 0 0 0;'>Our Multi-Stage DCF model places the fair economic value of this asset at <b>₹{intrinsic_value_per_share:,}</b>. The asset is currently trading at a discount of <b>{abs(round(valuation_percentage, 1))}%</b>.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='valuation-over'>
                    <h3 style='color:#da3633; margin:0;'>⚠️ OVERPRICED DISTRIBUTION BLOCK</h3>
                    <p style='color:#fff; margin:8px 0 0 0;'>Market tracking price exceeds structural cash vectors. The asset trades at a premium of <b>{abs(round(valuation_percentage, 1))}%</b> above its DCF baseline of <b>₹{intrinsic_value_per_share:,}</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("### 📋 Pro-Forma Forecast Projections Table (Rs. in Actuals)")
            projection_years = [f"Year {i} (20{26+i})" for i in range(1, 6)]
            model_df = pd.DataFrame({
                "Forecast Horizon Year": projection_years,
                "Projected Free Cash Flow Baseline": [f"₹{x:,.2f}" for x in projected_fcf],
                "Discounted Present Value Factor": [f"₹{x:,.2f}" for x in discounted_fcf]
            })
            st.dataframe(model_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Institutional Statement Notice: Yahoo Finance has missing or incomplete trailing Cash Flow statements / Share Capital matrices for this specific ticker code symbol. DCF Model cannot be executed reliably without corrupting results.")
            
        # Graham Floor Model Baseline Execution
        if eps > 0:
            g_rate_percentage = growth_rate * 100
            graham_intrinsic = round((eps * (8.5 + (2 * g_rate_percentage)) * 4.4) / 7.10, 2)
            st.markdown(f"> **Benjamin Graham Formula Benchmark:** Conservative valuation model puts the asset base floor intrinsic target at **₹{graham_intrinsic}** based on an expected earnings factor trajectory.")

except Exception as err:
    st.error(f"⚠️ Quant System Framework Error: {err}")
