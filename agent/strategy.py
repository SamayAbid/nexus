from dataclasses import dataclass
from typing import Literal
import pandas as pd
import pandas_ta as ta
from agent.signals import SignalComponents
from agent.regime import TRENDING, RANGING

Action = Literal["long", "short", "hold"]

@dataclass
class TradeSignal:
    action: Action
    pair: str
    strategy: str  # "trend_following" | "mean_reversion" | "none"

TREND_THRESHOLD = 0.55
MEAN_REV_THRESHOLD = 0.45
RSI_OVERSOLD = 32.0
RSI_OVERBOUGHT = 68.0
BB_TOUCH_MARGIN = 0.95  # price within 5% of band counts as touch

def _ema_crossover(df: pd.DataFrame) -> Literal["bullish", "bearish", "none"]:
    ema9  = ta.ema(df["close"], length=9)
    ema21 = ta.ema(df["close"], length=21)
    if ema9 is None or ema21 is None or len(ema9.dropna()) < 2:
        return "none"
    if ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2]:
        return "bullish"
    if ema9.iloc[-1] < ema21.iloc[-1] and ema9.iloc[-2] >= ema21.iloc[-2]:
        return "bearish"
    return "none"

def get_trade_signal(
    df: pd.DataFrame,
    signals: SignalComponents,
    regime: str,
    pair: str,
) -> TradeSignal:
    if regime == TRENDING:
        crossover = _ema_crossover(df)
        if crossover == "bullish" and signals.composite > TREND_THRESHOLD:
            return TradeSignal("long", pair, "trend_following")
        if crossover == "bearish" and signals.composite < -TREND_THRESHOLD:
            return TradeSignal("short", pair, "trend_following")

    elif regime == RANGING:
        oversold  = signals.rsi_raw < RSI_OVERSOLD
        overbought = signals.rsi_raw > RSI_OVERBOUGHT
        lower_bb  = signals.bb < -BB_TOUCH_MARGIN
        upper_bb  = signals.bb > BB_TOUCH_MARGIN

        if oversold and lower_bb and signals.composite > MEAN_REV_THRESHOLD:
            return TradeSignal("long", pair, "mean_reversion")
        if overbought and upper_bb and signals.composite < -MEAN_REV_THRESHOLD:
            return TradeSignal("short", pair, "mean_reversion")

    return TradeSignal("hold", pair, "none")
