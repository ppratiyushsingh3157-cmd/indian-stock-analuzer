import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up clean app layout page configuration
st.set_page_config(page_title="Equity Research & Portfolio Analytics Suite", layout="wide")

# Ensure matplotlib is available in the background environment
try:
    import matplotlib
except ImportError:
    st.error("Missing dependency: Please ensure 'matplotlib' is installed via pip.")

# -------------------------------------------------------------------
# 1. SIDEBAR CONFIGURATION & TICKER DICTIONARY (NIFTY 100)
# -------------------------------------------------------------------
st.sidebar.title("📊 Equity Research Suite")
st.sidebar.subheader("BFE Analytics Engine")

nifty_100_tickers = {
    "ABB India": "ABB.NS", "ACC": "ACC.NS", "Adani Enterprises": "ADANIENT.NS", 
    "Adani Green Energy": "ADANIGREEN.NS", "Adani Ports": "ADANIPORTS.NS", "Adani Power": "ADANIPOWER.NS",
    "Ambuja Cements": "AMBUJACEM.NS", "Apollo Hospitals": "APOLLOHOSP.NS", "Asian Paints": "ASIANPAINT.NS", 
    "Avenue Supermarts (DMart)": "DMART.NS", "Axis Bank": "AXISBANK.NS", "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Bajaj Finance": "BAJFINANCE.NS", "Bajaj Finserv": "BAJAJFINSV.NS", "Bajaj Holdings": "BAJAJHLDNG.NS", 
    "Bank of Baroda": "BANKBARODA.NS", "Bharat Electronics (BEL)": "BEL.NS", "Bharti Airtel": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS", "Britannia Industries": "BRITANNIA.NS", "BSE Limited": "BSE.NS", 
    "Canara Bank": "CANBK.NS", "Cipla": "CIPLA.NS", "Coal India": "COALINDIA.NS", 
    "Colgate-Palmolive": "COLPAL.NS", "Cummins India": "CUMMINSIND.NS", "DLF": "DLF.NS", 
    "Dabur India": "DABUR.NS", "Divi's Laboratories": "DIVISLAB.NS", "Dr. Reddy's": "DRREDDY.NS", 
    "Eicher Motors": "EICHERMOT.NS", "GAIL": "GAIL.NS", "Godrej Consumer Products": "GODREJCP.NS", 
    "Grasim Industries": "GRASIM.NS", "HCL Technologies": "HCLTECH.NS", "HDFC Bank": "HDFCBANK.NS", 
    "HDFC Life": "HDFCLIFE.NS", "Hero MotoCorp": "HEROMOTOCO.NS", "Hindalco Industries": "HINDALCO.NS", 
    "Hindustan Unilever": "HINDUNILVR.NS", "ICICI Bank": "ICICIBANK.NS", "ICICI Lombard": "ICICIGI.NS", 
    "ICICI Prudential Life": "ICICIPRULI.NS", "ITC": "ITC.NS", "Indian Oil Corporation (IOC)": "IOC.NS", 
    "IRCTC": "IRCTC.NS", "IRFC": "IRFC.NS", "IndusInd Bank": "INDUSINDBK.NS", 
    "Infosys": "INFY.NS", "InterGlobe Aviation (Indigo)": "INDIGO.NS", "JSW Steel": "JSWSTEEL.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS", "Larsen & Toubro (L&T)": "LT.NS", "LTIMindtree": "LTIM.NS", 
    "M&M": "M&M.NS", "Maruti Suzuki": "MARUTI.NS", "Muthoot Finance": "MUTHOOTFIN.NS", 
    "Nestle India": "NESTLEIND.NS", "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", 
    "Pidilite Industries": "PIDILITIND.NS", "Power Grid Corporation": "POWERGRID.NS", "PFC": "PFC.NS", 
    "Reliance Industries": "RELIANCE.NS", "SBI Cards": "SBICARD.NS", "SBI Life Insurance": "SBILIFE.NS", 
    "SRF Limited": "SRF.NS", "Samvardhana Motherson": "MOTHERSON.NS", "Shree Cement": "SHREECEM.NS", 
    "Shriram Finance": "SHRIRAMFIN.NS", "Siemens": "SIEMENS.NS", "State Bank of India (SBI)": "SBIN.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Tata Communications": "TATACOMM.NS", "Tata Consumer Products": "TATACONSUM.NS", 
    "Tata Motors": "TATAMOTORS.NS", "Tata Power": "TATAPOWER.NS", "Tata Steel": "TATASTEEL.NS",
    "TCS": "TCS.NS", "Tech Mahindra": "TECHM.NS", "Titan Company": "TITAN.NS", 
    "Trent": "TRENT.NS", "TVS Motor Company": "TVSMOTOR.NS", "UltraTech Cement": "ULTRACEMCO.NS", 
    "United Spirits (McDowell's)": "UNITDSPR.NS", "Varun Beverages (VBL)": "VBL.NS", "Vedanta": "VEDL.NS", 
    "Wipro": "WIPRO.NS", "Zomato": "ZOMATO.NS", "Zydus Lifesciences": "ZYDUSLIFE.NS", 
    "Hindustan Aeronautics (HAL)": "HAL.NS", "Jio Financial Services": "JIOFIN.NS", "REC Limited": "REC.NS"
}

