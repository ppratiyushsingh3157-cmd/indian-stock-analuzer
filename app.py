import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Hedge Fund Terminal", layout="wide")

st.title("💼 Hedge Fund Research Terminal")
st.caption("Quant + Fundamental + Momentum Stock Intelligence System")

# ---------------- WATCHLIST ----------------
WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "META", "NFLX",
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "LT.NS", "SBIN.NS"
]

# ---------------- DATA ----------------
@st.cache_data
def get_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")

    if hist.empty:
        return None

    returns = hist["Close"].pct_change().dropna()

    return {
        "ticker": ticker,
        "price": info.get("currentPrice"),
        "pe": info.get("trailingPE"),
        "roe": info.get("returnOnEquity", 0),
        "debt_equity": info.get("debtToEquity"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "volatility": returns.std() * np.sqrt(252),  # annualized
        "momentum": (hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1,
        "hist": hist
    }

# ---------------- SCORING ENGINE ----------------
def score_stock(s):
    score = 0

    # Value
    if s["pe"] and s["pe"] < 25:
        score += 2

    # Quality
    if s["roe"] and s["roe"] > 0.15:
        score += 2

    # Risk control
    if s["debt_equity"] and s["debt_equity"] < 1:
        score += 1

    # Momentum
    if s["momentum"] > 0.1:
        score += 2

    # Risk penalty
    if s["volatility"] < 0.3:
        score += 1

    return score

# ---------------- LOAD ALL ----------------
data = []
for t in WATCHLIST:
    d = get_data(t)
    if d:
        d["score"] = score_stock(d)
        data.append(d)

df = pd.DataFrame(data)

# ---------------- SIDEBAR ----------------
st.sidebar.header("🎯 Hedge Fund Filters")

min_score = st.sidebar.slider("Min Score", 0, 8, 4)
sector_filter = st.sidebar.multiselect("Sector Filter", df["sector"].dropna().unique())

filtered = df[df["score"] >= min_score]

if sector_filter:
    filtered = filtered[filtered["sector"].isin(sector_filter)]

# ---------------- TOP PICKS ----------------
st.subheader("🏆 Top Hedge Fund Picks")

top = filtered.sort_values("score", ascending=False).head(5)

st.dataframe(
    top[["ticker", "price", "pe", "roe", "momentum", "volatility", "score"]],
    use_container_width=True
)

# ---------------- FULL SCREEN ----------------
st.subheader("📊 Full Universe Ranking")

st.dataframe(
    filtered.sort_values("score", ascending=False),
    use_container_width=True
)

# ---------------- STOCK DEEP DIVE ----------------
st.subheader("🔍 Stock Deep Dive")

selected = st.selectbox("Select Stock", df["ticker"])

stock = df[df["ticker"] == selected].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Price", stock["price"])
col2.metric("Score", stock["score"])
col3.metric("Momentum", round(stock["momentum"], 2))
col4.metric("Volatility", round(stock["volatility"], 2))

st.markdown("### 📌 Hedge Fund View")

if stock["score"] >= 6:
    st.success("🟢 Strong Institutional Buy Candidate")
elif stock["score"] >= 4:
    st.warning("🟡 Watch / Accumulate Zone")
else:
    st.error("🔴 Avoid / High Risk")

# ---------------- CHART ----------------
st.subheader("📈 Price Action (1Y)")

st.line_chart(stock["hist"]["Close"])

# ---------------- RISK DASHBOARD ----------------
st.subheader("⚖️ Risk vs Return Map")

st.scatter_chart(df[["momentum", "volatility"]])
