import numpy as np
import pandas as pd
import pytest
from agent.regime import classify_regime, TRENDING, RANGING

def make_ohlcv(n: int = 100, high_multiplier: float = 1.002, low_multiplier: float = 0.998, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    prices = 50000.0 + np.cumsum(np.random.randn(n) * 150)
    return pd.DataFrame({
        "open":   prices * 0.999,
        "high":   prices * high_multiplier,
        "low":    prices * low_multiplier,
        "close":  prices,
        "volume": np.ones(n),
    })

def test_classify_regime_returns_valid_value():
    df = make_ohlcv()
    result = classify_regime(df)
    assert result in (TRENDING, RANGING)

def test_high_range_bars_are_trending():
    df = make_ohlcv(n=100)
    df.loc[df.index[-3:], "high"] = df["close"].iloc[-3:] * 1.15
    df.loc[df.index[-3:], "low"]  = df["close"].iloc[-3:] * 0.85
    assert classify_regime(df) == TRENDING

def test_tight_range_bars_are_ranging():
    df = make_ohlcv(n=100)
    df.loc[df.index[-3:], "high"] = df["close"].iloc[-3:] * 1.00005
    df.loc[df.index[-3:], "low"]  = df["close"].iloc[-3:] * 0.99995
    assert classify_regime(df) == RANGING

def test_too_few_bars_defaults_to_ranging():
    df = make_ohlcv(n=5)
    assert classify_regime(df) == RANGING

def test_trending_constant():
    assert TRENDING == "trending"

def test_ranging_constant():
    assert RANGING == "ranging"