selected_display_name = st.sidebar.selectbox("Select Target Enterprise", list(nifty_100_tickers.keys()))
target_ticker = nifty_100_tickers[selected_display_name]

chart_period = st.sidebar.selectbox("Analysis Horizon", ["1 Month", "3 Months", "1 Year", "5 Years"], index=2)
period_mapping = {"1 Month": "1mo", "3 Months": "3mo", "1 Year": "1y", "5 Years": "5y"}
selected_period = period_mapping[chart_period]

st.title(f"🔍 Analytics Dashboard: {selected_display_name} ({target_ticker.replace('.NS','')})")

@st.cache_data(ttl=3600)
def load_financial_profile(ticker_symbol):
    ticker_obj = yf.Ticker(ticker_symbol)
    return ticker_obj.info, ticker_obj

try:
    with st.spinner("Compiling fundamental metrics matrices..."):
        info_dict, ticker_instance = load_financial_profile(target_ticker)
except Exception as e:
    st.error(f"Data connection timeout for {target_ticker}. Details: {e}")
    st.stop()

# Top KPIs Ribbon Display
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Current Stock Price", f"₹ {info_dict.get('currentPrice', 'N/A')}")
kpi2.metric("Market Cap (Cr)", f"₹ {round(info_dict.get('marketCap', 0) / 10000000, 2):,}" if info_dict.get('marketCap') else "N/A")
kpi3.metric("Trailing P/E Ratio", f"{round(info_dict.get('trailingPE', 0), 2)}" if info_dict.get('trailingPE') else "N/A")
kpi4.metric("Enterprise Value / EBITDA", f"{round(info_dict.get('enterpriseToEbitda', 0), 2)}" if info_dict.get('enterpriseToEbitda') else "N/A")

st.markdown("---")

t1, t2, t3, t4 = st.tabs(["📈 Dynamic Technical Charts", "📋 Financial Statements Data", "👥 Peer Group Benchmarking", "🎯 Intrinsic Valuation Mode"])

# ===================================================================
# TAB 1: DYNAMIC TECHNICAL CHARTS
# ===================================================================
with t1:
    st.subheader("Technical Matrix Indicators Panel")
    interval_setting = "1d"
    if selected_period == "1mo":
        interval_setting = "1h"
        
    hist_prices = ticker_instance.history(period=selected_period, interval=interval_setting)
    
    if hist_prices.empty:
        st.warning("Insufficient trading interval data returned for this asset selection.")
    else:
        hist_prices['SMA_20'] = hist_prices['Close'].rolling(window=20).mean()
        rolling_std = hist_prices['Close'].rolling(window=20).std()
        hist_prices['BB_Upper'] = hist_prices['SMA_20'] + (2 * rolling_std)
        hist_prices['BB_Lower'] = hist_prices['SMA_20'] - (2 * rolling_std)
        
        hist_prices['VWAP'] = (hist_prices['Volume'] * (hist_prices['High'] + hist_prices['Low'] + hist_prices['Close']) / 3).cumsum() / hist_prices['Volume'].cumsum()
        
        price_delta = hist_prices['Close'].diff()
        positive_gains = price_delta.clip(lower=0)
        negative_losses = -1 * price_delta.clip(upper=0)
        ema_gains = positive_gains.ewm(com=13, adjust=False).mean()
        ema_losses = negative_losses.ewm(com=13, adjust=False).mean()
        rs_factor = ema_gains / ema_losses.replace(0, 0.00001)
        hist_prices['RSI_14'] = 100 - (100 / (1 + rs_factor))
        
        fh_chart = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
        
        fh_chart.add_trace(go.Candlestick(
            x=hist_prices.index, open=hist_prices['Open'], high=hist_prices['High'],
            low=hist_prices['Low'], close=hist_prices['Close'], name="Price Action"
        ), row=1, col=1)
        
        fh_chart.add_trace(go.Scatter(x=hist_prices.index, y=hist_prices['VWAP'], line=dict(color='orange', width=1.5), name='VWAP'), row=1, col=1)
        fh_chart.add_trace(go.Scatter(x=hist_prices.index, y=hist_prices['BB_Upper'], line=dict(color='rgba(173,216,230,0.6)', width=1, dash='dash'), name='BB Upper'), row=1, col=1)
        fh_chart.add_trace(go.Scatter(x=hist_prices.index, y=hist_prices['BB_Lower'], line=dict(color='rgba(173,216,230,0.6)', width=1, dash='dash'), name='BB Lower'), row=1, col=1)
        
        fh_chart.add_trace(go.Scatter(x=hist_prices.index, y=hist_prices['RSI_14'], line=dict(color='#3a86ff', width=1.8), name='RSI (14)'), row=2, col=1)
        fh_chart.add_hline(y=70, line_dash="dash", line_color="rgba(255,0,0,0.4)", row=2, col=1)
        fh_chart.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,0,0.4)", row=2, col=1)
        
        fh_chart.update_layout(
            height=650,
            xaxis_rangeslider_visible=False,
            margin=dict(l=40, r=40, t=20, b=20),
            annotations=[
                dict(
                    x=0.01, y=0.97, xref="paper", yref="paper",
                    text="<b>MAIN PANEL INDICATORS:</b> <span style='color:orange;'>● VWAP</span> | <span style='color:cyan;'>-- Bollinger Bands (20,2)</span>",
                    showarrow=False, font=dict(size=12, color="white"),
                    bgcolor="rgba(20,20,20,0.8)", bordercolor="gray", borderpad=5
                ),
                dict(
                    x=0.01, y=0.28, xref="paper", yref="paper",
                    text="<b>OSCILLATOR PANEL:</b> <span style='color:#3a86ff;'>● RSI (14)</span> [Overbought > 70 | Oversold < 30]",
                    showarrow=False, font=dict(size=12, color="white"),
                    bgcolor="rgba(20,20,20,0.8)", bordercolor="gray", borderpad=5
                )
            ]
        )
        
        fh_chart.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
        st.plotly_chart(fh_chart, use_container_width=True)

