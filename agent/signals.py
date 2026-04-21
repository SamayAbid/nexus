import numpy as np
import pandas as pd
import pandas_ta as ta
from dataclasses import dataclass

WEIGHTS = {"rsi": 0.30, "macd": 0.25, "vwap": 0.15, "bb": 0.15, "sentiment": 0.15}
WEIGHTS_NO_SENTIMENT = {"rsi": 0.35, "macd": 0.30, "vwap": 0.18, "bb": 0.17}

@dataclass
class SignalComponents:
    rsi_raw: float    # raw RSI value [0, 100] — used by strategy layer
    rsi: float        # normalised [-1, +1]
    macd: float       # normalised [-1, +1]
    vwap: float       # normalised [-1, +1]
    bb: float         # normalised [-1, +1]
    sentiment: float  # [-1, +1]
    composite: float  # weighted sum [-1, +1]

def _norm_rsi(rsi_val: float) -> float:
    return float(np.clip((rsi_val - 50.0) / 50.0, -1.0, 1.0))

def _norm_macd(macd_hist: float, price: float) -> float:
    if price == 0:
        return 0.0
    return float(np.clip(macd_hist / (price * 0.01), -1.0, 1.0))

def _norm_vwap(price: float, vwap: float) -> float:
    if vwap == 0:
        return 0.0
    return float(np.clip((price - vwap) / vwap, -1.0, 1.0))

def _norm_bb(price: float, upper: float, lower: float, mid: float) -> float:
    band_width = upper - lower
    if band_width == 0:
        return 0.0
    return float(np.clip(2.0 * (price - mid) / band_width, -1.0, 1.0))

def compute_signals(df: pd.DataFrame, sentiment: float | None) -> SignalComponents:
    close = df["close"]
    price = float(close.iloc[-1])

    rsi_series = ta.rsi(close, length=14)
    rsi_raw = float(rsi_series.dropna().iloc[-1]) if not rsi_series.dropna().empty else 50.0
    rsi_norm = _norm_rsi(rsi_raw)

    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_hist = float(macd_df["MACDh_12_26_9"].dropna().iloc[-1]) if macd_df is not None and not macd_df["MACDh_12_26_9"].dropna().empty else 0.0
    macd_norm = _norm_macd(macd_hist, price)

    vwap_val = float((df["close"] * df["volume"]).sum() / df["volume"].sum())
    vwap_norm = _norm_vwap(price, vwap_val)

    bb_df = ta.bbands(close, length=20, std=2)
    if bb_df is not None:
        cols = bb_df.columns.tolist()
        upper_col = next((c for c in cols if c.startswith("BBU_")), None)
        lower_col = next((c for c in cols if c.startswith("BBL_")), None)
        mid_col   = next((c for c in cols if c.startswith("BBM_")), None)
    if bb_df is not None and upper_col and not bb_df[upper_col].dropna().empty:
        bb_upper = float(bb_df[upper_col].dropna().iloc[-1])
        bb_lower = float(bb_df[lower_col].dropna().iloc[-1])
        bb_mid   = float(bb_df[mid_col].dropna().iloc[-1])
        bb_norm = _norm_bb(price, bb_upper, bb_lower, bb_mid)
    else:
        bb_norm = 0.0

    if sentiment is not None:
        s_norm = float(np.clip(sentiment, -1.0, 1.0))
        composite = (
            WEIGHTS["rsi"] * rsi_norm + WEIGHTS["macd"] * macd_norm +
            WEIGHTS["vwap"] * vwap_norm + WEIGHTS["bb"] * bb_norm +
            WEIGHTS["sentiment"] * s_norm
        )
        return SignalComponents(rsi_raw=rsi_raw, rsi=rsi_norm, macd=macd_norm,
                                vwap=vwap_norm, bb=bb_norm, sentiment=s_norm,
                                composite=float(np.clip(composite, -1.0, 1.0)))
    else:
        composite = (
            WEIGHTS_NO_SENTIMENT["rsi"] * rsi_norm + WEIGHTS_NO_SENTIMENT["macd"] * macd_norm +
            WEIGHTS_NO_SENTIMENT["vwap"] * vwap_norm + WEIGHTS_NO_SENTIMENT["bb"] * bb_norm
        )
        return SignalComponents(rsi_raw=rsi_raw, rsi=rsi_norm, macd=macd_norm,
                                vwap=vwap_norm, bb=bb_norm, sentiment=0.0,
                                composite=float(np.clip(composite, -1.0, 1.0)))
