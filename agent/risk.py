from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

@dataclass
class OrderParameters:
    pair: str
    direction: Literal["long", "short"]
    size: float
    stop_loss: float
    take_profit: float

@dataclass
class RiskState:
    open_positions: int
    daily_pnl: float
    starting_equity: float
    circuit_breaker_active: bool
    circuit_breaker_reset_date: str  # UTC "YYYY-MM-DD"

MAX_OPEN_POSITIONS = 3
MAX_POSITION_SIZE_PCT = 0.02
CIRCUIT_BREAKER_PCT = -0.05
TRAILING_TRIGGER_PCT = 0.02
TRAILING_TRAIL_PCT = 0.008

STOP_LOSS_PCT = {"trend_following": 0.015, "mean_reversion": 0.012}
TAKE_PROFIT_PCT = {"trend_following": 0.030, "mean_reversion": 0.020}

def compute_position_size(equity: float) -> float:
    return equity * MAX_POSITION_SIZE_PCT

def compute_stop_loss(entry: float, direction: str, strategy: str) -> float:
    pct = STOP_LOSS_PCT.get(strategy, 0.015)
    return entry * (1 - pct) if direction == "long" else entry * (1 + pct)

def compute_take_profit(entry: float, direction: str, strategy: str) -> float:
    pct = TAKE_PROFIT_PCT.get(strategy, 0.030)
    return entry * (1 + pct) if direction == "long" else entry * (1 - pct)

def can_open_position(state: RiskState) -> bool:
    if state.circuit_breaker_active:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if state.circuit_breaker_reset_date == today:
            return False
    return state.open_positions < MAX_OPEN_POSITIONS

def check_and_trigger_circuit_breaker(state: RiskState) -> RiskState:
    ratio = state.daily_pnl / state.starting_equity if state.starting_equity else 0
    if ratio <= CIRCUIT_BREAKER_PCT:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return RiskState(
            open_positions=state.open_positions,
            daily_pnl=state.daily_pnl,
            starting_equity=state.starting_equity,
            circuit_breaker_active=True,
            circuit_breaker_reset_date=today,
        )
    return state

def update_trailing_stop(
    current_price: float, direction: str,
    trailing_high: float, stop_loss: float
) -> tuple[float, float]:
    if direction == "long":
        new_high = max(trailing_high, current_price)
        new_stop = new_high * (1 - TRAILING_TRAIL_PCT)
        return new_high, max(stop_loss, new_stop)
    else:
        new_high = min(trailing_high, current_price)
        new_stop = new_high * (1 + TRAILING_TRAIL_PCT)
        return new_high, min(stop_loss, new_stop)

def build_order(
    pair: str, direction: str, strategy: str,
    entry_price: float, equity: float, state: RiskState
) -> OrderParameters | None:
    if not can_open_position(state):
        return None
    return OrderParameters(
        pair=pair,
        direction=direction,
        size=compute_position_size(equity),
        stop_loss=compute_stop_loss(entry_price, direction, strategy),
        take_profit=compute_take_profit(entry_price, direction, strategy),
    )