# ===================================================================
# TAB 2: FINANCIAL STATEMENTS DATA
# ===================================================================
with t2:
    st.subheader("Core Financial Statement Matrices")
    statement_view = st.radio("Toggle Document Perspective", ["Income Statement", "Balance Sheet", "Cash Flow"], horizontal=True)
    
    try:
        if statement_view == "Income Statement":
            raw_matrix = ticker_instance.financials
        elif statement_view == "Balance Sheet":
            raw_matrix = ticker_instance.balance_sheet
        else:
            raw_matrix = ticker_instance.cashflow
            
        if raw_matrix is None or raw_matrix.empty:
            st.warning(f"No indexed reports records found on Yahoo Finance for {target_ticker}")
        else:
            display_matrix = raw_matrix.copy()
            for col in display_matrix.columns:
                display_matrix[col] = pd.to_numeric(display_matrix[col], errors='coerce')
                
            display_matrix_crores = display_matrix / 10000000
            display_matrix_crores = display_matrix_crores.round(2).fillna("-")
            
            try:
                styled_view = display_matrix_crores.style.background_gradient(axis=1, cmap="RdYlGn")
                st.dataframe(styled_view, use_container_width=True)
            except Exception:
                st.dataframe(display_matrix_crores, use_container_width=True)
                
            st.caption("All statement line-item figures listed above are calibrated in Indian Crores (₹ Cr).")
    except Exception as financial_err:
        st.error(f"Failed to compile financial statements: {financial_err}")

