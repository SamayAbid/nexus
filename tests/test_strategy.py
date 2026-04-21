import numpy as np
import pandas as pd
import pytest
from agent.signals import SignalComponents
from agent.regime import TRENDING, RANGING
from agent.strategy import get_trade_signal, TradeSignal

def make_signals(rsi_raw: float = 50.0, composite: float = 0.0, bb: float = 0.0) -> SignalComponents:
    from agent.signals import _norm_rsi
    return SignalComponents(
        rsi_raw=rsi_raw, rsi=_norm_rsi(rsi_raw),
        macd=0.0, vwap=0.0, bb=bb,
        sentiment=0.0, composite=composite
    )

def make_ohlcv_with_ema_crossover(direction: str = "bullish", n: int = 30) -> pd.DataFrame:
    prices = np.linspace(50000, 50500, n) if direction == "bullish" else np.linspace(50500, 50000, n)
    return pd.DataFrame({
        "open": prices * 0.999, "high": prices * 1.001,
        "low": prices * 0.999, "close": prices, "volume": np.ones(n)
    })

def make_ohlcv_flat(n: int = 30) -> pd.DataFrame:
    prices = np.full(n, 50000.0)
    return pd.DataFrame({
        "open": prices, "high": prices * 1.0001,
        "low": prices * 0.9999, "close": prices, "volume": np.ones(n)
    })

def test_hold_when_signal_below_trend_threshold():
    df = make_ohlcv_with_ema_crossover("bullish")
    signals = make_signals(composite=0.30)  # below 0.55
    result = get_trade_signal(df, signals, TRENDING, "BTC/USD")
    assert result.action == "hold"

def test_hold_when_ranging_no_rsi_extreme():
    df = make_ohlcv_flat()
    signals = make_signals(rsi_raw=50.0, composite=0.60)
    result = get_trade_signal(df, signals, RANGING, "BTC/USD")
    assert result.action == "hold"

def test_mean_reversion_long_on_oversold_lower_bb():
    df = make_ohlcv_flat()
    signals = make_signals(rsi_raw=28.0, composite=0.50, bb=-1.0)
    result = get_trade_signal(df, signals, RANGING, "BTC/USD")
    assert result.action == "long"
    assert result.strategy == "mean_reversion"

def test_mean_reversion_short_on_overbought_upper_bb():
    df = make_ohlcv_flat()
    signals = make_signals(rsi_raw=72.0, composite=-0.50, bb=1.0)
    result = get_trade_signal(df, signals, RANGING, "BTC/USD")
    assert result.action == "short"
    assert result.strategy == "mean_reversion"

def test_trade_signal_carries_pair():
    df = make_ohlcv_flat()
    signals = make_signals(rsi_raw=28.0, composite=0.50, bb=-1.0)
    result = get_trade_signal(df, signals, RANGING, "ETH/USD")
    assert result.pair == "ETH/USD"

def test_hold_returns_none_strategy():
    df = make_ohlcv_flat()
    signals = make_signals(composite=0.0)
    result = get_trade_signal(df, signals, TRENDING, "BTC/USD")
    assert result.action == "hold"
    assert result.strategy == "none"
