import streamlit as st
import pandas as pd
import ccxt
import numpy as np

# ----------------------------------------
# Robust OHLCV Fetcher with Fallback
# ----------------------------------------
def get_ohlcv(symbol, timeframe="15m"):
    # Try CoinDCX first
    try:
        exchange = ccxt.coindcx()
        exchange.load_markets()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    except Exception as e:
        st.warning(f"CoinDCX failed for {symbol}, trying Binance... ({e})")
        try:
            exchange = ccxt.binance()
            exchange.load_markets()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        except Exception as e2:
            raise RuntimeError(f"Both CoinDCX and Binance failed for {symbol}: {e2}")

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# ----------------------------------------
# Pattern 1: Bullish Flag
# ----------------------------------------
def detect_bullish_flag(df):
    recent = df.tail(20)
    prices = recent["close"].values
    return (
        prices[-1] > prices[-2] > prices[-3]
        and prices[-4] > prices[-3]
        and prices[-5] > prices[-4]
        and prices[-6] > prices[-5]
    )

# ----------------------------------------
# Pattern 2: Bullish Pennant
# ----------------------------------------
def detect_bullish_pennant(df):
    recent = df.tail(30)
    closes = recent["close"].values
    max_idx = np.argmax(closes)
    min_idx = np.argmin(closes)
    return min_idx < max_idx and max_idx > len(closes) - 5

# ----------------------------------------
# Pattern 3: Double Bottom
# ----------------------------------------
def detect_double_bottom(df):
    recent = df.tail(50)
    closes = recent["close"].values
    minima = (closes[1:-1] < closes[:-2]) & (closes[1:-1] < closes[2:])
    min_indices = np.where(minima)[0] + 1
    if len(min_indices) >= 2:
        for i in range(len(min_indices) - 1):
            if abs(closes[min_indices[i]] - closes[min_indices[i + 1]]) / closes[min_indices[i]] < 0.02:
                return True
    return False

# ----------------------------------------
# Streamlit UI
# ----------------------------------------
st.set_page_config(page_title="Multi-Exchange Bullish Pattern Scanner", layout="wide")
st.title("📈 Multi-Exchange Bullish Pattern Scanner")

coins = ["PIPPIN/USDT", "SOL/USDT", "BTC/USDT", "ETH/USDT", "DOGE/USDT"]

if st.button("🔍 Scan Now"):
    results = []
    for symbol in coins:
        try:
            df = get_ohlcv(symbol)
            flag = detect_bullish_flag(df)
            pennant = detect_bullish_pennant(df)
            double_bottom = detect_double_bottom(df)

            patterns = []
            if flag:
                patterns.append("🏴 Bullish Flag")
            if pennant:
                patterns.append("📍 Bullish Pennant")
            if double_bottom:
                patterns.append("〰️ Double Bottom")

            results.append({
                "Symbol": symbol,
                "Detected Patterns": ", ".join(patterns) if patterns else "No Pattern"
            })

        except Exception as e:
            results.append({"Symbol": symbol, "Detected Patterns": f"❌ Error: {str(e)}"})

    st.dataframe(pd.DataFrame(results))