# ===================================================================
# TAB 3: PEER GROUP BENCHMARKING
# ===================================================================
with t3:
    st.subheader("Sector Comparative Peer Benchmarking")
    
    @st.cache_data(ttl=3600)
    def gather_sector_peer_nodes(current_symbol, target_name):
        energy_oil_peers = ["RELIANCE.NS", "BPCL.NS", "IOC.NS", "HPCL.NS", "MRPL.NS", "CHENNPETRO.NS"]
        it_services_peers = ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS"]
        banking_peers = ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BANKBARODA.NS"]
        auto_peers = ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS", "TVSMOTOR.NS"]
        
        clean_symbol = str(current_symbol).upper()
        clean_name = str(target_name).upper()
        
        if "RELIANCE" in clean_symbol or "RELIANCE" in clean_name:
            return energy_oil_peers
        elif any(x in clean_symbol for x in ["TCS", "INFY", "WIPRO", "HCL", "TECHM", "LTIM"]):
            return it_services_peers
        elif any(x in clean_symbol for x in ["BANK", "SBIN", "AXIS", "KOTAK"]):
            return banking_peers
        elif any(x in clean_symbol for x in ["MOTOR", "MARUTI", "BAJAJ", "EICHER", "TVS"]):
            return auto_peers
            
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "BHARTIARTL.NS"]

    peer_ticker_list = gather_sector_peer_nodes(target_ticker, selected_display_name)
    peer_records_accumulator = []
    
    with st.spinner("Compiling competitive benchmarking tables..."):
        for symbol_item in peer_ticker_list:
            try:
                peer_info, _ = load_financial_profile(symbol_item)
                peer_records_accumulator.append({
                    "Ticker Symbol": symbol_item.replace(".NS", ""),
                    "Company Name": peer_info.get("longName", "N/A"),
                    "Market Cap (Cr)": round(peer_info.get("marketCap", 0) / 10000000, 2) if peer_info.get("marketCap") else None,
                    "P/E Ratio": round(peer_info.get("trailingPE", 0), 2) if peer_info.get("trailingPE") else None,
                    "Price to Book (P/B)": round(peer_info.get("priceToBook", 0), 2) if peer_info.get("priceToBook") else None,
                    "Dividend Yield (%)": round(peer_info.get("dividendYield", 0) * 100, 2) if peer_info.get("dividendYield") else 0.0,
                    "Return on Equity (ROE %)": round(peer_info.get("returnOnEquity", 0) * 100, 2) if peer_info.get("returnOnEquity") else None
                })
            except Exception:
                continue
                
    if peer_records_accumulator:
        benchmarking_dataframe = pd.DataFrame(peer_records_accumulator)
        st.dataframe(benchmarking_dataframe.fillna("-"), use_container_width=True, hide_index=True)
    else:
        st.warning("Could not cross-reference market data feeds for peers.")

# ===================================================================
# TAB 4: INTRINSIC VALUATION MODE
# ===================================================================
with t4:
    st.subheader("Discounted Cash Flow (DCF) Valuation Engine")
    st.markdown("Calculate intrinsic equity values using traditional growth projection assumptions.")
    
    historical_eps = info_dict.get('trailingEps')
    
    if not historical_eps or historical_eps <= 0:
        st.warning("⚠️ Trailing 12-Month EPS is negative or missing. Traditional positive-growth DCF models require positive baseline earnings.")
        historical_eps = st.number_input("Manually enter a normalized baseline positive EPS value to unlock modeling:", value=10.0, step=1.0)
        
    vc1, vc2, vc3 = st.columns(3)
    growth_stage_1 = vc1.slider("Stage 1 Growth Rate (Years 1-5 %)", min_value=1.0, max_value=40.0, value=12.0, step=0.5) / 100
    growth_stage_2 = vc2.slider("Stage 2 Growth Rate (Years 6-10 %)", min_value=1.0, max_value=30.0, value=6.0, step=0.5) / 100
    discount_rate_wacc = vc3.slider("Required Rate of Discount / WACC (%)", min_value=5.0, max_value=25.0, value=11.0, step=0.5) / 100
    
    terminal_growth_g = 0.04
    
    projected_eps_series = []
    discount_factors_series = []
    pv_earnings_series = []
    current_eps_cursor = historical_eps
    
    for year_idx in range(1, 6):
        current_eps_cursor *= (1 + growth_stage_1)
        discount_multiplier = (1 + discount_rate_wacc) ** year_idx
        present_value_step = current_eps_cursor / discount_multiplier
        
        projected_eps_series.append(current_eps_cursor)
        discount_factors_series.append(discount_multiplier)
        pv_earnings_series.append(present_value_step)
        
    for year_idx in range(6, 11):
        current_eps_cursor *= (1 + growth_stage_2)
        discount_multiplier = (1 + discount_rate_wacc) ** year_idx
        present_value_step = current_eps_cursor / discount_multiplier
        
        projected_eps_series.append(current_eps_cursor)
        discount_factors_series.append(discount_multiplier)
        pv_earnings_series.append(present_value_step)
        
    estimated_terminal_value = (projected_eps_series[-1] * (1 + terminal_growth_g)) / (discount_rate_wacc - terminal_growth_g)
    pv_of_terminal_value = estimated_terminal_value / discount_factors_series[-1]
    
    calculated_intrinsic_value = sum(pv_earnings_series) + pv_of_terminal_value
    current_market_price = info_dict.get('currentPrice', 1.0)
    variance_pct = ((calculated_intrinsic_value - current_market_price) / current_market_price) * 100
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Calculated Intrinsic Value", f"₹ {round(calculated_intrinsic_value, 2)}")
    res2.metric("Market Price (Current)", f"₹ {round(current_market_price, 2)}")
    
    if variance_pct > 0:
        res3.metric("Valuation Margin", f"Undervalued by {round(variance_pct, 1)}%", delta=f"{round(variance_pct, 1)}% Margin of Safety")
    else:
        res3.metric("Valuation Margin", f"Overvalued by {round(abs(variance_pct), 1)}%", delta=f"-{round(abs(variance_pct), 1)}% Premium Over Value", delta_color="inverse")
