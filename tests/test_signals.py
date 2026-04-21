import numpy as np
import pandas as pd
import pytest
from agent.signals import (
    SignalComponents, compute_signals,
    _norm_rsi, _norm_macd, _norm_vwap, _norm_bb
)

def make_ohlcv(n: int = 60, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    prices = 50000.0 + np.cumsum(np.random.randn(n) * 150)
    return pd.DataFrame({
        "open":   prices * 0.999,
        "high":   prices * 1.002,
        "low":    prices * 0.998,
        "close":  prices,
        "volume": np.random.uniform(1.0, 10.0, n),
    })

def test_norm_rsi_midpoint_is_zero():
    assert _norm_rsi(50.0) == pytest.approx(0.0)

def test_norm_rsi_max_is_one():
    assert _norm_rsi(100.0) == pytest.approx(1.0)

def test_norm_rsi_min_is_minus_one():
    assert _norm_rsi(0.0) == pytest.approx(-1.0)

def test_norm_macd_clips_to_range():
    assert _norm_macd(macd_hist=10000.0, price=100.0) == pytest.approx(1.0)
    assert _norm_macd(macd_hist=-10000.0, price=100.0) == pytest.approx(-1.0)

def test_norm_vwap_price_above_is_positive():
    assert _norm_vwap(price=101.0, vwap=100.0) > 0

def test_norm_vwap_price_below_is_negative():
    assert _norm_vwap(price=99.0, vwap=100.0) < 0

def test_norm_bb_above_mid_is_positive():
    assert _norm_bb(price=105.0, upper=110.0, lower=90.0, mid=100.0) > 0

def test_norm_bb_below_mid_is_negative():
    assert _norm_bb(price=95.0, upper=110.0, lower=90.0, mid=100.0) < 0

def test_norm_bb_zero_bandwidth_returns_zero():
    assert _norm_bb(price=100.0, upper=100.0, lower=100.0, mid=100.0) == 0.0

def test_compute_signals_returns_dataclass():
    df = make_ohlcv()
    result = compute_signals(df, sentiment=0.0)
    assert isinstance(result, SignalComponents)

def test_composite_score_in_range():
    df = make_ohlcv()
    result = compute_signals(df, sentiment=0.0)
    assert -1.0 <= result.composite <= 1.0

def test_all_components_in_range():
    df = make_ohlcv()
    result = compute_signals(df, sentiment=0.3)
    for val in [result.rsi, result.macd, result.vwap, result.bb, result.sentiment, result.composite]:
        assert -1.0 <= val <= 1.0

def test_sentiment_none_uses_fallback_weights():
    df = make_ohlcv()
    result = compute_signals(df, sentiment=None)
    assert result.sentiment == pytest.approx(0.0)
    assert -1.0 <= result.composite <= 1.0

def test_rsi_raw_in_valid_range():
    df = make_ohlcv()
    result = compute_signals(df, sentiment=0.0)
    assert 0.0 <= result.rsi_raw <= 100.0

def test_weights_sum_check_with_sentiment():
    from agent.signals import WEIGHTS
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)

def test_weights_sum_check_without_sentiment():
    from agent.signals import WEIGHTS_NO_SENTIMENT
    assert sum(WEIGHTS_NO_SENTIMENT.values()) == pytest.approx(1.0)
