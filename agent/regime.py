import numpy as np
import pandas as pd
import pandas_ta as ta

TRENDING = "trending"
RANGING = "ranging"

def classify_regime(df: pd.DataFrame, percentile: int = 70, min_bars: int = 15) -> str:
    atr = ta.atr(df["high"], df["low"], df["close"], length=14)
    if atr is None:
        return RANGING
    clean = atr.dropna()
    if len(clean) < min_bars:
        return RANGING
    current_atr = float(clean.iloc[-1])
    p70 = float(np.percentile(clean, percentile))
    return TRENDING if current_atr > p70 else RANGING
