
import pandas as pd

def detect_bullish_flag(df, lookback=20):
    '''
    Detects bullish flag breakout in OHLCV dataframe.
    '''
    if len(df) < lookback:
        return None

    recent_high = df["high"].iloc[-lookback:-5].max()
    recent_low = df["low"].iloc[-lookback:-5].min()
    current_price = df["close"].iloc[-1]

    if current_price > recent_high:
        return {
            "signal": "BREAKOUT",
            "breakout_price": current_price,
            "resistance": recent_high,
            "support": recent_low
        }
    return None
