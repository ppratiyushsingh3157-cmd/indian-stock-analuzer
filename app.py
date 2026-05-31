import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Screener Clone", layout="wide")

st.title("📊 Screener.in Style Stock Research Tool")
st.caption("Search stocks • Screen • Analyze • Compare")

# ---------------- WATCHLIST ----------------
WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "LT.NS", "ITC.NS",
    "AAPL", "MSFT", "GOOGL", "AMZN"
]

# ---------------- FETCH FUNCTION ----------------
@st.cache_data
def get_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")
    return info, hist

# ---------------- SEARCH SECTION ----------------
st.subheader("🔎 Search Any Stock")

query = st.text_input("Enter Stock Symbol (e.g. RELIANCE.NS, TCS.NS, AAPL)")

if query:

    info, hist = get_stock(query)

    if not hist.empty:

        st.subheader(f"🏢 {info.get('shortName')}")

        # ---------------- METRICS ----------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Price", info.get("currentPrice"))
        col2.metric("P/E", info.get("trailingPE"))
        col3.metric("ROE", info.get("returnOnEquity"))
        col4.metric("Market Cap", info.get("marketCap"))

        st.divider()

        # ---------------- FUNDAMENTALS ----------------
        st.subheader("📊 Fundamentals")

        df = pd.DataFrame([{
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "P/B": info.get("priceToBook"),
            "Debt/Equity": info.get("debtToEquity"),
            "Profit Margin": info.get("profitMargins"),
            "52W High": info.get("fiftyTwoWeekHigh"),
            "52W Low": info.get("fiftyTwoWeekLow"),
        }])

        st.dataframe(df, use_container_width=True)

        # ---------------- 52 WEEK RANGE ----------------
        st.subheader("📈 52 Week Position")

        price = info.get("currentPrice")
        low = info.get("fiftyTwoWeekLow")
        high = info.get("fiftyTwoWeekHigh")

        if price and low and high:
            progress = (price - low) / (high - low)
            st.progress(float(progress))
            st.write(f"Low: {low} | High: {high}")

        # ---------------- CHART ----------------
        st.subheader("📉 Price Chart (1 Year)")
        st.line_chart(hist["Close"])

        # ---------------- SIMPLE SCORING ----------------
        st.subheader("🧠 Quick Analysis")

        score = 0

        if info.get("trailingPE") and info["trailingPE"] < 25:
            score += 1

        if info.get("returnOnEquity") and info["returnOnEquity"] > 0.15:
            score += 1

        if info.get("debtToEquity") and info["debtToEquity"] < 1:
            score += 1

        if score == 3:
            st.success("🟢 Strong Stock (Good Fundamentals)")
        elif score == 2:
            st.warning("🟡 Neutral Stock")
        else:
            st.error("🔴 Weak Fundamentals")

# ---------------- SCREENER ----------------
st.divider()
st.subheader("📊 Mini Screener (Top Stocks)")

data = []

for t in WATCHLIST:
    info, _ = get_stock(t)

    data.append({
        "Stock": t,
        "Price": info.get("currentPrice"),
        "PE": info.get("trailingPE"),
        "ROE": info.get("returnOnEquity"),
        "Market Cap": info.get("marketCap")
    })

df = pd.DataFrame(data)

# filters
max_pe = st.slider("Max P/E", 0, 100, 30)
min_roe = st.slider("Min ROE", 0.0, 1.0, 0.15)

filtered = df[
    (df["PE"].fillna(999) <= max_pe) &
    (df["ROE"].fillna(0) >= min_roe)
]

st.dataframe(filtered, use_container_width=True)

