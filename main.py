
import pandas as pd
import streamlit as st
from strategies.flag_breakout import detect_bullish_flag

# Mock function to simulate fetching OHLCV from CoinDCX (replace with actual fetch)
def get_ohlcv(symbol, timeframe="15m"):
    import ccxt
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Telegram alert function
def send_telegram(msg):
    import requests
    token = "7965615706:AAHHHFwMHYgRumpWgDeU3FdI0lllbNvtEGg"
    chat_id = "1096439077"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# Streamlit app
st.title("CoinDCX Bullish Flag Breakout Detector")
symbol = st.text_input("Enter symbol (e.g. PIPPIN/USDT):", "PIPPIN/USDT")

if st.button("Scan Now"):
    df = get_ohlcv(symbol)
    signal = detect_bullish_flag(df)

    if signal:
        st.success(f"🚀 Breakout detected at {signal['breakout_price']} USDT")
        send_telegram(f"🚨 {symbol} breakout above {signal['resistance']}! Current: {signal['breakout_price']}")
    else:
        st.warning("No breakout yet. Pattern still forming.")
